import uuid
from dataclasses import dataclass, field
from datetime import datetime
import json
from typing import List, Optional
# 定义 Metadata 类，为所有属性设置默认值
class Metadata:
    last_modified: Optional[str] = None
    page_number: Optional[int] = None
    languages: Optional[List[str]] = None
    parent_id: Optional[str] = None
    file_directory: Optional[str] = None
    filename: Optional[str] = None
    filetype: Optional[str] = None

    def to_json(self):
        # 返回基类的属性
        return self.__dict__


# 子类继承 Metadata
class ImageMetadata(Metadata):
    def __init__(
        self,
        image_path: Optional[str] = None,
        image_base64: Optional[str] = None,  # 新增属性
        image_mime_type: Optional[str] = None,  # 新增属性
        **kwargs  # 用于接收父类的属性
    ):
        # 调用父类的初始化方法（如果有）
        super().__init__()
        # 初始化子类的新增属性
        self.image_path = image_path
        self.image_base64 = image_base64
        self.image_mime_type = image_mime_type
        # 设置父类的属性
        for key, value in kwargs.items():
            setattr(self, key, value)

    # 新增方法
    def print_info(self):
        print(f"image_base64: {self.image_base64}, image_mime_type: {self.image_mime_type}")
        print(f"Last Modified: {self.last_modified}, Page Number: {self.page_number}")


class TableMetadata(Metadata):
    def __init__(
        self,
        image_path: Optional[str] = None,
        text_as_html:Optional[str] = None,
        image_base64: Optional[str] = None,  # 新增属性
        image_mime_type: Optional[str] = None,  # 新增属性
        **kwargs  # 用于接收父类的属性
    ):
        # 调用父类的初始化方法（如果有）
        super().__init__()
        # 初始化子类的新增属性
        self.image_path = image_path
        self.text_as_html = text_as_html
        self.image_base64 = image_base64
        self.image_mime_type = image_mime_type
        # 设置父类的属性
        for key, value in kwargs.items():
            setattr(self, key, value)

    # 新增方法
    def print_info(self):
        print(f"image_base64: {self.image_base64}, image_mime_type: {self.image_mime_type}, text_as_html: {self.text_as_html}")
        print(f"Last Modified: {self.last_modified}, Page Number: {self.page_number}")

