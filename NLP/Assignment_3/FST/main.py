from pathlib import Path

from lexicon import Lexicon
from generator import Generator
from analyzer import Analyzer
from transition_table import display_transition_table


def test_generation(generator):

    print("\nFST GENERATION\n")

    examples = [
        ("bag", "SG"),
        ("bag", "PL"),
        ("fox", "SG"),
        ("fox", "PL"),
        ("watch", "SG"),
        ("watch", "PL"),
        ("try", "SG"),
        ("try", "PL")
    ]

    for root, number in examples:

        result = generator.generate_analysis(root, number)

        print(result)


def test_analysis(analyzer):

    print("\nFST ANALYSIS\n")

    words = [
        "bag",
        "bags",
        "fox",
        "foxes",
        "watch",
        "watches",
        "try",
        "tries",
        "foxs",
        "dog1",
        "Dog"
    ]

    for word in words:

        result = analyzer.analyze(word)

        print(f"{word:<15} -> {result}")


def process_corpus(analyzer, lexicon):

    print("\nBROWN CORPUS MORPHOLOGICAL ANALYSIS\n")

    count = 0

    for word in sorted(lexicon.nouns):

        result = analyzer.analyze(word)

        print(f"{word:<20} -> {result}")

        count += 1

        # Display only first 100 words
        # to avoid flooding the terminal.

        if count >= 100:

            print("\nfirst 100 corpus words displayed...")

            break


def main():

    # Locate brown_nouns.txt

    base_dir = Path(__file__).resolve().parent
    brown_file = base_dir / "brown_nouns.txt"

    # Load Brown noun corpus

    lexicon = Lexicon(brown_file)

    print(" BROWN CORPUS")
    print(f"Unique noun entries = {lexicon.size()}")

    if lexicon.size() == 0:

        print("No nouns loaded.")
        return

    # Create FST generator

    generator = Generator(lexicon)

    # Create FST analyzer

    analyzer = Analyzer(lexicon)

    # Display FST transition table

    display_transition_table()

    # Test FST generation

    test_generation(generator)

    # Test FST analysis

    test_analysis(analyzer)

    # Process Brown corpus

    process_corpus(analyzer, lexicon)


if __name__ == "__main__":
    main()