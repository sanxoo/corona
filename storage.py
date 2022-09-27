import minio

params = {
    "endpoint": "192.168.203.30:9000",
    "access_key": "minioadmin",
    "secret_key": "minioadmin",
    "secure": False
}

def put(bucket_name, path):
    client = minio.Minio(**params)
    if not client.bucket_exists(bucket_name): client.make_bucket(bucket_name)
    client.fput_object(bucket_name, path.name, path)

def get(bucket_name, path):
    client = minio.Minio(**params)
    client.fget_object(bucket_name, path.name, str(path))

