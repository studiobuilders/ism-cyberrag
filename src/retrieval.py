from src.config import MATCH_COUNT


def match_chunks(client, query_embedding: list[float], match_count: int = MATCH_COUNT) -> list[dict]:
    """
    Calls the Supabase match_chunks() RPC function for vector similarity search.

    The RPC function is defined in Supabase SQL:
        match_chunks(query_embedding vector(768), match_count int)

    Returns a list of dicts with keys: id, content, control_id, category, similarity.
    """
    response = client.rpc(
        "match_chunks",
        {
            "query_embedding": query_embedding,
            "match_count": match_count,
        },
    ).execute()
    return response.data or []
