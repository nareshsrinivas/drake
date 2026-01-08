from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, status
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
import json
import os
import uuid
from uuid import UUID
from fastapi import Request
from sqlalchemy import select, func
from core.media import parse_media
from core.deps import get_db, get_current_user
from agency.agency_profile_schema import AgencyProfileCreate, AgencyProfileUpdate, AgencyProfileResponse
from agency.agency_profile_service import (
    create_agency_profile,
    update_agency_profile,
    get_agency_profile,
    get_agency_by_uuid
)
from agency.schema_jobposting import *
from agency.service_jobposting import *
from models import AgencyProfile

UPLOAD_DIR = "uploads/agency"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(prefix="/agency", tags=["Agency Profile"])

def parse_job_media(request: Request, job):
    base = str(request.base_url).rstrip("/")

    return {
        "logo": f"{base}/{job.logo}" if getattr(job, "logo", None) else None
    }

# ------------------------------------------------------------------------------------------------------------
# -------------------------------------------job posting ----------------------
# -------------------------------------------------------------------------------------------------------------

@router.post("/jobposting", status_code=status.HTTP_201_CREATED,response_model=JobPostingOut)
async def create_jobposting_api(
        data: JobPostingCreate,
        db: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_user)
):
    if current_user.user_type != 2:
        raise HTTPException(403, "Only agencies can create jobs")

    # ✅ ADD VALIDATION (no existing code changed)
    result = await db.execute(
        select(JobPosting).where(
            JobPosting.agency_id == current_user.id,
            JobPosting.is_delete == False
        )
    )
    job_count = len(result.scalars().all())

    if job_count >= 3:
        raise HTTPException(400, "subscribe for more job postings")

    job, err = await create_jobposting(db, data, current_user.id)
    if err:
        raise HTTPException(400, err)

    return job


# ---------------------------------------
# UPLOAD JOB POSTING LOGO
# ---------------------------------------
@router.post("/jobposting/{jobposting_uuid}/upload-logo")
async def upload_job_logo(
        job_uuid: UUID,
        file: UploadFile = File(...),
        db: AsyncSession = Depends(get_db),
        user=Depends(get_current_user)
):
    if user.user_type != 2:
        raise HTTPException(403, "Only agencies can upload job logos")

    if not file.filename.lower().endswith(("jpg", "jpeg", "png", "webp")):
        raise HTTPException(400, "Invalid image format")

    result = await db.execute(
        select(JobPosting).where(
            JobPosting.uuid == job_uuid,
            JobPosting.agency_id == user.id,
            JobPosting.is_delete == False
        )
    )
    job = result.scalars().first()

    if not job:
        raise HTTPException(404, "Job not found")

    filename = f"{uuid.uuid4()}_{file.filename.replace(' ', '_')}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    job.logo = file_path
    job.updated_by = user.id

    await db.commit()
    await db.refresh(job)

    return {
        "message": "Job logo uploaded successfully",
        "logo": file_path.replace("\\", "/"),
        "job_uuid": str(job.uuid)
    }


# -------- combined job posting = info + logo ---------
@router.post("/job/post", status_code=status.HTTP_201_CREATED, response_model=JobPostingOut)
async def create_job_with_logo(
    request: Request,

    # -------- job fields (FORM DATA) --------
    job_role: str = Form(...),
    description: str | None = Form(None),
    project_type: str | None = Form(None),

    gender: str | None = Form("any"),
    location: str | None = Form(None),

    pay_min: float | None = Form(None),
    pay_max: float | None = Form(None),
    pay_type: str | None = Form(None),
    pay_unit: str | None = Form(None),
    is_paid: bool | None = Form(True),

    qualifications: str | None = Form(None),
    required_skills: str | None = Form(None),

    requirements: str | None = Form(None),
    status: str | None = Form("open"),
    visibility: str | None = Form("public"),

    # -------- logo --------
    logo: UploadFile | None = File(None),

    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.user_type != 2:
        raise HTTPException(403, "Only agencies can create jobs")

    # 🔒 Job limit check
    result = await db.execute(
        select(JobPosting).where(
            JobPosting.agency_id == current_user.id,
            JobPosting.is_delete == False
        )
    )
    if len(result.scalars().all()) >= 3:
        raise HTTPException(400, "subscribe for more job postings")

    # ✅ UPDATED: SAFE requirements parsing
    parsed_requirements = None
    if requirements and requirements.strip():
        try:
            parsed_requirements = json.loads(requirements)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail="requirements must be valid JSON"
            )

    # 🧠 Build schema manually
    data = JobPostingCreate(
        job_role=job_role,
        description=description,
        project_type=project_type,
        gender=gender,
        location=location,
        pay_min=pay_min,
        pay_max=pay_max,
        pay_type=pay_type,
        pay_unit=pay_unit,
        is_paid=is_paid,
        qualifications=qualifications,
        required_skills=required_skills,
        requirements=parsed_requirements,
        status=status,
        visibility=visibility
    )

    job, err = await create_jobposting(db, data, current_user.id)
    if err:
        raise HTTPException(400, err)

    # 🖼️ LOGO UPLOAD
    if logo:
        if not logo.filename.lower().endswith(("jpg", "jpeg", "png", "webp")):
            raise HTTPException(400, "Invalid image format")

        filename = f"{uuid.uuid4()}_{logo.filename.replace(' ', '_')}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as f:
            f.write(await logo.read())

        job.logo = file_path
        job.updated_by = current_user.id
        await db.commit()
        await db.refresh(job)

    media = parse_job_media(request, job)

    return {
        **job.__dict__,
        **media
    }



@router.patch("/jobposting/{uuid}", response_model=JobPostingOut)
async def update_jobposting_api(
        uuid: UUID,
        data: JobPostingUpdate,
        db: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_user)
):
    job, err = await update_jobposting(db, uuid, data, current_user.id)
    if err:
        raise HTTPException(404, err)

    return job


@router.get("/jobposting/{uuid}", response_model=JobPostingOut)
async def get_job_details_api(
        uuid: UUID,
        request: Request,
        db: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_user)
):
    job = await get_jobposting_by_uuid(db, uuid)
    if not job:
        raise HTTPException(404, "Job not found")

    if job.visibility == "public" or job.agency_id == current_user.id:
        media = parse_job_media(request, job)
        return {
            **job.__dict__,
            **media
        }

    raise HTTPException(403, "Unauthorized")

# ------------job apply list-------------

@router.get("/job/status/{job_uuid}")
async def get_single_job_status(
    job_uuid: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.user_type != 2:
        raise HTTPException(403, "Only agencies allowed")

    return await get_agency_single_job_status(
        db,
        current_user.id,
        job_uuid
    )


@router.get("/jobposting", response_model=list[JobPostingOut])
async def get_all_jobs_api(
        request: Request,
        db: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_user)
):
    jobs = await get_all_jobpostings(db, current_user.id)

    response = []
    for job in jobs:
        media = parse_job_media(request, job)
        response.append({
            **job.__dict__,
            **media
        })

    return response

# @router.get("/jobposting", response_model=list[JobPostingOut])
# async def get_all_jobs_api(
#         db: AsyncSession = Depends(get_db),
#         current_user=Depends(get_current_user)
# ):
#     return await get_all_jobpostings(db, current_user.id)


@router.delete("/jobposting/{uuid}")
async def delete_job_api(
        uuid: UUID,
        db: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_user)
):
    ok, err = await delete_jobposting(db, uuid, current_user.id)
    if err:
        raise HTTPException(404, err)

    return {"message": "Job deleted successfully"}


# ------------------------------------------------------------------------------------------------------------
# -------------------------------------------Agency Profile Create ----------------------
# -------------------------------------------------------------------------------------------------------------
# -----------------------------
# CREATE PROFILE (FORM-DATA)
# -----------------------------

@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=AgencyProfileResponse)
async def create_profile(
        request: Request,
        company_name: str = Form(...),
        contact_name: str = Form(...),
        phone: str = Form(...),

        website: str = Form(None),
        address: str = Form(None),
        tagline: str = Form(None),
        about: str = Form(None),

        services: list[str] = Form(None),
        social_links: list[str] = Form(None),

        logo: UploadFile = File(None),
        # photos: list[UploadFile] = File(None),

        db: AsyncSession = Depends(get_db),
        user=Depends(get_current_user)
):
    social_dict = {}
    if social_links:
        for item in social_links:
            if ":" in item:
                k, v = item.split(":", 1)
                social_dict[k] = v

    logo_path = None
    if logo:
        name = f"{uuid.uuid4()}_{logo.filename}"
        path = os.path.join(UPLOAD_DIR, name)
        with open(path, "wb") as f:
            f.write(await logo.read())
        logo_path = path

    data = AgencyProfileCreate(
        company_name=company_name,
        contact_name=contact_name,
        phone=phone,
        website=website,
        address=address,
        tagline=tagline,
        about=about,
        services=services,
        social_links=social_dict
    )

    profile = await create_agency_profile(db, user.id, data)

    # store media paths
    profile.logo = logo_path
    # profile.photos = "|".join(photo_paths)

    await db.commit()
    await db.refresh(profile)

    # ✅ ADD MEDIA URLS
    media = parse_media(request, profile)

    return {
        **profile.__dict__,
        **media
    }


# -----------------------------
# UPDATE PROFILE
# -----------------------------
@router.patch("/update", response_model=AgencyProfileResponse)
async def update_profile(
        request: Request,

        # -------- text fields --------
        company_name: str | None = Form(None),
        contact_name: str | None = Form(None),
        phone: str | None = Form(None),
        website: str | None = Form(None),
        address: str | None = Form(None),
        tagline: str | None = Form(None),
        about: str | None = Form(None),

        services: list[str] | None = Form(None),
        social_links: list[str] | None = Form(None),

        # -------- media --------
        logo: UploadFile | None = File(None),

        db: AsyncSession = Depends(get_db),
        user=Depends(get_current_user)
):
    profile = await get_agency_profile(db, user.id)

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # 🔹 TEXT PATCH
    if company_name is not None:
        profile.company_name = company_name

    if contact_name is not None:
        profile.contact_name = contact_name

    if phone is not None:
        profile.phone = phone

    if website is not None:
        profile.website = website

    if address is not None:
        profile.address = address

    if tagline is not None:
        profile.tagline = tagline

    if about is not None:
        profile.about = about

    if services is not None:
        profile.services = services

    if social_links is not None:
        social_dict = {}
        for item in social_links:
            if ":" in item:
                k, v = item.split(":", 1)
                social_dict[k.strip()] = v.strip()
        profile.social_links = social_dict

    # 🔹 LOGO PATCH (ONLY IF SENT)
    if logo:
        filename = f"{uuid.uuid4()}_{logo.filename}"
        path = os.path.join(UPLOAD_DIR, filename)
        with open(path, "wb") as f:
            f.write(await logo.read())
        profile.logo = path

    profile.updated_by = user.id

    await db.commit()
    await db.refresh(profile)

    media = parse_media(request, profile)

    return {
        **profile.__dict__,
        **media
    }


# -----------------------------
# GET MY PROFILE
# -----------------------------

@router.get("/me", response_model=AgencyProfileResponse)
async def get_my_profile(
        request: Request,
        db: AsyncSession = Depends(get_db),
        user=Depends(get_current_user)
):
    if user.user_type != 2:
        raise HTTPException(status_code=403, detail="Only agencies can view profile")

    profile = await get_agency_profile(db, user.id)

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    media = parse_media(request, profile)

    return {
        **profile.__dict__,
        **media
    }



# -----------------------------
# PUBLIC GET PROFILE BY UUID
# -----------------------------

@router.get("/{uuid}", response_model=AgencyProfileResponse)
async def public_get_profile(
        uuid: str,
        request: Request,
        db: AsyncSession = Depends(get_db)
):
    # 🔒 HARD GUARD: validate UUID manually
    try:
        uuid_obj = UUID(uuid)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid agency UUID"
        )

    profile = await get_agency_by_uuid(db, uuid_obj)

    if not profile:
        raise HTTPException(status_code=404, detail="Agency not found")

    media = parse_media(request, profile)

    return {
        **profile.__dict__,
        **media
    }

# ---------------------------------------
# Post Agency without logo
# ---------------------------------------
@router.post("/agency-create", status_code=status.HTTP_201_CREATED, response_model=AgencyProfileResponse)
async def create_agency_profile_json(
    data: AgencyProfileCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.user_type != 2:
        raise HTTPException(403, "Only agencies can create profile")

    profile = await create_agency_profile(db, user.id, data)
    return profile


# ---------------------------------------
# Patch Agency without logo
# ---------------------------------------
@router.patch("/agency-create", response_model=AgencyProfileResponse)
async def update_agency_profile_json(
    data: AgencyProfileUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.user_type != 2:
        raise HTTPException(403, "Only agencies can update profile")

    profile = await update_agency_profile(db, user.id, data)
    if not profile:
        raise HTTPException(404, "Agency profile not found")

    return profile


# ---------------------------------------
# UPLOAD AGENCY LOGO
# ---------------------------------------
@router.post("/upload-logo")
def upload_logo(
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        user=Depends(get_current_user)
):
    if user.user_type != 2:
        raise HTTPException(status_code=403, detail="Only agencies can upload logo")

    # validate file type
    if not file.filename.lower().endswith(("jpg", "jpeg", "png", "webp")):
        raise HTTPException(status_code=400, detail="Invalid file format")

    # generate unique name
    filename = f"{uuid.uuid4()}_{file.filename.replace(' ', '_')}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    # save file
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    # update DB
    profile = get_agency_profile(db, user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Agency profile not found")

    profile.logo = file_path
    db.commit()
    db.refresh(profile)

    return {
        "message": "Logo uploaded successfully",
        "logo": file_path.replace("\\", "/"),
        "uuid": str(profile.uuid)
    }


# ----------------------------------------------
# agaency profile delete
# ----------------------------------------------

@router.delete("/delete")
async def delete_agency_profile(
        db: AsyncSession = Depends(get_db),
        user=Depends(get_current_user)
):
    if user.user_type != 2:
        raise HTTPException(
            status_code=403,
            detail="Only agencies can delete profile"
        )

    result = await db.execute(
        select(AgencyProfile).where(
            AgencyProfile.user_id == user.id
        )
    )
    profile = result.scalars().first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Agency profile not found"
        )

    await db.delete(profile)
    await db.commit()

    return {
        "message": "Agency profile deleted successfully"
    }



