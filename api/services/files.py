from pathlib import Path
from uuid import uuid4
import mimetypes

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from config import settings
from db.models import FileRecord


class FileService:
    def __init__(self, upload_dir: Path = settings.FILES_DIRECTORY):
        self.upload_dir = upload_dir
          # coerce upload_dir to Path in case a string was provided
        self.upload_dir = Path(upload_dir) if not isinstance(upload_dir, Path) else upload_dir

    def save_file_bytes(self, filename: str, content: bytes, content_type: str | None, db: Session, user_id: int) -> FileRecord:
        safe_name = Path(filename).name
        # normalize common extensions: prefer .jpg over .jpeg for saved filenames
        user_dir = self.upload_dir / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        dest = user_dir / safe_name

        attempts = 0
        while dest.exists():
            attempts += 1
            p = Path(safe_name)
            suffix = p.suffix
            stem = p.stem
            unique_name = f"{stem}_{uuid4().hex[:8]}{suffix}"
            safe_name = unique_name
            dest = user_dir / safe_name
            if attempts >= 10:
                unique_name = f"{stem}_{uuid4().hex}{suffix}"
                safe_name = unique_name
                dest = user_dir / safe_name
                break

        try:
            dest.write_bytes(content)
        except OSError as e:
            raise RuntimeError("failed to write file") from e

        file_rec = FileRecord(
            user_id=user_id,
            filename=safe_name,
            content_type=content_type,
            size=len(content),
            path=str(dest),
        )

        try:
            db.add(file_rec)
            db.commit()
            db.refresh(file_rec)
        except SQLAlchemyError as e:
            db.rollback()
            try:
                dest.unlink(missing_ok=True)
            except Exception:
                pass
            raise

        return file_rec

    def list_user_files(self, user_id: int, db: Session) -> list[FileRecord]:
        stmt = select(FileRecord).where(FileRecord.user_id == int(user_id))
        rows = db.execute(stmt).scalars().all()
        return rows

    def get_file_record(self, file_id: int, db: Session) -> FileRecord | None:
        stmt = select(FileRecord).where(FileRecord.id == int(file_id) and FileRecord.user_id == int(file_id))
        return db.execute(stmt).scalar_one_or_none()


def get_file_service() -> FileService:
    return FileService()
