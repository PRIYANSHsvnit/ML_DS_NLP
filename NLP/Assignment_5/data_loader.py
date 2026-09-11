import random


TOTAL_SENTENCES = 1_000_000
DEV_SIZE = 1_000
TEST_SIZE = 1_000


def get_split_indices():
    random.seed(42)

    selected = random.sample(
        range(TOTAL_SENTENCES),
        DEV_SIZE + TEST_SIZE
    )

    dev_indices = set(selected[:DEV_SIZE])
    test_indices = set(selected[DEV_SIZE:])

    return dev_indices, test_indices


def load_dev_test(filename):
    dev_indices, test_indices = get_split_indices()

    dev = []
    test = []

    with open(filename, encoding="utf-8") as f:
        for i, line in enumerate(f):

            line = line.strip()

            if not line:
                continue

            if i in dev_indices:
                dev.append(line)

            elif i in test_indices:
                test.append(line)

    return dev, test, dev_indices, test_indices