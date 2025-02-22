import base64


def base64_encode(image_path:str):
    # 读取图片文件并转换为 Base64

    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        return encoded_string


if __name__ == '__main__':

    print(base64_encode(
        "E:\devops\code\gitee\\fusion\\fusion-unstructure-processing\pipeline\.cache\phonix.pdf\images\9c35561b454d4e8725d768dfa4a6a2e06daf308a9813f65672ab3f225a0b65de.jpg"))