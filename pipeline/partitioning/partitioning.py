# 创建多个 NarrativeTextParams 实例
import json
from datetime import datetime

from pipeline.partitioning.metadata import ImageMetadata, TableMetadata
from pipeline.partitioning.element import Element, Metadata


def do(input_content_jsonfile:str , output_partition_jsonfile:str) -> None:
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
                element.metadata.image_path=item.get('img_path', 'N/A')
                element.metadata.image_base64=''
                element.metadata.image_mime_type='image/jpeg'
            if item.get('type', 'N/A') == 'table':
                element.metadata = TableMetadata(element.metadata);
                element.metadata.image_path=item.get('img_path', 'N/A')
                element.metadata.image_base64=''
                element.metadata.image_mime_type='application/octet-stream'
                element.metadata.text_as_html=item.get('table_body', 'N/A')

            element.metadata.last_modified = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            element.metadata.page_number = item.get('page_idx', 'N/A')
            element.metadata.languages = ["eng"]
            element.metadata.parent_id = parent_id
            element.metadata.file_directory = "N/A"
            element.metadata.filename = "N/A"
            element.metadata.filetype = element.type
            ################################################
            print(element.to_json())
            elements.append(element.to_json())
    with open(output_partition_jsonfile, 'w', encoding='utf-8') as json_file:
        json.dump(elements, json_file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    do('../.cache/321.pdf/_content_list.json' , '../.cache/321.pdf/_partition.json')