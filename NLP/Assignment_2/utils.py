import json


def load_dataset(
    path="text_segmentation_dataset.json"
):
    """
    Load JSON dataset.
    """

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def get_vocabulary(data):

    return data["word_counts"]


def get_test_cases(data):

    return data["test_cases"]


def get_max_word_length(word_counts):

    return max(
        len(word)
        for word in word_counts
    )