"""Sequential, resource-aware orchestration for all Assignment 8 experiments."""

import json
import time
from pathlib import Path

from midsem_solutions.fst import solve as solve_fst
from midsem_solutions.kneser_ney import solve as solve_kn
from midsem_solutions.naive_bayes import solve as solve_nb
from spell_correction.evaluate import evaluate as evaluate_spelling
from midsem_solutions.tfidf import solve as solve_tfidf
from midsem_solutions.wordpiece import solve as solve_wordpiece


def run(output_dir: Path, project_dir: Path, max_spell_errors: int | None = None) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    tasks = [
        ("fst", solve_fst), ("wordpiece", solve_wordpiece), ("tfidf", solve_tfidf),
        ("naive_bayes", solve_nb), ("kneser_ney", solve_kn),
        ("spell_correction", lambda: evaluate_spelling(project_dir, max_spell_errors)),
    ]
    results = {"assignment": "NLP Assignment 8", "experiments": []}
    for name, task in tasks:
        started = time.perf_counter()
        result = task()
        result["runtime_seconds"] = round(time.perf_counter() - started, 6)
        results["experiments"].append(result)
        print(f"[done] {name}: {result['runtime_seconds']:.3f}s")
    path = output_dir / "results.json"
    path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Results written to {path}")
    return path
