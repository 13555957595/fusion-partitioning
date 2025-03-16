import shutil
import oss2
import random
from magic_pdf.data.data_reader_writer import FileBasedDataWriter, FileBasedDataReader
from magic_pdf.data.dataset import PymuDocDataset
from magic_pdf.model.doc_analyze_by_custom_model import doc_analyze
from magic_pdf.config.enums import SupportedPdfParseMethod
from pathlib import Path
from pypinyin import pinyin, Style
import json
import os
from datetime import datetime
import sys
sys.path.append('../')
from pipeline.partitioning.metadata import ImageMetadata, TableMetadata
from pipeline.partitioning.element import Element, Metadata
from pipeline.chunking.composite_element import CompositeElement, generate_chunk_id


cache_dir = os.path.join(os.getcwd(), 'cache')  # cache 目录
os.makedirs(cache_dir, exist_ok=True)

# 阿里云 OSS 的 S3 协议端点
endpoint = 'oss-cn-beijing.aliyuncs.com'  # 替换为你的 OSS 区域端点
# 阿里云 OSS 的 Access Key ID 和 Access Key Secret
access_key_id = 'LTAI5tESDcw5pvZCeifgR6iB'
access_key_secret = 'SL1PGlqpJcOaNrTF9jNHDM1VBF2ZYi'
bucket_name="tuchong-ai"
auth = oss2.Auth(access_key_id, access_key_secret)
bucket = oss2.Bucket(auth, endpoint, bucket_name)


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
    # os.remove(src_file)






    return [workingFolder, imagesFolder,workingFolderName]

def on_processing(file_name:str, workingFoler:str, imagesFolder:str):
    print(file_name)
    print(workingFoler)
    print(imagesFolder)


    os.environ['MINERU_TOOLS_CONFIG_JSON'] = './magic-pdf.json'
    local_images_dir = imagesFolder
    local_md_dir=workingFoler
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
    ## draw model result on each page
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
    # middle_json_content = pipe_result.get_middle_json()
    # pipe_result.dump_middle_json(md_writer, "_middle.json")

def after_processing(file_name:str):

def content2PartitionJson(workingFolder:str, file_name:str, pinyinName:str) -> None:
    local_md_folder = workingFolder
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
                # 上传图片
                url = uploadImageOSS(item.get('img_path', 'N/A'), pinyinName)
                element.metadata.image_path = url
                element.metadata.image_base64=''
                element.metadata.image_mime_type='image/jpeg'
                element.metadata.image_caption=item.get('img_caption', 'N/A')
                element.metadata.image_footnote = item.get('img_footnote', 'N/A')

            if item.get('type', 'N/A') == 'table':
                element.metadata = TableMetadata(element.metadata);
                url = uploadImageOSS(item.get('img_path', 'N/A'), pinyinName)
                element.metadata.image_path = url
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


def partition2Chunk(workingFolder:str,file_name:str,pinyinName:str)-> None:
    target_file_path = os.path.join(workingFolder, "_partition.json")

    chunks = []

    with open(target_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        index = 0
        previous_chunk = None
        previous_element_type = None
        for item in data:
            current_element_type = item['type']
            file_name=item['metadata']['filename']
            page_number=item['metadata']['page_number']
            if index == 0 or (current_element_type=='title' and previous_element_type!='title'):
                previous_chunk = CompositeElement()
                previous_chunk.orig_file=item["metadata"]["file_directory"]
                previous_chunk.file_name = file_name
                previous_chunk.page_number = page_number + 1
                previous_chunk.chunk_id=generate_chunk_id()
                if item["text"] is not None and item["text"] != "":
                    previous_chunk.title=item["text"]
                    previous_chunk.text.append(item["text"])
                previous_chunk.orig_elements.append(item)
                chunks.append(previous_chunk.to_json())
            else:
                if item["text"] is not None and item["text"] != "":
                    previous_chunk.text.append(item["text"])
                previous_chunk.orig_elements.append(item)
            index = index + 1
            previous_element_type = current_element_type

        local_md_folder =workingFolder
        output_partition_jsonfile = os.path.join(local_md_folder, "_chunking.json")
        with open(output_partition_jsonfile, 'w', encoding='utf-8') as json_file:
            json.dump(chunks, json_file, ensure_ascii=False, indent=4)
        print(f"文件 {output_partition_jsonfile} 已经生成")
        chunk2txt(workingFolder,file_name)

        _txt_file = os.path.join(local_md_folder, file_name + ".txt")
        uploadImageOSS(_txt_file,pinyinName)


txt_file_name="_text.txt"
def chunk2txt(workingFolder:str,file_name:str):
    #将 chunk 转化成 txt , 便于快速测试使用
    local_md_folder = workingFolder
    _chunking_json_file = os.path.join(local_md_folder, "_chunking.json")
    # 读取 JSON 文件
    with open(_chunking_json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
        # 初始化结果列表
        result = []

        # 遍历每个对象
        for item in data:
            # 提取 text 数组并过滤掉 None 值
            texts = [text for text in item['text'] if text is not None]
            # 拼接 text 数组中的内容，使用句号连接
            concatenated_text = '。'.join(texts)
            concatenated_text = concatenated_text + " \n出自 文件:" + item['file_name'] + " 页码:" + str(
                item['page_number'])
            # 将拼接后的文本添加到结果列表中
            result.append(concatenated_text)
        # 使用 @@ 连接每段文字
        final_text = '\n@@\n'.join(result)

        # 将结果写入 txt 文件
        _txt_file = os.path.join(local_md_folder, file_name+".txt")
        with open(_txt_file, 'w', encoding='utf-8') as output_file:
            output_file.write(final_text)
        print(f"文件 {_txt_file} 已经生成")

def uploadImageOSS(image_path:str, prefix:str):
    if image_path !="" and image_path !="N/A" :
        file_name_with_ext = os.path.basename(image_path)
        print(file_name_with_ext)  # 输出: image.jpg
        oss_file = prefix + '/' + file_name_with_ext
        # 上传文件
        bucket.put_object_from_file(oss_file, image_path)
        url = 'https://' + bucket_name + '.' + endpoint + '/' + oss_file
        print('文件上传成功: ' + url)
        return url




















def startBatch(batch_dir:str):
    for filename in os.listdir(batch_dir):
        if filename.endswith('.pdf'):
            startOne(filename)


def startOne(filename:str):
    workingFolder, imagesFolder, pinyinName = before_processing(filename)
    on_processing(filename,workingFolder,imagesFolder)
    after_processing(filename)
    content2PartitionJson(workingFolder,filename,pinyinName)
    partition2Chunk(workingFolder,filename,pinyinName)







batch="batch1"
batch_dir = os.path.join(os.getcwd(), batch)  # batch 目录
if __name__ == "__main__":
    # startBatch(batch_dir)
    startOne("视觉神经生理学.pdf")