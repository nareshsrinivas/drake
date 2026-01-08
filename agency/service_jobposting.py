# agency/service_jobposting.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from uuid import UUID
from datetime import datetime
from models import JobPosting, JobApplication, User
from fastapi import HTTPException


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



# ----------------- job posting list service  ----

async def get_agency_single_job_status(
    db,
    agency_id: int,
    job_uuid
):
    # 1️⃣ Validate & fetch job (ownership check)
    result = await db.execute(
        select(JobPosting)
        .where(
            JobPosting.uuid == job_uuid,
            JobPosting.agency_id == agency_id,
            JobPosting.is_delete == False
        )
    )
    job = result.scalars().first()

    if not job:
        raise HTTPException(404, "Job not found")

    # 2️⃣ Fetch applicants for this job
    apps_result = await db.execute(
        select(
            JobApplication.uuid.label("application_uuid"),
            JobApplication.status,
            User.id.label("model_id"),
            User.uuid.label("model_uuid"),
            User.first_name,
            User.last_name,
            User.gender,
            User.current_city
        )
        .join(User, User.id == JobApplication.model_id)
        .where(
            JobApplication.job_id == job.id,
            JobApplication.is_delete == False
        )
    )

    applicants = [
        {
            "application_uuid": str(row.application_uuid),
            "model_id": row.model_id,
            "model_uuid": str(row.model_uuid),
            "name": f"{row.first_name} {row.last_name}",
            "gender": row.gender,
            "city": row.current_city,
            "status": row.status
        }
        for row in apps_result.all()
    ]

    # 3️⃣ Final response
    return {
        # "job_uuid": str(job.uuid),
        "job_role": job.job_role,
        "location": job.location,
        "total_applications": len(applicants),
        "applicants": applicants
    }

