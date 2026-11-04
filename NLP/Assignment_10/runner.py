from __future__ import annotations

import gc
import json
import os
import time
from pathlib import Path
from typing import Iterable

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import f1_score
from sklearn.neural_network import MLPClassifier
from threadpoolctl import threadpool_limits

from data import vocabulary
from embeddings import EmbeddingStore, load_embedding


def sentence_vectors(
    sentences: list[list[str]],
    store: EmbeddingStore,
    tfidf: TfidfVectorizer | None = None,
) -> np.ndarray:
    matrix = np.zeros((len(sentences), store.dimension), dtype=np.float32)
    for row, sentence in enumerate(sentences):
        weights = (
            tfidf.transform([" ".join(sentence)]).toarray()[0]
            if tfidf is not None
            else None
        )
        vectors = []
        vector_weights = []
        for token in sentence:
            vector = store.vector(token)
            if vector is not None:
                vectors.append(vector)
                if weights is not None:
                    index = tfidf.vocabulary_.get(token)
                    vector_weights.append(weights[index] if index is not None else 0.0)
        if vectors:
            values = np.asarray(vectors, dtype=np.float32)
            if weights is None:
                matrix[row] = values.mean(axis=0)
            else:
                weight_array = np.asarray(vector_weights, dtype=np.float32)
                total = float(weight_array.sum())
                matrix[row] = (
                    np.average(values, axis=0, weights=weight_array)
                    if total > 0
                    else values.mean(axis=0)
                )
    return matrix


def analogy_accuracy(
    store: EmbeddingStore, analogy_path: Path, limit: int | None
) -> tuple[float, int]:
    correct = total = 0
    with analogy_path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            if line.startswith(":"):
                continue
            parts = line.lower().split()
            if len(parts) != 4 or not all(store.contains(word) for word in parts):
                continue
            a, b, c, expected = parts
            best_word = store.nearest_analogy(a, b, c)
            if best_word is None:
                continue
            total += 1
            correct += best_word == expected
            if limit is not None and total >= limit:
                break
    return (correct / total if total else 0.0), total


def requested_analogies(store: EmbeddingStore) -> dict[str, str | None]:
    examples = {
        "good - bad + excellent": ("good", "bad", "excellent"),
        "delivery - late + fast": ("delivery", "late", "fast"),
    }
    return {
        expression: (
            store.nearest_analogy(*words)
            if all(store.contains(word) for word in words)
            else None
        )
        for expression, words in examples.items()
    }


def run(
    train_path: Path,
    test_path: Path,
    output_dir: Path,
    embeddings: dict[str, tuple[Path, str]],
    analogy_path: Path | None,
    train_size: int,
    test_size: int,
    max_analogies: int | None,
    random_state: int,
) -> Path:
    from data import load_stratified_data

    os.environ.setdefault("OMP_NUM_THREADS", "2")
    os.environ.setdefault("MKL_NUM_THREADS", "2")
    train, y_train, test, y_test = load_stratified_data(
        train_path, test_path, train_size, test_size, random_state
    )
    all_words = vocabulary(train + test)
    if analogy_path is not None:
        with analogy_path.open("r", encoding="utf-8", errors="ignore") as handle:
            for line in handle:
                parts = line.lower().split()
                if len(parts) == 4:
                    all_words.update(parts)
    tfidf = TfidfVectorizer(
        tokenizer=lambda value: value.split(),
        preprocessor=None,
        token_pattern=None,
        lowercase=False,
        dtype=np.float32,
    ).fit([" ".join(sentence) for sentence in train])
    output_dir.mkdir(parents=True, exist_ok=True)
    results: dict[str, object] = {
        "configuration": {
            "train_size": train_size,
            "test_size": test_size,
            "random_state": random_state,
            "threads": 2,
            "sequential": True,
        },
        "embeddings": {},
    }
    for name, (path, format_name) in embeddings.items():
        print(f"[embedding] loading {name}: {path}")
        store = load_embedding(path, all_words, format_name)
        entry: dict[str, object] = {"dimension": store.dimension}
        entry["requested_analogies"] = requested_analogies(store)
        if analogy_path is not None:
            score, count = analogy_accuracy(store, analogy_path, max_analogies)
            entry["analogy_accuracy"] = score
            entry["analogy_examples"] = count
        representations = {
            "average": (None, sentence_vectors(train, store), sentence_vectors(test, store)),
            "tfidf_weighted": (
                tfidf,
                sentence_vectors(train, store, tfidf),
                sentence_vectors(test, store, tfidf),
            ),
        }
        for representation, (_, x_train, x_test) in representations.items():
            print(f"[model] {name}/{representation}")
            started = time.perf_counter()
            classifier = MLPClassifier(
                hidden_layer_sizes=(128,),
                activation="relu",
                solver="adam",
                batch_size=64,
                learning_rate_init=1e-3,
                max_iter=40,
                early_stopping=True,
                validation_fraction=0.1,
                n_iter_no_change=5,
                random_state=random_state,
                verbose=False,
            )
            with threadpool_limits(limits=2):
                classifier.fit(x_train, y_train)
                prediction = classifier.predict(x_test)
            entry[f"{representation}_macro_f1"] = float(
                f1_score(y_test, prediction, average="macro", zero_division=0)
            )
            entry[f"{representation}_seconds"] = round(
                time.perf_counter() - started, 3
            )
            del classifier, x_train, x_test, prediction
            gc.collect()
        results["embeddings"][name] = entry
        store.close()
        del store
        gc.collect()
    result_path = output_dir / "results.json"
    result_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    return result_path
