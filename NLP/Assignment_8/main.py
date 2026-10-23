from argparse import ArgumentParser
from pathlib import Path

from experiment import run


def main() -> None:
    parser = ArgumentParser(description="Run NLP Assignment 8 sequentially.")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    parser.add_argument("--project-dir", type=Path, default=Path("."))
    parser.add_argument("--max-spell-errors", type=int, default=None)
    args = parser.parse_args()
    run(args.output_dir, args.project_dir.resolve(), args.max_spell_errors)


if __name__ == "__main__":
    main()
