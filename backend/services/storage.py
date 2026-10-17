"""
Spatial File & Blob Storage Service (S3 / Local Blob Container)

Manages:
- Satellite GeoTIFF radar bands (Sentinel-1 / Sentinel-3)
- SRTM 30m Digital Elevation Models (DEM)
- Neural network weights and model checkpoints
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class StoredBlobMetadata(BaseModel):
    blob_id: str
    filename: str
    content_type: str
    size_bytes: int
    storage_tier: str = "LOCAL_BLOB"  # 'LOCAL_BLOB' | 'AWS_S3' | 'AZURE_BLOB'
    uri: str
    uploaded_at: str


class StorageService:
    """
    Blob storage client supporting local filesystem buffer and cloud S3 routing.
    """

    def __init__(self, base_storage_dir: Optional[str] = None):
        if base_storage_dir:
            self.base_dir = Path(base_storage_dir)
        else:
            self.base_dir = Path(__file__).parent.parent / "storage_vault"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_index: Dict[str, StoredBlobMetadata] = {}

    def store_file(self, blob_id: str, filename: str, data: bytes, content_type: str = "application/octet-stream") -> StoredBlobMetadata:
        """Stores a binary raster / model checkpoint."""
        file_path = self.base_dir / filename
        with open(file_path, "wb") as f:
            f.write(data)

        meta = StoredBlobMetadata(
            blob_id=blob_id,
            filename=filename,
            content_type=content_type,
            size_bytes=len(data),
            storage_tier="LOCAL_BLOB",
            uri=f"file://{file_path.absolute()}",
            uploaded_at=str(Path(file_path).stat().st_mtime),
        )
        self.metadata_index[blob_id] = meta
        return meta

    def get_file_bytes(self, blob_id: str) -> Optional[bytes]:
        """Retrieves raw bytes for a stored blob."""
        meta = self.metadata_index.get(blob_id)
        if not meta:
            return None
        file_path = self.base_dir / meta.filename
        if file_path.exists():
            with open(file_path, "rb") as f:
                return f.read()
        return None

    def list_blobs(self) -> List[StoredBlobMetadata]:
        return list(self.metadata_index.values())


storage_service = StorageService()
