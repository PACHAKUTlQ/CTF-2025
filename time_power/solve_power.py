import numpy as np
import matplotlib.pyplot as plt
import sys

# --- Configuration ---
PLOT_AVERAGES = True  # Set to True to generate plots for each position
# ---

# Load the data
try:
    power_traces = np.load("power.npy")
    guessed_chars = np.load("input.npy")
    position_ids = np.load("input_id.npy")
    print("Successfully loaded .npy files.")
    print(f"Power traces shape: {power_traces.shape}")
    print(f"Guessed chars shape: {guessed_chars.shape}")
    print(f"Position IDs shape: {position_ids.shape}")

except FileNotFoundError:
    print(
        "Error: One or more .npy files (power.npy, input.npy, input_id.npy) not found."
    )
    # ... (rest of error handling)
    sys.exit(1)
except Exception as e:
    print(f"An error occurred loading the .npy files: {e}")
    sys.exit(1)

# Determine the length of the secret password/flag
num_positions = np.max(position_ids) + 1
print(f"\nInferred password/flag length: {num_positions}")

recovered_secret = ""

# Iterate through each position in the secret
for p in range(num_positions):
    print(f"\nAnalyzing position {p}...")

    indices_for_pos = np.where(position_ids == p)[0]
    if len(indices_for_pos) == 0:
        print(f"  Warning: No data found for position {p}. Skipping.")
        recovered_secret += "?"
        continue

    power_at_pos = power_traces[indices_for_pos]
    chars_at_pos = guessed_chars[indices_for_pos]
    unique_chars_guessed = np.unique(chars_at_pos)
    print(f"  Characters guessed at this position: {
          ''.join(unique_chars_guessed)}")

    overall_avg_trace = np.mean(power_at_pos, axis=0)
    char_metrics = {}  # Store a difference metric for each character

    if PLOT_AVERAGES:
        plt.figure(figsize=(12, 6))
        plt.title(
            f"Position {
                p
            }: Average Power Trace per Guessed Character (Metric: Max Abs Diff)"
        )  # Updated title
        plt.xlabel("Time Sample")
        plt.ylabel("Average Power")

    for char in unique_chars_guessed:
        indices_for_char = np.where(chars_at_pos == char)[0]
        traces_for_char = power_at_pos[indices_for_char]
        avg_trace_for_char = np.mean(traces_for_char, axis=0)
        diff_trace = avg_trace_for_char - overall_avg_trace

        # --- !!! USE MAX ABSOLUTE DIFFERENCE METRIC !!! ---
        metric = np.max(np.abs(diff_trace))
        # --- !!! ---

        char_metrics[char] = metric

        if PLOT_AVERAGES:
            # Changed label slightly to avoid confusion if metric values are very small/large
            plt.plot(
                avg_trace_for_char,
                label=f"Guess: '{char}' (Metric: {metric:.4f})",
                alpha=0.7,
            )

    if not char_metrics:
        print(f"  Error: No metrics calculated for position {p}.")
        best_char = "?"
    else:
        # Find the character with the maximum difference metric
        best_char = max(char_metrics, key=char_metrics.get)
        # Get the value for printing
        best_metric_value = char_metrics[best_char]
        print(
            f"  Best character based on MaxAbsDiff metric ({best_metric_value:.4f}): '{
                best_char
            }'"
        )

    recovered_secret += best_char

    if PLOT_AVERAGES:
        try:
            indices_for_best_char = np.where(chars_at_pos == best_char)[0]
            traces_for_best_char = power_at_pos[indices_for_best_char]
            avg_trace_for_best_char = np.mean(traces_for_best_char, axis=0)
            # Highlight the best trace
            plt.plot(
                avg_trace_for_best_char,
                label=f"BEST: '{best_char}'",
                linewidth=3,
                color="red",
            )
        except (ValueError, KeyError):
            print(f"  Could not plot best char '{best_char}'.")

        plt.legend(loc="center left", bbox_to_anchor=(1, 0.5))
        plt.grid(True)
        plt.tight_layout(rect=[0, 0, 0.85, 1])
        plt.savefig(f"position_{p}_avg_traces_maxabs.png")  # Changed filename
        plt.close()

# Print the final recovered secret
print(f"\n\nRecovered Secret (using MaxAbsDiff): {recovered_secret}")

# Check format again
if recovered_secret.startswith("0ops{") and recovered_secret.endswith(
    "}"
):  # Check end bracket if length allows
    print("Format looks like a flag!")
elif recovered_secret.startswith("0ops{"):
    print(
        "Starts like a flag, might be missing the closing bracket '}' if dataset was incomplete."
    )
else:
    print("Format might not be a standard flag, check the result carefully.")
