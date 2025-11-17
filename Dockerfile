FROM python:3.9-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt /app/

# === 核心升级：指定使用清华大学的高速镜像源 ===
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY . /app/

# 收集静态文件到STATIC_ROOT目录
RUN python manage.py collectstatic --noinput