from minio import Minio


class MinioClient:
    minio: Minio | None
    

minio_client = MinioClient()