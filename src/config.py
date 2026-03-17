import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root (works whether running from notebooks/ or root)
_project_root = Path(__file__).resolve().parent.parent
load_dotenv(_project_root / ".env")

# ── Supabase ──────────────────────────────────────────────
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_PUBLISHABLE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY", "")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY", "")

# ── Groq ──────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# ── LLM Provider ──────────────────────────────────────────
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq") # 'groq' or 'ollama'
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# ── ClearML ───────────────────────────────────────────────
# ClearML SDK auto-reads these env vars when Task.init() is called:
#   CLEARML_API_ACCESS_KEY, CLEARML_API_SECRET_KEY
#   CLEARML_API_HOST, CLEARML_WEB_HOST, CLEARML_FILES_HOST
# No need to reference them in code — just set them in .env
CLEARML_PROJECT = "ISM-CyberRAG"
CLEARML_TASK = "Sprint 1 – Baseline RAG"

# ── Models ────────────────────────────────────────────────
EMBEDDING_MODEL_NAME = "nomic-ai/nomic-embed-text-v1.5"
EMBEDDING_DIMENSION = 768
LLM_MODEL_NAME = "llama-3.1-8b-instant"

# ── RAG Parameters ────────────────────────────────────────
CHUNK_SIZE = 1000       # characters
CHUNK_OVERLAP = 200     # characters
MATCH_COUNT = 5         # top-k retrieval

# ── Paths ─────────────────────────────────────────────────
PROJECT_ROOT = str(_project_root)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
EVAL_DIR = os.path.join(PROJECT_ROOT, "evaluations")
EVAL_DATASET_PATH = os.path.join(EVAL_DIR, "eval_questions.json")
