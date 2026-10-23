from __future__ import annotations

from pathlib import Path

from data import limit_sentences, read_sentences
from evaluation import evaluate
from hmm import HMMTagger
from naive_bayes import NaiveBayesTagger
from reporting import write_report


def run_experiment(
    data_dir: Path,
    output_dir: Path,
    alpha: float = 0.1,
    max_train_sentences: int | None = None,
    max_eval_sentences: int | None = None,
    max_eval_tokens: int | None = None,
    plots: bool = True,
) -> None:
    paths = {
        "train": data_dir / "hindi-train-pos.txt",
        "dev": data_dir / "hindi-dev-pos.txt",
        "test": data_dir / "hindi-test-pos.txt",
    }
    for path in paths.values():
        if not path.exists():
            raise FileNotFoundError(f"Missing corpus file: {path.resolve()}")

    print("[1/4] Training Naive Bayes...")
    nb = NaiveBayesTagger(alpha).fit(
        limit_sentences(read_sentences(paths["train"]), max_train_sentences)
    )
    print("[2/4] Training HMM...")
    hmm = HMMTagger(alpha).fit(
        limit_sentences(read_sentences(paths["train"]), max_train_sentences)
    )
    predictors = {
        "naive_bayes": nb.predict,
        "hmm_forward": hmm.forward_viterbi,
        "hmm_backward": hmm.backward_viterbi,
        "hmm_forward_backward": hmm.forward_backward_viterbi,
    }
    for split in ("dev", "test"):
        print(f"[3/4] Evaluating {split}...")
        sentences = limit_sentences(
            read_sentences(paths[split]), max_eval_sentences, max_eval_tokens
        )
        scores, tokens = evaluate(sentences, predictors)
        write_report(output_dir, split, scores, plots)
        for name, values in scores.items():
            print(f"{split:4} {name:22} accuracy={values['__overall__']:.4f} tokens={tokens:,}")
    print(f"[4/4] Results saved to {output_dir.resolve()}")
