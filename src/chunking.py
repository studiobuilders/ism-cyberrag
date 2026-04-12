import re


# Regex to match the ISM control metadata line
_CONTROL_RE = re.compile(
    r"Control:\s*ISM-(\d+);\s*Revision:\s*(\d+);\s*Updated:\s*([\w-]+);\s*"
    r"Applicable:\s*([^;]+);\s*Essential\s*8:\s*(.+)",
    re.IGNORECASE,
)


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """
    Sprint 1 fixed-size chunking. Kept for backward compatibility.
    """
    if not text:
        return []

    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk.strip())
        start += chunk_size - overlap

    return [c for c in chunks if c]


def _parse_control_metadata(line: str) -> dict | None:
    """Parse a control metadata line into a dict, or return None if it doesn't match."""
    m = _CONTROL_RE.search(line)
    if not m:
        return None
    applicability = [a.strip() for a in m.group(4).split(",") if a.strip()]
    essential_8 = m.group(5).strip()
    return {
        "control_id": f"ISM-{m.group(1)}",
        "revision": int(m.group(2)),
        "updated": m.group(3).strip(),
        "applicability": applicability,
        "essential_8": essential_8 if essential_8.upper() != "N/A" else None,
    }


def _split_long_text(text: str, max_words: int = 800, overlap_words: int = 50) -> list[str]:
    """Split text longer than max_words using a sliding window over words."""
    words = text.split()
    if len(words) <= max_words:
        return [text]

    parts = []
    start = 0
    while start < len(words):
        end = min(start + max_words, len(words))
        parts.append(" ".join(words[start:end]))
        start += max_words - overlap_words

    return [p for p in parts if p.strip()]


def chunk_ism_document(text: str, source_file: str = "", min_words: int = 100, max_words: int = 800) -> list[dict]:
    """
    ISM-aware chunking that respects control boundaries and extracts metadata.

    Splits a parsed ISM document into chunks where each chunk is either:
    - A control with its metadata and surrounding context
    - A narrative section between controls

    Chunks smaller than min_words get merged with the next chunk.
    Chunks larger than max_words get split with a sliding window.

    Returns a list of dicts with keys:
        content, control_id, category, sub_topic, applicability, essential_8, revision, source_file
    """
    # Extract category from filename like "15. ISM - Guidelines for system hardening.pdf"
    category = ""
    cat_match = re.search(r"ISM\s*-\s*(.+?)\.pdf", source_file, re.IGNORECASE)
    if cat_match:
        category = cat_match.group(1).strip()

    lines = text.split("\n")
    segments = []
    current_narrative = []
    current_section = ""

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Try to match a control metadata line
        meta = _parse_control_metadata(line)
        if meta:
            # Save any accumulated narrative as its own segment
            narrative_text = "\n".join(current_narrative).strip()
            if narrative_text:
                segments.append({
                    "type": "narrative",
                    "content": narrative_text,
                    "metadata": None,
                    "section": current_section,
                })
                current_narrative = []

            # Collect the control body (lines after metadata until next control or blank section)
            control_lines = [line]  # include the metadata line for reference
            i += 1
            while i < len(lines):
                next_line = lines[i].strip()
                # Stop if we hit another control or a substantial blank gap
                if _CONTROL_RE.search(next_line):
                    break
                if next_line == "" and i + 1 < len(lines) and _CONTROL_RE.search(lines[i + 1].strip()):
                    break
                control_lines.append(next_line)
                i += 1

            control_text = "\n".join(control_lines).strip()
            segments.append({
                "type": "control",
                "content": control_text,
                "metadata": meta,
                "section": current_section,
            })
        else:
            # Track section headings (short lines that look like titles)
            if line and len(line.split()) <= 10 and not line.endswith(".") and line[0].isupper() if line else False:
                # Heuristic: short lines that don't end with a period are likely headings
                if len(line) < 80:
                    current_section = line
            current_narrative.append(line)
            i += 1

    # Don't forget trailing narrative
    narrative_text = "\n".join(current_narrative).strip()
    if narrative_text:
        segments.append({
            "type": "narrative",
            "content": narrative_text,
            "metadata": None,
            "section": current_section,
        })

    # Now build chunks, merging small segments with the next one
    chunks = []
    buffer_content = ""
    buffer_metadata = None
    buffer_section = ""

    for seg in segments:
        seg_text = seg["content"]
        seg_words = len(seg_text.split())

        if seg["type"] == "control":
            # Flush narrative buffer first if it's big enough on its own
            if buffer_content and len(buffer_content.split()) >= min_words:
                _emit_chunk(chunks, buffer_content, buffer_metadata, category, buffer_section, source_file, max_words)
                buffer_content = ""
                buffer_metadata = None

            # If there's a small narrative buffer, prepend it as context for this control
            if buffer_content:
                combined = buffer_content + "\n\n" + seg_text
                _emit_chunk(chunks, combined, seg["metadata"], category, seg["section"] or buffer_section, source_file, max_words)
                buffer_content = ""
                buffer_metadata = None
            else:
                # Check if this control is too small on its own
                if seg_words < min_words:
                    buffer_content = seg_text
                    buffer_metadata = seg["metadata"]
                    buffer_section = seg["section"]
                else:
                    _emit_chunk(chunks, seg_text, seg["metadata"], category, seg["section"], source_file, max_words)
        else:
            # Narrative segment - accumulate in buffer
            if buffer_content:
                buffer_content += "\n\n" + seg_text
            else:
                buffer_content = seg_text
                buffer_section = seg["section"]

            # If buffer is big enough, flush it
            if len(buffer_content.split()) >= min_words:
                _emit_chunk(chunks, buffer_content, buffer_metadata, category, buffer_section, source_file, max_words)
                buffer_content = ""
                buffer_metadata = None

    # Flush remaining buffer
    if buffer_content.strip():
        _emit_chunk(chunks, buffer_content, buffer_metadata, category, buffer_section, source_file, max_words)

    return chunks


def _emit_chunk(
    chunks: list[dict],
    content: str,
    metadata: dict | None,
    category: str,
    section: str,
    source_file: str,
    max_words: int,
):
    """Create one or more chunk dicts and append to chunks list. Splits if too long."""
    # Prepend guideline name and sub-topic as context header (per Sprint 2 plan)
    header_parts = []
    if category:
        header_parts.append(category)
    if section:
        header_parts.append(section)
    header = " > ".join(header_parts)

    parts = _split_long_text(content, max_words=max_words)
    for part in parts:
        text = part.strip()
        if header and not text.startswith(header):
            text = f"[{header}]\n{text}"

        chunk = {
            "content": text,
            "control_id": metadata["control_id"] if metadata else None,
            "category": category,
            "sub_topic": section if section else None,
            "applicability": metadata["applicability"] if metadata else None,
            "essential_8": metadata["essential_8"] if metadata else None,
            "revision": metadata["revision"] if metadata else None,
            "source_file": source_file,
        }
        chunks.append(chunk)
