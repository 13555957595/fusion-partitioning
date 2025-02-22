from minio.error import S3Error
from s3 import client, bucket_name

import os

from utils.directory_utils import get_document_directory, check_file_matching


def download_file_from_minio(target_folder:str,file_name:str):
    # Bucket 和文件信息
    object_path = f"{file_name}/{file_name}"  # 替换为你的文件路径
    local_file_path = f"{target_folder}/{file_name}"  # 替换为本地保存路径

    try:
        # 下载文件
        client.fget_object(bucket_name, object_path, local_file_path)
        print(f"文件已下载到: {local_file_path}")
    except S3Error as e:
        raise e
        print(f"下载文件时出错: {e}")



def upload_folder_to_minio(target_file_name:str):
    """
    将本地文件夹中的所有文件和子目录上传到 MinIO 的指定二级目录下，并保持相同的目录结构。

    参数:
    local_folder_path (str): 本地文件夹路径。
    minio_target_dir (str): MinIO 中的目标二级目录路径（例如 "parent-folder/my-folder"）。
    """
    local_folder_path = get_document_directory(target_file_name)
    print(f"folder={local_folder_path}")
    # 遍历本地文件夹
    for root, dirs, files in os.walk(local_folder_path):
        for file_name in files:
            # 本地文件的完整路径
            local_file_path = os.path.join(root, file_name)
            print(f"absolut_file_path={local_file_path}")
            if check_file_matching(target_file_name, local_file_path):#判断该路径是否是原始文件，如果是原始文件那么不上传
                continue
            relative_file_path = local_file_path.replace(local_folder_path,"")
            relative_file_path = relative_file_path.replace("\\", "/")
            object_name = f"{target_file_name}/partition{relative_file_path}"
            print(f"object_name={object_name}")
            try:
                # 上传文件
                client.fput_object(bucket_name, object_name, local_file_path)
                print(f"已上传: {local_file_path} -> {bucket_name}/{object_name}")
            except S3Error as e:
                print(f"上传文件 {local_file_path} 时出错: {e}")

def upload_partition_json_file_to_minio(file_name:str):
    local_md_folder = get_document_directory(file_name)
    _partition_json_file = os.path.join(local_md_folder, "_partition.json")
    if not os.path.exists(_partition_json_file):
        print(f"文件 {_partition_json_file} 不存在")
        return
    object_name = f"{file_name}/partition/_partition.json"
    print(f"object_name={object_name}")
    try:
        # 上传文件
        client.fput_object(bucket_name, object_name, _partition_json_file)
        print(f"已上传: {_partition_json_file} -> {bucket_name}/{object_name}")
    except S3Error as e:
        print(f"上传文件 {_partition_json_file} 时出错: {e}")



if __name__ == "__main__":
    upload_folder_to_minio("phonix.pdf")