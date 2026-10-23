
# DES Encryption and Decryption from Scratch
# No external libraries required

IP = [
    58,50,42,34,26,18,10,2,60,52,44,36,28,20,12,4,
    62,54,46,38,30,22,14,6,64,56,48,40,32,24,16,8,
    57,49,41,33,25,17,9,1,59,51,43,35,27,19,11,3,
    61,53,45,37,29,21,13,5,63,55,47,39,31,23,15,7
]

FP = [
    40,8,48,16,56,24,64,32,39,7,47,15,55,23,63,31,
    38,6,46,14,54,22,62,30,37,5,45,13,53,21,61,29,
    36,4,44,12,52,20,60,28,35,3,43,11,51,19,59,27,
    34,2,42,10,50,18,58,26,33,1,41,9,49,17,57,25
]

E = [
    32,1,2,3,4,5,4,5,6,7,8,9,
    8,9,10,11,12,13,12,13,14,15,16,17,
    16,17,18,19,20,21,20,21,22,23,24,25,
    24,25,26,27,28,29,28,29,30,31,32,1
]

P = [
    16,7,20,21,29,12,28,17,1,15,23,26,5,18,31,10,
    2,8,24,14,32,27,3,9,19,13,30,6,22,11,4,25
]

PC1 = [
    57,49,41,33,25,17,9,1,58,50,42,34,26,18,
    10,2,59,51,43,35,27,19,11,3,60,52,44,36,
    63,55,47,39,31,23,15,7,62,54,46,38,30,22,
    14,6,61,53,45,37,29,21,13,5,28,20,12,4
]

PC2 = [
    14,17,11,24,1,5,3,28,15,6,21,10,
    23,19,12,4,26,8,16,7,27,20,13,2,
    41,52,31,37,47,55,30,40,51,45,33,48,
    44,49,39,56,34,53,46,42,50,36,29,32
]

SHIFTS = [1,1,2,2,2,2,2,2,1,2,2,2,2,2,2,1]

S_BOXES = [
 [[14,4,13,1,2,15,11,8,3,10,6,12,5,9,0,7],
  [0,15,7,4,14,2,13,1,10,6,12,11,9,5,3,8],
  [4,1,14,8,13,6,2,11,15,12,9,7,3,10,5,0],
  [15,12,8,2,4,9,1,7,5,11,3,14,10,0,6,13]],

 [[15,1,8,14,6,11,3,4,9,7,2,13,12,0,5,10],
  [3,13,4,7,15,2,8,14,12,0,1,10,6,9,11,5],
  [0,14,7,11,10,4,13,1,5,8,12,6,9,3,2,15],
  [13,8,10,1,3,15,4,2,11,6,7,12,0,5,14,9]],

 [[10,0,9,14,6,3,15,5,1,13,12,7,11,4,2,8],
  [13,7,0,9,3,4,6,10,2,8,5,14,12,11,15,1],
  [13,6,4,9,8,15,3,0,11,1,2,12,5,10,14,7],
  [1,10,13,0,6,9,8,7,4,15,14,3,11,5,2,12]],

 [[7,13,14,3,0,6,9,10,1,2,8,5,11,12,4,15],
  [13,8,11,5,6,15,0,3,4,7,2,12,1,10,14,9],
  [10,6,9,0,12,11,7,13,15,1,3,14,5,2,8,4],
  [3,15,0,6,10,1,13,8,9,4,5,11,12,7,2,14]],

 [[2,12,4,1,7,10,11,6,8,5,3,15,13,0,14,9],
  [14,11,2,12,4,7,13,1,5,0,15,10,3,9,8,6],
  [4,2,1,11,10,13,7,8,15,9,12,5,6,3,0,14],
  [11,8,12,7,1,14,2,13,6,15,0,9,10,4,5,3]],

 [[12,1,10,15,9,2,6,8,0,13,3,4,14,7,5,11],
  [10,15,4,2,7,12,9,5,6,1,13,14,0,11,3,8],
  [9,14,15,5,2,8,12,3,7,0,4,10,1,13,11,6],
  [4,3,2,12,9,5,15,10,11,14,1,7,6,0,8,13]],

 [[4,11,2,14,15,0,8,13,3,12,9,7,5,10,6,1],
  [13,0,11,7,4,9,1,10,14,3,5,12,2,15,8,6],
  [1,4,11,13,12,3,7,14,10,15,6,8,0,5,9,2],
  [6,11,13,8,1,4,10,7,9,5,0,15,14,2,3,12]],

 [[13,2,8,4,6,15,11,1,10,9,3,14,5,0,12,7],
  [1,15,13,8,10,3,7,4,12,5,6,11,0,14,9,2],
  [7,11,4,1,9,12,14,2,0,6,10,13,15,3,5,8],
  [2,1,14,7,4,10,8,13,15,12,9,0,3,5,6,11]]
]


def permute(value, table, input_width):
    """Rearrange bits according to a DES permutation table."""
    result = 0
    for position in table:
        bit = (value >> (input_width - position)) & 1
        result = (result << 1) | bit
    return result


def left_rotate_28(value, shift):
    """Circular left shift of a 28-bit value."""
    value &= 0x0FFFFFFF
    return ((value << shift) |
            (value >> (28 - shift))) & 0x0FFFFFFF


def generate_round_keys(key_bytes):
    """Generate sixteen 48-bit round keys."""
    key_64 = int.from_bytes(key_bytes, "big")
    key_56 = permute(key_64, PC1, 64)

    c = (key_56 >> 28) & 0x0FFFFFFF
    d = key_56 & 0x0FFFFFFF
    round_keys = []

    for shift in SHIFTS:
        c = left_rotate_28(c, shift)
        d = left_rotate_28(d, shift)

        combined = (c << 28) | d
        round_key = permute(combined, PC2, 56)
        round_keys.append(round_key)

    return round_keys


def feistel(right, round_key):
    """DES round function: expansion, XOR, S-boxes, permutation."""
    expanded = permute(right, E, 32)
    mixed = expanded ^ round_key

    substituted = 0

    for i in range(8):
        six_bits = (mixed >> (42 - 6 * i)) & 0x3F

        # Outer bits select the row.
        row = ((six_bits & 0x20) >> 4) | (six_bits & 1)

        # Inner four bits select the column.
        column = (six_bits >> 1) & 0x0F

        value = S_BOXES[i][row][column]
        substituted = (substituted << 4) | value

    return permute(substituted, P, 32)


def process_block(block, round_keys):
    """Process one 64-bit block."""
    block = permute(block, IP, 64)

    left = (block >> 32) & 0xFFFFFFFF
    right = block & 0xFFFFFFFF

    for round_key in round_keys:
        left, right = right, left ^ feistel(right, round_key)

    # Swap the halves before the final permutation.
    pre_output = (right << 32) | left
    return permute(pre_output, FP, 64)


def pad(data):
    """Add PKCS#7 padding to make the length a multiple of 8 bytes."""
    padding_length = 8 - (len(data) % 8)
    return data + bytes([padding_length]) * padding_length


def unpad(data):
    """Remove and validate padding."""
    if not data:
        raise ValueError("Cannot unpad empty data.")

    padding_length = data[-1]

    if not 1 <= padding_length <= 8:
        raise ValueError("Invalid padding.")

    if data[-padding_length:] != bytes([padding_length]) * padding_length:
        raise ValueError("Invalid padding.")

    return data[:-padding_length]


def des_encrypt(plaintext_bytes, key_bytes):
    round_keys = generate_round_keys(key_bytes)
    padded = pad(plaintext_bytes)
    ciphertext = bytearray()

    for offset in range(0, len(padded), 8):
        block = int.from_bytes(padded[offset:offset + 8], "big")
        encrypted = process_block(block, round_keys)
        ciphertext.extend(encrypted.to_bytes(8, "big"))

    return bytes(ciphertext)


def des_decrypt(ciphertext, key_bytes):
    if not ciphertext or len(ciphertext) % 8 != 0:
        raise ValueError("Ciphertext must be a non-zero multiple of 8 bytes.")

    # Decryption uses the round keys in reverse order.
    round_keys = generate_round_keys(key_bytes)[::-1]
    plaintext_padded = bytearray()

    for offset in range(0, len(ciphertext), 8):
        block = int.from_bytes(ciphertext[offset:offset + 8], "big")
        decrypted = process_block(block, round_keys)
        plaintext_padded.extend(decrypted.to_bytes(8, "big"))

    return unpad(bytes(plaintext_padded))


def main():
    plaintext = input("Enter the plaintext message: ")
    key_text = input("Enter the secret key (8 ASCII characters): ")

    if not key_text.isascii() or len(key_text) != 8:
        raise ValueError("The DES key must contain exactly 8 ASCII characters.")

    key_bytes = key_text.encode("ascii")
    plaintext_bytes = plaintext.encode("utf-8")

    # Encryption
    ciphertext = des_encrypt(plaintext_bytes, key_bytes)

    print("\n--- Encryption ---")
    print("Original plaintext:", plaintext)
    print("Ciphertext (Hex):", ciphertext.hex().upper())

    # Decryption
    recovered_bytes = des_decrypt(ciphertext, key_bytes)
    recovered_plaintext = recovered_bytes.decode("utf-8")

    print("\n--- Decryption ---")
    print("Recovered plaintext:", recovered_plaintext)

    # Verification
    print("\n--- Verification ---")
    if recovered_plaintext == plaintext:
        print("Success: recovered plaintext matches original.")
    else:
        print("Failure: plaintext does not match.")


if __name__ == "__main__":
    main()