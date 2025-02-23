# 使用 Ubuntu 22.04 作为基础镜像
FROM ubuntu-conda:22.04

ENV DEBIAN_FRONTEND=noninteractive

# 设置工作目录为/app
WORKDIR /app

# 将当前目录内容复制到容器的/app中
COPY . /app


## 创建 Conda 环境并安装 Python 3.10
#RUN conda create -n fusion-unstructure-processing python=3.10 && \
#    conda init bash && \
#    /bin/bash -c "source ~/.bashrc && conda activate fusion-unstructure-processing"
#
#RUN conda activate fusion-unstructure-processing
#

RUN conda create --name fusion-unstructure-processing python=3.10 \
    && /bin/bash -c "source activate fusion-unstructure-processing" \
    && echo "conda activate fusion-unstructure-processing" >> ~/.bashrc

#更新pip
RUN pip install --upgrade pip

# 安装任何需要的库
RUN pip install -r requirements-1.0.1.txt -i https://mirrors.aliyun.com/pypi/simple --extra-index-url https://wheels.myhloli.com --extra-index-url https://download.pytorch.org/whl/cu118

# 使端口8000可公开访问
EXPOSE 8000

# 运行main.py
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]



