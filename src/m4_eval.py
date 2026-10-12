from __future__ import annotations

"""Module 4: RAGAS Evaluation — 4 metrics + failure analysis."""

import os, sys, json
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TEST_SET_PATH


@dataclass
class EvalResult:
    question: str
    answer: str
    contexts: list[str]
    ground_truth: str
    faithfulness: float
    answer_relevancy: float
    context_precision: float
    context_recall: float


def load_test_set(path: str = TEST_SET_PATH) -> list[dict]:
    """Load test set from JSON. (Đã implement sẵn)"""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


METRIC_NAMES = ("faithfulness", "answer_relevancy", "context_precision", "context_recall")


def _run_ragas_once(questions, answers, contexts, ground_truths, llm, embeddings) -> list[dict]:
    """One RAGAS 0.1.x pass; returns one dict of 4 metrics per input row (NaN kept)."""
    from datasets import Dataset
    from ragas import evaluate
    from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall

    dataset = Dataset.from_dict({
        "question": questions, "answer": answers,
        "contexts": contexts, "ground_truth": ground_truths,
    })
    result = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
        llm=llm, embeddings=embeddings,
        raise_exceptions=False,   # failed jobs become NaN; retried below, never zero-filled
    )
    df = result.to_pandas()
    if len(df) != len(questions):
        raise ValueError(f"RAGAS returned {len(df)} rows for {len(questions)} questions")
    return [{m: float(row[m]) for m in METRIC_NAMES} for _, row in df.iterrows()]


def evaluate_ragas(questions: list[str], answers: list[str],
                   contexts: list[list[str]], ground_truths: list[str],
                   max_retries: int = 2) -> dict:
    """Run RAGAS evaluation with explicit evaluator models.

    Returns {"per_question": [EvalResult, ...] (input order), 4 aggregate means,
             "metadata": {"evaluator_models": [llm_id, embedding_id]}}.
    Rows with NaN metrics are re-evaluated; persistent NaN raises (no fake scores).
    """
    import math
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    from config import OPENAI_API_KEY, EVALUATOR_LLM_MODEL, EVALUATOR_EMBEDDING_MODEL

    n = len(questions)
    if not (n and n == len(answers) == len(contexts) == len(ground_truths)):
        raise ValueError("questions/answers/contexts/ground_truths must be non-empty and equal length")
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is required for RAGAS evaluation")
    os.environ.setdefault("OPENAI_API_KEY", OPENAI_API_KEY)

    llm = ChatOpenAI(model=EVALUATOR_LLM_MODEL, temperature=0)
    embeddings = OpenAIEmbeddings(model=EVALUATOR_EMBEDDING_MODEL)

    scores = _run_ragas_once(questions, answers, contexts, ground_truths, llm, embeddings)

    def _bad(s):
        return any(not math.isfinite(s[m]) for m in METRIC_NAMES)

    for attempt in range(max_retries):
        bad_idx = [i for i, s in enumerate(scores) if _bad(s)]
        if not bad_idx:
            break
        print(f"  ↻ Re-evaluating {len(bad_idx)} rows with NaN metrics (retry {attempt + 1})")
        retry = _run_ragas_once([questions[i] for i in bad_idx], [answers[i] for i in bad_idx],
                                [contexts[i] for i in bad_idx], [ground_truths[i] for i in bad_idx],
                                llm, embeddings)
        for i, s in zip(bad_idx, retry):
            # keep any metric that was already finite; fill only the missing ones
            scores[i] = {m: (scores[i][m] if math.isfinite(scores[i][m]) else s[m]) for m in METRIC_NAMES}

    still_bad = [i for i, s in enumerate(scores) if _bad(s)]
    if still_bad:
        raise ValueError(f"RAGAS produced NaN metrics for rows {still_bad} after {max_retries} retries")

    per_question = [
        EvalResult(question=q, answer=a, contexts=c, ground_truth=g, **s)
        for q, a, c, g, s in zip(questions, answers, contexts, ground_truths, scores)
    ]
    means = {m: sum(s[m] for s in scores) / n for m in METRIC_NAMES}
    return {
        **means,
        "per_question": per_question,
        "metadata": {"evaluator_models": [EVALUATOR_LLM_MODEL, EVALUATOR_EMBEDDING_MODEL]},
    }


def failure_analysis(eval_results: list[EvalResult], bottom_n: int = 10) -> list[dict]:
    """Analyze bottom-N worst questions using Diagnostic Tree."""
    diagnostic_tree = {
        "faithfulness": ("LLM hallucinating", "Tighten prompt, lower temperature"),
        "context_recall": ("Missing relevant chunks", "Improve chunking or add BM25"),
        "context_precision": ("Too many irrelevant chunks", "Add reranking or metadata filter"),
        "answer_relevancy": ("Answer doesn't match question", "Improve prompt template"),
    }

    scored = []
    for r in eval_results:
        # accept both EvalResult dataclass and plain dict
        if isinstance(r, dict):
            get = lambda k: r.get(k, 0.0) or 0.0  # noqa: E731
        else:
            get = lambda k: getattr(r, k, 0.0) or 0.0  # noqa: E731
        metrics = {
            "faithfulness": get("faithfulness"),
            "context_recall": get("context_recall"),
            "context_precision": get("context_precision"),
            "answer_relevancy": get("answer_relevancy"),
        }
        avg = sum(metrics.values()) / len(metrics)
        worst_metric = min(metrics, key=lambda k: metrics[k])
        diagnosis, suggested_fix = diagnostic_tree[worst_metric]
        question = r.get("question", "") if isinstance(r, dict) else getattr(r, "question", "")
        scored.append({
            "question": question,
            "worst_metric": worst_metric,
            "score": round(metrics[worst_metric], 4),
            "avg_score": round(avg, 4),
            "diagnosis": diagnosis,
            "suggested_fix": suggested_fix,
        })

    scored.sort(key=lambda x: x["avg_score"])
    return scored[:bottom_n]


def save_report(results: dict, failures: list[dict], path: str = "reports/ragas_report.json"):
    """Save evaluation report to JSON. (Đã implement sẵn)"""
    parent_dir = os.path.dirname(path)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)
    report = {
        "aggregate": {k: v for k, v in results.items() if k != "per_question"},
        "num_questions": len(results.get("per_question", [])),
        "failures": failures,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"Report saved to {path}")


if __name__ == "__main__":
    test_set = load_test_set()
    print(f"Loaded {len(test_set)} test questions")
    print("Run pipeline.py first to generate answers, then call evaluate_ragas().")
