from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="View Assignment 9 results.")
    parser.add_argument("--results", type=Path, default=Path("outputs/results.json"))
    parser.add_argument("--html", type=Path, default=None)
    args = parser.parse_args()
    data = json.loads(args.results.read_text(encoding="utf-8"))
    print("NLP Assignment 9 - Hindi POS tagging")
    for split, scores in data["scores"].items():
        print(f"\n{split.upper()} ({data['token_counts'][split]:,} tokens)")
        for model, values in sorted(
            scores.items(), key=lambda item: item[1]["__overall__"], reverse=True
        ):
            print(f"  {model:14} accuracy={values['__overall__']:.4f}")
    if args.html:
        sections = []
        for split, scores in data["scores"].items():
            rows = "".join(
                f"<tr><td>{html.escape(model)}</td><td>{values['__overall__']:.4f}</td></tr>"
                for model, values in sorted(
                    scores.items(), key=lambda item: item[1]["__overall__"], reverse=True
                )
            )
            sections.append(
                f"<h2>{split.title()}</h2><table><tr><th>Model</th><th>Accuracy</th></tr>{rows}</table>"
            )
        document = (
            "<!doctype html><meta charset=utf-8><title>Assignment 9 Results</title>"
            "<style>body{font:16px system-ui;max-width:900px;margin:2rem auto}"
            "table{border-collapse:collapse}td,th{border:1px solid #ccc;padding:.5rem}</style>"
            + "".join(sections)
            + "<h2>Method explanations</h2>"
            + "".join(
                f"<p><b>{html.escape(k)}:</b> {html.escape(v)}</p>"
                for k, v in data["explanations"].items()
            )
        )
        args.html.parent.mkdir(parents=True, exist_ok=True)
        args.html.write_text(document, encoding="utf-8")
        print(f"\nHTML viewer written to {args.html.resolve()}")


if __name__ == "__main__":
    main()
