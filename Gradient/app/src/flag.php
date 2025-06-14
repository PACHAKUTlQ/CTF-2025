<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>Hello</title>
    <link rel="stylesheet" href="index.css">
</head>
<body>
    <div>
        <p>
        <?php
        error_reporting(0);
        $flag = getenv('FLAG') ?? "0ops{test}";
        $colors = ['#F44336', '#FF9800', '#FFEB3B', '#8BC34A', '#03A9F4', '#5C6BC0', '#AB47BC'];
        
        if (!empty($flag)) {
            for ($i = 0; $i < strlen($flag); $i++) {
                $color_index = $i % 7;
                $char = htmlspecialchars($flag[$i]);
                echo "<span style=\"color: {$colors[$color_index]}\">$char</span>";
            }
        }
        ?>
        </p>
        <div class="line" />
    </div>
</body>
</html>