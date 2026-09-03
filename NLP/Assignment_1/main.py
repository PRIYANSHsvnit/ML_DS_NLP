# from src.download_data import download_indic
# from src.download_data import download_oscar

# indic = download_indic(10000)

# print(indic)
# print(indic.column_names)
# print(indic[0])

# oscar = download_oscar(10000)

# print(oscar)
# print(oscar.column_names)
# print(oscar[0])

from pathlib import Path

from datasets import load_dataset

from src.preprocess import preprocess_dataset
from src.statistics import corpus_statistics


# Project Directory

BASE_DIR = Path(__file__).resolve().parent


# Hindi IndicCorpV2 Full Shard

dataset_path = (
    BASE_DIR
    / "data"
    / "raw"
    / "hi"
    / "partial"
    / "train"
    / "0000.parquet"
)


# Check File

print("\nIndicCorpV2 Hindi\n")

print(f"\nLooking for dataset at = ")
print(dataset_path)

if not dataset_path.exists():
    raise FileNotFoundError(
        f"\nDataset not found!\n"
        f"Expected location = \n{dataset_path}"
    )


# Load Dataset

print("\nLoading dataset...")

dataset = load_dataset(
    "parquet",
    data_files=str(dataset_path),
    split="train"
)

print("\nDataset loaded successfully = ")
print(dataset)

print(
    f"Total paragraphs: {len(dataset):,}"
)


# Preprocessing + Tokenization

tokenized_file = preprocess_dataset(
    dataset,
    output_prefix="indic",
    target_sentences=1_000_000,
    chunk_size=10_000
)


# Corpus Statistics

corpus_statistics(
    tokenized_file,
    output_prefix="indic"
)