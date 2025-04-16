import base64
import requests
from gmssl import sm3, func
import binascii
import struct

# Step 1: Obtain a valid token by logging in
url = "http://ww7xxw29fv8k3tg4.instance.penguin.0ops.sjtu.cn:18080/login"
data = {"username": "tomo0", "password": "penguins"}
response = requests.post(url, data=data, allow_redirects=False)
original_token = response.headers["Location"].split("=")[1]
print(f"Original token: {original_token}")

# Step 2: Decode the token to get payload and signature
payload_b64, signature_b64 = original_token.split(".")
payload = base64.urlsafe_b64decode(
    payload_b64 + "=" * (4 - len(payload_b64) % 4)
).decode()
original_signature = base64.urlsafe_b64decode(
    signature_b64 + "=" * (4 - len(signature_b64) % 4)
).decode()
print(f"Original payload: {payload}")
print(f"Original signature: {original_signature}")

# Step 3: Prepare the new payload for CRYCRY
new_payload = "tomo0.CRYCRY"
new_payload_b64 = base64.urlsafe_b64encode(new_payload.encode()).decode().rstrip("=")
print(f"New payload (b64): {new_payload_b64}")

# Function to perform length extension attack


def sm3_length_extension(original_hash_hex, original_length, append_data):
    # Convert the original hash to the internal state
    state = []
    for i in range(0, len(original_hash_hex), 8):
        state.append(int(original_hash_hex[i : i + 8], 16))

    # Create the padding
    # Original message length in bits
    bit_length = original_length * 8
    # Padding: 0x80 followed by zeros and the length
    padding = b"\x80"
    padding += b"\x00" * ((56 - (original_length + 1) % 64) % 64)
    padding += struct.pack(">Q", bit_length)

    # Combine padding and append_data
    message = padding + append_data.encode()

    # Compute the new hash using the original state
    new_hash = sm3.sm3_hash(func.bytes_to_list(message), state)
    return new_hash


# Possible secret hex lengths (10-20 bytes => 20-40 hex chars)
possible_lengths = range(20, 41, 2)  # 20, 22, ..., 40

for length in possible_lengths:
    # Calculate the original message length in characters
    # secret_hex (length chars) + ".penguins.tomo0.GO"
    original_msg_length = length + len(".penguins.tomo0.GO")

    # Compute the new signature using length extension
    try:
        new_signature_hex = sm3_length_extension(
            original_signature, original_msg_length, ".CRYCRY"
        )
        new_signature_b64 = (
            base64.urlsafe_b64encode(binascii.unhexlify(new_signature_hex))
            .decode()
            .rstrip("=")
        )

        # Create the new token
        new_token = f"{new_payload_b64}.{new_signature_b64}"
        print(f"Trying token with length {length}: {new_token}")

        # Step 4: Send the new token to the server
        response = requests.get(
            f"http://ww7xxw29fv8k3tg4.instance.penguin.0ops.sjtu.cn:18080/login/note?token={
                new_token
            }"
        )
        if response.status_code == 200:
            print("Success! Response:")
            print(response.text)
            break
    except Exception as e:
        print(f"Error with length {length}: {e}")
else:
    print("Failed to find valid token within the length guesses.")
