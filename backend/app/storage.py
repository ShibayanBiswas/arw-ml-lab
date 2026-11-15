"""StoragePort — Supabase signed upload when configured; local filesystem otherwise."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from backend.app.settings import Settings, get_settings

ROOT = Path(__file__).resolve().parents[2]
LOCAL_ROOT = ROOT / ".cache" / "uploads"


class StoragePort(ABC):
    @abstractmethod
    def create_upload_url(
        self, *, workspace_id: str, filename: str, content_type: str
    ) -> dict[str, Any]: ...

    @abstractmethod
    def put_bytes(
        self, key: str, data: bytes, *, content_type: str = "application/octet-stream"
    ) -> str: ...

    @abstractmethod
    def get_bytes(self, key: str) -> bytes: ...

    @abstractmethod
    def local_path(self, key: str) -> Path | None: ...


class LocalStorage(StoragePort):
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or LOCAL_ROOT
        self.root.mkdir(parents=True, exist_ok=True)

    def create_upload_url(
        self, *, workspace_id: str, filename: str, content_type: str
    ) -> dict[str, Any]:
        key = f"{workspace_id}/{uuid.uuid4().hex}_{filename}"
        path = self.root / key
        path.parent.mkdir(parents=True, exist_ok=True)
        # Local "signed URL" is a path token the client POSTs to /datasets/upload-local
        return {
            "key": key,
            "upload_url": f"/api/v1/datasets/upload-local/{key}",
            "method": "PUT",
            "headers": {"Content-Type": content_type},
            "backend": "local",
        }

    def put_bytes(
        self, key: str, data: bytes, *, content_type: str = "application/octet-stream"
    ) -> str:
        _ = content_type
        path = self.root / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return key

    def get_bytes(self, key: str) -> bytes:
        return (self.root / key).read_bytes()

    def local_path(self, key: str) -> Path | None:
        path = self.root / key
        return path if path.exists() else None


class SupabaseStorage(StoragePort):
    def __init__(self, settings: Settings) -> None:
        from supabase import create_client

        self.settings = settings
        self.client = create_client(settings.supabase_url, settings.supabase_service_role_key)
        self.bucket = "datasets"

    def create_upload_url(
        self, *, workspace_id: str, filename: str, content_type: str
    ) -> dict[str, Any]:
        key = f"{workspace_id}/{uuid.uuid4().hex}_{filename}"
        signed = self.client.storage.from_(self.bucket).create_signed_upload_url(key)
        return {
            "key": key,
            "upload_url": signed.get("signedUrl") or signed.get("signed_url"),
            "token": signed.get("token"),
            "method": "PUT",
            "headers": {"Content-Type": content_type},
            "backend": "supabase",
        }

    def put_bytes(
        self, key: str, data: bytes, *, content_type: str = "application/octet-stream"
    ) -> str:
        self.client.storage.from_(self.bucket).upload(
            key, data, file_options={"content-type": content_type, "upsert": "true"}
        )
        return key

    def get_bytes(self, key: str) -> bytes:
        return self.client.storage.from_(self.bucket).download(key)

    def local_path(self, key: str) -> Path | None:
        return None


def get_storage(settings: Settings | None = None) -> StoragePort:
    settings = settings or get_settings()
    if (
        settings.supabase_service_role_key
        and settings.supabase_url
        and "127.0.0.1" not in settings.supabase_url
    ):
        try:
            return SupabaseStorage(settings)
        except Exception:
            return LocalStorage()
    return LocalStorage()
