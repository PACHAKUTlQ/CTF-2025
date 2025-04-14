import math

# RSA parameters from previous steps
p = 66720953144911165998838491049270049821121906475512246576323412599571011308613
q = 93496017058652140120451192281187268387402942550918512435321834788719825835671
n_hex = "771b68deea7e2ecd0fa15099ae9085e1a6b163c415bde56c61ec811201d52e456e4a876db6da7af2695e206d9e3b23de02a16f675ad087c4bef3acc6c4e16ab3"
e = 65537
c_hex = "5641d8b05fda28c9af355a488bb6d97d9fe21ea645bc25814db317f04faa84a6fd93fa383396523f050b968e197f89febad840614840eebd675a3f917324f9d0"

# Convert hex strings to integers
n = int(n_hex, 16)
c = int(c_hex, 16)

# Sanity check: Ensure p * q = n
if p * q != n:
    print("Warning: p * q does not equal n! Check the factors.")
    # Use the provided n anyway for decryption if factors are suspect
    pass
else:
    print("Factors p and q multiply correctly to n.")

# 1. Calculate phi
phi = (p - 1) * (q - 1)
print(f"\nCalculated phi: {phi}")

# 2. Calculate the private exponent d (modular inverse of e mod phi)
# Using Python's built-in pow(base, exponent, modulus) for modular inverse (exponent=-1)
try:
    d = pow(e, -1, phi)
    print(f"\nCalculated private exponent d: {d}")

    # 3. Decrypt the message m = c^d mod n
    m = pow(c, d, n)
    print(f"\nCalculated decrypted message (integer): {m}")

    # 4. Convert the message integer to bytes
    # Determine the number of bytes needed (usually ceil(n.bit_length() / 8))
    byte_length = math.ceil(n.bit_length() / 8)
    message_bytes = m.to_bytes(byte_length, byteorder="big")
    print(f"\nDecrypted message (bytes): {message_bytes}")

    # 5. Decode bytes to text (assuming UTF-8)
    # Often, RSA plaintexts have leading null bytes due to padding; we might need to strip them.
    # Let's try decoding directly first.
    try:
        # Remove potential leading null bytes before decoding
        message_text = message_bytes.lstrip(b"\x00").decode("utf-8")
        print("\nDecoded message (text):")
        print("-" * 20)
        print(message_text)
        print("-" * 20)

        # Check if it looks like the flag format
        if message_text.startswith("0ops{") and message_text.endswith("}"):
            print("\nSuccess! Flag format matches.")
        else:
            print(
                "\nWarning: Decoded text might not be the flag or needs further processing."
            )

    except UnicodeDecodeError:
        print("\nError: Could not decode the decrypted bytes as UTF-8.")
        print(
            "The raw bytes might represent something else, or need different encoding."
        )

except ValueError as ve:
    print(f"\nError calculating modular inverse: {ve}")
    print(
        "This usually means e and phi are not coprime (gcd(e, phi) != 1), which would be unusual for standard RSA."
    )
except Exception as ex:
    print(f"\nAn unexpected error occurred during decryption: {ex}")
