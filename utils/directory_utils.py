import os


def get_project_root():
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    project_root = os.path.dirname(script_dir)
    return project_root

def get_document_directory(file_name:str):
    project_root = get_project_root()
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    project_root = os.path.dirname(script_dir)
    local_md_dir = os.path.join(project_root, "pipeline", ".cache", file_name)
    os.makedirs(local_md_dir, exist_ok=True)
    return local_md_dir

def get_image_directory(file_name:str):
    project_root = get_project_root()
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    project_root = os.path.dirname(script_dir)
    local_images_dir = os.path.join(project_root, "pipeline", ".cache", file_name, "images")
    os.makedirs(local_images_dir, exist_ok=True)
    return local_images_dir

def check_file_matching(file_name:str,absolute_file_path:str):
    # 获取文件的名称和路径
    actual_file_name = os.path.basename(absolute_file_path)
    # 比较它们是否匹配
    if actual_file_name == file_name:
        return True
    else:
        return False

if __name__ == '__main__':
    result = check_file_matching("_spans1.pdf","E:\devops\code\gitee\fusion\fusion-unstructure-processing\pipeline\.cache\phonix.pdf\_spans.pdf")
    print(result)