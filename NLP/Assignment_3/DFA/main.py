from dfa import DFA


def main():

    dfa = DFA()

    print("QUESTION 1 = DFA\n")

    test_words = [
        "cat",
        "dog",
        "a",
        "zebra",
        "hello",
        "dog1",
        "1dog",
        "DogHouse",
        "Dog_house",
        " cats",
        "hello world",
        "",
        "abc123",
        "abc!",
        "ABC"
    ]

    for word in test_words:

        if dfa.accepts(word):
            print(f"{word!r:15} -> Accepted")
        else:
            print(f"{word!r:15} -> Not Accepted")


if __name__ == "__main__":
    main()