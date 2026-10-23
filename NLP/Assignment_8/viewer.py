"""Terminal and HTML result viewer."""

import argparse
import html
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="View Assignment 8 results.")
    parser.add_argument("--results", type=Path, default=Path("outputs/results.json"))
    parser.add_argument("--html", type=Path, default=None)
    args = parser.parse_args()
    data = json.loads(args.results.read_text(encoding="utf-8"))
    blocks = []
    for item in data["experiments"]:
        summary = item.get("accuracy", item.get("prediction", item.get("newest_tokens", "")))
        blocks.append(f"<section><h2>{html.escape(item['topic'])}</h2><p><b>Result:</b> {html.escape(str(summary))}</p><p>{html.escape(item.get('explanation', ''))}</p><pre>{html.escape(json.dumps(item, indent=2))}</pre></section>")
    document = "<!doctype html><meta charset=utf-8><title>NLP Assignment 8 Results</title><style>body{font:16px system-ui;max-width:1000px;margin:2rem auto}section{border:1px solid #ddd;padding:1rem;margin:1rem 0}pre{white-space:pre-wrap;background:#f6f8fa;padding:1rem}</style>" + "".join(blocks)
    print("NLP Assignment 8 results")
    for item in data["experiments"]:
        print(f"- {item['topic']}: {item.get('accuracy', item.get('prediction', item.get('newest_tokens', 'completed')))}")
    if args.html:
        args.html.write_text(document, encoding="utf-8")
        print(f"HTML viewer written to {args.html}")


if __name__ == "__main__":
    main()
