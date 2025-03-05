from minio import Minio


bucket_name = "fusion-v1"

# MinIO 本地服务服务器信息
# endpoint = "localhost:9000"  # 替换为你的 MinIO 服务器地址
# access_key = "1crWtlpyNrtxfqGIMuDb"  # 替换为你的 Access Key
# secret_key = "aB89qxRziGdKHYIwvSoQ9aZGqO3G6vv4LUv2bEe7"  # 替换为你的 Secret Key

#阿里云服务器配置
endpoint = "localhost:9000"  # 替换为你的 MinIO 服务器地址
access_key = "nJuySBK9RNRkT6POJldP"  # 替换为你的 Access Key
secret_key = "uQMShA9puTroYkdXnOwsktEmu7JTaYUwGozNjNSN"  # 替换为你的 Secret Key


secure = False  # 如果使用 HTTPS，设置为 True；否则设置为 False

# 初始化 MinIO 客户端
client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=secure)
