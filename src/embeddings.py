from sentence_transformers import SentenceTransformer
from src.config import EMBEDDING_MODEL_NAME


def load_embedding_model() -> SentenceTransformer:
    """
    Loads the nomic-embed-text-v1.5 model via sentence-transformers.
    Returns a SentenceTransformer instance.
    """
    model = SentenceTransformer(EMBEDDING_MODEL_NAME, trust_remote_code=True)
    return model


def embed_texts(model: SentenceTransformer, texts: list[str]) -> list[list[float]]:
    """
    Generates embeddings for a list of document texts.

    nomic-embed-text requires a task prefix for best results:
      - 'search_document: ' for documents being stored
      - 'search_query: '    for queries at retrieval time
    """
    prefixed = [f"search_document: {t}" for t in texts]
    embeddings = model.encode(prefixed, show_progress_bar=True)
    return embeddings.tolist()


def embed_query(model: SentenceTransformer, query: str) -> list[float]:
    """
    Generates an embedding for a single search query.
    Uses the 'search_query: ' prefix required by nomic-embed-text.
    """
    prefixed = f"search_query: {query}"
    embedding = model.encode(prefixed)
    return embedding.tolist()
