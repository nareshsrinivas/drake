from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, cast, String, update, delete
from datetime import datetime

from models import JobApplication, JobPosting


# CREATE APPLICATION
async def create_job_application(
    db: AsyncSession,
    data,
    model_id: int
):
    result = await db.execute(
        select(JobPosting).where(
            JobPosting.uuid == data.job_uuid,
            JobPosting.is_delete == False
        )
    )
    job = result.scalar_one_or_none()

    if not job:
        return None, "Job not found"

    application = JobApplication(
        job_id=job.id,
        model_id=model_id,
        status="applied"
    )

    db.add(application)
    await db.commit()
    await db.refresh(application)

    return application, None


# UPDATE APPLICATION
async def update_job_application(
    db: AsyncSession,
    uuid: str,
    data
):
    result = await db.execute(
        select(JobApplication).where(
            cast(JobApplication.uuid, String) == uuid,
            JobApplication.is_delete == False
        )
    )
    application = result.scalar_one_or_none()

    if not application:
        return None, "Application not found"

    for field, value in data.dict(exclude_unset=True).items():
        setattr(application, field, value)

    application.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(application)

    return application, None


# GET BY UUID
async def get_application_by_uuid(
    db: AsyncSession,
    uuid: str
):
    result = await db.execute(
        select(JobApplication).where(
            cast(JobApplication.uuid, String) == uuid,
            JobApplication.is_delete == False
        )
    )
    return result.scalar_one_or_none()


# LIST APPLICATIONS
async def list_applications_service(
    db: AsyncSession,
    job_id: int | None = None
):
    stmt = select(JobApplication).where(
        JobApplication.is_delete == False
    )

    if job_id:
        stmt = stmt.where(JobApplication.job_id == job_id)

    stmt = stmt.order_by(JobApplication.created_at.desc())

    result = await db.execute(stmt)
    return result.scalars().all()


# HARD DELETE
async def hard_delete_application(
    db: AsyncSession,
    uuid: str
):
    stmt = delete(JobApplication).where(
        cast(JobApplication.uuid, String) == uuid
    )

    result = await db.execute(stmt)

    if result.rowcount == 0:
        return None, "Application not found"

    await db.commit()
    return True, None














# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select, cast, String, update, delete
# from datetime import datetime
#
# from models import JobApplication, JobPosting
#
#
# # CREATE APPLICATION
# async def create_job_application(
#     db: AsyncSession,
#     data,
#     model_id: int,
#     resume_path: str | None = None
# ):
#     result = await db.execute(
#         select(JobPosting).where(
#             JobPosting.uuid == data.job_uuid,
#             JobPosting.is_delete == False
#         )
#     )
#     job = result.scalar_one_or_none()
#
#     if not job:
#         return None, "Job not found"
#
#     app = JobApplication(
#         job_id=job.id,
#         model_id=model_id,
#         message=data.message,
#         resume_upload=resume_path,
#         status="applied"
#     )
#
#     db.add(app)
#     await db.commit()
#     await db.refresh(app)
#
#     return app, None
#
# # async def create_job_application(
# #     db: AsyncSession,
# #     data,
# #     model_id: int
# # ):
# #     result = await db.execute(
# #         select(JobPosting).where(
# #             JobPosting.uuid == data.job_uuid,
# #             JobPosting.is_delete == False
# #         )
# #     )
# #     job = result.scalar_one_or_none()
# #
# #     if not job:
# #         return None, "Job not found"
# #
# #     app = JobApplication(
# #         job_id=job.id,
# #         model_id=model_id,
# #         message=data.message,
# #         selected_media=data.selected_media,
# #         status="applied"
# #     )
# #
# #     db.add(app)
# #     await db.commit()
# #     await db.refresh(app)
# #
# #     return app, None
#
#
# # UPDATE APPLICATION
# async def update_job_application(
#     db: AsyncSession,
#     uuid: str,
#     data
# ):
#     result = await db.execute(
#         select(JobApplication).where(
#             cast(JobApplication.uuid, String) == uuid,
#             JobApplication.is_delete == False
#         )
#     )
#     app = result.scalar_one_or_none()
#
#     if not app:
#         return None, "Application not found"
#
#     for field, value in data.dict(exclude_unset=True).items():
#         setattr(app, field, value)
#
#     app.updated_at = datetime.utcnow()
#     await db.commit()
#     await db.refresh(app)
#
#     return app, None
#
#
# # GET BY UUID
# async def get_application_by_uuid(
#     db: AsyncSession,
#     uuid: str
# ):
#     result = await db.execute(
#         select(JobApplication).where(
#             cast(JobApplication.uuid, String) == uuid,
#             JobApplication.is_delete == False
#         )
#     )
#     return result.scalar_one_or_none()
#
#
# # LIST APPLICATIONS
# async def list_applications_service(
#     db: AsyncSession,
#     job_id: int | None = None
# ):
#     stmt = select(JobApplication).where(
#         JobApplication.is_delete == False
#     )
#
#     if job_id:
#         stmt = stmt.where(JobApplication.job_id == job_id)
#
#     stmt = stmt.order_by(JobApplication.created_at.desc())
#
#     result = await db.execute(stmt)
#     return result.scalars().all()
#
#
# # SOFT DELETE
#
# async def hard_delete_application(
#     db: AsyncSession,
#     uuid: str
# ):
#     stmt = delete(JobApplication).where(
#         cast(JobApplication.uuid, String) == uuid
#     )
#
#     result = await db.execute(stmt)
#
#     if result.rowcount == 0:
#         return None, "Application not found"
#
#     await db.commit()
#     return True, None
#
#
# # async def soft_delete_application(
# #     db: AsyncSession,
# #     uuid: str
# # ):
# #     result = await db.execute(
# #         select(JobApplication).where(
# #             cast(JobApplication.uuid, String) == uuid,
# #             JobApplication.is_delete == False
# #         )
# #     )
# #     app = result.scalar_one_or_none()
#
# #     if not app:
# #         return None, "Application not found"
#
# #     app.is_delete = True
# #     await db.commit()
#
# #     return True, None
#
#
#
#
#
#
#
# # gaurav bhai backup code
# # from fastapi.concurrency import run_in_threadpool
# # from sqlalchemy.orm import Session
# # from sqlalchemy import cast, String
# # from datetime import datetime
# # from models import JobApplication, JobPosting
# # import uuid
#
#
# # async def create_job_application(db: Session, data, model_id: int):
#
# #     def _create():
# #         job_uuid = data.job_uuid
# #         # Convert job_uuid → job_id
# #         # try:
# #         #     job_uuid = uuid.UUID(data['job_uuid'])
# #         # except:
# #         #     return None, "Invalid UUID format"
#
# #         job = db.query(JobPosting).filter(
# #             JobPosting.uuid == job_uuid,
# #             JobPosting.is_delete == False
# #         ).first()
#
# #         if not job:
# #             return None, "Job not found"
#
# #         app = JobApplication(
# #             job_id=job.id,
# #             model_id=model_id,
# #             message=data.message,
# #             selected_media=data.selected_media,
# #             status="applied",
# #         )
# #         db.add(app)
# #         db.commit()
# #         db.refresh(app)
# #         return app, None
#
# #     return await run_in_threadpool(_create)
#
#
#
# # async def update_job_application(db: Session, uuid: str, data):
# #     def _update():
# #         app = db.query(JobApplication).filter(
# #             cast(JobApplication.uuid, String) == uuid,
# #             JobApplication.is_delete == False
# #         ).first()
#
# #         if not app:
# #             return None, "Application not found"
#
# #         for field, value in data.dict(exclude_unset=True).items():
# #             setattr(app, field, value)
#
# #         app.updated_at = datetime.utcnow()
# #         db.commit()
# #         db.refresh(app)
# #         return app, None
#
# #     return await run_in_threadpool(_update)
#
#
#
# # def get_application_by_uuid(db: Session, uuid: str):
# #     return db.query(JobApplication).filter(
# #         cast(JobApplication.uuid, String) == uuid,
# #         JobApplication.is_delete == False
# #     ).first()
#
#
#
# # def list_applications_service(db: Session, job_id: int | None = None):
# #     q = db.query(JobApplication).filter(JobApplication.is_delete == False)
#
# #     if job_id:
# #         q = q.filter(JobApplication.job_id == job_id)
#
# #     return q.order_by(JobApplication.created_at.desc()).all()
#
#
#
# # async def soft_delete_application(db: Session, uuid: str):
# #     def _delete():
# #         app = db.query(JobApplication).filter(
# #             cast(JobApplication.uuid, String) == uuid
# #         ).first()
#
# #         if not app:
# #             return None, "Application not found"
#
# #         app.is_delete = True
# #         db.commit()
# #         return True, None
#
# #     return await run_in_threadpool(_delete)
