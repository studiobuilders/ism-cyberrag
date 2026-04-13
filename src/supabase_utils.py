from supabase import create_client


def get_supabase_client():
    """
    Creates and returns a Supabase client.
    Reads SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY from environment / config.
    """
    from src.config import SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY

    if not SUPABASE_URL or not SUPABASE_PUBLISHABLE_KEY:
        raise ValueError(
            "SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY must be set. "
            "Check your .env file or environment variables."
        )
    return create_client(SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY)


def insert_chunks(client, chunks: list[dict], table_name: str = "chunks"):
    """
    Inserts a list of chunk dicts into Supabase.

    Each dict should have at minimum:
        - content (str)
        - embedding (list[float])

    The Supabase pgvector column accepts the embedding as a plain list.
    """
    response = client.table(table_name).insert(chunks).execute()
    return response


def upsert_document(client, doc: dict, table_name: str = "documents"):
    """
    Inserts a document record into the documents table.

    Args:
        doc: dict with keys title, source_file, content.
    """
    response = client.table(table_name).insert(doc).execute()
    return response


def count_rows(client, table_name: str = "chunks") -> int:
    """Returns the number of rows in the given table."""
    response = client.table(table_name).select("id", count="exact").execute()
    return response.count or 0


def clear_all_data(client):
    """
    Deletes all rows from both chunks and documents tables.
    USE WITH CAUTION. Useful for resetting the POC.
    """
    # Delete chunks first because they reference documents
    client.table("chunks").delete().neq("id", -1).execute()
    client.table("documents").delete().neq("id", -1).execute()
    print("All data cleared from Supabase.")
