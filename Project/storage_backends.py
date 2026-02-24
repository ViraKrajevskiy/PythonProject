"""
Хранилище вложений задач в Google Drive.
Все загружаемые файлы (фото и др.) сохраняются в указанную папку на Google Drive,
а не на диск сервера.
"""
import io
import re
from django.conf import settings
from django.core.files.base import File
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible


# Проверка: похоже на ID файла Google Drive (без слэшей)
DRIVE_ID_RE = re.compile(r'^[a-zA-Z0-9_-]{20,}$')


@deconstructible
class GoogleDriveStorage(Storage):
    """Storage для FileField: сохраняет файлы в папку Google Drive по service account."""

    def __init__(self, json_key_file=None, folder_id=None, fallback_storage=None):
        self._json_key_file = json_key_file or getattr(
            settings, 'GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE', None
        )
        self._folder_id = folder_id or getattr(
            settings, 'GOOGLE_DRIVE_STORAGE_FOLDER_ID', None
        )
        self._fallback = fallback_storage

    def _get_drive_service(self):
        if not self._json_key_file or not self._folder_id:
            return None
        try:
            from google.oauth2.service_account import Credentials
            from googleapiclient.discovery import build

            # drive (не drive.file!) — нужен доступ к папке, расшаренной с service account
            creds = Credentials.from_service_account_file(
                str(self._json_key_file),
                scopes=['https://www.googleapis.com/auth/drive']
            )
            return build('drive', 'v3', credentials=creds)
        except Exception as e:
            if getattr(settings, 'DEBUG', False):
                import logging
                logging.getLogger(__name__).warning('Google Drive storage init failed: %s', e)
            return None

    def _open(self, name, mode='rb'):
        if mode != 'rb':
            raise ValueError('GoogleDriveStorage поддерживает только чтение (rb).')
        if not name or '/' in name or not DRIVE_ID_RE.match(name.strip()):
            return self._fallback_open(name, mode)
        service = self._get_drive_service()
        if not service:
            return self._fallback_open(name, mode)
        try:
            request = service.files().get_media(fileId=name, supportsAllDrives=True)
            content_bytes = request.execute()
            return File(io.BytesIO(content_bytes), name=name)
        except Exception:
            return self._fallback_open(name, mode)

    def _fallback_open(self, name, mode):
        if self._fallback is not None:
            return self._fallback._open(name, mode)
        from django.core.files.storage import default_storage
        return default_storage._open(name, mode)

    def _save(self, name, content):
        service = self._get_drive_service()
        if not service:
            return self._fallback_save(name, content)
        # Имя файла: берём из content или из name (после последнего /)
        file_name = getattr(content, 'name', None) or name.split('/')[-1] or 'file'
        if not file_name or file_name == 'file':
            import uuid
            file_name = f'upload_{uuid.uuid4().hex[:8]}'
        try:
            from googleapiclient.http import MediaIoBaseUpload
            content.seek(0)
            if hasattr(content, 'read'):
                body = io.BytesIO(content.read())
            else:
                body = io.BytesIO(content)
            body.seek(0)
            media = MediaIoBaseUpload(body, mimetype='application/octet-stream', resumable=False)
            meta = {'name': file_name, 'parents': [self._folder_id]}
            created = service.files().create(
                body=meta,
                media_body=media,
                fields='id',
                supportsAllDrives=True
            ).execute()
            return created.get('id') or name
        except Exception as e:
            if getattr(settings, 'DEBUG', False):
                import logging
                logging.getLogger(__name__).warning('Google Drive upload failed: %s', e)
            return self._fallback_save(name, content)

    def _fallback_save(self, name, content):
        if self._fallback is not None:
            return self._fallback._save(name, content)
        from django.core.files.storage import default_storage
        return default_storage._save(name, content)

    def delete(self, name):
        if not name or '/' in name or not DRIVE_ID_RE.match(name.strip()):
            return self._fallback_delete(name)
        service = self._get_drive_service()
        if not service:
            return self._fallback_delete(name)
        try:
            service.files().delete(fileId=name, supportsAllDrives=True).execute()
        except Exception:
            self._fallback_delete(name)

    def _fallback_delete(self, name):
        if self._fallback is not None:
            return self._fallback.delete(name)
        from django.core.files.storage import default_storage
        return default_storage.delete(name)

    def exists(self, name):
        if not name:
            return False
        if '/' in name or not DRIVE_ID_RE.match(name.strip()):
            return self._fallback_exists(name)
        service = self._get_drive_service()
        if not service:
            return self._fallback_exists(name)
        try:
            service.files().get(fileId=name, fields='id', supportsAllDrives=True).execute()
            return True
        except Exception:
            return False

    def _fallback_exists(self, name):
        if self._fallback is not None:
            return self._fallback.exists(name)
        from django.core.files.storage import default_storage
        return default_storage.exists(name)

    def size(self, name):
        if not name or '/' in name or not DRIVE_ID_RE.match(name.strip()):
            return self._fallback_size(name)
        service = self._get_drive_service()
        if not service:
            return self._fallback_size(name)
        try:
            meta = service.files().get(fileId=name, fields='size', supportsAllDrives=True).execute()
            return int(meta.get('size', 0))
        except Exception:
            return self._fallback_size(name)

    def _fallback_size(self, name):
        if self._fallback is not None:
            return self._fallback.size(name)
        from django.core.files.storage import default_storage
        return default_storage.size(name)
