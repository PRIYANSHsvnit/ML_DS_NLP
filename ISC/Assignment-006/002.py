def mod_inverse(a, m):
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return -1


def encrypt_affine(plaintext, a, b):
    ciphertext = ""

    for ch in plaintext.upper():
        P = ord(ch) - ord('A')

        C = (a * P + b) % 26

        ciphertext += chr(C + ord('A'))

    return ciphertext


def decrypt_affine(ciphertext, a, b):
    plaintext = ""

    a_inv = mod_inverse(a, 26)

    for ch in ciphertext.upper():
        C = ord(ch) - ord('A')
        P = (a_inv * (C - b)) % 26

        plaintext += chr(P + ord('A'))

    return plaintext


# Main program
plaintext = input("Enter plaintext (letters only) = ")
a = int(input("Enter value of a = "))
b = int(input("Enter value of b = "))

# Find inverse of a
a_inv = mod_inverse(a, 26)

if a_inv == -1:
    print("Invalid value of a.")
    print("a must be relatively prime to 26.")
else:
    ciphertext = encrypt_affine(plaintext, a, b)
    decrypted = decrypt_affine(ciphertext, a, b)

    print("\nMultiplicative inverse of a = ", a_inv)
    print("Ciphertext = ", ciphertext)
    print("Decrypted = ", decrypted)