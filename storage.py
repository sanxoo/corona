import minio

def put(bucket_name, path):
    info = {
        "endpoint": "192.168.203.30:9000",
        "access_key": "minioadmin",
        "secret_key": "minioadmin",
        "secure": False
    }
    client = minio.Minio(**info)
    if not client.bucket_exists(bucket_name): client.make_bucket(bucket_name)
    client.fput_object(bucket_name, path.name, path)

