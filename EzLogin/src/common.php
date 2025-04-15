<?php
error_reporting(0);
session_start();

function userLogin($username, $password)
{
    $pass_param = http_build_query([
        $username, $password,
    ]);
    $url = "http://127.0.0.1/internal/db_class.php/db/login?".$pass_param;
    $response = file_get_contents($url);
    $result = json_decode($response, true);
    if (json_last_error() !== JSON_ERROR_NONE) {
        throw new Exception("JSON 解析错误：" . json_last_error_msg());
    }
    if (isset($result['error']))
    {
        throw new Exception($result['error']);
    }
    if (!isset($result['data']))
    {
        throw new Exception("找不到数据");
    }
    return $result['data'];
}

function activateUser(int $id)
{
    $pass_param = http_build_query([
        $id
    ]);
    $url = "http://127.0.0.1/internal/db_class.php/db/activate-user?".$pass_param;
    $response = file_get_contents($url);
    $result = json_decode($response, true);
    if (json_last_error() !== JSON_ERROR_NONE) {
        throw new Exception("JSON 解析错误：" . json_last_error_msg());
    }
    if (isset($result['error']))
    {
        throw new Exception($result['error']);
    }
    if (!isset($result['data']))
    {
        throw new Exception("找不到数据");
    }
    return $result['data'];
}

function getUserById(int $id)
{
    $pass_param = http_build_query([
        $id
    ]);
    $url = "http://127.0.0.1/internal/db_class.php/db/get-user-by-id?".$pass_param;
    $response = file_get_contents($url);
    $result = json_decode($response, true);
    if (json_last_error() !== JSON_ERROR_NONE) {
        throw new Exception("JSON 解析错误：" . json_last_error_msg());
    }
    if (isset($result['error']))
    {
        throw new Exception($result['error']);
    }
    if (!isset($result['data']))
    {
        throw new Exception("找不到数据");
    }
    if ($result['data']['enabled'] == 0)
    {
        throw new Exception("用户被禁用");
    }
    return $result['data'];
}

?>