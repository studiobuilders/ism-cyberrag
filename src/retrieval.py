from src.config import MATCH_COUNT, INITIAL_RETRIEVE_COUNT, RRF_K


def match_chunks(client, query_embedding: list[float], match_count: int = MATCH_COUNT) -> list[dict]:
    """
    Sprint 1 vector-only search. Kept for backward compatibility.
    """
    response = client.rpc(
        "match_chunks",
        {
            "query_embedding": query_embedding,
            "match_count": match_count,
        },
    ).execute()
    return response.data or []


def hybrid_search(
    client,
    query_text: str,
    query_embedding: list[float],
    match_count: int = INITIAL_RETRIEVE_COUNT,
    full_text_weight: float = 1.0,
    semantic_weight: float = 1.0,
    rrf_k: int = RRF_K,
) -> list[dict]:
    """
    Hybrid search combining vector similarity and BM25 full-text search
    using Reciprocal Rank Fusion (RRF).

    Returns a list of dicts with keys:
        id, content, control_id, category, sub_topic, applicability,
        essential_8, revision, similarity, rrf_score
    """
    response = client.rpc(
        "hybrid_search",
        {
            "query_text": query_text,
            "query_embedding": query_embedding,
            "match_count": match_count,
            "full_text_weight": full_text_weight,
            "semantic_weight": semantic_weight,
            "rrf_k": rrf_k,
        },
    ).execute()
    return response.data or []
