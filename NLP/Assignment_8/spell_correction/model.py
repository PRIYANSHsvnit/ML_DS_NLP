"""Noisy-channel spell correction with bounded candidate generation."""

from math import log


def edits(word: str) -> set[str]:
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    candidates = set()
    for left, right in splits:
        if right:
            candidates.add(left + right[1:])
        if len(right) > 1:
            candidates.add(left + right[1] + right[0] + right[2:])
        for letter in alphabet:
            if right:
                candidates.add(left + letter + right[1:])
            candidates.add(left + letter + right)
    return candidates


class NoisyChannel:
    def __init__(self, unigrams: dict[str, int], edit_counts: dict[str, int], max_candidates: int = 64):
        self.unigrams = unigrams
        self.edit_counts = edit_counts
        self.max_candidates = max_candidates
        self.total = sum(unigrams.values()) or 1

    def candidates(self, word: str) -> list[str]:
        known = {candidate for candidate in edits(word) if candidate in self.unigrams}
        if word in self.unigrams:
            known.add(word)
        return sorted(known, key=lambda candidate: self.unigrams[candidate], reverse=True)[:self.max_candidates]

    def correct(self, word: str) -> str:
        word = word.lower()
        candidates = self.candidates(word)
        if not candidates:
            return word
        def score(candidate: str) -> float:
            # The supplied table counts character edit operations (for example
            # ``e|i``). Use the operation evidence for each candidate/error
            # pair; unseen operations receive a small but non-zero score.
            operations = edit_operations(candidate, word)
            channel = sum(self.edit_counts.get(operation, 1) for operation in operations)
            return log(channel) + log(self.unigrams[candidate] / self.total)
        return max(candidates, key=score)


def edit_operations(candidate: str, observed: str) -> list[str]:
    """Return compact replacement/insertion/deletion operations for one edit."""
    for index in range(max(len(candidate), len(observed))):
        if candidate[index:index + 1] != observed[index:index + 1]:
            if index < len(candidate) and index < len(observed):
                return [f"{candidate[index]}|{observed[index]}"]
            if index < len(candidate):
                return [f"{candidate[index]}|"]
            return [f"|{observed[index]}"]
    if len(candidate) != len(observed):
        return [f"{candidate[-1:] or ''}|{observed[-1:] or ''}"]
    return ["identity"]
