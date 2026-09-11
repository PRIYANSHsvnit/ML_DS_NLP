import numpy as np

def mod26(x):
    return x % 26


# Function: Find modular multiplicative inverse
def modular_inverse(a):
    a = a % 26

    for i in range(1, 26):
        if (a * i) % 26 == 1:
            return i

    return None


# Function: Convert numbers to letters
def numbers_to_letters(numbers):
    result = ""

    for num in numbers:
        result += chr(num + ord('A'))

    return result


# MAIN PROGRAM

print("HILL CIPHER (2 x 2) == ")


# 1. Construct and display key matrix

K = np.array([
    [3, 3],
    [2, 5]
])

print("\n1. KEY MATRIX")
print("K = ", K)


# 2. Preprocess plaintext

plaintext = "MEET AT BASE"

# Convert to uppercase and remove spaces
processed_text = ""

for char in plaintext:
    if char.isalpha():
        processed_text += char.upper()

print("\n2. PLAINTEXT")
print("Original plaintext = ", plaintext)
print("Processed plaintext = ", processed_text)


# Convert letters to numbers
# A = 0, B = 1, ..., Z = 25

plaintext_numbers = []

for char in processed_text:
    plaintext_numbers.append(ord(char) - ord('A'))

print("Numerical plaintext = ", plaintext_numbers)


# 3. Divide into 2-letter blocks

blocks = []

for i in range(0, len(plaintext_numbers), 2):
    block = plaintext_numbers[i:i + 2]
    blocks.append(block)

print("\n3. 2-LETTER BLOCKS")

for block in blocks:
    print(block)


# 4. Encrypt each block

# C = K × P mod 26

ciphertext_numbers = []

print("\n4. ENCRYPTION")

for block in blocks:

    # Convert block into column vector
    P = np.array(block).reshape(2, 1)

    # Matrix multiplication
    C = np.dot(K, P) % 26

    encrypted_block = C.flatten().tolist()

    print(f"{block} -> {encrypted_block}")

    ciphertext_numbers.extend(encrypted_block)


# 5. Display encrypted values and ciphertext

print("\n5. CIPHERTEXT")

print("Encrypted numerical values = ", ciphertext_numbers)

ciphertext = numbers_to_letters(ciphertext_numbers)

print("Ciphertext = ", ciphertext)


# 6. Find modular inverse of key matrix

print("\n6. MODULAR INVERSE OF KEY MATRIX")

a = K[0][0]
b = K[0][1]
c = K[1][0]
d = K[1][1]

# Determinant
det = a * d - b * c

print("Determinant = ", det)

det_mod = det % 26

print("Determinant mod 26 = ", det_mod)

# Find inverse of determinant modulo 26
det_inverse = modular_inverse(det_mod)

print("Multiplicative inverse of determinant = ", det_inverse)


if det_inverse is None:
    print("No modular inverse exists.")
    print("Decryption is not possible.")
    exit()


# Formula:
# K^-1 = [ d  -b ]  × det^-1 mod 26
#        [ -c  a ]

K_inverse = np.array([
    [d, -b],
    [-c, a]
])

K_inverse = (det_inverse * K_inverse) % 26

print("\nInverse key matrix K^-1 mod 26 = ")
print(K_inverse)


# 7. Decrypt ciphertext

# P = K^-1 × C mod 26

decrypted_numbers = []

print("\n7. DECRYPTION")

for i in range(0, len(ciphertext_numbers), 2):

    cipher_block = ciphertext_numbers[i:i + 2]

    C = np.array(cipher_block).reshape(2, 1)

    P = np.dot(K_inverse, C) % 26

    decrypted_block = P.flatten().tolist()

    print(f"{cipher_block} -> {decrypted_block}")

    decrypted_numbers.extend(decrypted_block)


# 8. Convert numbers back to letters

print("\n8. VERIFICATION")

print("Decrypted numerical values = ", decrypted_numbers)

decrypted_text = numbers_to_letters(decrypted_numbers)

print("Decrypted text = ", decrypted_text)

print("\nOriginal processed text = ", processed_text)


if decrypted_text == processed_text:
    print("\n VERIFICATION SUCCESSFUL")
    print("Original plaintext has been recovered.")
else:
    print("\n✗ VERIFICATION FAILED")