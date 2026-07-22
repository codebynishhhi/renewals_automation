import hashlib
import io 
import logging
from minio import Minio
from minio.error import S3Error
from src.common.settings import settings

logger = logging.getLogger(__name__)

# singleton client - reuse everywhere
client : Minio | None = None

def get_minio_client() -> Minio:
    """ Establish minio client connection. Returns the shared minio client. Creates it once """
    global client 
    if client is None:
        client = Minio(
            endpoint = settings.minio_endpoint,
            access_key = settings.minio_access_key,
            secret_key = settings.minio_secret_key,
            secure = settings.minio_secure
        )
        ensure_bucket_exists(client)
    return client

def ensure_bucket_exists(client : Minio) -> None:
    """ Create the bucket if it dosen't exist """
    if not client.bucket_exists(settings.minio_bucket):
        client.make_bucket(settings.minio_bucket)
        logger.info("Created MinIO bucket : %s", settings.minio_bucket)

def upload_file(file_bytes : bytes, storage_key : str, content_type :str  = "application/octet-stream") -> str:
    """ 
    Upload bytes to minio. Return storage key.
    This storage key is save in postgres and retrieved later
    """
    client = get_minio_client()
    client.put_object(
        bucket_name=settings.minio_bucket,
        object_name=storage_key,
        data = io.BytesIO(file_bytes),
        length=len(file_bytes),
        content_type=content_type
    )
    logger.info("Upoaded to Minio | key=%s | size=%d bytes", storage_key, len(file_bytes))
    return storage_key

def download_file(storage_key : str) -> bytes:
    """ Retrieve / download a file from minio using storage key """
    client = get_minio_client()
    response = client.get_object(settings.minio_bucket, storage_key)
    try:
        return response.read()
    finally:
        response.close()
        response.release_conn()

def compute_hash(file_bytes: bytes) -> str:
    """ SHA-256 hash of file contents - used for deduplication """
    return hashlib.sha256(file_bytes).hexdigest()
