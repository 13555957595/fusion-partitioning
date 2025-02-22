import os

from magic_pdf.data.data_reader_writer import FileBasedDataWriter, FileBasedDataReader
from magic_pdf.data.dataset import PymuDocDataset
from magic_pdf.model.doc_analyze_by_custom_model import doc_analyze
from magic_pdf.config.enums import SupportedPdfParseMethod

from s3 import minio_client
from s3.minio_client import upload_folder_to_minio
from utils import directory_utils


def before_processing(file_name:str):
    try:
        local_md_dir=directory_utils.get_document_directory(file_name)
        local_images_dir=directory_utils.get_image_directory(file_name)
        # 从minio下载这个文件,并临时存在该文件夹中
        minio_client.download_file_from_minio(local_md_dir, file_name);
        return [local_md_dir, local_images_dir]
    except Exception as e:
        raise e


def on_processing(file_name:str):
    os.environ['MINERU_TOOLS_CONFIG_JSON'] = './magic-pdf.json'

    local_md_dir = directory_utils.get_document_directory(file_name)
    local_images_dir = directory_utils.get_image_directory(file_name)

    image_writer, md_writer = FileBasedDataWriter(local_images_dir), FileBasedDataWriter(local_md_dir)
    # read bytes
    reader1 = FileBasedDataReader("")
    pdf_bytes = reader1.read(f"{local_md_dir}/{file_name}")  # read the pdf content
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


def do(file_name:str) :
    local_md_dir,local_images_dir = before_processing(file_name)
    on_processing(file_name, local_md_dir, local_images_dir)
    # after_partitioning(file_name, local_md_dir, local_images_dir)


if __name__ == "__main__":
    on_processing("phonix.pdf")
    # before_partitioning("test.pdf")
