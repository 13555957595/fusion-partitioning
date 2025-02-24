
在阿里云ubuntu22.04 下安装过程
1. 安装conda
    1. wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
    2. chmod +x Miniconda3-latest-Linux-x86_64.sh
    3. ./Miniconda3-latest-Linux-x86_64.sh
2. 重新打开命令行窗口
3. git clone https://gitee.com/guiding-me/fusion-unstructure-processing.git
4. conda create -n fusion-unstructure-processing python=3.10
5. conda activate  fusion-unstructure-processing
6. pip install -U magic-pdf[full]==1.1.0 --extra-index-url https://wheels.myhloli.com -i https://mirrors.aliyun.com/pypi/simple
7. 检查magic-pdf版本是否是1.1.0 命令：magic-pdf --version
8. pip install uvicorn==0.34.0 fastapi==0.115.6 minio==7.2.15 neo4j==5.28.1 -i https://mirrors.aliyun.com/pypi/simple
9. 安装模型：
    1. pip install modelscope
    2. @Deprecated  wget https://gcore.jsdelivr.net/gh/opendatalab/MinerU@master/scripts/download_models.py -O /home/download_models.py
    3. 上面一步如果不想从网络下载，也可以直接进入项目目录 /fusion-unstructure-processing/models/modelscope/download_models.py
    4. python download_models.py
10. 下载模型之后配置文件存放的路径是 /home/{user}/magic-pdf.json  模型文件路径是/home/{user}.cache/modelscope
11. 执行测试
    1. 进入测试程序目录 {fusion-unstructure-processing(git clone的项目根目录)}/demo
    2. 执行测试程序 python demo.py
12. 看日志是否正常输出
13. 如果需要GPU加速执行以下步骤
    1. 安装NVIDIA显卡驱动，自行安装，此步骤略(阿里云会自动安装显卡驱动)
    2. 检查显卡nvidia-smi 要求cuda>12.1
    3. 修改/home/{user}/magic-pdf.json   "device-mode":"cuda"
    4. 为ocr开启cuda加速 python -m pip install paddlepaddle-gpu==3.0.0b1 -i https://www.paddlepaddle.org.cn/packages/stable/cu118/
    5. CUDA加速之后性能是CPU的10倍