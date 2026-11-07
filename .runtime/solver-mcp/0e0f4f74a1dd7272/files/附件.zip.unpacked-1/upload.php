<?php
require 'auth.php';

$upload_dir = "uploads/";
$msg = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_FILES['image'])) {
    $file = $_FILES['image'];
    $filename = basename($file['name']);
    $target = $upload_dir . $filename;

    // 从数据包中获取 Content-Type 和文件后缀
    $content_type = $file['type']; // 来自请求头
    $file_ext = strtolower(pathinfo($filename, PATHINFO_EXTENSION));

    // 读取文件内容用于检测可疑代码
    $file_content = file_get_contents($file['tmp_name']);

    // 定义要检测的可疑 PHP 代码特征
    $dangerous_patterns = [
        '<?php', '<?=','<?','`','$',
        'eval', 'system', 'exec', 'shell_exec', 'passthru',
        'base64_decode', 'assert', 'preg_replace', 'create_function', 'php'
    ];

    // 检查是否包含 PHP 代码特征
    $contains_php_code = false;
    foreach ($dangerous_patterns as $pattern) {
        if (stripos($file_content, $pattern) !== false) {
            $contains_php_code = true;
            break;
        }
    }

    // 仅当 Content-Type 和扩展名都符合要求时才允许上传
    if ($content_type === 'image/png' && $file_ext === 'png') {
        if ($contains_php_code) {
            $msg = "文件中含有可疑代码，禁止上传。";
        } elseif (move_uploaded_file($file['tmp_name'], $target)) {
            $msg = "上传成功！";
        } else {
            $msg = "上传失败。";
        }
    } else {
        $msg = "只允许上传 png 文件。";
    }

    echo $msg;
}
?>