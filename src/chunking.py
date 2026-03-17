def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """
    Splits text into fixed-size chunks with overlap.

    Args:
        text:       The full document text.
        chunk_size: Maximum characters per chunk.
        overlap:    Number of overlapping characters between consecutive chunks.

    Returns:
        List of text chunks.
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

    # Filter out empty chunks
    return [c for c in chunks if c]
