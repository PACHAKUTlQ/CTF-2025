# Rickroll

```php
<?php
highlight_file(__FILE__);

$password =
    "Never gonna give you up," .
    "Never gonna let you down," .
    "Never gonna run around and desert you." .
    "Never gonna make you cry," .
    "Never gonna say goodbye," .
    "Never gonna tell a lie and hurt you.";
assert(strlen($password) === 172);

if (isset($_GET["input"])) {
    $input = $_GET["input"]; // try to input something with the same hash
    $input_hash = password_hash($input, PASSWORD_BCRYPT);

    if (strlen($input) < strlen($password) / 2) { // but shorter
        if (strpos($input, "cry") === false) { // and don't cry
            if (password_verify($password, $input_hash)) {
                echo 'impossible!' . PHP_EOL;
                include 'rickroll.php';
                echo $flag;
                die();
            }
        }
    }

    echo 'hello hacker';
}

?>
```

---

Bcrypt truncates passwords longer than 72 characters. Thus, any password longer than 72 characters will have the same hash as its first 72 characters.

The original password is 172 characters long. We need an input shorter than 86 characters (half of 172) that does not contain "cry" and matches the first 72 characters of the password.

Solution:

```php
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
```

Visit `http://redacted.com/?input=Never+gonna+give+you+up%2CNever+gonna+let+you+down%2CNever+gonna+run+around+`, and got result:

`impossible! 0ops{Y0u_know_7he_ru1e5_6nd_BV1GJ411x7h7}`