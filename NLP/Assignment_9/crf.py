from __future__ import annotations

from typing import Iterable, Sequence

from data import Sentence
from features import sentence_features


class CRFTagger:
    """Linear-chain CRF using the assignment's required lexical features."""

    def __init__(
        self,
        max_iterations: int = 75,
        c1: float = 0.1,
        c2: float = 0.1,
    ) -> None:
        self.max_iterations = max_iterations
        self.c1 = c1
        self.c2 = c2
        self.model = None

    def fit(self, sentences: Iterable[Sentence]) -> "CRFTagger":
        try:
            import sklearn_crfsuite
        except ImportError as exc:
            raise RuntimeError(
                "CRF requires sklearn-crfsuite. Install dependencies with: "
                "python -m pip install -r requirements.txt"
            ) from exc

        sequences = list(sentences)
        if not sequences:
            raise ValueError("The training corpus contains no tagged sentences")
        features, labels = zip(*(sentence_features(sentence) for sentence in sequences))
        self.model = sklearn_crfsuite.CRF(
            algorithm="lbfgs",
            c1=self.c1,
            c2=self.c2,
            max_iterations=self.max_iterations,
            all_possible_transitions=False,
            verbose=False,
        )
        self.model.fit(list(features), list(labels))
        return self

    def predict(self, words: Sequence[str]) -> list[str]:
        if self.model is None:
            raise RuntimeError("CRFTagger must be fitted before prediction")
        sentence = list(zip(words, [""] * len(words)))
        features, _ = sentence_features(sentence)
        return list(self.model.predict_single(features))
