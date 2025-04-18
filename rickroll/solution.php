<?php
// Reconstruct the password
$password = "Never gonna give you up," .
    "Never gonna let you down," .
    "Never gonna run around and desert you." .
    "Never gonna make you cry," .
    "Never gonna say goodbye," .
    "Never gonna tell a lie and hurt you.";

// Take the first 72 characters of the password
$input = substr($password, 0, 72);

// URL encode the input to handle spaces and special characters
$urlEncodedInput = urlencode($input);

// Output the payload URL
echo "Payload URL: http://example.com/challenge.php?input=" . $urlEncodedInput . "\n";
?>
