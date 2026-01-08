# public/routes_public.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, cast, String
from sqlalchemy.orm import joinedload
from fastapi import Request

from admin.schema_contact import ContactCreate
from admin.service_contact import create_contact
from core.deps import get_db
from models import (
    HomeSlider, Skill, WorkType, User, ModelMedia, ModelProfile,
    ModelProfessional, ModelPortfolio, AgencyProfile, ContactBanner,
    JobPosting, UserSocialLink, ModelImages, Image_Videos
)
from utils.email_utils import send_email_sendgrid, NOTIFY_USERS

router = APIRouter(prefix="/public", tags=["Public APIs"])


# -------------------------------
# 🖼️ PUBLIC SLIDERS
# -------------------------------

@router.get("/sliders")
async def get_public_sliders(
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(HomeSlider)
        .where(HomeSlider.is_delete == False)
        .order_by(HomeSlider.is_order.asc())
    )

    result = await db.execute(stmt)
    sliders = result.scalars().all()

    return [
        {
            "uuid": str(s.uuid),
            "title": s.slider_title,   # ✅ FIXED
            "image": s.image,
            "is_order": s.is_order
        }
        for s in sliders
    ]


@router.get("/sliders/{uuid}")
async def get_public_slider_by_uuid(
    uuid: str,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(HomeSlider).where(
        HomeSlider.uuid == uuid,
        HomeSlider.is_delete == False
    )

    result = await db.execute(stmt)
    slider = result.scalar_one_or_none()

    if not slider:
        raise HTTPException(status_code=404, detail="Slider not found")

    return {
        "uuid": str(slider.uuid),
        "title": slider.slider_title,  # ✅ FIXED
        "image": slider.image,
        "is_order": slider.is_order
    }

# -------------------------------
# 🟦 PUBLIC SKILLS LIST
# -------------------------------
@router.get("/skills")
async def get_public_skills(
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Skill)
        .where(Skill.is_delete == False)
        .order_by(Skill.is_order.asc())
    )

    result = await db.execute(stmt)
    skills = result.scalars().all()

    return [
        {
            "uuid": str(skill.uuid),
            "name": skill.title,        # ✅ FIXED
            "is_order": skill.is_order
        }
        for skill in skills
    ]


@router.get("/skills/{uuid}")
async def get_public_skill_by_uuid(
    uuid: str,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Skill).where(
        Skill.uuid == uuid,
        Skill.is_delete == False
    )

    result = await db.execute(stmt)
    skill = result.scalar_one_or_none()

    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    return {
        "uuid": str(skill.uuid),
        "name": skill.title,          # ✅ FIXED
        "is_order": skill.is_order
    }


# -------------------------------
# 🧩 PUBLIC WORK TYPES
# -------------------------------
@router.get("/work-types")
async def get_public_work_types(
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(WorkType)
        .where(WorkType.is_delete == False)
        .order_by(WorkType.is_order.asc())
    )

    result = await db.execute(stmt)
    work_types = result.scalars().all()

    return [
        {
            "uuid": str(w.uuid),
            "name": w.work_type,     # ✅ FIXED
            "is_order": w.is_order
        }
        for w in work_types
    ]


@router.get("/work-types/{uuid}")
async def get_public_single_work_type(
    uuid: str,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(WorkType).where(
        WorkType.uuid == uuid,
        WorkType.is_delete == False
    )

    result = await db.execute(stmt)
    work_type = result.scalar_one_or_none()

    if not work_type:
        raise HTTPException(status_code=404, detail="Work type not found")

    return {
        "uuid": str(work_type.uuid),
        "name": work_type.work_type,   # ✅ FIXED
        "is_order": work_type.is_order
    }


# -----------------------------------
# 👥 PUBLIC: LIST ALL MODELS (SHORT INFO)
# -----------------------------------

def is_model_profile_complete(
        user,
        profile,
        professional,
        profile_photo_url
) -> bool:
    """Check if model profile is complete enough to display publicly"""

    # BASIC INFO (required)
    if not all([
        user.first_name,
        user.last_name,
        user.current_city,
        user.gender,
        user.nationality,
    ]):
        return False

    if user.age is None:
        return False

    # PROFILE (required)
    if not profile:
        return False

    numeric_fields = [
        profile.height,
        profile.weight,
        profile.chest_bust,
        profile.waist,
        profile.hips,
        profile.shoulder,
        profile.shoe_size,
    ]

    if any(field is None for field in numeric_fields):
        return False

    text_fields = [
        profile.complexion,
        profile.eye_color,
        profile.hair_color,
        profile.body_type,
        profile.hair_length,
    ]

    if any(not f for f in text_fields):
        return False

    # PROFESSIONAL (required) - Fixed attribute names
    if not professional:
        return False

    # Check only the attributes that exist in ModelProfessional
    if (
            not professional.experience_details or
            not professional.skills or
            not professional.languages or
            not professional.interested_categories
    ):
        return False

    return True


@router.get("/models")
async def get_public_models(
        request: Request,
        db: AsyncSession = Depends(get_db)
):
    """Get list of all models with basic information"""
    q = select(User).where(User.user_type == 1).order_by(User.first_name.asc())
    result = await db.execute(q)
    models = result.scalars().all()

    base_url = str(request.base_url).rstrip("/")
    response = []

    for user in models:
        # PROFILE
        profile = (await db.execute(
            select(ModelProfile).where(ModelProfile.user_id == user.id).limit(1)
        )).scalars().first()

        # PROFESSIONAL
        professional = (await db.execute(
            select(ModelProfessional).where(ModelProfessional.user_id == user.id).limit(1)
        )).scalars().first()

        # MEDIA GALLERY
        media_gallery = (await db.execute(
            select(Image_Videos).where(Image_Videos.user_id == user.id)
        )).scalars().first()

        images = []
        video = None
        profile_photo_url = None

        if media_gallery:
            images_res = await db.execute(
                select(ModelImages)
                .where(ModelImages.media_uuid == media_gallery.uuid)
                .order_by(ModelImages.image_index)
                .limit(5)
            )
            images_db = images_res.scalars().all()

            images = [
                f"{base_url}/{img.image_path}"
                for img in images_db
            ]

            # First image as profile photo (optional)
            profile_photo_url = images[0] if images else None

            if media_gallery.video:
                video = f"{base_url}/{media_gallery.video}"

        # Check completeness
        if not is_model_profile_complete(
                user=user,
                profile=profile,
                professional=professional,
                profile_photo_url=profile_photo_url
        ):
            continue

        response.append({
            "uuid": str(user.uuid),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": f"{user.first_name} {user.last_name}",
            "profile_photo": profile_photo_url,
            "current_city": user.current_city,
            "age": user.age,
            "gender": user.gender,
            "nationality": user.nationality,
            "approved": user.approved,
            "profile": {
                "height": profile.height,
                "weight": profile.weight,
                "chest_bust": profile.chest_bust,
                "waist": profile.waist,
                "hips": profile.hips,
                "shoe_size": profile.shoe_size,
                "eye_color": profile.eye_color,
                "hair_color": profile.hair_color,
                "complexion": profile.complexion,
            }
        })

    return response


# -----------------------------------
# 👤 PUBLIC: GET BASIC MODEL INFO
# -----------------------------------
@router.get("/models/basic/{uuid}")
async def get_public_model_basic(uuid: str, db: AsyncSession = Depends(get_db)):
    """Get basic information for a specific model"""
    q = select(User).where(cast(User.uuid, String) == uuid, User.user_type == 1)
    result = await db.execute(q)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="Model not found")

    q_media = select(ModelMedia).where(ModelMedia.user_id == user.id).limit(1)
    media_res = await db.execute(q_media)
    media = media_res.scalars().first()

    return {
        "uuid": str(user.uuid),
        "first_name": user.first_name,
        "last_name": user.last_name,
        "full_name": f"{user.first_name} {user.last_name}",
        "profile_photo": media.profile_photo if media else None,
        "current_city": user.current_city,
        "age": user.age,
        "gender": user.gender,
        "nationality": user.nationality,
        "approved": user.approved
    }


# -----------------------------------
# 📄 PUBLIC: FULL MODEL DETAILS
# -----------------------------------

@router.get("/models/details/{uuid}")
async def get_public_model_details(
        uuid: str,
        request: Request,
        db: AsyncSession = Depends(get_db)
):
    """Get complete details for a specific model including media gallery"""
    q = select(User).where(cast(User.uuid, String) == uuid, User.user_type == 1)
    result = await db.execute(q)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="Model not found")

    # Fetch related objects
    media_res = await db.execute(
        select(ModelMedia).where(ModelMedia.user_id == user.id).limit(1)
    )
    media = media_res.scalars().first()

    profile_res = await db.execute(
        select(ModelProfile).where(ModelProfile.user_id == user.id).limit(1)
    )
    profile = profile_res.scalars().first()

    professional_res = await db.execute(
        select(ModelProfessional).where(ModelProfessional.user_id == user.id).limit(1)
    )
    professional = professional_res.scalars().first()

    portfolio_res = await db.execute(
        select(ModelPortfolio).where(ModelPortfolio.user_id == user.id)
    )
    portfolio = portfolio_res.scalars().all()

    # SOCIAL LINKS
    social_links_res = await db.execute(
        select(UserSocialLink).where(UserSocialLink.user_id == user.id)
    )
    social_links = social_links_res.scalars().all()

    # =========================
    # ✅ IMAGES + VIDEO (FIXED)
    # =========================
    base_url = str(request.base_url).rstrip("/")

    # Parent media (for video)
    media_gallery_res = await db.execute(
        select(Image_Videos).where(Image_Videos.user_id == user.id)
    )
    media_gallery_db = media_gallery_res.scalars().first()

    images = []
    video = None
    profile_photo = None

    # Only fetch images if media_gallery exists
    if media_gallery_db:
        # Fetch images from ModelImages table
        images_res = await db.execute(
            select(ModelImages)
            .where(ModelImages.media_uuid == media_gallery_db.uuid)
            .order_by(ModelImages.image_index)
            .limit(5)
        )
        images_db = images_res.scalars().all()

        images = [
            f"{base_url}/{img.image_path}"
            for img in images_db
        ]

        # Set profile photo as first image
        profile_photo = images[0] if images else None

        # Set video if exists
        if media_gallery_db.video:
            video = f"{base_url}/{media_gallery_db.video}"

    return {
        "basic_info": {
            "uuid": str(user.uuid),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": f"{user.first_name} {user.last_name}",
            "profile_photo": profile_photo,
            "current_city": user.current_city,
            "age": user.age,
            "gender": user.gender,
            "nationality": user.nationality,
        },

        "profile": {
            "height": profile.height if profile else None,
            "weight": profile.weight if profile else None,
            "chest_bust": profile.chest_bust if profile else None,
            "waist": profile.waist if profile else None,
            "hips": profile.hips if profile else None,
            "shoulder": profile.shoulder if profile else None,
            "shoe_size": profile.shoe_size if profile else None,
            "complexion": profile.complexion if profile else None,
            "eye_color": profile.eye_color if profile else None,
            "hair_color": profile.hair_color if profile else None,
            "body_type": profile.body_type if profile else None,
            "hair_length": profile.hair_length if profile else None,
        },

        "professional": {
            "experience_details": professional.experience_details if professional else None,
            "skills": professional.skills if professional else [],
            "languages": professional.languages if professional else [],
            "interested_categories": professional.interested_categories if professional else [],
        },

        "media_gallery": {
            "images": images,  # max 5
            "video": video  # single
        },

        "social_links": [
            {
                "uuid": str(link.uuid),
                "platform": link.platform,
                "url": link.url,
            }
            for link in social_links
        ],

        "portfolio": [
            {
                "uuid": str(item.uuid),
                "media_type": item.media_type,
                "file_url": item.file_url
            }
            for item in portfolio
        ]
    }


# -----------------------------------
# 🏢 PUBLIC: LIST ALL APPROVED AGENCIES (WITH SERVICES + SOCIAL LINKS)
# -----------------------------------

@router.get("/agencies")
async def get_public_agencies(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    base_url = str(request.base_url).rstrip("/")

    stmt = (
        select(User, AgencyProfile)
        .join(AgencyProfile, AgencyProfile.user_id == User.id)
        .where(User.user_type == 2)
        .order_by(AgencyProfile.company_name.asc())
    )

    result = await db.execute(stmt)

    return [
        {
            "uuid": str(user.uuid),
            "company_name": profile.company_name,
            "contact_name": profile.contact_name,
            "phone": profile.phone,
            "website": profile.website,
            "tagline": profile.tagline,
            "services": profile.services,
            "social_links": profile.social_links,
            "logo": f"{base_url}/{profile.logo}" if profile.logo else None
        }
        for user, profile in result.all()
    ]


# 🎯 PUBLIC API – Save Contact Form
@router.post("/contact")
async def submit_contact(data: ContactCreate, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    """Submit contact form and send notification email"""
    saved = await create_contact(db, data)

    # Email subject + HTML body
    subject = f"New Contact Inquiry from {data.name}"
    body = f"""
        <h2>New Contact Form Submission</h2>
        <p><strong>Name:</strong> {data.name}</p>
        <p><strong>Email:</strong> {data.email}</p>
        <p><strong>Phone:</strong> {data.phone}</p>
        <p><strong>Subject:</strong> {data.subject}</p>
        <p><strong>Message:</strong> {data.message}</p>
        <br>
        <p><strong>UUID:</strong> {saved.uuid}</p>
    """

    # Send email in background
    background_tasks.add_task(
        send_email_sendgrid,
        subject,
        body,
        NOTIFY_USERS
    )

    return {
        "message": "Contact form submitted successfully",
        "id": saved.id,
        "uuid": saved.uuid
    }


# -------------------------------
# 📞 PUBLIC CONTACT BANNER
# -------------------------------
@router.get("/contact-banner")
async def get_public_contact_banner(db: AsyncSession = Depends(get_db)):
    """Get contact banner information"""
    q = select(ContactBanner).where(ContactBanner.is_delete == False)
    result = await db.execute(q)
    banner = result.scalars().all()
    return [
        {
             "title": b.banner_title,
            "description": b.banner_description,
            "contact_info_email": b.contact_info_email,
            "contact_info_phone": b.contact_info_phone,
            "contact_info_day": b.contact_info_day,
            "contact_info_time": b.contact_info_time
        }
        for b in banner
    ]


# -------------------------------
# 💼 PUBLIC JOB POSTINGS
# -------------------------------

from datetime import datetime
from fastapi import Request
from sqlalchemy import func
import os

def parse_job_media(request: Request, job):
    base = str(request.base_url).rstrip("/")

    return {
        "logo": f"{base}/{job.logo}" if getattr(job, "logo", None) else None
    }

def build_pay_string(job):
    if not job.pay_min and not job.pay_max:
        return None

    # 💰 Amount
    if job.pay_min and job.pay_max:
        amount = f"${job.pay_min:,.0f} – ${job.pay_max:,.0f}"
    elif job.pay_min:
        amount = f"From ${job.pay_min:,.0f}"
    else:
        amount = f"Up to ${job.pay_max:,.0f}"

    # 🧠 Unit mapping
    unit_map = {
        "per_day": "per day",
        "per_month": "per month",
        "per_year": "per year",
        "per_episode": "per episode",
        "per_movie": "per movie",
        "per_project": "per project"
    }

    unit = None
    if job.pay_unit:
        unit = unit_map.get(job.pay_unit.strip().lower())

    # ✅ FINAL STRING
    return f"{amount} {unit}".strip() if unit else amount

@router.get("/jobs")
async def get_all_jobs(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(JobPosting, AgencyProfile)
        .join(User, User.id == JobPosting.agency_id)
        .join(AgencyProfile, AgencyProfile.user_id == User.id)
        .where(
            JobPosting.is_delete == False,
            JobPosting.visibility == "public"
        )
        .order_by(JobPosting.id.desc())
    )

    result = await db.execute(stmt)
    rows = result.all()

    now = datetime.utcnow()
    base = str(request.base_url).rstrip("/")
    response = []

    for job, profile in rows:
        logo_path = job.logo or profile.logo
        logo = f"{base}/{logo_path.replace('\\', '/')}" if logo_path else None

        posted = None
        if job.date_from:
            days = (now - job.date_from).days
            posted = "Today" if days <= 0 else f"{days} days ago"

        response.append({
            "uuid": str(job.uuid),
            "job_role": job.job_role,
            "description": job.description,
            "project_type": job.project_type,
            "location": job.location,

            "logo": logo,

            "pay": build_pay_string(job),
            "pay_unit": job.pay_unit,

            "qualifications": job.qualifications,
            "required_skills": job.required_skills,

            "posted": posted,

            "agency": {
                "uuid": str(profile.uuid),
                "company_name": profile.company_name
            }
        })

    return response


# @router.get("/jobs")
# async def get_all_jobs(db: AsyncSession = Depends(get_db)):
#     stmt = (
#         select(JobPosting, AgencyProfile)
#         .join(User, User.id == JobPosting.agency_id)
#         .join(AgencyProfile, AgencyProfile.user_id == User.id)
#         .where(
#             JobPosting.is_delete == False,
#             JobPosting.visibility == "public"
#         )
#         .order_by(JobPosting.id.desc())
#     )
#
#     result = await db.execute(stmt)
#     rows = result.all()
#
#     now = datetime.utcnow()
#     response = []
#
#     for job, profile in rows:
#         logo_path = job.logo or profile.logo
#         logo = logo_path.replace("\\", "/") if logo_path else None
#
#         posted = None
#         if job.date_from:
#             days = (now - job.date_from).days
#             posted = "Today" if days <= 0 else f"{days} days ago"
#
#         response.append({
#             "uuid": str(job.uuid),
#             "job_role": job.job_role,
#             "description": job.description,
#             "project_type": job.project_type,
#             "location": job.location,
#             "logo": logo,
#
#             # 🔥 PAY DISPLAY
#             "pay": build_pay_string(job),
#             "pay_unit": job.pay_unit,
#
#             "qualifications": job.qualifications,
#             "required_skills": job.required_skills,
#
#             "posted": posted,
#
#             "agency": {
#                 "uuid": str(profile.uuid),
#                 "company_name": profile.company_name
#             }
#         })
#
#     return response



#====================
# get public profile
#====================
@router.get("/profile/{token:path}")
async def get_public_profile_by_token(
    token: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    from core.aes_encryption import aes_decrypt
    from urllib.parse import unquote

    # ---------------- TOKEN DECRYPT ----------------
    try:
        safe_token = unquote(token)
        decrypted_token = aes_decrypt(safe_token)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid token")

    # ---------------- USER ----------------
    user = await db.scalar(
        select(User).where(User.share_token == decrypted_token)
    )

    if not user:
        raise HTTPException(status_code=404, detail="Invalid or expired link")

    # ---------------- FETCH RELATED DATA ----------------
    profile = await db.scalar(
        select(ModelProfile).where(ModelProfile.user_id == user.id)
    )

    professional = await db.scalar(
        select(ModelProfessional).where(ModelProfessional.user_id == user.id)
    )

    portfolio = (
        await db.execute(
            select(ModelPortfolio).where(ModelPortfolio.user_id == user.id)
        )
    ).scalars().all()

    social_link = await db.scalar(
        select(UserSocialLink).where(UserSocialLink.user_id == user.id)
    )

    # ---------------- MEDIA ----------------
    base_url = str(request.base_url).rstrip("/")

    media_gallery = await db.scalar(
        select(Image_Videos).where(Image_Videos.user_id == user.id)
    )

    images = []
    video = None
    profile_photo = None

    if media_gallery:
        images_db = (
            await db.execute(
                select(ModelImages)
                .where(ModelImages.media_uuid == media_gallery.uuid)
                .order_by(ModelImages.image_index)
                .limit(5)
            )
        ).scalars().all()

        images = [f"{base_url}/{img.image_path}" for img in images_db]
        profile_photo = images[0] if images else None

        if media_gallery.video:
            video = f"{base_url}/{media_gallery.video}"

    # ---------------- RESPONSE ----------------
    return {
        "basic_info": {
            "uuid": str(user.uuid),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": f"{user.first_name} {user.last_name}",
            "profile_photo": profile_photo,
            "current_city": user.current_city,
            "age": user.age,
            "gender": user.gender,
            "nationality": user.nationality,
            "profile_visible": True,
        },

        "profile": {
            "height": profile.height if profile else None,
            "weight": profile.weight if profile else None,
            "chest_bust": profile.chest_bust if profile else None,
            "waist": profile.waist if profile else None,
            "hips": profile.hips if profile else None,
            "shoulder": profile.shoulder if profile else None,
            "shoe_size": profile.shoe_size if profile else None,
            "complexion": profile.complexion if profile else None,
            "eye_color": profile.eye_color if profile else None,
            "hair_color": profile.hair_color if profile else None,
            "body_type": profile.body_type if profile else None,
            "hair_length": profile.hair_length if profile else None,
        },

        "professional": {
            "experience_details": professional.experience_details if professional else None,
            "skills": professional.skills if professional else [],
            "languages": professional.languages if professional else [],
            "interested_categories": professional.interested_categories if professional else [],
        },

        "media_gallery": {
            "images": images,
            "video": video,
        },

        # ✅ FIXED SOCIAL LINKS (NO platform/url)
        "social_links": {
            "x": social_link.x if social_link else None,
            "instagram": social_link.instagram if social_link else None,
            "tiktok": social_link.tiktok if social_link else None,
            "snapchat": social_link.snapchat if social_link else None,
            "pinterest": social_link.pinterest if social_link else None,
            "linkedin": social_link.linkedin if social_link else None,
            "youtube": social_link.youtube if social_link else None,
        },

        "portfolio": [
            {
                "uuid": str(item.uuid),
                "media_type": item.media_type,
                "file_url": item.file_url,
            }
            for item in portfolio
        ],
    }

