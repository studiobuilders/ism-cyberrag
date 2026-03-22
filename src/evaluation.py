import json
import time
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
    Tracks per-question latency for retrieval and generation.

    Args:
        eval_dataset: List of dicts with 'question' and 'ground_truth'.
        retrieve_fn:  callable(question: str) -> list[dict]  (each dict has 'content').
        generate_fn:  callable(question: str, chunks: list[dict]) -> str.

    Returns:
        List of result dicts with keys:
        question, ground_truth, answer, contexts,
        retrieval_time_s, generation_time_s, total_time_s.
    """
    results = []
    total = len(eval_dataset)

    for i, item in enumerate(eval_dataset, 1):
        question = item["question"]
        ground_truth = item["ground_truth"]

        retrieval_time = 0.0
        generation_time = 0.0

        try:
            # Retrieve (timed)
            t0 = time.time()
            chunks = retrieve_fn(question)
            retrieval_time = time.time() - t0
            contexts = [c["content"] for c in chunks]

            # Generate (timed)
            t0 = time.time()
            answer = generate_fn(question, chunks)
            generation_time = time.time() - t0
        except Exception as e:
            print(f"  [{i}/{total}] ERROR: {e}")
            contexts = []
            answer = f"Error: {e}"

        results.append({
            "question": question,
            "ground_truth": ground_truth,
            "answer": answer,
            "contexts": contexts,
            "retrieval_time_s": round(retrieval_time, 4),
            "generation_time_s": round(generation_time, 4),
            "total_time_s": round(retrieval_time + generation_time, 4),
        })
        print(f"  [{i}/{total}] ({retrieval_time + generation_time:.2f}s) {question[:60]}...")

    # Print latency summary
    avg_retrieval = sum(r["retrieval_time_s"] for r in results) / len(results)
    avg_generation = sum(r["generation_time_s"] for r in results) / len(results)
    avg_total = sum(r["total_time_s"] for r in results) / len(results)
    print(f"\n  Avg retrieval: {avg_retrieval:.3f}s | Avg generation: {avg_generation:.3f}s | Avg total: {avg_total:.3f}s")

    return results


def compute_ragas_scores(eval_results: list[dict]) -> tuple[dict, "pd.DataFrame"]:
    """
    Computes RAGAS metrics using the configured Eval LLM as the judge and
    HuggingFace (nomic-embed-text-v1.5) for embeddings.

    Args:
        eval_results: List of dicts from run_ragas_evaluation(), each
                      containing 'question', 'answer', 'contexts', 'ground_truth'.

    Returns:
        Tuple of (score_dict, results_df):
        - score_dict: dict of metric_name -> average float score.
        - results_df: pandas DataFrame with per-question scores and latency.
    """
    import pandas as pd
    from datasets import Dataset
    from ragas import evaluate
    from ragas.run_config import RunConfig
    from ragas.metrics import (
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
    )
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from src.config import GROQ_API_KEY, EMBEDDING_MODEL_NAME, OLLAMA_BASE_URL, EVAL_LLM_PROVIDER, EVAL_LLM_MODEL
    
    # ── LLM judge (Groq or Ollama) ──
    if EVAL_LLM_PROVIDER == "ollama":
        from langchain_community.chat_models import ChatOllama
        eval_llm = ChatOllama(
            model=EVAL_LLM_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0,
        )
        print(f"Using Ollama as RAGAS judge (model: {EVAL_LLM_MODEL})")
    else:
        from langchain_groq import ChatGroq
        eval_llm = ChatGroq(
            model_name=EVAL_LLM_MODEL,
            api_key=GROQ_API_KEY,
            temperature=0,
        )
        print(f"Using Groq as RAGAS judge (model: {EVAL_LLM_MODEL})")

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

    # ── Evaluate (sequential with retries to avoid timeouts) ──
    run_cfg = RunConfig(max_workers=1, max_retries=3, max_wait=120)
    print("Computing RAGAS metrics (sequential, max_retries=3)...")
    result = evaluate(
        ragas_dataset,
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
        llm=eval_llm,
        embeddings=eval_embeddings,
        run_config=run_cfg,
    )

    # ── Build per-question results DataFrame ──
    if hasattr(result, "to_pandas"):
        ragas_df = result.to_pandas()
    else:
        ragas_df = pd.DataFrame([dict(result)])

    # Merge latency data from eval_results into the RAGAS DataFrame
    latency_df = pd.DataFrame([{
        "retrieval_time_s": r.get("retrieval_time_s", 0),
        "generation_time_s": r.get("generation_time_s", 0),
        "total_time_s": r.get("total_time_s", 0),
    } for r in eval_results])

    if len(latency_df) == len(ragas_df):
        results_df = pd.concat([ragas_df, latency_df], axis=1)
    else:
        results_df = ragas_df

    # ── Compute average scores ──
    metric_cols = ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]
    score_dict = {}
    for col in metric_cols:
        if col in results_df.columns:
            score_dict[col] = float(results_df[col].mean())

    # Add latency averages to score_dict
    for col in ["retrieval_time_s", "generation_time_s", "total_time_s"]:
        if col in results_df.columns:
            score_dict[f"avg_{col}"] = float(results_df[col].mean())

    print("\n══════ RAGAS Evaluation Results ══════")
    for name, score in score_dict.items():
        print(f"  {name:25s} {score:.4f}")

    return score_dict, results_df


def log_metrics_to_clearml(
    metrics: dict,
    params: dict | None = None,
    results_df: "pd.DataFrame | None" = None,
    eval_results: list[dict] | None = None,
):
    """
    Logs RAGAS metrics, pipeline parameters, evaluation results, and
    sample Q&A outputs to the current ClearML task.

    ClearML must already be initialized via Task.init() before calling this.

    Args:
        metrics:      dict of metric_name -> float score.
        params:       dict of parameter_name -> value (logged as hyperparameters).
        results_df:   pandas DataFrame with per-question RAGAS scores (optional).
        eval_results: list of dicts from run_ragas_evaluation() for sample Q&A (optional).
    """
    from clearml import Task

    task = Task.current_task()
    if task is None:
        print("⚠ No active ClearML task found. Skipping metric logging.")
        return

    logger = task.get_logger()

    # ── 1. Log each RAGAS metric as a scalar ──
    for name, value in metrics.items():
        if isinstance(value, (int, float)):
            logger.report_scalar(title="RAGAS Metrics", series=name, value=value, iteration=0)

    # ── 2. Log pipeline parameters as hyperparameters ──
    if params:
        task.connect(params, name="Pipeline Parameters")

    # ── 3. Upload full results DataFrame as CSV artifact ──
    if results_df is not None:
        task.upload_artifact(
            name="eval_results",
            artifact_object=results_df,
        )
        print(f"✓ Uploaded eval_results artifact ({len(results_df)} rows).")

        # ── 4. Log results as a table in ClearML ──
        # Select display columns (exclude raw contexts for readability)
        display_cols = [c for c in results_df.columns if c != "contexts"]
        logger.report_table(
            title="Evaluation Results",
            series="Per-Question Scores",
            table_plot=results_df[display_cols],
        )

    # ── 5. Log sample Q&A outputs ──
    if eval_results:
        import pandas as pd
        sample_count = min(10, len(eval_results))
        samples = []
        for r in eval_results[:sample_count]:
            samples.append({
                "question": r["question"][:120],
                "answer": r["answer"][:200],
                "ground_truth": r["ground_truth"][:200],
                "retrieval_time_s": r.get("retrieval_time_s", ""),
                "generation_time_s": r.get("generation_time_s", ""),
            })
        sample_df = pd.DataFrame(samples)
        logger.report_table(
            title="Sample Q&A Outputs",
            series="First 10 Questions",
            table_plot=sample_df,
        )
        print(f"✓ Logged {sample_count} sample Q&A outputs to ClearML.")

    print(f"✓ Logged {len(metrics)} metrics to ClearML.")
