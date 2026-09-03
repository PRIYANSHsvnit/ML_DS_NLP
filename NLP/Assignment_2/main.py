import json
import os

from utils import load_dataset
from greedy import greedy_segment
from dp import dp_segment
from evaluation import evaluate


# Get the folder where main.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Dataset is in the same folder as main.py
DATASET_PATH = os.path.join(
    BASE_DIR,
    "text_segmentation_dataset.json"
)

# Output folder is also relative to main.py
OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "outputs"
)


def save_json(filename, data):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    path = os.path.join(OUTPUT_DIR, filename)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main():

    # Load dataset
    data = load_dataset(DATASET_PATH)

    word_counts = data["word_counts"]
    test_cases = data["test_cases"]
    total_corpus_words = data["metadata"]["total_corpus_words"]

    # GREEDY

    greedy_results = evaluate(
        test_cases,
        lambda text: greedy_segment(
            text,
            word_counts
        )
    )

    # DYNAMIC PROGRAMMING

    dp_results = evaluate(
        test_cases,
        lambda text: dp_segment(
            text,
            word_counts,
            total_corpus_words
        )
    )

    # Save individual results
    save_json(
        "greedy_results.json",
        greedy_results
    )

    save_json(
        "dp_results.json",
        dp_results
    )

    # PRINT RESULTS

    print("TEXT SEGMENTATION RESULTS = ")

    print("\nGreedy Longest Match\n")

    print(
        f"Exact Accuracy: "
        f"{greedy_results['exact_accuracy'] * 100:.2f}%"
    )

    print(
        f"Boundary Accuracy: "
        f"{greedy_results['boundary_accuracy'] * 100:.2f}%"
    )

    print(
        f"Average Edit Distance: "
        f"{greedy_results['average_edit_distance']:.4f}"
    )

    print("\nDynamic Programming\n")

    print(
        f"Exact Accuracy: "
        f"{dp_results['exact_accuracy'] * 100:.2f}%"
    )

    print(
        f"Boundary Accuracy: "
        f"{dp_results['boundary_accuracy'] * 100:.2f}%"
    )

    print(
        f"Average Edit Distance: "
        f"{dp_results['average_edit_distance']:.4f}"
    )

    # COMPARISON FILE

    comparison = f"""TEXT SEGMENTATION COMPARISON
    

Dataset:
- Vocabulary size: {data["metadata"]["vocabulary_size"]}
- Test cases: {data["metadata"]["test_case_count"]}
- Total corpus words: {total_corpus_words}


GREEDY LONGEST MATCH = 

Exact Accuracy: {greedy_results["exact_accuracy"] * 100:.2f}%
Boundary Accuracy: {greedy_results["boundary_accuracy"] * 100:.2f}%
Average Edit Distance: {greedy_results["average_edit_distance"]:.4f}


DYNAMIC PROGRAMMING =

Exact Accuracy: {dp_results["exact_accuracy"] * 100:.2f}%
Boundary Accuracy: {dp_results["boundary_accuracy"] * 100:.2f}%
Average Edit Distance: {dp_results["average_edit_distance"]:.4f}


CONCLUSION =

Dynamic Programming performs better on this dataset.

It considers the global log-probability of the
complete segmentation, whereas Greedy Longest
Match makes a local longest-word decision at
every position.
"""

    with open(
        os.path.join(
            OUTPUT_DIR,
            "comparison.txt"
        ),
        "w",
        encoding="utf-8"
    ) as f:

        f.write(comparison)


if __name__ == "__main__":
    main()