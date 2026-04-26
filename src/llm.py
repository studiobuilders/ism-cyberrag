from src.config import GROQ_API_KEY, LLM_MODEL_NAME, LLM_PROVIDER, OLLAMA_BASE_URL

# System prompt for the ISM CyberRAG assistant
SYSTEM_PROMPT = """You are an expert assistant on the Australian Information Security Manual (ISM).
Your goal is to provide helpful, accurate, and concise answers based on the provided ISM context.

Rules:
1. Use ONLY the provided context to answer. If the context contains information related to the topic but not a direct answer, summarize what is available and note any missing specifics.
2. If the topic is entirely absent from the context (e.g., product pricing, coding tutorials, or non-ISM topics), respond with: "I don't have enough information from the ISM documents to answer this. This topic is outside the scope of the ISM."
3. Always cite specific ISM control IDs (e.g., ISM-1234) when they appear in the context you use.
4. If multiple guidelines or controls are relevant, group them logically.
5. Be professional, factual, and do not make up information."""


def generate_answer(question: str, context_chunks: list[dict]) -> str:
    """
    Generates an answer using the configured LLM provider (Groq or Ollama) with source context.

    Args:
        question:        The user's question.
        context_chunks:  List of chunk dicts (must have 'content' key,
                         optionally 'control_id', 'category', 'similarity').

    Returns:
        The generated answer string.
    """
    # Build context block from retrieved chunks
    context_parts = []
    for i, chunk in enumerate(context_chunks, 1):
        control = chunk.get("control_id", "N/A")
        category = chunk.get("category", "")
        sim = chunk.get("similarity", "")
        header = f"[Chunk {i}] Control: {control}"
        if category:
            header += f" | Category: {category}"
        if sim:
            header += f" | Similarity: {sim:.4f}" if isinstance(sim, float) else f" | Similarity: {sim}"
        context_parts.append(f"{header}\n{chunk['content']}")

    context_text = "\n\n".join(context_parts)

    user_message = f"""Context:
{context_text}

Question: {question}"""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    if LLM_PROVIDER == "ollama":
        from openai import OpenAI
        # Ollama provides an OpenAI compatible API
        client = OpenAI(base_url=f"{OLLAMA_BASE_URL}/v1", api_key="ollama")
        
        response = client.chat.completions.create(
            model=LLM_MODEL_NAME, # using model from config
            messages=messages,
            temperature=0.1,
        )
        return response.choices[0].message.content
        
    else: # Default to Groq
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY must be set when LLM_PROVIDER='groq'. Check your .env file.")
        
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        
        response = client.chat.completions.create(
            model=LLM_MODEL_NAME,
            messages=messages,
            temperature=0.1,
            max_tokens=1024,
        )
        return response.choices[0].message.content
