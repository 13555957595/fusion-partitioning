import os
import shutil
import subprocess
import sys

def get_conda_env_path():
    """获取当前 Conda 环境的路径"""
    conda_prefix = os.environ.get("CONDA_PREFIX")
    if not conda_prefix:
        raise RuntimeError("当前不在 Conda 环境中，请激活 Conda 环境后再运行此脚本。")
    return conda_prefix

def copy_dependency_to_site_packages(project_dir, conda_env_path):
    """将 dependency 目录下的内容复制到 Conda 环境的 site-packages 目录中"""
    dependency_dir = os.path.join(project_dir, "dependency")
    site_packages_dir = os.path.join(conda_env_path, "Lib", "site-packages")

    if not os.path.exists(dependency_dir):
        raise FileNotFoundError(f"依赖目录 {dependency_dir} 不存在。")

    if not os.path.exists(site_packages_dir):
        raise FileNotFoundError(f"site-packages 目录 {site_packages_dir} 不存在。")

    # 复制所有文件和文件夹
    for item in os.listdir(dependency_dir):
        source = os.path.join(dependency_dir, item)
        destination = os.path.join(site_packages_dir, item)

        if os.path.isdir(source):
            shutil.copytree(source, destination, dirs_exist_ok=True)
        else:
            shutil.copy2(source, destination)

    print(f"已将 {dependency_dir} 中的内容复制到 {site_packages_dir}。")

def install_requirements(project_dir):
    """执行 pip install -r requirements.txt 命令"""
    requirements_file = os.path.join(project_dir, "requirements.txt")
    if not os.path.exists(requirements_file):
        raise FileNotFoundError(f"requirements.txt 文件 {requirements_file} 不存在。")

    command = [
        "pip", "install", "-r", requirements_file,
        "-i", "https://mirrors.aliyun.com/pypi/simple",
        "--extra-index-url", "https://wheels.myhloli.com",
        "--extra-index-url", "https://download.pytorch.org/whl/cu118"
    ]

    try:
        subprocess.run(command, check=True)
        print("依赖安装完成。")
    except subprocess.CalledProcessError as e:
        print(f"依赖安装失败：{e}")

def main():
    # 获取当前项目目录
    project_dir = os.getcwd()

    try:
        # 获取当前 Conda 环境路径
        conda_env_path = get_conda_env_path()
        print(f"当前 Conda 环境路径：{conda_env_path}")

        # 复制 dependency 目录到 site-packages
        copy_dependency_to_site_packages(project_dir, conda_env_path)

        # 安装 requirements.txt 中的依赖
        install_requirements(project_dir)
    except Exception as e:
        print(f"脚本执行失败：{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()