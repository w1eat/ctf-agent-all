<?php
session_start();

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = $_POST['username'];
    $password = $_POST['password'];

    if ($username==='7900F3DE89AF8E2E210263B0BEB2E431'&&$password==='6D77A7F84DE7F0A43D18E1943A1C41AD') {
        $_SESSION['user'] = $username;
        header("Location: index.php");
        exit();
    } else {
        $error = "用户名或密码错误";
    }
}
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>车载系统登录</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="assets/style.css" rel="stylesheet">
</head>
<body>
<div class="login-box">
    <h2 class="text-center">车载系统登录</h2>
    <?php if (isset($error)): ?>
        <div class="alert alert-danger"><?= $error ?></div>
    <?php endif; ?>
    <form method="post">
        <div class="mb-3">
            <input type="text" name="username" class="form-control" placeholder="用户名" required>
        </div>
        <div class="mb-3">
            <input type="password" name="password" class="form-control" placeholder="密码" required>
        </div>
        <button class="btn btn-primary w-100">登录</button>
    </form>
</div>
</body>
</html>
