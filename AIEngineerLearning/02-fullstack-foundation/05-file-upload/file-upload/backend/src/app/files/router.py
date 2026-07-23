import uuid
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    status,
)

from app.files.dependencies import (
    get_current_owner_id,
    get_file_service,
)
from app.files.schemas import FileMetadataResponse
from app.files.service import FileService

router = APIRouter(
    prefix="/files",
    tags=["files"],
)


FileServiceDependency = Annotated[
    FileService,
    Depends(get_file_service),
]

OwnerDependency = Annotated[
    str,
    Depends(get_current_owner_id),
]


@router.post(
    "",
    response_model=FileMetadataResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_file(
    service: FileServiceDependency,
    owner_id: OwnerDependency,
    file: Annotated[
        UploadFile,
        File(description="A .txt or .md file"),
    ],
) -> FileMetadataResponse:
    uploaded_file = await service.upload_file(
        upload=file,
        owner_id=owner_id,
    )

    return FileMetadataResponse.model_validate(uploaded_file)


@router.get(
    "",
    response_model=list[FileMetadataResponse],
)
async def list_files(
    service: FileServiceDependency,
    owner_id: OwnerDependency,
) -> list[FileMetadataResponse]:
    uploaded_files = await service.list_files(owner_id)

    return [FileMetadataResponse.model_validate(uploaded_file) for uploaded_file in uploaded_files]


@router.get(
    "/{file_id}",
    response_model=FileMetadataResponse,
)
async def get_file_metadata(
    file_id: uuid.UUID,
    service: FileServiceDependency,
    owner_id: OwnerDependency,
) -> FileMetadataResponse:
    uploaded_file = await service.get_file(
        file_id=file_id,
        owner_id=owner_id,
    )

    return FileMetadataResponse.model_validate(uploaded_file)


@router.delete(
    "/{file_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_file(
    file_id: uuid.UUID,
    service: FileServiceDependency,
    owner_id: OwnerDependency,
) -> None:
    await service.delete_file(
        file_id=file_id,
        owner_id=owner_id,
    )
