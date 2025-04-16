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
