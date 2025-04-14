# RFC 1924 Character Set
RFC1924_CHARS = b"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{|}~"
# Create a reverse mapping (char -> index)
RFC1924_MAP = {char: index for index, char in enumerate(RFC1924_CHARS)}


def decode_rfc1924_base85(encoded_str):
    encoded_bytes = encoded_str.encode("ascii")
    # Ignore whitespace
    encoded_bytes = bytes(c for c in encoded_bytes if not chr(c).isspace())

    decoded_data = bytearray()
    n = len(encoded_bytes)
    i = 0

    while i < n:
        # Process group of up to 5 chars
        group_chars = encoded_bytes[i : min(i + 5, n)]
        num_chars = len(group_chars)
        i += 5  # Move index forward by 5 regardless of actual group size read

        if num_chars == 0:
            break

        value = 0
        power = 4  # Start with the highest power (85^4)

        # Calculate numerical value for the group
        for k in range(num_chars):
            char_byte = group_chars[k]
            if char_byte not in RFC1924_MAP:
                raise ValueError(
                    f"Invalid character in RFC 1924 Base85 input: '{
                        chr(char_byte)
                    }' at position {i - 5 + k}"
                )
            value += RFC1924_MAP[char_byte] * (85 ** (power - k))

        # If the group was short (last group), add implicit padding value contribution
        # The spec implies padding with '0's conceptually for calculation if short
        for k in range(num_chars, 5):
            value += RFC1924_MAP[b"0"[0]] * (
                85 ** (power - k)
            )  # RFC1924 uses '0' for 0

        # Determine number of output bytes based on original number of chars processed
        num_output_bytes = 4 if num_chars == 5 else num_chars - 1
        if num_output_bytes < 0:  # Should not happen if num_chars > 0
            num_output_bytes = 0

        # Convert the value to 4 bytes (big-endian)
        temp_bytes = value.to_bytes(4, byteorder="big")

        # Append the correct number of bytes
        decoded_data.extend(temp_bytes[:num_output_bytes])

    return bytes(decoded_data)


ciphertext_block2 = "NhfU}b8jGXZ*p>ZEFeiBW^Zz5Z*(AZZy<AFc4Z)RXk{R9a%py9bY&oGWqBZUZy;o4V{c?-AarPDAZBb~XD%Q@b#x$eZ*65Db9HcKa$|38aCLNLav*47c4Z)8Y;t8`WO*QCa$#d@Wn>^}bRc1FWFU2LY;R#?Wn>_9Zy;fAAa8DLX>Mg8WMVELLt$<pd2e+fW@&C@AarPDAZBb~XFm!GZXi7%FnBjNF=942WMySxH)S$qV`MO9VKFr@IXPivIWRaiWieqkVlg%|V>B@}Vq|4CHe)t1Wn(xoF)}bQWHmBnG&MG5G+{V5He_NpWMMa9W->N8HDxj|He@+vGh#9`WMwciVKFvlHa9h4WH2~4V>DuAW;0=9V>V+nWid8kVlxV5AUz;9H8nFg3S%HWATW3}HZ(D0IASn0W@KS9IAb|sW-~Q4VKg{6Vq!LAIX7fEW@R!lWnnfnHDY5jH8?ReWMVThH)b$2W?^ACG+{PoWH~ctVKX>0GdVUjGBai{H85g1HaKN5IX7lFIc8;IVPrToFg7tXI5aS2WnyGDH#K21W;ro8Gcq)0Ib<*j"

try:
    decoded_bytes = decode_rfc1924_base85(ciphertext_block2)

    # Assume the output contains RSA parameters (N, e, c) usually separated or in a known format
    # A common way is just concatenating them as bytes, or using some separator like newline.
    # Let's print the result as hex first to inspect.

    print("Successfully decoded RFC 1924 Base85.")
    print("Decoded bytes (hex):")
    print(decoded_bytes.hex())

    # Also try to print as text in case it's formatted that way
    try:
        print("\nAttempting to decode bytes as UTF-8 text:")
        print("-" * 20)
        print(decoded_bytes.decode("utf-8"))
        print("-" * 20)
    except UnicodeDecodeError:
        print("\nDecoded bytes are not valid UTF-8 text (as expected for RSA params).")
        # If it's not text, perhaps we can guess the structure?
        # Often e is small (like 65537). N and c are large.
        # Let's assume it's N || e || c or similar. Need length info.
        # For now, manual inspection of the hex output is needed.

except ValueError as e:
    print(f"Error decoding RFC 1924 Base85: {e}")
except Exception as e:
    print(f"An unexpected error occurred during decoding: {e}")
