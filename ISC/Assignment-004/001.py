def create_matrix(key):
    key = key.upper().replace("J", "I")

    # Remove duplicate characters from key
    key_unique = ""
    for ch in key:
        if ch.isalpha() and ch not in key_unique:
            key_unique += ch

    # Add remaining alphabet characters
    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"

    for ch in alphabet:
        if ch not in key_unique:
            key_unique += ch

    # Create 5x5 matrix
    matrix = [
        key_unique[i:i + 5]
        for i in range(0, 25, 5)
    ]

    return matrix


def find_position(matrix, letter):
    for row in range(5):
        for col in range(5):
            if matrix[row][col] == letter:
                return row, col

    raise ValueError(f"Letter {letter} not found")


def prepare_plaintext(plaintext):
    # Remove spaces and convert J -> I
    text = ""
    for ch in plaintext.upper():
        if ch.isalpha():
            if ch == "J":
                ch = "I"
            text += ch

    digraphs = []
    i = 0

    while i < len(text):
        first = text[i]

        # Last character -> add X
        if i + 1 >= len(text):
            digraphs.append(first + "X")
            i += 1

        else:
            second = text[i + 1]

            # Repeated letters in a pair
            if first == second:
                digraphs.append(first + "X")
                i += 1

            else:
                digraphs.append(first + second)
                i += 2

    return digraphs


def encrypt_digraph(pair, matrix):
    a, b = pair

    r1, c1 = find_position(matrix, a)
    r2, c2 = find_position(matrix, b)

    # Same row
    if r1 == r2:
        a = matrix[r1][(c1 + 1) % 5]
        b = matrix[r2][(c2 + 1) % 5]

    # Same column
    elif c1 == c2:
        a = matrix[(r1 + 1) % 5][c1]
        b = matrix[(r2 + 1) % 5][c2]

    # Rectangle rule
    else:
        a = matrix[r1][c2]
        b = matrix[r2][c1]

    return a + b


def decrypt_digraph(pair, matrix):
    a, b = pair

    r1, c1 = find_position(matrix, a)
    r2, c2 = find_position(matrix, b)

    # Same row
    if r1 == r2:
        a = matrix[r1][(c1 - 1) % 5]
        b = matrix[r2][(c2 - 1) % 5]

    # Same column
    elif c1 == c2:
        a = matrix[(r1 - 1) % 5][c1]
        b = matrix[(r2 - 1) % 5][c2]

    # Rectangle rule
    else:
        a = matrix[r1][c2]
        b = matrix[r2][c1]

    return a + b


# MAIN PROGRAM

key = "DRONE"
plaintext = "ATTACK AT THE STATION"

# 1. Create matrix
matrix = create_matrix(key)

print("PLAYFAIR KEY MATRIX = \n")

for row in matrix:
    print(" ".join(row))


# 2. Prepare plaintext
digraphs = prepare_plaintext(plaintext)

print("\nPLAINTEXT DIGRAPHS = \n")
print(" ".join(digraphs))


# 3. Encrypt
encrypted_digraphs = []

for pair in digraphs:
    encrypted_digraphs.append(
        encrypt_digraph(pair, matrix)
    )

ciphertext = "".join(encrypted_digraphs)

print("\nENCRYPTED DIGRAPHS = \n")
print(" ".join(encrypted_digraphs))

print("\nCIPHERTEXT = \n")
print(ciphertext)


# 4. Decrypt
decrypted_digraphs = []

for pair in encrypted_digraphs:
    decrypted_digraphs.append(
        decrypt_digraph(pair, matrix)
    )

decrypted_text = "".join(decrypted_digraphs)

print("\nDECRYPTED DIGRAPHS = \n")
print(" ".join(decrypted_digraphs))

print("\nDECRYPTED TEXT = \n")
print(decrypted_text)