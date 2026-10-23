from __future__ import annotations

import math
from collections import Counter, defaultdict
from typing import Iterable, Sequence

from data import Sentence
from probability import log_smoothed_probability

START = "<START>"
END = "<END>"


class NaiveBayesTagger:
    """Multinomial NB using all five features specified by the assignment."""

    def __init__(self, alpha: float = 0.1) -> None:
        self.alpha = alpha
        self.tags: tuple[str, ...] = ()
        self.tag_counts: Counter[str] = Counter()
        self.feature_counts: dict[str, Counter[tuple[str, str]]] = defaultdict(Counter)
        self.feature_values: dict[str, set[str]] = defaultdict(set)

    @staticmethod
    def features(
        word: str, previous_word: str, next_word: str, previous_tag: str
    ) -> dict[str, str]:
        return {
            "length": "MORE" if len(word) > 4 else "LESS",
            "word": word,
            "previous_word": previous_word,
            "next_word": next_word,
            "previous_tag": previous_tag,
        }

    def fit(self, sentences: Iterable[Sentence]) -> "NaiveBayesTagger":
        for sentence in sentences:
            for index, (word, tag) in enumerate(sentence):
                values = self.features(
                    word,
                    sentence[index - 1][0] if index else START,
                    sentence[index + 1][0] if index + 1 < len(sentence) else END,
                    sentence[index - 1][1] if index else START,
                )
                self.tag_counts[tag] += 1
                for name, value in values.items():
                    self.feature_counts[name][(tag, value)] += 1
                    self.feature_values[name].add(value)
        self.tags = tuple(sorted(self.tag_counts))
        if not self.tags:
            raise ValueError("The training corpus contains no tagged tokens")
        return self

    def predict(self, words: Sequence[str]) -> list[str]:
        total_tokens = sum(self.tag_counts.values())
        predictions: list[str] = []
        for index, word in enumerate(words):
            values = self.features(
                word,
                words[index - 1] if index else START,
                words[index + 1] if index + 1 < len(words) else END,
                predictions[-1] if predictions else START,
            )
            scores: dict[str, float] = {}
            for tag in self.tags:
                score = math.log(
                    (self.tag_counts[tag] + self.alpha)
                    / (total_tokens + self.alpha * len(self.tags))
                )
                for name, value in values.items():
                    score += log_smoothed_probability(
                        self.feature_counts[name][(tag, value)],
                        self.tag_counts[tag],
                        max(1, len(self.feature_values[name])),
                        self.alpha,
                    )
                scores[tag] = score
            predictions.append(max(scores, key=scores.get))
        return predictions
