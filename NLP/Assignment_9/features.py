from __future__ import annotations

from typing import Sequence

from data import Sentence

START = "<START>"
END = "<END>"
NULL = "NULL"


def token_features(
    words: Sequence[str],
    index: int,
    previous_tag: str = START,
) -> dict[str, str]:
    word = words[index]
    previous_word = words[index - 1] if index else START
    next_word = words[index + 1] if index + 1 < len(words) else END
    features = {
        "word": word,
        "previous_word": previous_word,
        "next_word": next_word,
        "previous_tag": previous_tag,
        "length_feature": "LESS" if len(word) <= 4 else "MORE",
    }
    for length in range(1, 5):
        features[f"prefix_{length}"] = word[:length] or NULL
        features[f"suffix_{length}"] = word[-length:] if len(word) >= length else NULL
    return features


def sentence_features(sentence: Sentence) -> tuple[list[dict[str, str]], list[str]]:
    words = [word for word, _ in sentence]
    tags = [tag for _, tag in sentence]
    return [token_features(words, index) for index in range(len(words))], tags
