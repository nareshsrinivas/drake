from sqlalchemy import select, or_, and_
from models import JobPosting


async def smart_search_jobs(db, search: str | None = None):
    stmt = (
        select(JobPosting)
        .where(
            JobPosting.visibility == "public",
            JobPosting.is_delete == False
        )
    )

    if search:
        keywords = search.lower().split()

        keyword_filters = []

        for word in keywords:
            conditions = []

            # 🔹 text based fields
            conditions.append(JobPosting.job_role.ilike(f"%{word}%"))
            conditions.append(JobPosting.location.ilike(f"%{word}%"))
            conditions.append(JobPosting.project_type.ilike(f"%{word}%"))
            conditions.append(JobPosting.gender.ilike(f"%{word}%"))
            conditions.append(JobPosting.required_skills.ilike(f"%{word}%"))
            conditions.append(JobPosting.status.ilike(f"%{word}%"))

            # 🔹 paid / unpaid keywords
            if word in ["paid", "unpaid", "free"]:
                conditions.append(
                    JobPosting.is_paid == (word == "paid")
                )

            keyword_filters.append(or_(*conditions))

        # 🔥 IMPORTANT:
        # all keywords must match somewhere
        stmt = stmt.where(and_(*keyword_filters))

    result = await db.execute(stmt)
    jobs = result.scalars().all()

    # 🔹 sparse response
    return [
        {
            "job_uuid": str(job.uuid),
            "job_role": job.job_role,
            "project_type": job.project_type,
            "location": job.location,
            "gender": job.gender,
            "pay_min": job.pay_min,
            "pay_max": job.pay_max,
            "is_paid": job.is_paid,
            "required_skills": job.required_skills,
            "status": job.status
        }
        for job in jobs
    ]
