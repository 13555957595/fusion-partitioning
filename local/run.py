from pipeline.partitioning import partitioning
from pipeline.partitioning.processing import before_processing, on_processing, after_processing
import os
import shutil
import random
from magic_pdf.data.data_reader_writer import FileBasedDataWriter, FileBasedDataReader
from magic_pdf.data.dataset import PymuDocDataset
from magic_pdf.model.doc_analyze_by_custom_model import doc_analyze
from magic_pdf.config.enums import SupportedPdfParseMethod
from pathlib import Path
from pipeline.partitioning import partitioning
from s3 import minio_client
from s3.minio_client import upload_folder_to_minio
from utils import directory_utils
from pypinyin import pinyin, Style
import json
import os
from datetime import datetime

from pipeline.partitioning.metadata import ImageMetadata, TableMetadata
from pipeline.partitioning.element import Element, Metadata
from s3.minio_client import upload_partition_json_file_to_minio
from utils.directory_utils import get_project_root, get_document_directory




batch_dir = os.path.join(os.getcwd(), 'batch1')  # batch 目录
cache_dir = os.path.join(os.getcwd(), 'cache')  # cache 目录
os.makedirs(cache_dir, exist_ok=True)

def hanzi2pinyin(name:str):
    # 定义汉字
    text = name
    # 转换为拼音
    pinyin_result = pinyin(text, style=Style.NORMAL)
    # 将拼音列表拼接为字符串
    pinyin_str = ''.join([item[0] for item in pinyin_result])
    return pinyin_str

def getWorkingFolderName(fileName:str):
    name_without_extension = Path(fileName).stem
    folderName=hanzi2pinyin(name_without_extension)
    randomNumber = random.randint(10, 99)  # 生成2位随机数
    new_folder_name = f"{folderName}"
    return new_folder_name


def before_processing(file_name:str):
    # 准备目录
    workingFolderName = getWorkingFolderName(file_name)
    workingFolder =os.path.join(cache_dir, workingFolderName)
    os.makedirs(workingFolder, exist_ok=True)
    imagesFolder = os.path.join(workingFolder,"images")
    os.makedirs(imagesFolder, exist_ok=True)
    src_file = os.path.join(batch_dir, file_name)
    dest_file = os.path.join(workingFolder, file_name)
    shutil.copy(src_file, dest_file)
    os.remove(src_file)
    return [workingFolder, imagesFolder]

def on_processing(file_name:str, workingFoler:str, imagesFolder:str):
    os.environ['MINERU_TOOLS_CONFIG_JSON'] = './magic-pdf.json'

    local_images_dir = directory_utils.get_image_directory(file_name)

    image_writer, md_writer = FileBasedDataWriter(imagesFolder), FileBasedDataWriter(workingFoler)
    # read bytes
    reader1 = FileBasedDataReader("")
    pdf_bytes = reader1.read(f"{workingFoler}/{file_name}")  # read the pdf content
    # proc
    ## Create Dataset Instance
    ds = PymuDocDataset(pdf_bytes)
    ## inference
    if ds.classify() == SupportedPdfParseMethod.OCR:
        infer_result = ds.apply(doc_analyze, ocr=True)
        ## pipeline
        pipe_result = infer_result.pipe_ocr_mode(image_writer)
    else:
        infer_result = ds.apply(doc_analyze, ocr=False)
        ## pipeline
        pipe_result = infer_result.pipe_txt_mode(image_writer)
    ### draw model result on each page
    infer_result.draw_model(os.path.join(local_md_dir, "_model.pdf"))
    ### get model inference result
    model_inference_result = infer_result.get_infer_res()
    ### draw layout result on each page
    pipe_result.draw_layout(os.path.join(local_md_dir, "_layout.pdf"))
    ### draw spans result on each page
    pipe_result.draw_span(os.path.join(local_md_dir, "_spans.pdf"))
    ### get markdown content
    md_content = pipe_result.get_markdown(local_images_dir)
    ### dump markdown
    pipe_result.dump_md(md_writer, ".md", local_images_dir)
    ### get content list content
    content_list_content = pipe_result.get_content_list(local_images_dir)
    ### dump content list
    pipe_result.dump_content_list(md_writer, "_content_list.json", local_images_dir)
    ### get middle json
    middle_json_content = pipe_result.get_middle_json()
    ### dump middle json
    pipe_result.dump_middle_json(md_writer, "_middle.json")
def after_processing(file_name:str):
    upload_folder_to_minio(file_name)

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
                element.type = "title" # 20250302 fixing 如果element的id和parent_id相等，那么说明他是一个title
            else:
                element.type = item.get('type', 'N/A')
            element.element_id = element_id
            # 初始化 Metadata 实例并赋值

            element.metadata = Metadata()
            if item.get('type', 'N/A') == 'text':
                if item.get('text', 'N/A')=="":   # 20250302 fixing 如果当前是一个text类型的element，并且他的text中没有字符，那么忽略该element
                    continue
                else:
                    element.text = item.get('text', 'N/A')
            if item.get('type', 'N/A') == 'image':
                element.metadata = ImageMetadata(element.metadata);
                element.metadata.image_path=item.get('img_path', 'N/A')
                element.metadata.image_base64=''
                element.metadata.image_mime_type='image/jpeg'
                element.metadata.image_caption=item.get('img_caption', 'N/A')
                element.metadata.image_footnote = item.get('img_footnote', 'N/A')

            if item.get('type', 'N/A') == 'table':
                element.metadata = TableMetadata(element.metadata);
                element.metadata.image_path=item.get('img_path', 'N/A')
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

def start():
    for filename in os.listdir(batch_dir):
        if filename.endswith('.pdf'):
            workingFolder, imagesFolder = before_processing(filename)
            on_processing(filename,workingFolder,imagesFolder)
            after_processing(filename)