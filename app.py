from http.client import HTTPException

from Crypto.SelfTest.Cipher.test_CFB import file_name
from fastapi import FastAPI

from pipeline.partitioning import partitioning
from pipeline.partitioning.processing import before_processing, on_processing, after_processing

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.get("/processing/{file_name}")
async def partitioning(file_name: str):
    try:
        before_processing(file_name)#download 目标文件本地目录 从minio
        on_processing(file_name)#文件前置处理
        after_processing(file_name)#前置处理中间文件上传到minio
        partitioning.do(file_name)#分区处理 处理后的文件上传到minio
    except HTTPException as e:
        raise e

    return {"message": f"Hello {file_name}"}

@app.get("/chunking/{strategy}/{file_name}")
async def document_partitioning(strategy:str ,file_name: str):
    # try:
    #
    # except HTTPException as e:
    #     raise e

    return {"message": f"Hello {file_name}"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)