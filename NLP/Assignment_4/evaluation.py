import math


def perplexity(model, sentences, n):

    log_probability = 0.0
    token_count = 0

    for sentence in sentences:

        words = (
            ["<BOS>"]
            + sentence.split()
            + ["<EOS>"]
        )

        for i in range(n - 1, len(words)):

            current_words = words[
                i - n + 1:i + 1
            ]

            ids = [
                model.get_id(word)
                for word in current_words
            ]

            if n == 1:

                probability = (
                    model.unigram_probability(
                        ids[0]
                    )
                )

            elif n == 2:

                probability = (
                    model.bigram_probability(
                        ids[0],
                        ids[1]
                    )
                )

            elif n == 3:

                probability = (
                    model.trigram_probability(
                        ids[0],
                        ids[1],
                        ids[2]
                    )
                )

            else:

                probability = (
                    model.quadrigram_probability(
                        ids[0],
                        ids[1],
                        ids[2],
                        ids[3]
                    )
                )

            log_probability += math.log(
                probability
            )

            token_count += 1

    return math.exp(
        -log_probability / token_count
    )