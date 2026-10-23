from __future__ import annotations

import time
from pathlib import Path
from typing import Callable

from crf import CRFTagger
from data import Sentence, limit_sentences, read_sentences
from evaluation import evaluate
from hmm import HMMTagger
from memm import MEMMTagger
from naive_bayes import NaiveBayesTagger
from reporting import write_metrics, write_results

Predictor = Callable[[list[str]], list[str]]


def _bounded(path: Path, sentence_limit: int | None, token_limit: int | None):
    return limit_sentences(read_sentences(path), sentence_limit, token_limit)


def run_experiment(
    data_dir: Path,
    output_dir: Path,
    alpha: float = 0.1,
    max_train_sentences: int | None = 5000,
    max_eval_sentences: int | None = 300,
    max_eval_tokens: int | None = None,
    memm_iterations: int = 8,
    crf_iterations: int = 50,
    plots: bool = True,
    full_dataset: bool = False,
) -> Path:
    if full_dataset:
        max_train_sentences = max_eval_sentences = max_eval_tokens = None
    paths = {
        split: data_dir / f"hindi-{split}-pos.txt"
        for split in ("train", "dev", "test")
    }
    for path in paths.values():
        if not path.exists():
            raise FileNotFoundError(f"Missing corpus file: {path.resolve()}")

    models: dict[str, Predictor] = {}
    timings: dict[str, float] = {}
    tasks = [
        (
            "naive_bayes",
            lambda: NaiveBayesTagger(alpha).fit(
                _bounded(paths["train"], max_train_sentences, None)
            ).predict,
        ),
        (
            "hmm",
            lambda: HMMTagger(alpha).fit(
                _bounded(paths["train"], max_train_sentences, None)
            ).forward_viterbi,
        ),
        (
            "memm",
            lambda: MEMMTagger(memm_iterations).fit(
                _bounded(paths["train"], max_train_sentences, None)
            ).predict,
        ),
        (
            "crf",
            lambda: CRFTagger(max_iterations=crf_iterations).fit(
                _bounded(paths["train"], max_train_sentences, None)
            ).predict,
        ),
    ]
    for index, (name, train) in enumerate(tasks, 1):
        print(f"[{index}/4] Training {name} sequentially...")
        started = time.perf_counter()
        models[name] = train()
        timings[name] = round(time.perf_counter() - started, 3)
        print(f"      {name} ready in {timings[name]:.3f}s")

    all_scores: dict[str, dict[str, dict[str, float]]] = {}
    token_counts: dict[str, int] = {}
    for split in ("dev", "test"):
        print(f"[evaluation] {split}...")
        scores, token_count = evaluate(
            _bounded(paths[split], max_eval_sentences, max_eval_tokens),
            models,
        )
        all_scores[split] = scores
        token_counts[split] = token_count
        write_metrics(output_dir, split, scores, token_count, plots)
        for name, values in scores.items():
            print(
                f"  {split:4} {name:12} accuracy={values['__overall__']:.4f}"
                f" tokens={token_count:,}"
            )

    payload = {
        "assignment": "NLP Assignment 9",
        "models": ["memm", "crf", "naive_bayes", "hmm"],
        "configuration": {
            "max_train_sentences": max_train_sentences,
            "max_eval_sentences": max_eval_sentences,
            "max_eval_tokens": max_eval_tokens,
            "memm_iterations": memm_iterations,
            "crf_iterations": crf_iterations,
            "sequential": True,
        },
        "training_seconds": timings,
        "token_counts": token_counts,
        "scores": all_scores,
        "explanations": {
            "memm": "Locally normalizes a MaxEnt decision using the previous predicted tag.",
            "crf": "Globally scores the tag sequence with the required lexical and context features.",
            "naive_bayes": "Assignment 7 multinomial baseline.",
            "hmm": "Assignment 7 first-order generative baseline with Viterbi decoding.",
        },
    }
    path = write_results(output_dir, payload)
    print(f"[complete] Results written to {path.resolve()}")
    return path
