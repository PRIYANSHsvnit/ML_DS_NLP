"""Streaming readers for the supplied spell-correction files."""

from pathlib import Path
import re


ERROR_LINE = re.compile(r"^(.*?):\s*(.*)$")


def read_unigrams(path: Path) -> dict[str, int]:
    counts = {}
    with path.open(encoding="latin-1") as handle:
        for line in handle:
            parts = line.strip().rsplit(maxsplit=1)
            if len(parts) == 2:
                word, count = parts
                try:
                    counts[word.lower()] = int(count)
                except ValueError:
                    continue
    return counts


def read_edits(path: Path) -> dict[str, int]:
    counts = {}
    with path.open(encoding="latin-1") as handle:
        for line in handle:
            parts = line.rstrip("\n").split("\t")
            if len(parts) == 2:
                try:
                    counts[parts[0].lower()] = int(parts[1])
                except ValueError:
                    continue
    return counts


def read_holbrook(path: Path):
    """Yield (misspelling, correct_word) pairs without loading the corpus."""
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            for match in re.finditer(r"<ERR targ=([^>]+)>\s*([^<]+?)\s*</ERR>", line):
                yield match.group(2).strip().lower(), match.group(1).strip().lower()


def read_spell_errors(path: Path):
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            match = ERROR_LINE.match(line.strip())
            if not match:
                continue
            correct = match.group(1).strip().lower()
            for candidate in match.group(2).split(","):
                candidate = re.sub(r"\*\d+$", "", candidate.strip().lower())
                if candidate:
                    yield candidate, correct
