import time

from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel

from pipeline.partitioning.async_processing import async_processing

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

class PartitioningRequest(BaseModel):
    file_name: str  # 文件名，类型为字符串
    call_back_api: str  # 回调URL，类型为字符串
    access_token: str #访问凭证

def process_file_async(file_name: str, call_back_api: str):
    """
    这是一个模拟的耗时逻辑函数。
    """
    print(f"开始处理文件: {file_name}")
    time.sleep(10)  # 模拟耗时操作
    print(f"文件处理完成: {file_name}")
    print(f"回调 URL: {call_back_api}")

@app.post("/partitioning")
async def handle_post(request: PartitioningRequest, background_tasks: BackgroundTasks):
    # 解析参数
    file_name = request.file_name
    call_back_api = request.call_back_api
    access_token = request.access_token
    # 打印参数
    print(f"Filename: {file_name}")
    print(f"Callback URL: {call_back_api}")
    # 收到处理请求后，直接返回给客户端，开启异步方式对文件进行分区处理
    background_tasks.add_task(async_processing, file_name, call_back_api, access_token)
    # 返回响应
    return {"status": "success", "filename": file_name, "callbackURL": call_back_api}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000,log_level="debug")