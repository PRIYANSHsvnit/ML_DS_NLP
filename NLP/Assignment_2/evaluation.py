def edit_distance(predicted, actual):
    """
    Token-level Levenshtein edit distance.

    Operations:
        insertion
        deletion
        substitution
    """

    m = len(predicted)
    n = len(actual)

    dp = [
        [0] * (n + 1)
        for _ in range(m + 1)
    ]

    # Base cases

    for i in range(m + 1):
        dp[i][0] = i

    for j in range(n + 1):
        dp[0][j] = j

    # DP

    for i in range(1, m + 1):

        for j in range(1, n + 1):

            if predicted[i - 1] == actual[j - 1]:
                cost = 0
            else:
                cost = 1

            dp[i][j] = min(

                # Delete
                dp[i - 1][j] + 1,

                # Insert
                dp[i][j - 1] + 1,

                # Substitute / Match
                dp[i - 1][j - 1] + cost
            )

    return dp[m][n]


def boundary_accuracy(
    predicted,
    actual,
    text_length
):
    """
    Character-boundary accuracy.

    Checks whether a word boundary exists
    at every possible character position.
    """

    # Predicted boundaries

    predicted_boundaries = set()

    position = 0

    for word in predicted:

        position += len(word)

        if position < text_length:

            predicted_boundaries.add(
                position
            )

    # Actual boundaries

    actual_boundaries = set()

    position = 0

    for word in actual:

        position += len(word)

        if position < text_length:

            actual_boundaries.add(
                position
            )

    # Compare boundaries

    correct = 0

    total = max(
        0,
        text_length - 1
    )

    for position in range(
        1,
        text_length
    ):

        predicted_boundary = (
            position in predicted_boundaries
        )

        actual_boundary = (
            position in actual_boundaries
        )

        if (
            predicted_boundary
            == actual_boundary
        ):

            correct += 1

    return correct, total


def evaluate(
    test_cases,
    segment_function
):
    """
    Evaluate one segmentation algorithm.
    """

    total_cases = len(test_cases)

    exact_correct = 0

    total_edit_distance = 0

    boundary_correct = 0

    boundary_total = 0

    results = []

    for case in test_cases:

        text = case["input"]

        ground_truth = (
            case["ground_truth"].split()
        )

        # Run algorithm
        predicted = segment_function(text)

        if predicted is None:
            predicted = []

        # Exact Accuracy

        exact_match = (
            predicted == ground_truth
        )

        if exact_match:
            exact_correct += 1

        # Edit Distance

        ed = edit_distance(
            predicted,
            ground_truth
        )

        total_edit_distance += ed

        # Boundary Accuracy

        bc, bt = boundary_accuracy(
            predicted,
            ground_truth,
            len(text)
        )

        boundary_correct += bc
        boundary_total += bt

        # Save prediction
        results.append({

            "input": text,

            "predicted":
                " ".join(predicted),

            "ground_truth":
                " ".join(ground_truth),

            "edit_distance": ed,

            "exact_match":
                exact_match
        })

    # Final metrics

    exact_accuracy = (
        exact_correct
        / total_cases
    )

    average_edit_distance = (
        total_edit_distance
        / total_cases
    )

    boundary_acc = (
        boundary_correct
        / boundary_total
        if boundary_total > 0
        else 0
    )

    return {

        "exact_accuracy":
            exact_accuracy,

        "boundary_accuracy":
            boundary_acc,

        "average_edit_distance":
            average_edit_distance,

        "results":
            results
    }