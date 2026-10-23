from __future__ import annotations

import argparse
from pathlib import Path

from experiment import run_experiment


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run Hindi POS MEMM/CRF comparison sequentially."
    )
    parser.add_argument("--data-dir", type=Path, default=Path("Hindi-POS-Data"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    parser.add_argument("--alpha", type=float, default=0.1)
    parser.add_argument(
        "--max-train-sentences", type=int, default=5000,
        help="Safe default; use --full-dataset for all training sentences.",
    )
    parser.add_argument("--max-eval-sentences", type=int, default=300)
    parser.add_argument("--max-eval-tokens", type=int)
    parser.add_argument("--memm-iterations", type=int, default=8)
    parser.add_argument("--crf-iterations", type=int, default=50)
    parser.add_argument("--full-dataset", action="store_true")
    parser.add_argument("--skip-plots", action="store_true")
    args = parser.parse_args()
    run_experiment(
        data_dir=args.data_dir,
        output_dir=args.output_dir,
        alpha=args.alpha,
        max_train_sentences=args.max_train_sentences,
        max_eval_sentences=args.max_eval_sentences,
        max_eval_tokens=args.max_eval_tokens,
        memm_iterations=args.memm_iterations,
        crf_iterations=args.crf_iterations,
        plots=not args.skip_plots,
        full_dataset=args.full_dataset,
    )


if __name__ == "__main__":
    main()
