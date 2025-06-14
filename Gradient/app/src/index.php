<?php
error_reporting(0);
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $gradient = $_POST['gradient'] ?? '';
    
    if (!empty($gradient)) {
        $filePath = '/var/www/html/index.css';
        $cssContent = "
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            font-size: 4em;
        }

        p {
            margin-block-start: 0px;
            margin-block-end: 0.1em;
        }

        .line {
            height: 0.1em;
            width: 100%;
            background: linear-gradient(90deg, $gradient);
        }
        ";

        if (file_put_contents($filePath, $cssContent)) {
            echo "文件更新成功！";
        } else {
            throw new Exception("文件写入失败");
        }
    }
}
?>

<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>渐变色编辑器</title>
    <style>
        body {
            margin: 0;
            padding: 0px;
            min-height: 100vh;
            transition: background 0.5s ease;
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: flex-start;
        }

        .container {
            max-width: 800px;
            margin-top: 20px;
            background: rgba(255, 255, 255, 0.9);
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
        }

        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 40px;
        }

        .color-schemes {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            justify-content: center;
        }

        .scheme-option {
            position: relative;
            width: 180px;
            height: 60px;
            border-radius: 8px;
            overflow: hidden;
            cursor: pointer;
            border: 2px solid transparent;
            transition: all 0.3s ease;
        }

        .scheme-option:hover {
            transform: translateY(-3px);
        }

        .scheme-option.selected {
            border-color: #2196F3;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }

        .scheme-preview {
            width: 100%;
            height: 100%;
        }

        .scheme-name {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(0, 0, 0, 0.6);
            color: white;
            padding: 8px;
            font-size: 14px;
            text-align: center;
        }

        input[type="radio"] {
            display: none;
        }

        .submit-btn {
            display: block;
            margin: 30px auto 0;
            padding: 12px 40px;
            background: #2196F3;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            transition: background 0.3s;
        }

        .submit-btn:hover {
            background: #1976D2;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 渐变色编辑器</h1>
        
        <form id="colorForm" action="index.php" method="POST">
            <div class="color-schemes" id="schemesContainer"></div>
            <button type="submit" class="submit-btn">提交配色方案</button>
        </form>
    </div>

    <script>
        const colorSchemes = [
            {
                name: "黄昏之时",
                colors: ["#FFA6B7", "#1E2AD2"],
                direction: "to right"
            },
            {
                name: "碧海蓝天",
                colors: ["#4CA1AF", "#C4E0E5"],
                direction: "to bottom"
            },
            {
                name: "紫罗兰之梦",
                colors: ["#8E2DE2", "#4A00E0"],
                direction: "135deg"
            },
            {
                name: "薄荷清晨",
                colors: ["#83E8BA", "#F0F7D4"],
                direction: "to top right"
            },
            {
                name: "落日余晖",
                colors: ["#FF5F6D", "#FFC371"],
                direction: "to left"
            },
            {
                name: "深空之谜",
                colors: ["#0F2027", "#2C5364"],
                direction: "to bottom right"
            }
        ];

        function renderColorSchemes() {
            const container = document.getElementById('schemesContainer');
            
            colorSchemes.forEach((scheme, index) => {
                const wrapper = document.createElement('label');
                wrapper.className = 'scheme-option';
                wrapper.innerHTML = `
                    <input type="radio" name="colorScheme" value="${index}" 
                           ${index === 0 ? 'checked' : ''}>
                    <div class="scheme-preview" style="background: linear-gradient(
                        ${scheme.direction}, 
                        ${scheme.colors[0]}, 
                        ${scheme.colors[1]}
                    );"></div>
                    <div class="scheme-name">${scheme.name}</div>
                `;

                wrapper.addEventListener('click', () => {
                    document.querySelectorAll('.scheme-option').forEach(opt => {
                        opt.classList.remove('selected');
                    });
                    wrapper.classList.add('selected');
                    
                    document.body.style.background = `linear-gradient(
                        ${scheme.direction}, 
                        ${scheme.colors[0]}, 
                        ${scheme.colors[1]}
                    )`;
                });

                container.appendChild(wrapper);
            });
        }

        document.getElementById('colorForm').addEventListener('submit', (e) => {
            e.preventDefault();
            
            const selectedIndex = document.querySelector('input[name="colorScheme"]:checked').value;
            const selectedScheme = colorSchemes[selectedIndex];
            
            const formData = new FormData();
            formData.append('gradient', `${selectedScheme.colors[0]}, ${selectedScheme.colors[1]}`);
            
            fetch('index.php', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                alert('配色方案已提交！');
            })
            .catch(error => {
                alert('Error:', error);
            });
        });

        renderColorSchemes();
        document.querySelector('.scheme-option').click();
    </script>
</body>
</html>