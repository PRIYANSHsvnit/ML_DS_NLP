from __future__ import annotations

import argparse
from pathlib import Path

from experiment import run_experiment


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the complete Hindi POS tagging experiment sequentially."
    )
    parser.add_argument("--data-dir", type=Path, default=Path("Hindi-POS-Data"))
    parser.add_argument("--output-dir", type=Path, default=Path("results"))
    parser.add_argument("--alpha", type=float, default=0.1)
    parser.add_argument("--max-train-sentences", type=int)
    parser.add_argument("--max-eval-sentences", type=int)
    parser.add_argument("--max-eval-tokens", type=int)
    parser.add_argument("--skip-plots", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_experiment(
        data_dir=args.data_dir,
        output_dir=args.output_dir,
        alpha=args.alpha,
        max_train_sentences=args.max_train_sentences,
        max_eval_sentences=args.max_eval_sentences,
        max_eval_tokens=args.max_eval_tokens,
        plots=not args.skip_plots,
    )
