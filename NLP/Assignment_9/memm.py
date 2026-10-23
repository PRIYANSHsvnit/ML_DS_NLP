from __future__ import annotations

from typing import Iterable, Sequence

from data import Sentence
from features import START, token_features


class MEMMTagger:
    """A first-order Maximum Entropy Markov Model using NLTK MaxEnt."""

    def __init__(self, max_iter: int = 10) -> None:
        self.max_iter = max_iter
        self.classifier = None
        self.tags: tuple[str, ...] = ()

    def fit(self, sentences: Iterable[Sentence]) -> "MEMMTagger":
        try:
            from nltk.classify import MaxentClassifier
        except ImportError as exc:
            raise RuntimeError(
                "MEMM requires NLTK. Install dependencies with: python -m pip install -r requirements.txt"
            ) from exc

        instances: list[tuple[dict[str, str], str]] = []
        tag_set: set[str] = set()
        for sentence in sentences:
            words = [word for word, _ in sentence]
            previous_tag = START
            for index, (_, tag) in enumerate(sentence):
                instances.append((token_features(words, index, previous_tag), tag))
                previous_tag = tag
                tag_set.add(tag)
        if not instances:
            raise ValueError("The training corpus contains no tagged tokens")
        self.classifier = MaxentClassifier.train(
            instances,
            algorithm="iis",
            max_iter=self.max_iter,
            trace=0,
        )
        self.tags = tuple(sorted(tag_set))
        return self

    def predict(self, words: Sequence[str]) -> list[str]:
        if self.classifier is None:
            raise RuntimeError("MEMMTagger must be fitted before prediction")
        predictions: list[str] = []
        for index in range(len(words)):
            features = token_features(
                words,
                index,
                predictions[-1] if predictions else START,
            )
            predictions.append(self.classifier.classify(features))
        return predictions
