"""
NEO Storage Service

Replaces Supabase Storage with MinIO-based object storage.
Provides file upload, download, and management capabilities.
"""

import os
import uuid
import logging
import mimetypes
from typing import Dict, Any, Optional, List, BinaryIO
from datetime import datetime, timezone
import aiofiles
from minio import Minio
from minio.error import S3Error
import asyncio
from concurrent.futures import ThreadPoolExecutor

from services.database import db_service
from utils.config import config

logger = logging.getLogger(__name__)

class StorageService:
    """
    NEO Storage Service - MinIO-based object storage.
    Replaces Supabase Storage functionality.
    """
    
    def __init__(self):
        self.minio_client = None
        self.endpoint = config.get('MINIO_ENDPOINT', 'localhost:9000')
        self.access_key = config.get('MINIO_ACCESS_KEY', 'neo_minio')
        self.secret_key = config.get('MINIO_SECRET_KEY', 'neo_minio_password')
        self.secure = config.get('MINIO_SECURE', False)
        self.default_bucket = 'neo-storage'
        self.executor = ThreadPoolExecutor(max_workers=4)
        self._initialized = False
    
    async def initialize(self):
        """Initialize MinIO client and create default bucket."""
        if self._initialized:
            return
        
        try:
            # Initialize MinIO client
            self.minio_client = Minio(
                endpoint=self.endpoint,
                access_key=self.access_key,
                secret_key=self.secret_key,
                secure=self.secure
            )
            
            # Create default bucket if it doesn't exist
            await self._create_bucket_if_not_exists(self.default_bucket)
            
            self._initialized = True
            logger.info("Storage service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize storage service: {e}")
            raise
    
    async def _create_bucket_if_not_exists(self, bucket_name: str):
        """Create bucket if it doesn't exist."""
        def _check_and_create():
            if not self.minio_client.bucket_exists(bucket_name):
                self.minio_client.make_bucket(bucket_name)
                logger.info(f"Created bucket: {bucket_name}")
            else:
                logger.info(f"Bucket already exists: {bucket_name}")
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(self.executor, _check_and_create)
    
    def _generate_file_path(self, account_id: str, filename: str, bucket: str = None) -> str:
        """Generate unique file path."""
        bucket = bucket or self.default_bucket
        file_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime('%Y/%m/%d')
        return f"{account_id}/{timestamp}/{file_id}_{filename}"
    
    async def upload_file(
        self,
        account_id: str,
        file_data: bytes,
        filename: str,
        content_type: str = None,
        bucket: str = None,
        is_public: bool = False,
        metadata: Dict = None
    ) -> Dict[str, Any]:
        """Upload file to storage."""
        if not self._initialized:
            await self.initialize()
        
        try:
            bucket = bucket or self.default_bucket
            
            # Generate unique file path
            storage_path = self._generate_file_path(account_id, filename, bucket)
            
            # Detect content type if not provided
            if not content_type:
                content_type, _ = mimetypes.guess_type(filename)
                content_type = content_type or 'application/octet-stream'
            
            # Upload file to MinIO
            def _upload():
                from io import BytesIO
                file_stream = BytesIO(file_data)
                self.minio_client.put_object(
                    bucket_name=bucket,
                    object_name=storage_path,
                    data=file_stream,
                    length=len(file_data),
                    content_type=content_type
                )
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(self.executor, _upload)
            
            # Store file metadata in database
            file_id = await db_service.insert('files', {
                'account_id': account_id,
                'filename': os.path.basename(storage_path),
                'original_filename': filename,
                'content_type': content_type,
                'file_size': len(file_data),
                'storage_path': storage_path,
                'bucket': bucket,
                'is_public': is_public,
                'metadata': metadata or {}
            })
            
            # Generate URL
            url = await self.get_file_url(file_id, bucket)
            
            logger.info(f"File uploaded: {filename} -> {storage_path}")
            
            return {
                'id': file_id,
                'filename': filename,
                'storage_path': storage_path,
                'content_type': content_type,
                'file_size': len(file_data),
                'url': url,
                'bucket': bucket,
                'is_public': is_public
            }
            
        except Exception as e:
            logger.error(f"File upload failed: {e}")
            raise
    
    async def upload_file_from_path(
        self,
        account_id: str,
        file_path: str,
        filename: str = None,
        content_type: str = None,
        bucket: str = None,
        is_public: bool = False,
        metadata: Dict = None
    ) -> Dict[str, Any]:
        """Upload file from local path."""
        filename = filename or os.path.basename(file_path)
        
        async with aiofiles.open(file_path, 'rb') as f:
            file_data = await f.read()
        
        return await self.upload_file(
            account_id=account_id,
            file_data=file_data,
            filename=filename,
            content_type=content_type,
            bucket=bucket,
            is_public=is_public,
            metadata=metadata
        )
    
    async def upload_base64_image(
        self,
        account_id: str,
        base64_data: str,
        filename: str = None,
        bucket: str = None,
        is_public: bool = True
    ) -> str:
        """Upload base64 encoded image and return URL."""
        import base64
        
        try:
            # Remove data URL prefix if present
            if base64_data.startswith('data:'):
                header, base64_data = base64_data.split(',', 1)
                # Extract content type from header
                content_type = header.split(';')[0].split(':')[1]
            else:
                content_type = 'image/png'
            
            # Decode base64 data
            file_data = base64.b64decode(base64_data)
            
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                ext = content_type.split('/')[-1]
                filename = f"image_{timestamp}.{ext}"
            
            # Upload file
            result = await self.upload_file(
                account_id=account_id,
                file_data=file_data,
                filename=filename,
                content_type=content_type,
                bucket=bucket or 'images',
                is_public=is_public
            )
            
            return result['url']
            
        except Exception as e:
            logger.error(f"Base64 image upload failed: {e}")
            raise
    
    async def download_file(self, file_id: str) -> Dict[str, Any]:
        """Download file by ID."""
        if not self._initialized:
            await self.initialize()
        
        try:
            # Get file metadata from database
            file_info = await db_service.select('files', where={'id': file_id})
            if not file_info:
                raise FileNotFoundError(f"File {file_id} not found")
            
            file_info = file_info[0]
            
            # Download file from MinIO
            def _download():
                response = self.minio_client.get_object(
                    bucket_name=file_info['bucket'],
                    object_name=file_info['storage_path']
                )
                return response.read()
            
            loop = asyncio.get_event_loop()
            file_data = await loop.run_in_executor(self.executor, _download)
            
            return {
                'data': file_data,
                'filename': file_info['original_filename'],
                'content_type': file_info['content_type'],
                'file_size': file_info['file_size']
            }
            
        except Exception as e:
            logger.error(f"File download failed: {e}")
            raise
    
    async def delete_file(self, file_id: str):
        """Delete file by ID."""
        if not self._initialized:
            await self.initialize()
        
        try:
            # Get file metadata from database
            file_info = await db_service.select('files', where={'id': file_id})
            if not file_info:
                raise FileNotFoundError(f"File {file_id} not found")
            
            file_info = file_info[0]
            
            # Delete file from MinIO
            def _delete():
                self.minio_client.remove_object(
                    bucket_name=file_info['bucket'],
                    object_name=file_info['storage_path']
                )
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(self.executor, _delete)
            
            # Delete file metadata from database
            await db_service.delete('files', {'id': file_id})
            
            logger.info(f"File deleted: {file_id}")
            
        except Exception as e:
            logger.error(f"File deletion failed: {e}")
            raise
    
    async def get_file_url(self, file_id: str, bucket: str = None) -> str:
        """Get file URL."""
        if not self._initialized:
            await self.initialize()
        
        try:
            # Get file metadata from database
            file_info = await db_service.select('files', where={'id': file_id})
            if not file_info:
                raise FileNotFoundError(f"File {file_id} not found")
            
            file_info = file_info[0]
            
            # Generate presigned URL for private files or direct URL for public files
            if file_info['is_public']:
                # For public files, return direct URL
                return f"http://{self.endpoint}/{file_info['bucket']}/{file_info['storage_path']}"
            else:
                # For private files, generate presigned URL
                def _get_presigned_url():
                    from datetime import timedelta
                    return self.minio_client.presigned_get_object(
                        bucket_name=file_info['bucket'],
                        object_name=file_info['storage_path'],
                        expires=timedelta(hours=1)
                    )
                
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(self.executor, _get_presigned_url)
            
        except Exception as e:
            logger.error(f"Get file URL failed: {e}")
            raise
    
    async def list_files(
        self,
        account_id: str,
        bucket: str = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List files for account."""
        try:
            where_clause = {'account_id': account_id}
            if bucket:
                where_clause['bucket'] = bucket
            
            files = await db_service.execute_query("""
                SELECT * FROM files
                WHERE account_id = $1
                AND ($2::text IS NULL OR bucket = $2)
                ORDER BY created_at DESC
                LIMIT $3 OFFSET $4
            """, account_id, bucket, limit, offset, fetch="all")
            
            # Add URLs to file info
            for file_info in files:
                file_info['url'] = await self.get_file_url(file_info['id'])
            
            return files
            
        except Exception as e:
            logger.error(f"List files failed: {e}")
            raise
    
    async def get_file_info(self, file_id: str) -> Dict[str, Any]:
        """Get file information."""
        try:
            file_info = await db_service.select('files', where={'id': file_id})
            if not file_info:
                raise FileNotFoundError(f"File {file_id} not found")
            
            file_info = file_info[0]
            file_info['url'] = await self.get_file_url(file_id)
            
            return file_info
            
        except Exception as e:
            logger.error(f"Get file info failed: {e}")
            raise

# Global storage service instance
storage_service = StorageService()