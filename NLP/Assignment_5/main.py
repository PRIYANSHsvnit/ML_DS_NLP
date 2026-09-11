from pathlib import Path

from data_loader import load_dev_test
from ngram_model import NGramModel
from evaluation import perplexity


BASE_DIR = Path(__file__).resolve().parent

FILE = BASE_DIR / "indic_tokenized.txt"
DB = BASE_DIR / "ngram_model.db"


def main():

    print("=" * 60)
    print("NLP ASSIGNMENT 5")
    print("N-GRAM MODELS - ADD-K SMOOTHING")
    print("K = 0.3")
    print("=" * 60)

    print("\nSelecting data...")

    dev, test, dev_idx, test_idx = (
        load_dev_test(FILE)
    )

    print(f"Development: {len(dev):,}")
    print(f"Testing:     {len(test):,}")
    print("Training:    998,000")

    print("\nTraining models...")

    model = NGramModel(DB)

    model.reset()

    model.train(
        FILE,
        dev_idx,
        test_idx
    )

    print("\nTraining completed.")

    print(
        f"Vocabulary: "
        f"{model.vocab_size:,}"
    )

    print(
        f"Training tokens: "
        f"{model.total_tokens:,}"
    )

    models = [
        (1, "Unigram"),
        (2, "Bigram"),
        (3, "Trigram"),
        (4, "Quadrigram")
    ]

    dev_results = {}
    test_results = {}

    print("\n" + "=" * 60)
    print("DEVELOPMENT SET")
    print("=" * 60)

    for n, name in models:

        pp = perplexity(
            model,
            dev,
            n
        )

        dev_results[name] = pp

        print(
            f"{name:<12}: {pp:.4f}"
        )

    print("\n" + "=" * 60)
    print("TEST SET")
    print("=" * 60)

    for n, name in models:

        pp = perplexity(
            model,
            test,
            n
        )

        test_results[name] = pp

        print(
            f"{name:<12}: {pp:.4f}"
        )

    best = min(
        test_results,
        key=test_results.get
    )

    print("\n" + "=" * 60)
    print(f"Best Model: {best}")
    print("=" * 60)

    model.close()


if __name__ == "__main__":
    main()