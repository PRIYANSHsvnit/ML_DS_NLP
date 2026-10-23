"""Evaluate the noisy-channel model on supplied tagged errors."""

from pathlib import Path
from .data import read_edits, read_holbrook, read_spell_errors, read_unigrams
from .model import NoisyChannel


def evaluate(data_dir: Path, max_errors: int | None = None) -> dict:
    unigrams = read_unigrams(data_dir / "Spell-Correction" / "count_unigram.txt")
    edits = read_edits(data_dir / "Spell-Correction" / "count_1edit.txt")
    model = NoisyChannel(unigrams, edits)
    pairs = list(read_holbrook(data_dir / "holbrook-tagged-errors-with-correct-words.txt"))
    if not pairs:
        pairs = list(read_spell_errors(data_dir / "Spell-Correction" / "spell-errors.txt"))
    if max_errors is not None:
        pairs = pairs[:max_errors]
    correct = sum(model.correct(wrong) == target for wrong, target in pairs)
    return {
        "topic": "spell_correction",
        "examples": len(pairs), "correct": correct,
        "accuracy": correct / len(pairs) if pairs else 0.0,
        "model": "Noisy channel: log P(error|candidate) + log P(candidate)",
        "candidate_limit": model.max_candidates,
    }
