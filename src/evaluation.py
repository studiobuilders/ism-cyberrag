import json
from typing import Callable


def load_eval_dataset(path: str) -> list[dict]:
    """
    Loads the evaluation dataset from a JSON file.

    Expected format:
    [
        {"question": "...", "ground_truth": "...", "category": "easy|medium|hard|out_of_scope"},
        ...
    ]
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"Loaded {len(data)} evaluation questions.")
    return data


def run_ragas_evaluation(
    eval_dataset: list[dict],
    retrieve_fn: Callable,
    generate_fn: Callable,
) -> list[dict]:
    """
    Runs the full RAG pipeline on every evaluation question.

    Args:
        eval_dataset: List of dicts with 'question' and 'ground_truth'.
        retrieve_fn:  callable(question: str) -> list[dict]  (each dict has 'content').
        generate_fn:  callable(question: str, chunks: list[dict]) -> str.

    Returns:
        List of result dicts with keys: question, ground_truth, answer, contexts.
    """
    results = []
    total = len(eval_dataset)

    for i, item in enumerate(eval_dataset, 1):
        question = item["question"]
        ground_truth = item["ground_truth"]

        try:
            # Retrieve
            chunks = retrieve_fn(question)
            contexts = [c["content"] for c in chunks]

            # Generate
            answer = generate_fn(question, chunks)
        except Exception as e:
            print(f"  [{i}/{total}] ERROR: {e}")
            contexts = []
            answer = f"Error: {e}"

        results.append({
            "question": question,
            "ground_truth": ground_truth,
            "answer": answer,
            "contexts": contexts,
        })
        print(f"  [{i}/{total}] {question[:60]}...")

    return results


def compute_ragas_scores(eval_results: list[dict]) -> dict:
    """
    Computes RAGAS metrics using Groq or Ollama as the LLM judge and
    HuggingFace (nomic-embed-text-v1.5) for embeddings.

    This avoids the default RAGAS behaviour of requiring an OpenAI key.

    Args:
        eval_results: List of dicts from run_ragas_evaluation(), each
                      containing 'question', 'answer', 'contexts', 'ground_truth'.

    Returns:
        The RAGAS result dict with metric scores.
    """
    from datasets import Dataset
    from ragas import evaluate
    from ragas.metrics import (
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
    )
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from src.config import GROQ_API_KEY, EMBEDDING_MODEL_NAME, LLM_PROVIDER, OLLAMA_BASE_URL

    # ── LLM judge (Groq or Ollama) ──
    if LLM_PROVIDER == "ollama":
        from langchain_community.chat_models import ChatOllama
        eval_llm = ChatOllama(
            model="llama3.1:8b", # using standard ollama tag
            base_url=OLLAMA_BASE_URL,
            temperature=0,
        )
        print(f"Using Ollama as RAGAS judge (model: llama3.1:8b)")
    else:
        from langchain_groq import ChatGroq
        eval_llm = ChatGroq(
            model_name="llama-3.1-8b-instant",
            api_key=GROQ_API_KEY,
            temperature=0,
        )
        print(f"Using Groq as RAGAS judge (model: llama-3.1-8b-instant)")

    # ── Embedding model (local, same as pipeline) ──
    eval_embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={"trust_remote_code": True},
    )

    # ── Build RAGAS-compatible dataset ──
    ragas_data = {
        "question": [r["question"] for r in eval_results],
        "answer": [r["answer"] for r in eval_results],
        "contexts": [r["contexts"] for r in eval_results],
        "ground_truth": [r["ground_truth"] for r in eval_results],
    }
    ragas_dataset = Dataset.from_dict(ragas_data)

    # ── Evaluate ──
    print("Computing RAGAS metrics (this may take a while)...")
    result = evaluate(
        ragas_dataset,
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
        llm=eval_llm,
        embeddings=eval_embeddings,
    )

    print("\n══════ RAGAS Baseline Results ══════")
    if hasattr(result, "to_pandas"):
        df = result.to_pandas()
        score_dict = df.mean(numeric_only=True).to_dict()
    else:
        score_dict = dict(result)

    for name, score in score_dict.items():
        print(f"  {name:25s} {float(score):.4f}")

    return score_dict


def log_metrics_to_clearml(metrics: dict, params: dict | None = None):
    """
    Logs RAGAS metrics and pipeline parameters to the current ClearML task.

    ClearML must already be initialized via Task.init() before calling this.

    Args:
        metrics: dict of metric_name -> float score.
        params:  dict of parameter_name -> value (logged as hyperparameters).
    """
    from clearml import Task

    task = Task.current_task()
    if task is None:
        print("⚠ No active ClearML task found. Skipping metric logging.")
        return

    logger = task.get_logger()

    # Log each RAGAS metric as a scalar
    for name, value in metrics.items():
        if isinstance(value, (int, float)):
            logger.report_scalar(title="RAGAS Metrics", series=name, value=value, iteration=0)

    # Log pipeline parameters as hyperparameters
    if params:
        task.connect(params, name="Pipeline Parameters")

    print(f"✓ Logged {len(metrics)} metrics to ClearML.")
