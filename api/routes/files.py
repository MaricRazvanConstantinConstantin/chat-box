

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
import logging
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from api.deps import get_current_user
from pathlib import Path as LocalPath
from db.database import get_db
from api.services.files import FileService, get_file_service
from models.File import File as FileModel
import mimetypes
from fastapi.responses import FileResponse


router = APIRouter(prefix="/files", tags=["files"])

logger = logging.getLogger(__name__)


@router.post("", response_model=FileModel, status_code=status.HTTP_200_OK)
async def upload_file(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
    file_service: FileService = Depends(get_file_service),
):
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Filename is required")

    content = await file.read()

    try:
        file_rec = file_service.save_file_bytes(file.filename, content, file.content_type, db, int(current_user.id))
    except SQLAlchemyError as e:
        logger.exception("DB error while saving file record")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except RuntimeError as e:
        logger.exception("Filesystem error while writing uploaded file")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error during file upload")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return FileModel(
        user_id=file_rec.user_id,
        id=file_rec.id,
        filename=file_rec.filename,
        content_type=file_rec.content_type,
        size=file_rec.size,
        path=file_rec.path,
        uploaded_at=file_rec.uploaded_at,
    )



@router.get("", response_model=List[FileModel], status_code=status.HTTP_200_OK)
def list_files(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
    file_service: FileService = Depends(get_file_service),
):
    rows = file_service.list_user_files(int(current_user.id), db)
    return [FileModel.model_validate(r) for r in rows]



@router.get("/{file_id}/content", status_code=status.HTTP_200_OK, response_class=FileResponse)
def get_file_content(file_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db), file_service: FileService = Depends(get_file_service)):
    rec = file_service.get_file_record(int(file_id), db)
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    if int(rec.user_id) != int(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this file")

    path = LocalPath(rec.path)
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File missing on disk")

    media_type = rec.content_type or mimetypes.guess_type(str(path))[0] or "application/octet-stream"
    print(f"Serving file {rec.filename} with media type {media_type} and path {rec.path}")

    headers = {"Content-Disposition": f'inline; filename="{rec.filename}"'}
    return FileResponse(path=rec.path, media_type=media_type, headers=headers)


@router.get("/{file_id}/meta", response_model=FileModel, status_code=status.HTTP_200_OK)
def get_file_metadata(file_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db), file_service: FileService = Depends(get_file_service)):
    rec = file_service.get_file_record(int(file_id), db)
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    if int(rec.user_id) != int(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this file")

    return FileModel.model_validate(rec)
