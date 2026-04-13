from fastapi import APIRouter
from pydantic import BaseModel

from src.embeddings import load_embedding_model, embed_query
from src.retrieval import hybrid_search
from src.reranking import rerank
from src.llm import generate_answer
from src.supabase_utils import get_supabase_client
from src.config import INITIAL_RETRIEVE_COUNT, RERANK_TOP_K

router = APIRouter()

# Load models and clients once at startup
_embedding_model = None
_supabase_client = None


def _get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = load_embedding_model()
    return _embedding_model


def _get_supabase():
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = get_supabase_client()
    return _supabase_client


class ChatRequest(BaseModel):
    question: str


class ChunkResponse(BaseModel):
    content: str
    control_id: str | None = None
    category: str | None = None
    sub_topic: str | None = None
    similarity: float | None = None
    rerank_score: float | None = None


class ChatResponse(BaseModel):
    answer: str
    chunks: list[ChunkResponse]


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    question = req.question.strip()
    if not question:
        return ChatResponse(answer="Please enter a question.", chunks=[])

    model = _get_embedding_model()
    client = _get_supabase()

    # Step 1: Embed the query
    query_embedding = embed_query(model, question)

    # Step 2: Hybrid search (vector + BM25 with RRF)
    raw_chunks = hybrid_search(client, question, query_embedding, match_count=INITIAL_RETRIEVE_COUNT)

    # Step 3: Cross-encoder reranking
    reranked = rerank(question, raw_chunks, top_k=RERANK_TOP_K)

    # Step 4: Generate answer
    answer = generate_answer(question, reranked)

    # Build response
    chunk_responses = []
    for c in reranked:
        chunk_responses.append(ChunkResponse(
            content=c.get("content", ""),
            control_id=c.get("control_id"),
            category=c.get("category"),
            sub_topic=c.get("sub_topic"),
            similarity=c.get("similarity"),
            rerank_score=c.get("rerank_score"),
        ))

    return ChatResponse(answer=answer, chunks=chunk_responses)
