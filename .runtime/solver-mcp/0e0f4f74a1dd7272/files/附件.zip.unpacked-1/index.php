<?php
require 'auth.php';
?>
<!DOCTYPE html>
<html>
<head>
    <title>车载应用</title>
    <link rel="stylesheet" href="assets/style.css" />
    <style>
        body {
            background: url('assets/background.png') no-repeat center center fixed;
            background-size: cover;
            color: #eee;
            font-family: "微软雅黑", sans-serif;
            margin: 0;
            padding: 0;
        }
        .container {
            text-align: center;
            padding-top: 50px;
            min-height: 100vh;
            background-color: rgba(17, 17, 17, 0);
        }
        /* 两排浮窗，三列布局 */
        .floating-boxes {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 20px;
            max-width: 960px;
            margin: 40px auto 20px auto;
        }
        .floating-box {
            flex: 0 0 calc(33.33% - 20px);
            background: rgba(0, 0, 0, 0.7);
            border: 1px solid #00b3ff;
            border-radius: 10px;
            box-shadow: 0 0 15px #00b3ff;
            height: 220px;
            color: #ddd;
            display: flex;
            justify-content: center;
            align-items: center;
            cursor: pointer;
            transition: background-color 0.3s ease, box-shadow 0.3s ease;
            text-decoration: none;
            user-select: none;
        }
        .floating-box:hover {
            background-color: rgba(0, 179, 255, 0.2);
            box-shadow: 0 0 25px #00b3ff;
            color: #00b3ff;
        }
        .floating-box h2 {
            margin: 0;
            font-size: 1.8em;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }
        /* 退出链接 */
        a.logout {
            color: #00b3ff;
            text-decoration: none;
            font-weight: bold;
            display: inline-block;
            margin-top: 20px;
        }
        a.logout:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
<div class="container">
    <h1>欢迎，<?= htmlspecialchars($_SESSION['user']) ?>！</h1>
    <p>你已成功登录车载系统。</p>

    <div class="floating-boxes">
        <a href="file.php" class="floating-box"><h2>阅读</h2></a>
        <a href="upload.php" class="floating-box"><h2>上传文件</h2></a>
        <a href="" class="floating-box"><h2>应用</h2></a>
        <a href="" class="floating-box"><h2>应用</h2></a>
        <a href="" class="floating-box"><h2>应用</h2></a>
        <a href="" class="floating-box"><h2>应用</h2></a>
    </div>

    <a href="logout.php" class="logout">退出登录</a>
</div>
</body>
</html>
