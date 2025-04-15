<?php
require_once 'common.php';
try
{
    if (!isset($_SESSION['id'])) {
        header("Location: /index.php");
        exit;
    }
    $user = getUserById($_SESSION['id']);
    if ($user['state'] != 1) {
        throw new Exception("用户未激活");
    }
    if ($_SESSION['role'] !== "admin") {
        throw new Exception("仅限 admin 身份访问");
    }
    $flag = getenv('FLAG') ?? "0ops{test}";
}
catch (Exception $ex)
{
    $is_err = TRUE;
    $err_message = $ex->getMessage();
}

?>

<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>🚩</title>
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
            <h1 class="text-center mb-4 display-4 fw-bold text-primary">欢迎回来</h1>

              <?php 
                if ($is_err) {
                    echo '
                    <div class="alert alert-warning" role="alert">
                        '.htmlspecialchars($err_message).'
                    </div>
                    ';
                }
                else {
                    echo '
                    <div class="alert alert-primary" role="alert">
                        '.htmlspecialchars($flag).'
                    </div>
                    ';
                }
              ?>
          </div>
        </div>
      </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
  </body>
</html>