from datasets import load_dataset
from huggingface_hub import hf_hub_download
from pathlib import Path

# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"

RAW_DIR.mkdir(parents=True, exist_ok=True)


def download_indic(sample=10000):
    """
    Downloads Hindi IndicCorpV2 parquet shard
    and returns first 'sample' examples.
    """

    print("Downloading IndicCorpV2 Hindi shard (~207 MB)...")

    parquet_path = hf_hub_download(
        repo_id="satpalsr/indicCorpv2",
        repo_type="dataset",
        revision="refs/convert/parquet",
        filename="hi/partial/train/0000.parquet",
        local_dir=str(RAW_DIR),
    )

    print(f"\nDownloaded file:\n{parquet_path}")

    print("\nLoading IndicCorpV2...")

    dataset = load_dataset(
        "parquet",
        data_files=parquet_path,
        split="train"
    )

    dataset = dataset.select(range(min(sample, len(dataset))))

    output_file = RAW_DIR / "indic_raw.parquet"

    dataset.to_parquet(str(output_file))

    print(f"\nSaved sampled dataset -> {output_file}")
    print(f"Loaded {len(dataset)} samples.")

    return dataset


# OSCAR

"""
def download_oscar(sample=10000):

    print("Loading OSCAR...")

    dataset = load_dataset(
        "oscar",
        "unshuffled_deduplicated_hi",
        split=f"train[:{sample}]"
    )

    dataset.to_parquet(str(RAW_DIR / "oscar_raw.parquet"))

    return dataset
"""