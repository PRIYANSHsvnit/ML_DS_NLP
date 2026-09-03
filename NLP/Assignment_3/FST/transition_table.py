def display_transition_table():

    print("\nFST TRANSITION TABLE\n")

    print(
        f"{'Current State':<18}"
        f"{'Input':<25}"
        f"{'Output':<20}"
        f"{'Next State':<18}"
    )

    print("-" * 81)

    transitions = [

        # Start / Root

        (
            "q0",
            "root characters",
            "same characters",
            "q1"
        ),

        # Noun category

        (
            "q1",
            "+N",
            "ε",
            "q2"
        ),

        # Singular

        (
            "q2",
            "+SG",
            "ε",
            "FINAL"
        ),

        # Plural - S addition

        (
            "q2",
            "+PL / normal root",
            "s",
            "FINAL"
        ),

        # Plural - E insertion

        (
            "q2",
            "+PL / s,z,x,ch,sh ending",
            "es",
            "FINAL"
        ),

        # Plural - Y replacement

        (
            "q2",
            "+PL / consonant+y",
            "ies",
            "FINAL"
        ),
    ]

    for state, inp, output, next_state in transitions:

        print(
            f"{state:<18}"
            f"{inp:<25}"
            f"{output:<20}"
            f"{next_state:<18}"
        )