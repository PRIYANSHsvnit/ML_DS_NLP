from __future__ import annotations

from collections import Counter
from typing import Iterable, Sequence

from data import Sentence
from probability import log_smoothed_probability

START = "<START>"
END = "<END>"


class HMMTagger:
    def __init__(self, alpha: float = 0.1) -> None:
        self.alpha = alpha
        self.tags: tuple[str, ...] = ()
        self.tag_counts: Counter[str] = Counter()
        self.transition_counts: Counter[tuple[str, str]] = Counter()
        self.emission_counts: Counter[tuple[str, str]] = Counter()
        self.transition_totals: Counter[str] = Counter()
        self.vocabulary: set[str] = set()

    def fit(self, sentences: Iterable[Sentence]) -> "HMMTagger":
        for sentence in sentences:
            previous = START
            for word, tag in sentence:
                self.tag_counts[tag] += 1
                self.emission_counts[(tag, word)] += 1
                self.vocabulary.add(word)
                self.transition_counts[(previous, tag)] += 1
                self.transition_totals[previous] += 1
                previous = tag
            self.transition_counts[(previous, END)] += 1
            self.transition_totals[previous] += 1
        self.tags = tuple(sorted(self.tag_counts))
        if not self.tags:
            raise ValueError("The training corpus contains no tagged tokens")
        return self

    def transition(self, previous: str, current: str) -> float:
        return log_smoothed_probability(
            self.transition_counts[(previous, current)],
            self.transition_totals[previous],
            len(self.tags) + (previous != START),
            self.alpha,
        )

    def emission(self, tag: str, word: str) -> float:
        return log_smoothed_probability(
            self.emission_counts[(tag, word)],
            self.tag_counts[tag],
            len(self.vocabulary) + 1,
            self.alpha,
        )

    def forward_viterbi(self, words: Sequence[str]) -> list[str]:
        scores: list[dict[str, float]] = []
        back: list[dict[str, str]] = []
        for index, word in enumerate(words):
            current: dict[str, float] = {}
            pointers: dict[str, str] = {}
            for tag in self.tags:
                if index == 0:
                    current[tag] = self.transition(START, tag) + self.emission(tag, word)
                    pointers[tag] = START
                else:
                    previous = max(
                        self.tags,
                        key=lambda candidate: scores[-1][candidate]
                        + self.transition(candidate, tag),
                    )
                    current[tag] = (
                        scores[-1][previous]
                        + self.transition(previous, tag)
                        + self.emission(tag, word)
                    )
                    pointers[tag] = previous
            scores.append(current)
            back.append(pointers)
        current = max(scores[-1], key=scores[-1].get)
        result = [current]
        for index in range(len(scores) - 1, 0, -1):
            current = back[index][current]
            result.append(current)
        result.reverse()
        return result

    def backward_viterbi(self, words: Sequence[str]) -> list[str]:
        scores = [{} for _ in words]
        next_tags = [{} for _ in words]
        for tag in self.tags:
            scores[-1][tag] = self.emission(tag, words[-1]) + self.transition(tag, END)
        for index in range(len(words) - 2, -1, -1):
            for tag in self.tags:
                following = max(
                    self.tags,
                    key=lambda candidate: self.transition(tag, candidate)
                    + self.emission(candidate, words[index + 1])
                    + scores[index + 1][candidate],
                )
                scores[index][tag] = (
                    self.transition(tag, following)
                    + self.emission(following, words[index + 1])
                    + scores[index + 1][following]
                )
                next_tags[index][tag] = following
        current = max(
            self.tags,
            key=lambda tag: self.transition(START, tag)
            + self.emission(tag, words[0])
            + scores[0][tag],
        )
        result = [current]
        for index in range(len(words) - 1):
            result.append(next_tags[index][result[-1]])
        return result

    def forward_backward_viterbi(self, words: Sequence[str]) -> list[str]:
        forward = [{} for _ in words]
        backward = [{} for _ in words]
        for tag in self.tags:
            forward[0][tag] = self.transition(START, tag) + self.emission(tag, words[0])
            backward[-1][tag] = self.transition(tag, END)
        for index in range(1, len(words)):
            for tag in self.tags:
                forward[index][tag] = self.emission(tag, words[index]) + max(
                    forward[index - 1][previous] + self.transition(previous, tag)
                    for previous in self.tags
                )
        for index in range(len(words) - 2, -1, -1):
            for tag in self.tags:
                backward[index][tag] = max(
                    self.transition(tag, following)
                    + self.emission(following, words[index + 1])
                    + backward[index + 1][following]
                    for following in self.tags
                )
        return [
            max(self.tags, key=lambda tag: forward[index][tag] + backward[index][tag])
            for index in range(len(words))
        ]
