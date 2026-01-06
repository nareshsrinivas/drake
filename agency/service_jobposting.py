# agency/service_jobposting.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from uuid import UUID
from datetime import datetime
from models import JobPosting, JobApplication


def to_naive(dt: datetime | None):
    """Convert tz-aware datetime to tz-naive (UTC stripped)"""
    if dt and dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt


async def create_jobposting(db: AsyncSession, data, agency_id: int):
    job = JobPosting(
        agency_id=agency_id,
        job_role=data.job_role,
        description=data.description,
        project_type=data.project_type,
        gender=data.gender,
        location=data.location,
        pay_min=data.pay_min,
        pay_max=data.pay_max,
        pay_type=data.pay_type,
        pay_unit=data.pay_unit,
        is_paid=data.is_paid,

        qualifications=data.qualifications,
        required_skills=data.required_skills,

        # 🔥 CLEAN DATETIMES HERE
        date_from=to_naive(data.date_from),
        date_to=to_naive(data.date_to),
        expires_at=to_naive(data.expires_at),
        deadline=to_naive(data.deadline),

        requirements=data.requirements,
        status=data.status,
        visibility=data.visibility,
        created_by=agency_id,
        updated_by=agency_id,
    )

    db.add(job)
    await db.commit()
    await db.refresh(job)

    return job, None


async def update_jobposting(db: AsyncSession, uuid: UUID, data, agency_id: int):
    result = await db.execute(
        select(JobPosting).where(
            JobPosting.uuid == uuid,
            JobPosting.agency_id == agency_id,
            JobPosting.is_delete == False
        )
    )
    job = result.scalars().first()

    if not job:
        return None, "Job not found"

    for field, value in data.dict(exclude_unset=True).items():
        setattr(job, field, value)

    job.updated_by = agency_id

    await db.commit()
    await db.refresh(job)

    return job, None


async def get_all_jobpostings(db: AsyncSession, agency_id: int):
    result = await db.execute(
        select(JobPosting).where(
            JobPosting.agency_id == agency_id,
            JobPosting.is_delete == False
        )
    )
    return result.scalars().all()


async def get_jobposting_by_uuid(db: AsyncSession, uuid: UUID):
    result = await db.execute(
        select(JobPosting).where(
            JobPosting.uuid == uuid,
            JobPosting.is_delete == False
        )
    )
    return result.scalars().first()



async def delete_jobposting(db: AsyncSession, uuid: UUID, agency_id: int):
    # 🔎 Fetch job
    result = await db.execute(
        select(JobPosting).where(
            JobPosting.uuid == uuid,
            JobPosting.agency_id == agency_id
        )
    )
    job = result.scalars().first()

    if not job:
        return None, "Job not found"

    # ❗ HARD DELETE: pehle job applications delete karo
    await db.execute(
        delete(JobApplication).where(
            JobApplication.job_id == job.id
        )
    )

    # ❗ Ab job delete karo
    await db.delete(job)
    await db.commit()

    return True, None


# async def delete_jobposting(db: AsyncSession, uuid: UUID, agency_id: int):
#     result = await db.execute(
#         select(JobPosting).where(JobPosting.uuid == uuid)
#     )
#     job = result.scalars().first()
#
#     if not job:
#         return None, "Job not found"
#
#     if job.agency_id != agency_id:
#         return None, "Unauthorized"
#
#     await db.delete(job)
#     await db.commit()
#
#     return True, None

