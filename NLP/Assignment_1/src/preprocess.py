from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from src.tokenizer import sentence_tokenizer
from src.tokenizer import word_tokenizer


# Project Directories

BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUT_DIR = BASE_DIR / "output"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# Preprocess Dataset

def preprocess_dataset(
    dataset,
    output_prefix="indic",
    target_sentences=1_000_000,
    chunk_size=10_000
):
    """
    Tokenizes the dataset into sentences and words.

    Processing stops after target_sentences are collected.

    Saves:
        output/<prefix>_tokenized.txt
        output/<prefix>.parquet

    Parquet uses Snappy compression.

    Returns:
        Path of the tokenized TXT file.
    """

    TEXT_COLUMN = "text"

    # Check column

    if TEXT_COLUMN not in dataset.column_names:

        raise ValueError(
            f"Column '{TEXT_COLUMN}' not found in dataset."
        )

    # Output paths

    txt_path = (
        OUTPUT_DIR /
        f"{output_prefix}_tokenized.txt"
    )

    parquet_path = (
        OUTPUT_DIR /
        f"{output_prefix}.parquet"
    )

    total_sentences = 0

    # Temporary buffer for Parquet
    parquet_buffer = []

    parquet_writer = None

    # Start

    print("\nStarting preprocessing...\n")
    print(
        f"Target sentences: {target_sentences:,}\n"
    )

    try:

        # Open TXT

        with open(
            txt_path,
            "w",
            encoding="utf-8"
        ) as txt_file:

            # Iterate through entire dataset

            for row_number, row in enumerate(
                dataset,
                start=1
            ):

                paragraph = row[TEXT_COLUMN]

                if paragraph is None:
                    continue

                paragraph = paragraph.strip()

                if not paragraph:
                    continue

                # Sentence Tokenization

                sentences = sentence_tokenizer(
                    paragraph
                )

                # Process each sentence

                for sentence in sentences:

                    tokens = word_tokenizer(
                        sentence
                    )

                    if not tokens:
                        continue

                    # Combine tokens

                    tokenized_sentence = " ".join(
                        tokens
                    )

                    # Save TXT

                    txt_file.write(
                        tokenized_sentence + "\n"
                    )

                    # Add to Parquet buffer

                    parquet_buffer.append(
                        tokenized_sentence
                    )

                    total_sentences += 1

                    # Write Parquet chunk

                    if len(parquet_buffer) >= chunk_size:

                        table = pa.Table.from_pydict({
                            "tokenized_sentence":
                                parquet_buffer
                        })

                        # Create writer first time
                        if parquet_writer is None:

                            parquet_writer = pq.ParquetWriter(
                                parquet_path,
                                table.schema,
                                compression="snappy"
                            )

                        parquet_writer.write_table(
                            table
                        )

                        parquet_buffer.clear()

                    # Progress

                    if total_sentences % 10_000 == 0:

                        print(
                            f"Paragraphs processed: "
                            f"{row_number:,} | "
                            f"Sentences: "
                            f"{total_sentences:,}"
                        )

                    # Stop at target

                    if (
                        total_sentences
                        >= target_sentences
                    ):
                        break

                # Stop paragraph loop
                if (
                    total_sentences
                    >= target_sentences
                ):
                    break

        # Write remaining Parquet rows

        if parquet_buffer:

            table = pa.Table.from_pydict({
                "tokenized_sentence":
                    parquet_buffer
            })

            if parquet_writer is None:

                parquet_writer = pq.ParquetWriter(
                    parquet_path,
                    table.schema,
                    compression="snappy"
                )

            parquet_writer.write_table(
                table
            )

            parquet_buffer.clear()

    finally:

        # Close Parquet writer

        if parquet_writer is not None:
            parquet_writer.close()

    # Final Result

    print("\nPreprocessing completed\n")

    print(
        f"Total sentences: "
        f"{total_sentences:,}"
    )

    print(
        f"Saved tokenized TXT -> "
        f"{txt_path}"
    )

    print(
        f"Saved compressed Parquet -> "
        f"{parquet_path}"
    )

    return txt_path