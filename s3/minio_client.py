from minio.error import S3Error
from s3 import client, bucket_name

import os

def download_file_from_minio(target_folder:str,file_name:str):
    # Bucket 和文件信息
    object_path = f"{file_name}/{file_name}"  # 替换为你的文件路径
    local_file_path = f"{target_folder}/{file_name}"  # 替换为本地保存路径

    try:
        # 下载文件
        client.fget_object(bucket_name, object_path, local_file_path)
        print(f"文件已下载到: {local_file_path}")
    except S3Error as e:
        print(f"下载文件时出错: {e}")



def upload_folder_to_minio(local_folder_path, minio_target_dir):
    """
    将本地文件夹中的所有文件和子目录上传到 MinIO 的指定二级目录下，并保持相同的目录结构。

    参数:
    local_folder_path (str): 本地文件夹路径。
    minio_target_dir (str): MinIO 中的目标二级目录路径（例如 "parent-folder/my-folder"）。
    """

    # 遍历本地文件夹
    for root, dirs, files in os.walk(local_folder_path):
        for file_name in files:
            # 本地文件的完整路径
            local_file_path = os.path.join(root, file_name)

            # 在 MinIO 中的对象键（保持相同的目录结构）
            relative_path = os.path.relpath(local_file_path, local_folder_path)
            object_name = os.path.join(minio_target_dir, relative_path).replace("\\", "/")

            try:
                # 上传文件
                client.fput_object(bucket_name, object_name, local_file_path)
                print(f"已上传: {local_file_path} -> {bucket_name}/{object_name}")
            except S3Error as e:
                print(f"上传文件 {local_file_path} 时出错: {e}")


if __name__ == "__main__":
    upload_folder_to_minio(local_folder_path="../pipeline/.cache/456.pdf", minio_target_dir="456.pdf/partition")