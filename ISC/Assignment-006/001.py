def encrypt_otp(plaintext, key):
    ciphertext = ""

    for p, k in zip(plaintext.upper(), key.upper()):
        P = ord(p) - ord('A')
        K = ord(k) - ord('A')

        C = (P + K) % 26

        ciphertext += chr(C + ord('A'))

    return ciphertext


def decrypt_otp(ciphertext, key):
    plaintext = ""

    for c, k in zip(ciphertext.upper(), key.upper()):
        C = ord(c) - ord('A')
        K = ord(k) - ord('A')

        P = (C - K) % 26

        plaintext += chr(P + ord('A'))

    return plaintext


# Main program
plaintext = input("Enter plaintext (letters only) = ")
key = input("Enter key (same length as plaintext) = ")

if len(plaintext) != len(key):
    print("Error: Key must be the same length as plaintext.")
else:
    ciphertext = encrypt_otp(plaintext, key)
    decrypted = decrypt_otp(ciphertext, key)

    print("\nCiphertext = ", ciphertext)
    print("Decrypted = ", decrypted)