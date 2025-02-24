import requests

from pipeline.partitioning import partitioning
from pipeline.partitioning.processing import before_processing, on_processing, after_processing


def async_processing(file_name:str , call_back_api: str, access_token: str) :
    before_processing(file_name)
    on_processing(file_name)
    after_processing(file_name)
    partitioning.do(file_name)
    callback(file_name, call_back_api,access_token)

def callback(file_name:str, call_back_api: str, access_token: str) :
    # 目标 URL
    url = call_back_api
    # 请求体（JSON 数据）
    payload = {
        "file_name": file_name,
        "status":"1",
        "access_token": access_token,
        "message":"processing finished!"
    }
    # 请求头
    headers = {
        "Content-Type": "application/json"
    }
    # 发送 POST 请求
    response = requests.post(url, json=payload, headers=headers)
    # 检查响应状态码
    if response.status_code == 200:
        # 解析 JSON 响应
        data = response.__str__()
        print("Get Response Data From Call Back Service:", data)
    else:
        print(f"Error: {response.status_code}")
