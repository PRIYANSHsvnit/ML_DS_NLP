from __future__ import annotations

from collections import Counter, defaultdict
from typing import Callable, Iterable

from data import Sentence

Predictor = Callable[[list[str]], list[str]]


def evaluate(
    sentences: Iterable[Sentence],
    predictors: dict[str, Predictor],
) -> tuple[dict[str, dict[str, float]], int]:
    tp: dict[str, Counter[str]] = defaultdict(Counter)
    fp: dict[str, Counter[str]] = defaultdict(Counter)
    fn: dict[str, Counter[str]] = defaultdict(Counter)
    token_count = 0
    for sentence in sentences:
        words = [word for word, _ in sentence]
        gold = [tag for _, tag in sentence]
        for name, predictor in predictors.items():
            predicted = predictor(words)
            if len(predicted) != len(gold):
                raise RuntimeError(f"{name} returned an invalid sequence length")
            for expected, actual in zip(gold, predicted):
                if expected == actual:
                    tp[name][expected] += 1
                else:
                    fn[name][expected] += 1
                    fp[name][actual] += 1
        token_count += len(sentence)
    tags = sorted(set().union(*(set(tp[n]) | set(fp[n]) | set(fn[n]) for n in predictors)))
    scores: dict[str, dict[str, float]] = {}
    for name in predictors:
        scores[name] = {}
        for tag in tags:
            denominator = 2 * tp[name][tag] + fp[name][tag] + fn[name][tag]
            scores[name][tag] = 2 * tp[name][tag] / denominator if denominator else 0.0
        scores[name]["__overall__"] = (
            sum(tp[name].values()) / token_count if token_count else 0.0
        )
    return scores, token_count
