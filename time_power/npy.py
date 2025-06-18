import numpy as np
import sys
import glob  # To find .npy files

# --- Assume data.npz was successfully UNZIPPED in the current directory ---

# Find all .npy files in the current directory
npy_files = glob.glob("*.npy")

if not npy_files:
    print("Error: Could not find any extracted .npy files in the current directory.")
    print("Please make sure you have successfully run 'unzip data.npz'.")
    sys.exit(1)

print(f"Found .npy files: {npy_files}")

# Analyze each extracted .npy file
for npy_file in npy_files:
    print(f"\n--- Loading Array File: '{npy_file}' ---")
    try:
        # Load the individual .npy file
        array_content = np.load(npy_file)

        # Reuse the analysis logic from the previous script
        print(f"  Shape: {array_content.shape}")
        print(f"  Data type: {array_content.dtype}")

        if array_content.ndim == 1:
            print(f"  Length: {len(array_content)}")
            if array_content.dtype.kind in ("U", "S"):  # Character data
                try:
                    joined_string = "".join(array_content.astype(str))
                    print(f"  Content interpreted as string (first 500 chars):")
                    print(
                        joined_string[:500]
                        + ("..." if len(joined_string) > 500 else "")
                    )
                    # Check for flag
                    if "0ops{" in joined_string or "ctf{" in joined_string:
                        print("\n>>> Potential flag found in string content! <<<")
                        import re

                        flag_match = re.search(
                            r"(flag\{.*?\})|(ctf\{.*?\})", joined_string, re.IGNORECASE
                        )
                        if flag_match:
                            print(f"Extracted Flag: {flag_match.group(0)}")
                except Exception as e:
                    print(f"  Could not join array elements into a string: {e}")
                    print(f"  Content (first 200 elements): {array_content[:200]}")
            else:  # Numerical data
                print(f"  Content (first 200 elements): {array_content[:200]}")
        else:
            print(f"  Content (excerpt): {array_content}")

    except Exception as e:
        print(f"An error occurred while loading or analyzing '{npy_file}': {e}")
        import traceback

        traceback.print_exc()
