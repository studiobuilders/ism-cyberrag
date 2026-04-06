from src.config import GROQ_API_KEY, LLM_MODEL_NAME, LLM_PROVIDER, OLLAMA_BASE_URL

# System prompt for the ISM CyberRAG assistant
SYSTEM_PROMPT = """You are an expert assistant on the Australian Information Security Manual (ISM).
You answer questions using ONLY the context provided below.
Rules:
1. If the question asks about vendor-specific product configurations, product pricing, programming tutorials, exploit code, or any topic NOT covered by the ISM, respond ONLY with: "I don't have enough information from the ISM documents to answer this. This question is outside the scope of the Australian Information Security Manual (ISM)."
2. If the provided context does not contain enough information to answer the question, say "I don't have enough information from the ISM documents to answer this."
3. Always cite ISM control IDs (e.g. ISM-1234) when they appear in the context.
4. Be concise and factual.
5. Do not make up information."""


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
