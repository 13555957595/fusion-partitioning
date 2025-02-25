import json
import os
from datetime import datetime

from pipeline.partitioning.metadata import ImageMetadata, TableMetadata
from pipeline.partitioning.element import Element, Metadata
from s3.minio_client import upload_partition_json_file_to_minio
from utils.directory_utils import get_project_root, get_document_directory


def do(file_name:str) -> None:
    local_md_folder = get_document_directory(file_name)
    input_content_jsonfile = os.path.join(local_md_folder, "_content_list.json")
    if not os.path.exists(input_content_jsonfile):
        print(f"文件 {input_content_jsonfile} 不存在")
        return
    output_partition_jsonfile = os.path.join(local_md_folder, "_partition.json")
    with open(output_partition_jsonfile, "w") as file:
        pass  # 不需要写入内容
    elements = []
    with open(input_content_jsonfile, 'r', encoding='utf-8') as file:
        data = json.load(file)
        parent_id = ''
        for item in data:
            element = Element();
            text_level = item.get('text_level', 'N/A')
            element_id = element.generate_element_id();
            if text_level == 1:
                parent_id = element_id
            element.type = item.get('type', 'N/A')
            element.element_id = element_id
            # 初始化 Metadata 实例并赋值

            element.metadata = Metadata()
            if item.get('type', 'N/A') == 'text':
                element.text = item.get('text', 'N/A')
            if item.get('type', 'N/A') == 'image':
                element.metadata = ImageMetadata(element.metadata);
                index = item.get('img_path', 'N/A').find("images")
                image_path = item.get('img_path', 'N/A')[index:]
                element.metadata.image_path=image_path
                element.metadata.image_base64=''
                element.metadata.image_mime_type='image/jpeg'
                element.metadata.image_caption=item.get('img_caption', 'N/A')
                element.metadata.image_footnote = item.get('img_footnote', 'N/A')

            if item.get('type', 'N/A') == 'table':
                element.metadata = TableMetadata(element.metadata);
                index = item.get('img_path', 'N/A').find("images")
                image_path = item.get('img_path', 'N/A')[index:]
                element.metadata.image_path=image_path
                element.metadata.image_base64=''
                element.metadata.image_mime_type='application/octet-stream'
                element.metadata.text_as_html=item.get('table_body', 'N/A')
                element.metadata.table_caption = item.get('table_caption', 'N/A')
                element.metadata.table_footnote = item.get('table_footnote', 'N/A')

            element.metadata.last_modified = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            element.metadata.page_number = item.get('page_idx', 'N/A')
            element.metadata.languages = ["eng"]
            element.metadata.parent_id = parent_id
            element.metadata.file_directory = f"{file_name}/{file_name}"
            element.metadata.filename = file_name
            element.metadata.filetype = file_extension = os.path.splitext(file_name)[1]
            ################################################
            elements.append(element.to_json())
    with open(output_partition_jsonfile, 'w', encoding='utf-8') as json_file:
        json.dump(elements, json_file, ensure_ascii=False, indent=4)

    upload_partition_json_file_to_minio(file_name)

if __name__ == "__main__":
    do('321.pdf' )