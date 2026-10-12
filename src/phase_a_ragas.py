from __future__ import annotations

"""Phase A: RAGAS Production Evaluation — 50q, 3 distributions, cluster analysis."""

import json
import os
import re
import sys
from dataclasses import asdict, dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TEST_SET_PATH, ANSWERS_PATH, ARTIFACTS_DIR
from src.experiment_support import write_json

Distribution = str  # "factual" | "multi_hop" | "adversarial"

DIAGNOSTIC_TREE = {
    "faithfulness":      ("LLM hallucinating", "Tighten system prompt, lower temperature"),
    "context_recall":    ("Missing relevant chunks", "Improve chunking or add BM25"),
    "context_precision": ("Too many irrelevant chunks", "Add reranking or metadata filter"),
    "answer_relevancy":  ("Answer doesn't match question", "Improve prompt template"),
}


@dataclass
class RagasResult:
    question_id: int
    distribution: Distribution
    question: str
    answer: str
    contexts: list[str]
    ground_truth: str
    faithfulness: float
    answer_relevancy: float
    context_precision: float
    context_recall: float

    @property
    def avg_score(self) -> float:
        return (self.faithfulness + self.answer_relevancy +
                self.context_precision + self.context_recall) / 4

    @property
    def worst_metric(self) -> str:
        scores = {
            "faithfulness":      self.faithfulness,
            "answer_relevancy":  self.answer_relevancy,
            "context_precision": self.context_precision,
            "context_recall":    self.context_recall,
        }
        return min(scores, key=scores.get)


# ─── Đã implement sẵn ────────────────────────────────────────────────────────

@dataclass
class RagasEvaluation:
    """Task 2 output: measured rows plus model identifiers reported by m4."""
    results: list[RagasResult]
    evaluator_models: list[str]

def load_test_set_50q(path: str = TEST_SET_PATH) -> list[dict]:
    """Load 50q test set với 3 distributions."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_answers(path: str = ANSWERS_PATH) -> list[dict]:
    """Load pre-generated answers từ setup_answers.py."""
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"answers_50q.json không tìm thấy tại {path}\n"
            "→ Chạy trước: python scripts/setup_answers.py --live"
        )
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_phase_a_report(results: list[RagasResult], clusters: dict, bottom: list[dict]) -> dict:
    """Provided exporter: preserve the student-produced Task 3 rows verbatim."""
    per_dist: dict[str, dict] = {}
    for dist in ["factual", "multi_hop", "adversarial"]:
        subset = [r for r in results if r.distribution == dist]
        if subset:
            per_dist[dist] = {
                "count": len(subset),
                "faithfulness":      sum(r.faithfulness for r in subset) / len(subset),
                "answer_relevancy":  sum(r.answer_relevancy for r in subset) / len(subset),
                "context_precision": sum(r.context_precision for r in subset) / len(subset),
                "context_recall":    sum(r.context_recall for r in subset) / len(subset),
                "avg_score":         sum(r.avg_score for r in subset) / len(subset),
            }

    report = {
        "total_questions": len(results),
        "per_question": [asdict(r) for r in results],
        "per_distribution": per_dist,
        "failure_clusters": clusters,
        "bottom_10": bottom,
    }
    return report


def save_phase_a_report(results: list[RagasResult], clusters: dict, bottom: list[dict],
                        path: str = os.path.join(ARTIFACTS_DIR, "ragas_50q.json")) -> None:
    write_json(path, build_phase_a_report(results, clusters, bottom))



# ─── Tasks 1-4: Sinh viên implement ──────────────────────────────────────────

DISTRIBUTIONS = ("factual", "multi_hop", "adversarial")
METRICS = ("faithfulness", "answer_relevancy", "context_precision", "context_recall")


def group_by_distribution(test_set: list[dict]) -> dict[str, list[dict]]:
    """Task 1: Nhóm 50 câu hỏi theo 3 distributions.

    Returns:
        {"factual": [...], "multi_hop": [...], "adversarial": [...]}
    """
    groups: dict[str, list[dict]] = {d: [] for d in DISTRIBUTIONS}
    for item in test_set:
        dist = item["distribution"]
        if dist not in groups:
            raise ValueError(f"Unknown distribution {dist!r} for question {item.get('id')}")
        groups[dist].append(item)
    return groups


def run_ragas_50q(answers: list[dict]) -> RagasEvaluation:
    """Task 2: Chạy RAGAS 4 metrics trên toàn bộ 50 câu hỏi qua m4.evaluate_ragas.

    Trả RagasEvaluation(results, evaluator_models) với evaluator_models lấy trực tiếp
    từ metadata m4 của chính lượt chạy này (không đoán từ JUDGE_MODEL).
    """
    import math
    try:
        from src.m4_eval import evaluate_ragas
    except ImportError as exc:
        raise ValueError("Missing src/m4_eval.py; cannot declare its actual models") from exc

    if not answers:
        raise ValueError("No answers to evaluate")

    raw = evaluate_ragas(
        [a["question"] for a in answers],
        [a["answer"] for a in answers],
        [a["contexts"] for a in answers],
        [a["ground_truth"] for a in answers],
    )
    per_q = list(raw.get("per_question", []))
    if len(per_q) != len(answers):
        raise ValueError(f"m4 returned {len(per_q)} rows for {len(answers)} answers")
    evaluator_models = list((raw.get("metadata") or {}).get("evaluator_models") or [])
    if not evaluator_models:
        raise ValueError("m4 metadata.evaluator_models is missing; fix the m4 adapter")

    def _metric(pq, name):
        value = pq[name] if isinstance(pq, dict) else getattr(pq, name)
        value = float(value)
        if not math.isfinite(value) or not 0.0 <= value <= 1.0:
            raise ValueError(f"Invalid {name}={value!r}; NaN/out-of-range scores are not allowed")
        return value

    results = [
        RagasResult(
            question_id=a["id"], distribution=a["distribution"],
            question=a["question"], answer=a["answer"],
            contexts=a["contexts"], ground_truth=a["ground_truth"],
            **{m: _metric(pq, m) for m in METRICS},
        )
        for a, pq in zip(answers, per_q)
    ]
    return RagasEvaluation(results, evaluator_models)


_VERSION_RE = re.compile(r"\bv\s?\d+(?:\.\d+)?\b|\b20\d\d\b", re.IGNORECASE)
_TOKEN_RE = re.compile(r"\w+", re.UNICODE)


def _gt_coverage(result: RagasResult) -> float:
    """Share of distinctive ground-truth tokens (digits or >3 chars) found in contexts."""
    gt_tokens = {t for t in _TOKEN_RE.findall(result.ground_truth.lower())
                 if t.isdigit() or len(t) > 3}
    if not gt_tokens:
        return 1.0
    ctx = " ".join(result.contexts).lower()
    return sum(t in ctx for t in gt_tokens) / len(gt_tokens)


def _diagnose(result: RagasResult) -> tuple[str, str]:
    """Question-specific diagnosis built from this row's metrics, contexts and answer."""
    base_diag, base_fix = DIAGNOSTIC_TREE[result.worst_metric]
    scores = ", ".join(f"{m}={getattr(result, m):.2f}" for m in METRICS)
    coverage = _gt_coverage(result)
    notes, fixes = [], []

    if "không tìm thấy" in result.answer.lower():
        notes.append("answer từ chối ('Không tìm thấy') dù có reference")
        fixes.append("tăng recall (top_k rerank 3→5, query rewriting) trước khi cho phép từ chối")
    if coverage < 0.5:
        notes.append(f"contexts chỉ chứa {coverage:.0%} từ khóa của ground truth → lỗi retrieval")
        fixes.append("bổ sung BM25/HyQA cho thuật ngữ trong câu hỏi, tăng HYBRID/RERANK top_k")
    elif result.worst_metric in ("faithfulness", "answer_relevancy"):
        notes.append(f"contexts đã chứa {coverage:.0%} từ khóa ground truth → lỗi ở bước generation")
        fixes.append("prompt bắt buộc trích dẫn đúng số liệu/điều kiện trong context, temperature=0")

    versions = {v.lower().replace(" ", "") for v in _VERSION_RE.findall(" ".join(result.contexts))}
    if len(versions) >= 2 or result.distribution == "adversarial":
        if versions:
            notes.append(f"contexts trộn nhiều phiên bản ({', '.join(sorted(versions))}) → nguy cơ version conflict")
        fixes.append("gắn metadata version/effective_date cho chunk, ưu tiên bản mới nhất khi rerank")
    if result.distribution == "multi_hop":
        fixes.append("tách câu hỏi multi-hop thành sub-queries và gộp contexts")

    diagnosis = f"{base_diag} ({scores})" + (": " + "; ".join(notes) if notes else "")
    suggested_fix = "; ".join(dict.fromkeys(fixes)) or base_fix
    return diagnosis, suggested_fix


def bottom_10(results: list[RagasResult]) -> list[dict]:
    """Task 3: Lấy 10 câu hỏi có avg_score thấp nhất (tăng dần, hòa thì theo id).

    Returns:
        [{"rank": 1, "question_id": ..., "distribution": ...,
          "question": ..., "avg_score": ..., "worst_metric": ...,
          "diagnosis": ..., "suggested_fix": ...}, ...]
    """
    ranked = sorted(results, key=lambda r: (r.avg_score, r.question_id))[:10]
    rows = []
    for rank, r in enumerate(ranked, 1):
        diagnosis, suggested_fix = _diagnose(r)
        rows.append({
            "rank": rank,
            "question_id": r.question_id,
            "distribution": r.distribution,
            "question": r.question,
            "avg_score": r.avg_score,
            "worst_metric": r.worst_metric,
            "diagnosis": diagnosis,
            "suggested_fix": suggested_fix,
        })
    return rows


def cluster_analysis(results: list[RagasResult]) -> dict:
    """Task 4: Phân tích failure clusters theo (worst_metric × distribution).

    Matrix thống kê worst_metric của mọi câu, không coi mọi câu là một failure.
    Nhóm yếu nhất = distribution có avg_score trung bình thấp nhất (bỏ nhóm rỗng).
    Tổng matrix theo cột chỉ là kích thước nhóm 20/20/10, không đo chất lượng.
    """
    if not results:
        raise ValueError("cluster_analysis needs at least one result")

    matrix = {m: {d: 0 for d in DISTRIBUTIONS} for m in METRICS}
    for r in results:
        matrix[r.worst_metric][r.distribution] += 1

    means = {}
    for d in DISTRIBUTIONS:
        subset = [r.avg_score for r in results if r.distribution == d]
        if subset:  # empty groups are skipped, never scored as 0
            means[d] = sum(subset) / len(subset)
    weakest = min(means, key=means.get)

    totals = {m: sum(matrix[m].values()) for m in METRICS}
    dominant_metric = max(METRICS, key=lambda m: totals[m])
    weakest_rows = [r for r in results if r.distribution == weakest]
    weakest_metric_means = {m: sum(getattr(r, m) for r in weakest_rows) / len(weakest_rows)
                            for m in METRICS}
    weakest_metric = min(weakest_metric_means, key=weakest_metric_means.get)

    ranking = ", ".join(f"{d}={v:.3f}" for d, v in sorted(means.items(), key=lambda kv: kv[1]))
    insight = (
        f"Mean avg_score theo distribution: {ranking}. Nhóm yếu nhất là '{weakest}' "
        f"(chọn theo mean thấp nhất, không theo số câu). Trong nhóm này metric thấp nhất là "
        f"{weakest_metric}={weakest_metric_means[weakest_metric]:.3f}. Trên toàn bộ {len(results)} câu, "
        f"'{dominant_metric}' là worst_metric của {totals[dominant_metric]} câu "
        f"→ {DIAGNOSTIC_TREE[dominant_metric][0]}; hướng sửa: {DIAGNOSTIC_TREE[dominant_metric][1]}."
    )
    return {
        "matrix": matrix,
        "distribution_avg_scores": means,
        "dominant_failure_distribution": weakest,
        "dominant_failure_metric": dominant_metric,
        "insight": insight,
    }


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from scripts.run_experiments import main
    raise SystemExit(main(["--phase", "a", *sys.argv[1:]]))
