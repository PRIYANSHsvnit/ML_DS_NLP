from pathlib import Path

# Project Directories

BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUT_DIR = BASE_DIR / "output"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# Corpus Statistics

def corpus_statistics(
    tokenized_file,
    output_prefix="indic"
):
    """
    Computes corpus statistics from tokenized TXT.

    Statistics:

        1. Total number of sentences
        2. Total number of words/tokens
        3. Total number of characters
        4. Average sentence length
        5. Average word length
        6. Number of unique tokens
        7. Type/Token Ratio
    """

    total_sentences = 0

    total_words = 0

    total_characters = 0

    unique_words = set()

    # Read Tokenized File

    print("\nCalculating corpus statistics...\n")

    with open(
        tokenized_file,
        "r",
        encoding="utf-8"
    ) as f:

        for line in f:

            line = line.strip()

            if not line:
                continue

            # Each line represents one sentence
            tokens = line.split()

            total_sentences += 1

            total_words += len(tokens)

            # Process tokens

            for token in tokens:

                # Unique token
                unique_words.add(token)

                # Character count
                total_characters += len(token)

    # Calculate averages

    if total_sentences > 0:

        average_sentence_length = (
            total_words /
            total_sentences
        )

    else:

        average_sentence_length = 0


    if total_words > 0:

        average_word_length = (
            total_characters /
            total_words
        )

    else:

        average_word_length = 0


    # Unique Tokens

    unique_token_count = len(
        unique_words
    )


    # Type Token Ratio

    if total_words > 0:

        ttr = (
            unique_token_count /
            total_words
        )

    else:

        ttr = 0


    # Statistics Dictionary

    stats = {

        "Total Sentences":
            total_sentences,

        "Total Words":
            total_words,

        "Total Characters":
            total_characters,

        "Average Sentence Length":
            round(
                average_sentence_length,
                2
            ),

        "Average Word Length":
            round(
                average_word_length,
                2
            ),

        "Unique Words":
            unique_token_count,

        "Type Token Ratio":
            round(
                ttr,
                4
            )
    }


    # Save Statistics

    stats_path = (
        OUTPUT_DIR /
        f"{output_prefix}_statistics.txt"
    )

    with open(
        stats_path,
        "w",
        encoding="utf-8"
    ) as f:

        for key, value in stats.items():

            f.write(
                f"{key}: {value}\n"
            )


    # Display Statistics

    print("\nCorpus Statistics\n")

    for key, value in stats.items():

        print(
            f"{key}: {value}"
        )

    print(
        f"\nStatistics saved -> "
        f"{stats_path}"
    )

    return stats