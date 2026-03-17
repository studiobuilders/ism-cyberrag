# ISM-CyberRAG

A Retrieval-Augmented Generation (RAG) system for the Australian Information Security Manual (ISM).

Built as a university capstone project across three development sprints.

## Project Structure

```
ism-cyberrag/
├── data/                    # ISM PDF documents (01–25)
├── evaluations/             # Evaluation datasets (JSON)
│   └── eval_questions.json  # 20 Q&A pairs for RAGAS evaluation
├── notebooks/
│   └── sprint1_poc.ipynb    # Sprint 1 POC notebook
├── src/
│   ├── __init__.py
│   ├── config.py            # Environment variables and settings
│   ├── parse_pdf.py         # PDF text extraction (pypdf)
│   ├── chunking.py          # Fixed-size chunking with overlap
│   ├── embeddings.py        # Embedding generation (nomic-embed-text-v1.5)
│   ├── supabase_utils.py    # Supabase client and database helpers
│   ├── retrieval.py         # Vector similarity search via Supabase RPC
│   ├── llm.py               # Answer generation via Groq (Llama 3.1 8B)
│   └── evaluation.py        # RAGAS evaluation + ClearML logging
├── .env.example             # Template for environment variables
├── .gitignore
├── requirements.txt
└── README.md
```

## Tech Stack

| Component | Tool | Details |
|-----------|------|---------|
| **PDF Parsing** | pypdf | Extracts text from 25 ISM guideline documents |
| **Chunking** | Custom | Fixed-size (1000 chars) with 200 char overlap |
| **Embeddings** | nomic-ai/nomic-embed-text-v1.5 | 768-dim vectors via sentence-transformers |
| **Vector Database** | Supabase + pgvector | PostgreSQL with vector similarity search |
| **LLM** | Groq API | Llama 3.1 8B Instant |
| **Evaluation** | RAGAS | Faithfulness, relevancy, precision, recall |
| **Experiment Tracking** | ClearML | Logs metrics, parameters, and artifacts |

## Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/studiobuilders/ism-cyberrag.git
cd ism-cyberrag
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up environment variables

```bash
cp .env.example .env
# Edit .env with your actual keys
```

Required variables:

| Variable | Source |
|----------|--------|
| `SUPABASE_URL` | Supabase project settings → API |
| `SUPABASE_KEY` | Supabase project settings → API (anon key) |
| `GROQ_API_KEY` | https://console.groq.com/keys |
| `CLEARML_API_ACCESS_KEY` | ClearML Settings → Workspace → Create credentials |
| `CLEARML_API_SECRET_KEY` | ClearML Settings → Workspace → Create credentials |
| `CLEARML_API_HOST` | `https://api.clear.ml` |
| `CLEARML_WEB_HOST` | `https://app.clear.ml` |
| `CLEARML_FILES_HOST` | `https://files.clear.ml` |

### 4. Set up Supabase

Run the SQL queries found in `database/schema.sql` in your Supabase SQL Editor to create the required tables and functions.

### 5. Run the notebook

Open `notebooks/sprint1_poc.ipynb` in:
- **AWS SageMaker**: Clone repo → open notebook → run all
- **Google Colab**: Click the "Open in Colab" badge at the top of the notebook
- **Local**: `jupyter notebook notebooks/sprint1_poc.ipynb`

## Sprint 1 Pipeline

```
ISM PDFs (25 files)
    │
    ▼
Parse (pypdf) → Plain text
    │
    ▼
Chunk (1000 chars, 200 overlap)
    │
    ▼
Embed (nomic-embed-text-v1.5, 768-dim)
    │
    ▼
Store in Supabase pgvector
    │
    ▼
Query → Embed → match_chunks() RPC → Top-5
    │
    ▼
Generate answer (Groq / Llama 3.1 8B)
    │
    ▼
Evaluate (RAGAS) → Log (ClearML)
```

## ClearML Setup

ClearML reads credentials from environment variables automatically. Set these in your `.env` file:

```
CLEARML_API_ACCESS_KEY=your-key
CLEARML_API_SECRET_KEY=your-secret
CLEARML_API_HOST=https://api.clear.ml
CLEARML_WEB_HOST=https://app.clear.ml
CLEARML_FILES_HOST=https://files.clear.ml
```

When you run `Task.init()` in the notebook, it connects to ClearML and creates an experiment. All metrics, parameters, and console output are logged automatically.

## Evaluation

The evaluation dataset (`evaluations/eval_questions.json`) contains 20 questions across four categories:
- **Easy** (5): Direct control lookups
- **Medium** (7): Cross-section queries
- **Hard** (5): Reasoning and comparison questions
- **Out of scope** (3): Guardrail test questions

Sprint 1 RAGAS targets:

| Metric | Target |
|--------|--------|
| Faithfulness | > 0.60 |
| Answer Relevancy | > 0.60 |
| Context Precision | > 0.50 |
| Context Recall | > 0.50 |

## Team

| Member | Sprint 1 Role |
|--------|---------------|
| Sreekar | Product Owner |
| Chandan | Data Engineer |
| Ruben | Data Scientist |

## Troubleshooting

### 1. `ImportError: einops`
**Issue:** The Nomic embedding model (`nomic-embed-text-v1.5`) requires the `einops` library for its internal architecture when `trust_remote_code=True` is used.
**Fix:** 
```bash
pip install einops
```

### 2. `OpenAIError` or `ValueError` in RAGAS Evaluation
**Issue:** By default, RAGAS tries to use OpenAI for scoring. Additionally, models like Nomic require `trust_remote_code=True`.
**Fix:** You must explicitly configure RAGAS to use Groq and trust remote code. Update your RAGAS evaluation cell with code that calls a configured score function, or ensure your `HuggingFaceEmbeddings` initialization looks like this:

```python
eval_embeddings = HuggingFaceEmbeddings(
    model_name="nomic-ai/nomic-embed-text-v1.5",
    model_kwargs={'trust_remote_code': True}
)
```

> [!TIP]
> Use the `compute_ragas_scores()` function in `src/evaluation.py` which handles this automatically.

## License
MIT
