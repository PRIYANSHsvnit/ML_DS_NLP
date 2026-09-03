import math


def dp_segment(
    text,
    word_counts,
    total_corpus_words
):
    """
    Dynamic Programming word segmentation.

    Finds the segmentation with the maximum
    sum of log word probabilities.

    log P(word) =
        log(count(word) / total_corpus_words)
    """

    n = len(text)

    max_word_length = max(
        len(word)
        for word in word_counts
    )

    # dp[i] = best score for text[:i]
    dp = [float("-inf")] * (n + 1)

    # previous[i] = previous boundary
    previous = [None] * (n + 1)

    # Empty string has probability 1
    # log(1) = 0
    dp[0] = 0.0

    # DP

    for i in range(1, n + 1):

        start = max(
            0,
            i - max_word_length
        )

        for j in range(start, i):

            word = text[j:i]

            if word in word_counts:

                probability = (
                    word_counts[word]
                    / total_corpus_words
                )

                log_probability = math.log(
                    probability
                )

                candidate_score = (
                    dp[j]
                    + log_probability
                )

                if candidate_score > dp[i]:

                    dp[i] = candidate_score

                    previous[i] = j

    # No valid segmentation
    if previous[n] is None:
        return None

    # Reconstruct answer

    result = []

    i = n

    while i > 0:

        j = previous[i]

        word = text[j:i]

        result.append(word)

        i = j

    result.reverse()

    return result