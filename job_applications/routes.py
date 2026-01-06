from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.deps import get_db, get_current_user
from job_applications.schema import (
    JobApplicationCreate,
    JobApplicationUpdate,
    JobApplicationOut
)
from job_applications.service import (
    create_job_application,
    update_job_application,
    get_application_by_uuid,
    list_applications_service,
    hard_delete_application
)

router = APIRouter(prefix="/applications", tags=["Applications"])


# APPLY JOB
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=JobApplicationOut)
async def apply_job(
    data: JobApplicationCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.user_type != 1:
        raise HTTPException(status_code=403, detail="Only models can apply")

    application, err = await create_job_application(
        db, data, user.id
    )
    if err:
        raise HTTPException(status_code=400, detail=err)

    return application


# UPDATE APPLICATION
@router.patch("/{uuid}", response_model=JobApplicationOut)
async def update_application(
    uuid: str,
    data: JobApplicationUpdate,
    db: AsyncSession = Depends(get_db)
):
    application, err = await update_job_application(db, uuid, data)
    if err:
        raise HTTPException(status_code=404, detail=err)

    return application


# GET APPLICATION DETAILS
@router.get("/{uuid}", response_model=JobApplicationOut)
async def get_application_details(
    uuid: str,
    db: AsyncSession = Depends(get_db)
):
    application = await get_application_by_uuid(db, uuid)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    return application


# LIST APPLICATIONS
@router.get("/", response_model=list[JobApplicationOut])
async def list_applications(
    job_id: int | None = None,
    db: AsyncSession = Depends(get_db)
):
    return await list_applications_service(db, job_id)


# DELETE APPLICATION
@router.delete("/{uuid}")
async def delete_application(
    uuid: str,
    db: AsyncSession = Depends(get_db)
):
    ok, err = await hard_delete_application(db, uuid)
    if err:
        raise HTTPException(status_code=404, detail=err)

    return {"message": "Application deleted"}















# from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
# from sqlalchemy.ext.asyncio import AsyncSession
# import os
# import uuid
#
# from core.deps import get_db, get_current_user
# from job_applications.schema import (
#     JobApplicationCreate,
#     JobApplicationUpdate,
#     JobApplicationOut
# )
# from job_applications.service import (
#     create_job_application,
#     update_job_application,
#     get_application_by_uuid,
#     list_applications_service,
#     # soft_delete_application,
#     hard_delete_application
# )
#
#
# router = APIRouter(prefix="/applications", tags=["Applications"])
#
# UPLOAD_DIR = "uploads/resume"
# os.makedirs(UPLOAD_DIR, exist_ok=True)
#
# ALLOWED_EXTENSIONS = {"pdf", "doc", "docx"}
#
# # APPLY JOB
#
# @router.post("/", status_code=status.HTTP_201_CREATED, response_model=JobApplicationOut)
# async def apply_job(
#     data: JobApplicationCreate = Depends(),
#     resume_upload: UploadFile | None = File(None),
#     db: AsyncSession = Depends(get_db),
#     user=Depends(get_current_user)
# ):
#     if user.user_type != 1:
#         raise HTTPException(status_code=403, detail="Only models can apply")
#
#     resume_path = None
#
#     if resume_upload:
#         ext = resume_upload.filename.split(".")[-1].lower()
#         if ext not in ALLOWED_EXTENSIONS:
#             raise HTTPException(
#                 status_code=400,
#                 detail="Only PDF or DOC files allowed"
#             )
#
#         filename = f"{uuid.uuid4()}.{ext}"
#         resume_path = os.path.join(UPLOAD_DIR, filename)
#
#         with open(resume_path, "wb") as f:
#             f.write(await resume_upload.read())
#
#     application, err = await create_job_application(
#         db, data, user.id, resume_path
#     )
#     if err:
#         raise HTTPException(status_code=400, detail=err)
#
#     return application
#
# # @router.post("/", status_code=status.HTTP_201_CREATED,response_model=JobApplicationOut)
# # async def apply_job(
# #     data: JobApplicationCreate,
# #     db: AsyncSession = Depends(get_db),
# #     user=Depends(get_current_user)
# # ):
# #     if user.user_type != 1:
# #         raise HTTPException(status_code=403, detail="Only models can apply")
# #
# #     application, err = await create_job_application(db, data, user.id)
# #     if err:
# #         raise HTTPException(status_code=400, detail=err)
# #
# #     return application
#
#
# # UPDATE APPLICATION
# @router.patch("/{uuid}", response_model=JobApplicationOut)
# async def update_application(
#     uuid: str,
#     data: JobApplicationUpdate,
#     db: AsyncSession = Depends(get_db)
# ):
#     app, err = await update_job_application(db, uuid, data)
#     if err:
#         raise HTTPException(status_code=404, detail=err)
#
#     return app
#
#
# # GET APPLICATION DETAILS
# @router.get("/{uuid}", response_model=JobApplicationOut)
# async def get_application_details(
#     uuid: str,
#     db: AsyncSession = Depends(get_db)
# ):
#     app = await get_application_by_uuid(db, uuid)
#     if not app:
#         raise HTTPException(status_code=404, detail="Application not found")
#
#     return app
#
#
# # LIST APPLICATIONS
# @router.get("/", response_model=list[JobApplicationOut])
# async def list_applications(
#     job_id: int | None = None,
#     db: AsyncSession = Depends(get_db)
# ):
#     return await list_applications_service(db, job_id)
#
#
# # DELETE APPLICATION
#
# @router.delete("/{uuid}")
# async def delete_application(
#     uuid: str,
#     db: AsyncSession = Depends(get_db)
# ):
#     ok, err = await hard_delete_application(db, uuid)
#     if err:
#         raise HTTPException(status_code=404, detail=err)
#
#     return {"message": "Application deleted"}
#
