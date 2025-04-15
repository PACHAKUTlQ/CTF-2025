<?php

$pdo = new PDO('sqlite:/app/ezlogin.db');
$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

$method_map = [
    '/db/login' => 'login',
    '/db/get-user-by-id' => 'getUserById',
    '/db/activate-user' => 'activateUser',
];

$route = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$script_name = $_SERVER['SCRIPT_NAME'];
$route = str_replace($script_name, '', $route);
$queryString = $_SERVER['QUERY_STRING'] ?? '';
$params = parseQueryString($queryString);

if (isset($method_map[$route])) {
    $function = $method_map[$route];
    $result = $function($params);
    header('Content-Type: application/json');
    echo json_encode($result);
} else {
    header("HTTP/1.1 404 Not Found");
    header('Content-Type: application/json');
    echo json_encode(["error" => "路由错误"]);
}

function parseQueryString($query) {
    $result = [];
    $pairs = explode('&', $query);
    foreach ($pairs as $pair) {
        $split = explode('=', $pair, 2);
        $key = urldecode($split[0] ?? '');
        $value = urldecode($split[1] ?? '');
        array_push($result, $value);
    }
    return $result;
}

function login($params) {
    global $pdo;
    try {
        $query = "SELECT id FROM users WHERE username = '$params[0]' and password = '$params[1]'";
        $stmt = $pdo->query($query);
        $user = $stmt->fetch(PDO::FETCH_ASSOC);
    
        if ($user) {
            return ["data" => $user];
        } else {
            return ["error" => "用户名或密码错误"];
        }
    } catch (PDOException $e) {
        return ["error" => "数据库错误".$e];
    }
}

function getUserById($params) {
    global $pdo;
    try {
        $query = "SELECT * FROM users WHERE id = $params[0]";
        $stmt = $pdo->query($query);
        $user = $stmt->fetch(PDO::FETCH_ASSOC);
    
        if ($user) {
            return ["data" => $user];
        } else {
            return ["error" => "找不到用户"];
        }
    } catch (PDOException $e) {
        return ["error" => "数据库错误"];
    }
}

function activateUser($params) {
    global $pdo;
    try {
        $query = "UPDATE users SET state = 1 WHERE id = $params[0]";
        $rows_changed = $pdo->exec($query);
    
        if ($rows_changed === 1) {
            return ["data" => TRUE];
        } else {
            return ["error" => "更新失败"];
        }
    } catch (PDOException $e) {
        return ["error" => "数据库错误"];
    }
}

?>