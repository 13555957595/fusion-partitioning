import uuid
from dataclasses import dataclass, field
from datetime import datetime
import json
from typing import List, Optional

from pipeline.partitioning.metadata import Metadata


# 定义 Element 类，为所有属性设置默认值
@dataclass
class Element:
    type: Optional[str] = None
    element_id: Optional[str] = None
    text: Optional[str] = None
    metadata: Optional[Metadata] = None

    # 生成 JSON 数据的方法
    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4,ensure_ascii=False)

    def generate_element_id(self):
        unique_id = uuid.uuid4()
        formatted_id = unique_id.hex[:24] + "d1"  # 取前 24 位并加上 "d1"
        return formatted_id

# # 创建一个空实例
# element = Element()
#
# # 逐个赋值
# element.type = "NarrativeText"
# element.element_id = "5ef1d1117721f0472c1ad825991d7d37"
# element.text = "The Unstructured documentation covers the following services:"
#
# # 初始化 Metadata 实例并赋值
# element.metadata = Metadata()
#
# element.metadata = TableMetadata(element.metadata)
# element.metadata.image_mime_type = "text/html"
# element.metadata.last_modified = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
# element.metadata.page_number = 1
# element.metadata.languages = ["eng"]
# element.metadata.parent_id = "56f24319ae258b735cac3ec2a271b1d9"
# element.metadata.file_directory = "/content"
# element.metadata.filename = "Unstructured documentation.html"
# element.metadata.filetype = "text/html"
# element.metadata.text_as_html="sdlfkjslkdjf"
# # 生成 JSON 数据
# json_data = element.to_json()
# print(json_data)