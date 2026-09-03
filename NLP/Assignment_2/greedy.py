def greedy_segment(text, word_counts):
    """
    Greedy longest-match word segmentation.

    At every position, choose the longest
    vocabulary word that matches the text.
    """

    vocabulary = set(word_counts)

    max_word_length = max(
        len(word)
        for word in vocabulary
    )

    result = []

    i = 0

    while i < len(text):

        found_word = None

        max_end = min(
            len(text),
            i + max_word_length
        )

        # Try longest word first
        for j in range(
            max_end,
            i,
            -1
        ):

            candidate = text[i:j]

            if candidate in vocabulary:

                found_word = candidate
                break

        # Safety fallback
        if found_word is None:

            found_word = text[i]

        result.append(found_word)

        i += len(found_word)

    return result