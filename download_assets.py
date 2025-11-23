import os
import urllib.request
import ssl
import time

# 忽略 SSL 证书验证 (解决 UNEXPECTED_EOF_WHILE_READING 错误)
ssl._create_default_https_context = ssl._create_unverified_context

# 定义要下载的资源和目标路径
ASSETS = [
    # CSS
    ("https://lib.baomitu.com/twitter-bootstrap/5.3.3/css/bootstrap.min.css", "volunteer/static/vendor/css/bootstrap.min.css"),
    ("https://lib.baomitu.com/bootstrap-icons/1.11.3/font/bootstrap-icons.min.css", "volunteer/static/vendor/css/bootstrap-icons.min.css"),
    ("https://lib.baomitu.com/animate.css/4.1.1/animate.min.css", "volunteer/static/vendor/css/animate.min.css"),
    
    # JS
    ("https://lib.baomitu.com/twitter-bootstrap/5.3.3/js/bootstrap.bundle.min.js", "volunteer/static/vendor/js/bootstrap.bundle.min.js"),
    ("https://lib.baomitu.com/masonry/4.2.2/masonry.pkgd.min.js", "volunteer/static/vendor/js/masonry.pkgd.min.js"),
    
    # 字体 (Bootstrap Icons 必须)
    # 注意：如果 baomitu 下载失败，脚本会自动尝试备用源
    ("https://lib.baomitu.com/bootstrap-icons/1.11.3/font/fonts/bootstrap-icons.woff2", "volunteer/static/vendor/css/fonts/bootstrap-icons.woff2"),
    ("https://lib.baomitu.com/bootstrap-icons/1.11.3/font/fonts/bootstrap-icons.woff", "volunteer/static/vendor/css/fonts/bootstrap-icons.woff"),
]

def download_file(url, filepath, retries=3):
    # 创建目录
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    for i in range(retries):
        print(f"正在下载: {filepath} (第 {i+1} 次尝试)...")
        try:
            # 伪装 User-Agent 防止被拦截
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            
            # 增加 timeout 防止卡死
            with urllib.request.urlopen(req, timeout=30) as response, open(filepath, 'wb') as out_file:
                out_file.write(response.read())
            
            print("✅ 成功")
            return # 下载成功直接退出函数
            
        except Exception as e:
            print(f"⚠️ 失败: {e}")
            if i < retries - 1:
                print("   等待 2 秒后重试...")
                time.sleep(2)
            else:
                print("❌ 最终失败，请手动下载该文件。")

if __name__ == "__main__":
    print("=== 开始下载静态资源到本地 (增强版) ===")
    for url, path in ASSETS:
        download_file(url, path)
    print("\n如果显示所有 ✅ 成功，请继续执行 Docker 构建。")