from http.client import HTTPException

from Crypto.SelfTest.Cipher.test_CFB import file_name
from fastapi import FastAPI

from pipeline.partitioning.processing import before_processing, on_processing, after_processing

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.get("/processing/{file_name}")
async def document_partitioning(file_name: str):
    try:
        before_processing(file_name)#download 目标文件本地目录
        on_processing(file_name)#文件分区
        after_processing(file_name)#分区后的中间文件上传
    except HTTPException as e:
        raise e

    return {"message": f"Hello {file_name}"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)