import logging
from io import BytesIO
from uuid import uuid4

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from minio import Minio
from minio.error import S3Error

logger = logging.getLogger(__name__)


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class MinioClient(metaclass=SingletonMeta):
    """Singleton wrapper around the Minio SDK client."""

    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_USE_SSL,
        )
        self.bucket = settings.MINIO_BUCKET_NAME
        self._ensure_bucket()

    def _ensure_bucket(self):
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)
            logger.info("Bucket '%s' created.", self.bucket)


@deconstructible
class MinioStorage(Storage):
    """
    Custom Django storage backend that stores files in MinIO
    using the minio Python SDK.  Works transparently with
    Wagtail images & documents.
    """

    def __init__(self):
        self._minio = None

    @property
    def minio(self) -> MinioClient:
        if self._minio is None:
            self._minio = MinioClient()
        return self._minio

    # ---- required Storage API ----

    def _save(self, name: str, content) -> str:
        data = content.read()
        content_type = getattr(content, "content_type", "application/octet-stream")
        self.minio.client.put_object(
            self.minio.bucket,
            name,
            BytesIO(data),
            len(data),
            content_type=content_type,
        )
        return name

    def _open(self, name: str, mode="rb"):
        try:
            response = self.minio.client.get_object(self.minio.bucket, name)
            data = response.read()
            response.close()
            response.release_conn()
            return ContentFile(data)
        except S3Error:
            raise FileNotFoundError(f"File '{name}' not found in MinIO.")

    def exists(self, name: str) -> bool:
        try:
            self.minio.client.stat_object(self.minio.bucket, name)
            return True
        except S3Error:
            return False

    def delete(self, name: str):
        try:
            self.minio.client.remove_object(self.minio.bucket, name)
        except S3Error:
            pass

    def url(self, name: str) -> str:
        external = getattr(settings, "MINIO_EXTERNAL_URL", None)
        if external:
            return f"{external.rstrip('/')}/{self.minio.bucket}/{name}"
        scheme = "https" if settings.MINIO_USE_SSL else "http"
        return f"{scheme}://{settings.MINIO_ENDPOINT}/{self.minio.bucket}/{name}"

    def size(self, name: str) -> int:
        stat = self.minio.client.stat_object(self.minio.bucket, name)
        return stat.size

    def listdir(self, path=""):
        dirs, files = [], []
        prefix = path.rstrip("/") + "/" if path else ""
        objects = self.minio.client.list_objects(self.minio.bucket, prefix=prefix)
        for obj in objects:
            relative = obj.object_name[len(prefix):]
            if obj.is_dir:
                dirs.append(relative.rstrip("/"))
            else:
                files.append(relative)
        return dirs, files

    def get_available_name(self, name, max_length=None):
        # Keep the original name whenever possible. Only suffix on collisions.
        if max_length and len(name) > max_length:
            name = name[:max_length]

        if not self.exists(name):
            return name

        ext = ""
        if "." in name:
            ext = name[name.rfind("."):]
            base = name[:name.rfind(".")]
        else:
            base = name

        while True:
            candidate = f"{base}_{uuid4().hex[:8]}{ext}"
            if max_length and len(candidate) > max_length:
                candidate = candidate[:max_length]
            if not self.exists(candidate):
                return candidate
