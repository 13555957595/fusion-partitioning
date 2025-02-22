# 使用官方Python基础镜像
FROM python:3.10-slim

# 设置工作目录为/app
WORKDIR /app

# 将当前目录内容复制到容器的/app中
COPY . /app

#更新pip
RUN pip install --upgrade pip

# 安装任何需要的库
RUN pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple --extra-index-url https://wheels.myhloli.com --extra-index-url https://download.pytorch.org/whl/cu118

# 使端口8000可公开访问
EXPOSE 8000

# 运行main.py
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]