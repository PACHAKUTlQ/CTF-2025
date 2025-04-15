<?php
require_once 'common.php';
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $username = $password = '';
    extract($_POST, EXTR_IF_EXISTS);
    
    try {
        if (preg_match('/[^\w]/', $username) or preg_match('/[^\w]/', $password)) {
            throw new Exception("用户名和密码只能包含字母、数字和下划线！");
        }
        $login_res = userLogin($username, $password);
        if (isset($login_res) and isset($login_res['id']) and ctype_digit($login_res['id']))
        {
            $user = getUserById($login_res['id']);
            activateUser($login_res['id']);
            $_SESSION['id'] = $user['id'];
            $_SESSION['role'] = $user['role'];
        }
        else 
        {
            throw new Exception("id 错误");
        }
        $is_post = TRUE;
        $is_err = FALSE;
        header("Location: /admin.php");
        exit;
    }
    catch (Exception $ex)
    {
        $is_post = TRUE;
        $is_err = TRUE;
        $err_message = $ex->getMessage();
    }
} 
?>

<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>登录页面</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
      body {
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        min-height: 100vh;
      }
      
      .login-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
        transition: transform 0.3s ease;
      }
      
      .login-card:hover {
        transform: translateY(-5px);
      }
      
      .form-control:focus {
        border-color: #23d5ab;
        box-shadow: 0 0 0 0.25rem rgba(35, 213, 171, 0.25);
      }
      
      @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
      }
    </style>
  </head>
  <body class="d-flex align-items-center">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-12 col-md-8 col-lg-6">
          <div class="login-card p-5">
            <h1 class="text-center mb-4 display-4 fw-bold text-primary">欢迎登录</h1>
            <form method="POST" action="<?= htmlspecialchars($_SERVER['PHP_SELF']) ?>">
              <!-- 用户名输入 -->
              <div class="mb-4">
                <label for="username" class="form-label">用户名</label>
                <input 
                  type="text" 
                  class="form-control form-control-lg" 
                  id="username"
                  name="username"
                  placeholder="请输入用户名"
                  required
                >
              </div>

              <!-- 密码输入 -->
              <div class="mb-4">
                <label for="password" class="form-label">密码</label>
                <input 
                  type="password" 
                  class="form-control form-control-lg" 
                  id="password"
                  name="password"
                  placeholder="请输入密码"
                  required
                >
              </div>

              <?php 
                if ($is_err) {
                    echo '
                    <div class="alert alert-warning" role="alert">
                        '.htmlspecialchars($err_message).'
                    </div>
                    ';
                }
              ?>

              <!-- 登录按钮 -->
              <button 
                type="submit" 
                class="btn btn-primary btn-lg w-100 mt-3 fw-bold"
                style="letter-spacing: 2px;"
              >
                登 录
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
  </body>
</html>