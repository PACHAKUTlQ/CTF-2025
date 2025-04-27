package main

import (
	"bufio"
	"context"
	"fmt"
	"io"
	"log"
	"net"
	"net/http"
	"net/url"
	"os"
	"os/signal"
	"regexp"
	"strconv"
	"strings"
	"sync"
	"syscall"
	"time"
)

const (
	proxyAPIURL = "http://dddip.top/api/get?token=6a10c737762325648501984856361d&number=50&type=https&format=3"
	// proxyAPIURL        = "http://58ip.top/api/get?token=07b572fe1f007b6f5ebf4f832b74e3&number=50&type=socket5&format=3"
	targetURL          = "http://141.148.189.179:40529/collect.php?id=B3g5VNPisFZABxYs" // must be http
	proxyFetchInterval = 5200 * time.Millisecond
	numWorkers         = 20               // Number of concurrent workers visiting the target
	httpClientTimeout  = 15 * time.Second // Timeout for visiting the target via proxy
	proxyChannelSize   = 100              // Buffer size for the proxy channel
)

// Thread-safe set for unused /8 ranges
type UnusedRanges struct {
	mu     sync.RWMutex
	ranges map[int]struct{}
}

// Global variables
var (
	unusedRanges = &UnusedRanges{ranges: make(map[int]struct{})}
	proxyChan    = make(chan string, proxyChannelSize)
	wg           sync.WaitGroup
	// Regex to find the list of unused ranges in the HTML
	// Looks for "<p>未占领的/8网段：" followed by numbers and commas, ending with "</p>"
	unusedRangesRegex = regexp.MustCompile(`未占领的/8网段：([0-9,\s]+)</p>`)
	// Regex to find individual numbers in the comma-separated list
	numberRegex = regexp.MustCompile(`\d+`)
	// Success/Fail messages
	successMessage     = "现已占领成功"
	alreadyUsedMessage = "已被成功占领过"
)

// --- Initialization ---

// Fetches the initial list of unused ranges from the target site without a proxy
func fetchInitialUnusedRanges() error {
	log.Println("Attempting to fetch initial list of unused /8 ranges...")
	client := &http.Client{
		Timeout: httpClientTimeout,
	}
	resp, err := client.Get(targetURL)
	if err != nil {
		return fmt.Errorf("failed to fetch initial page: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("initial fetch failed with status code: %d", resp.StatusCode)
	}

	bodyBytes, err := io.ReadAll(resp.Body)
	if err != nil {
		return fmt.Errorf("failed to read initial response body: %w", err)
	}

	bodyString := string(bodyBytes)
	newRanges, err := parseUnusedRanges(bodyString)
	if err != nil {
		// Log the body if parsing fails, it might help debugging
		log.Printf("Failed to parse initial ranges. Body received:\n%s", bodyString)
		return fmt.Errorf("failed to parse initial unused ranges: %w", err)
	}

	unusedRanges.mu.Lock()
	unusedRanges.ranges = newRanges
	count := len(unusedRanges.ranges)
	unusedRanges.mu.Unlock()

	log.Printf("Successfully fetched and parsed initial unused ranges. Count: %d", count)
	return nil
}

// Parses the comma-separated list of /8 ranges from the HTML body
func parseUnusedRanges(body string) (map[int]struct{}, error) {
	matches := unusedRangesRegex.FindStringSubmatch(body)
	if len(matches) < 2 {
		// Try harder: look for just the numbers if the exact pattern failed
		potentialNumbers := numberRegex.FindAllString(body, -1)
		if len(potentialNumbers) > 5 { // Heuristic: If we find many numbers, assume it's the list
			log.Printf("Warning: Could not find exact pattern '未占领的/8网段：...'. Found loose numbers: %v", potentialNumbers)
			numListStr := strings.Join(potentialNumbers, ",")
			return parseNumbersFromString(numListStr)
		}
		log.Printf("Body content: %s", body) // Log body if parsing fails
		return nil, fmt.Errorf("could not find unused ranges pattern in body")
	}

	numListStr := matches[1]
	return parseNumbersFromString(numListStr)
}

func parseNumbersFromString(numListStr string) (map[int]struct{}, error) {
	parsedRanges := make(map[int]struct{})
	numbers := numberRegex.FindAllString(numListStr, -1)
	if numbers == nil {
		// This case might happen if the list is empty or format is unexpected
		log.Printf("Warning: No numbers found in the supposedly matched range string: '%s'", numListStr)
		return parsedRanges, nil // Return an empty map
	}

	for _, numStr := range numbers {
		numStr = strings.TrimSpace(numStr)
		if numStr == "" {
			continue
		}
		num, err := strconv.Atoi(numStr)
		if err != nil {
			log.Printf("Warning: Failed to convert number '%s' to int: %v", numStr, err)
			continue // Skip invalid numbers
		}
		if num >= 0 && num <= 255 {
			parsedRanges[num] = struct{}{}
		} else {
			log.Printf("Warning: Parsed number %d is outside valid /8 range (0-255)", num)
		}
	}
	return parsedRanges, nil
}

// --- Proxy Fetcher ---

func proxyFetcher(ctx context.Context) {
	defer wg.Done()
	ticker := time.NewTicker(proxyFetchInterval)
	defer ticker.Stop()

	client := &http.Client{
		Timeout: proxyFetchInterval - 1*time.Second, // Timeout slightly less than interval
	}

	for {
		select {
		case <-ctx.Done():
			log.Println("Proxy fetcher stopping...")
			return
		case <-ticker.C:
			log.Println("Fetching new proxies...")
			resp, err := client.Get(proxyAPIURL)
			if err != nil {
				log.Printf("Error fetching proxies: %v", err)
				continue
			}

			if resp.StatusCode != http.StatusOK {
				log.Printf("Error fetching proxies: Status code %d", resp.StatusCode)
				io.Copy(io.Discard, resp.Body) // Consume body to allow connection reuse
				resp.Body.Close()
				continue
			}

			scanner := bufio.NewScanner(resp.Body)
			fetchedCount := 0
			for scanner.Scan() {
				proxy := strings.TrimSpace(scanner.Text())
				if proxy != "" && strings.Contains(proxy, ":") {
					// Try adding to channel, but don't block if full
					select {
					case proxyChan <- proxy:
						fetchedCount++
					default:
						log.Println("Proxy channel full, discarding fetched proxy.")
					}
				}
			}
			resp.Body.Close() // Close body explicitly

			if err := scanner.Err(); err != nil {
				log.Printf("Error reading proxy response body: %v", err)
			}
			if fetchedCount > 0 {
				log.Printf("Fetched and added %d proxies to the channel.", fetchedCount)
			} else {
				log.Println("No valid proxies found in the response.")
			}
		}
	}
}

// --- Visit Worker ---

func visitWorker(ctx context.Context, id int) {
	defer wg.Done()
	log.Printf("Worker %d starting...", id)

	for {
		select {
		case <-ctx.Done():
			log.Printf("Worker %d stopping...", id)
			return
		case proxyAddr := <-proxyChan:
			// 1. Parse Proxy and get /8
			host, _, err := net.SplitHostPort(proxyAddr)
			if err != nil {
				log.Printf("[Worker %d] Error parsing proxy address '%s': %v", id, proxyAddr, err)
				continue
			}
			ip := net.ParseIP(host)
			if ip == nil || ip.To4() == nil {
				log.Printf("[Worker %d] Invalid or non-IPv4 proxy IP '%s'", id, host)
				continue
			}
			ipV4 := ip.To4()
			slash8 := int(ipV4[0])

			// 2. Check if /8 is needed (Read Lock)
			unusedRanges.mu.RLock()
			_, needed := unusedRanges.ranges[slash8]
			currentCount := len(unusedRanges.ranges)
			unusedRanges.mu.RUnlock()

			if !needed {
				// log.Printf("[Worker %d] Skipping proxy %s, /8 range %d is not needed.", id, proxyAddr, slash8)
				continue
			}
			if currentCount == 0 {
				log.Printf("[Worker %d] Unused range set is empty, worker stopping.", id)
				// Potentially signal global completion here if needed
				return
			}

			log.Printf("[Worker %d] Trying proxy %s for /8 range %d (Remaining: %d)", id, proxyAddr, slash8, currentCount)

			// 3. Visit Target using Proxy
			proxyURL, err := url.Parse("http://" + proxyAddr) // Assuming HTTP proxy, change to https if needed
			if err != nil {
				log.Printf("[Worker %d] Error parsing proxy URL '%s': %v", id, proxyAddr, err)
				continue
			}

			client := &http.Client{
				Transport: &http.Transport{
					Proxy: http.ProxyURL(proxyURL),
					DialContext: (&net.Dialer{ // Add dial timeout
						Timeout:   httpClientTimeout,
						KeepAlive: 30 * time.Second, // Optional KeepAlive
					}).DialContext,
					TLSHandshakeTimeout:   10 * time.Second, // Relevant even for HTTP proxies if they tunnel HTTPS
					ExpectContinueTimeout: 1 * time.Second,
				},
				Timeout: httpClientTimeout,
			}

			req, err := http.NewRequestWithContext(ctx, "GET", targetURL, nil)
			if err != nil {
				log.Printf("[Worker %d] Error creating request for %s: %v", id, targetURL, err)
				continue
			}
			// Add a common user agent?
			req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

			resp, err := client.Do(req)
			if err != nil {
				// Handle context deadline explicitly
				if ctx.Err() != nil {
					log.Printf("[Worker %d] Context cancelled/timed out during request for /8 %d via %s.", id, slash8, proxyAddr)
					return // Exit worker if context is done
				}
				log.Printf("[Worker %d] Error visiting target with proxy %s for /8 %d: %v", id, proxyAddr, slash8, err)
				continue // Try next proxy
			}

			bodyBytes, readErr := io.ReadAll(resp.Body)
			resp.Body.Close() // Close body immediately after reading

			if resp.StatusCode != http.StatusOK {
				log.Printf("[Worker %d] Target visit failed with proxy %s (/8: %d): Status %d", id, proxyAddr, slash8, resp.StatusCode)
				continue // Try next proxy
			}

			if readErr != nil {
				log.Printf("[Worker %d] Error reading target response body with proxy %s (/8: %d): %v", id, proxyAddr, slash8, readErr)
				continue // Try next proxy
			}

			bodyString := string(bodyBytes)

			// 4. Parse Response and Update State (Write Lock)
			newRangesMap, parseErr := parseUnusedRanges(bodyString)
			if parseErr != nil {
				log.Printf("[Worker %d] CRITICAL: Failed to parse unused ranges from server response using proxy %s (/8: %d): %v. Body: %s", id, proxyAddr, slash8, parseErr, bodyString)
				// Don't update the set if we can't parse the authoritative list
				continue
			}

			// Determine outcome
			visitSucceeded := strings.Contains(bodyString, successMessage)
			visitAlreadyUsed := strings.Contains(bodyString, alreadyUsedMessage)

			// Acquire Write Lock to update the shared state
			unusedRanges.mu.Lock()

			// **Crucially, update our set based on the *server's* response**
			unusedRanges.ranges = newRangesMap
			updatedCount := len(unusedRanges.ranges)

			if visitSucceeded {
				log.Printf("[Worker %d] SUCCESS! Claimed /8 range %d using proxy %s. Remaining: %d", id, slash8, proxyAddr, updatedCount)
				// The range should already be gone from newRangesMap if the server response is accurate
				// _, stillExists := unusedRanges.ranges[slash8]
				// if stillExists {
				//     log.Printf("[Worker %d] WARNING: Range %d claimed but still present in server list?!", id, slash8)
				//     delete(unusedRanges.ranges, slash8) // Force remove if inconsistent
				//     updatedCount = len(unusedRanges.ranges)
				// }

			} else if visitAlreadyUsed {
				log.Printf("[Worker %d] Info: Range %d via proxy %s was already claimed by someone. Remaining: %d", id, slash8, proxyAddr, updatedCount)
				// Ensure it's removed locally based on the server list update above
				// _, stillExists := unusedRanges.ranges[slash8]
				// if stillExists {
				//     log.Printf("[Worker %d] WARNING: Range %d already claimed but still present in server list?!", id, slash8)
				//     delete(unusedRanges.ranges, slash8) // Force remove if inconsistent
				//     updatedCount = len(unusedRanges.ranges)
				// }
			} else {
				// Neither success nor already used message found. Maybe an error page or unexpected content.
				log.Printf("[Worker %d] Warning: Unexpected content received for /8 %d via proxy %s. Neither success nor already-used message found. Remaining: %d. Body snippet: %s", id, slash8, proxyAddr, updatedCount, firstN(bodyString, 100))
				// We still trust the parsed list of ranges from this response.
			}

			unusedRanges.mu.Unlock() // Release Write Lock

			// Check for completion after update
			if updatedCount == 0 {
				log.Printf("***** All /8 ranges claimed! Worker %d detected completion. *****", id)
				// This worker can exit. Need a mechanism to stop others.
				// We rely on the main context cancellation for now.
				return
			}
		}
	}
}

// Helper to get first N characters of a string
func firstN(s string, n int) string {
	if len(s) > n {
		return s[:n] + "..."
	}
	return s
}

// --- Main ---

func main() {
	log.Println("Starting CTF /8 range claimer...")

	// Basic validation
	if targetURL == "http://<target-ip-or-domain>" || proxyAPIURL == "http://proxy-pool.com/some-path" {
		log.Fatal("Please change placeholder URLs (targetURL, proxyAPIURL) in the code.")
	}
	if !strings.HasPrefix(targetURL, "http://") {
		log.Fatal("Target URL must use http://")
	}

	// 1. Initial fetch of unused ranges
	err := fetchInitialUnusedRanges()
	if err != nil {
		log.Fatalf("Failed to get initial state: %v", err)
	}

	unusedRanges.mu.RLock()
	initialCount := len(unusedRanges.ranges)
	unusedRanges.mu.RUnlock()
	if initialCount == 0 {
		log.Println("Initial fetch shows 0 unused ranges. Nothing to do.")
		return
	}

	// Context for cancellation
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel() // Ensure cancel is called eventually

	// Start signal handler for graceful shutdown (optional but good practice)
	go func() {
		sigChan := make(chan os.Signal, 1)
		signal.Notify(sigChan, os.Interrupt, syscall.SIGTERM)
		<-sigChan
		log.Println("Received shutdown signal, cancelling operations...")
		cancel()
	}()

	// 2. Start Proxy Fetcher
	wg.Add(1)
	go proxyFetcher(ctx)

	// 3. Start Workers
	log.Printf("Starting %d workers...", numWorkers)
	for i := 0; i < numWorkers; i++ {
		wg.Add(1)
		go visitWorker(ctx, i+1)
	}

	// Monitor goroutine to check for completion and cancel context
	go func() {
		ticker := time.NewTicker(5 * time.Second) // Check every 5 seconds
		defer ticker.Stop()
		for {
			select {
			case <-ctx.Done():
				return // Context already cancelled
			case <-ticker.C:
				unusedRanges.mu.RLock()
				count := len(unusedRanges.ranges)
				unusedRanges.mu.RUnlock()
				if count == 0 {
					log.Println("Completion detected by monitor: 0 unused ranges remaining. Stopping...")
					cancel() // Signal all goroutines to stop
					return
				}
			}
		}
	}()

	log.Println("Initialization complete. Workers running.")
	wg.Wait() // Wait for all goroutines (fetcher + workers) to finish
	log.Println("All workers and fetcher have stopped. Exiting.")
}
