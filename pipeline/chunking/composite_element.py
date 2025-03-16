import uuid
from typing import Optional, List

from dataclasses import dataclass, field


def generate_chunk_id():
    unique_id = uuid.uuid4()
    formatted_id = unique_id.hex[:24] + "d1"  # 取前 24 位并加上 "d1"
    return formatted_id


@dataclass
class CompositeElement:
    type: Optional[str] = "CompositeElement"
    chunk_id: Optional[str] = None
    title: Optional[str] = None
    file_name: Optional[str] = None
    page_number: Optional[str] = None
    text: Optional[List[str]] = field(default_factory=list)
    orig_file: Optional[str] = None
    orig_elements: List[str] = field(default_factory=list)


    def to_json(self) -> dict:
        data = {
            "type": "CompositeElement",  # 添加类型字段
            "chunk_id": self.chunk_id,
            "title": self.title,
            "file_name": self.file_name,
            "page_number": self.page_number,
            "text": self.text,
            "orig_file": self.orig_file,
            "orig_elements": self.orig_elements
        }

        return data

