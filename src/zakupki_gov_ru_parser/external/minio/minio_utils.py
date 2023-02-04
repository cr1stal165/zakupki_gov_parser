import io
import os

import numpy as np
from loguru import logger
from minio import Minio

from ...setings import settings
from .minio import minio_client


def connect_to_minio():
    logger.info("Start minio connection")
    minio_client.minio = Minio(
        f"{settings.minio_host}:{settings.minio_port}",
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=False,
    )


def save_vector(s3_bucket: str, s3_path: str, s3_filename: str, vector):
    vector_path = os.path.join(s3_path, s3_filename)

    output = io.BytesIO()
    np.savez(output, vector=vector)
    output.seek(0)

    result = minio_client.minio.put_object(
        s3_bucket,
        vector_path,
        output,
        length=output.getbuffer().nbytes,
    )

