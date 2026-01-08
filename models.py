import uuid
from sqlalchemy import Column, Integer, Enum, JSON, Numeric, Float, String, Date, ForeignKey, Table, UniqueConstraint, \
    Text, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from database import Base
import enum
from sqlalchemy.dialects.postgresql import JSONB, ARRAY


# -------------------------
# ENUMS
# -------------------------
class ExperienceLevelEnum(enum.Enum):
    beginner = "Beginner"
    intermediate = "Intermediate"
    professional = "Professional"
    expert = "Expert"


# -------------------------
# USER MODEL
# -------------------------
class User(Base):
    __tablename__ = "users"

    __table_args__ = (
        UniqueConstraint('email', name='uq_users_email'),
        UniqueConstraint('phone', name='uq_users_phone'),
    )

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)

    share_token = Column(String, unique=True, nullable=True, index=True)
    user_type = Column(Integer, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    country_code = Column(String, nullable=False)
    phone = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    dob = Column(Date, nullable=False)
    age = Column(Integer, nullable=False)

    # 🔥 New Fields (NULL allowed)
    gender = Column(String, nullable=True)
    current_city = Column(String, nullable=True)
    nationality = Column(String, nullable=True)
    home_town = Column(String, nullable=True)

    approved = Column(Boolean, default=False)
    job_postings = relationship("JobPosting", back_populates="agency")


class ModelProfile(Base):
    __tablename__ = "model_profile"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    height = Column(String(100), nullable=True)
    weight = Column(String(100), nullable=True)
    chest_bust = Column(String(100), nullable=True)
    waist = Column(String(100), nullable=True)
    hips = Column(String(100), nullable=True)
    shoulder = Column(String(100), nullable=True)
    shoe_size = Column(String(100), nullable=True)
    complexion = Column(String(255), nullable=True)
    eye_color = Column(String(255), nullable=True)
    hair_color = Column(String(255), nullable=True)
    tattoos_piercings = Column(Boolean, default=False)
    tattoos_details = Column(String(255), nullable=True)
    suit_jacket_dress_size = Column(String(100), nullable=True)
    hair_length = Column(String(255), nullable=True)
    body_type = Column(String(255), nullable=True)
    body_shape = Column(String(255), nullable=True)
    facial_hair = Column(String(255), nullable=True)
    bust_cup_size = Column(String(100), nullable=True)
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class ModelProfessional(Base):
    __tablename__ = "model_professional"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    professional_experience = Column(Boolean, default=False)
    experience_details = Column(String(255), nullable=True)
    languages = Column(ARRAY(String), nullable=True)
    skills = Column(ARRAY(String), nullable=True)
    interested_categories = Column(ARRAY(String), nullable=True)
    willing_to_travel = Column(Boolean, default=False)
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class ModelMedia(Base):
    __tablename__ = "model_media"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    full_body_front = Column(String, nullable=True)
    full_body_left_side = Column(String, nullable=True)
    full_body_right_side = Column(String, nullable=True)
    head_shot = Column(String, nullable=True)
    profile_photo = Column(String, nullable=True)
    introduction_video = Column(String, nullable=True)
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class ModelPortfolio(Base):
    __tablename__ = "model_protfolio"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    media_type = Column(String, nullable=False)  # "photo" or "video"
    file_url = Column(String, nullable=False)

    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class UserSocialLink(Base):
    __tablename__ = "user_social_links"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    x = Column(String, nullable=True)
    instagram = Column(String, nullable=True)
    tiktok = Column(String, nullable=True)
    snapchat = Column(String, nullable=True)
    pinterest = Column(String, nullable=True)
    linkedin = Column(String, nullable=True)
    youtube = Column(String, nullable=True)
    facebook = Column(String, nullable=True)


class AgencyProfile(Base):
    __tablename__ = "agency_profile"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    company_name = Column(String(255), nullable=False)
    contact_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    website = Column(String(255), nullable=True)
    address = Column(String(500), nullable=True)

    # ⭐ NEW FIELDS
    logo = Column(String(255), nullable=True)  # Agency Logo
    tagline = Column(String(255), nullable=True)  # Small tagline
    about = Column(Text, nullable=True)  # Agency description

    # Multiple Services (Stored as JSON ARRAY)
    services = Column(JSON, nullable=True)  # e.g. ["Model Casting", "Portfolio Shoot"]

    # Social Links (JSON)
    social_links = Column(JSON, nullable=True)
    # Example:
    # {
    #   "facebook": "https://fb.com/star",
    #   "instagram": "https://instagram.com/star",
    #   "youtube": "https://youtube.com/star",
    #   "linkedin": "https://linkedin.com/star"
    # }

    verified = Column(Boolean, default=False)

    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    username = Column(String(50), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    role = Column(String(20), default="admin")


class HomeSlider(Base):
    __tablename__ = "home_slider"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    image = Column(String(1024), nullable=True)
    slider_title = Column(String(255), nullable=True)
    slider_type = Column(Integer, nullable=False, default=0)
    is_order = Column(Integer, nullable=True, default=0)
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_delete = Column(Boolean, default=False)


class WorkType(Base):
    __tablename__ = "work_type"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    work_type = Column(String(255), nullable=False)
    is_order = Column(Integer, nullable=True, default=0)
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_delete = Column(Boolean, default=False)


class Skill(Base):
    __tablename__ = "skill"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    other_title = Column(String(255), nullable=True)
    is_order = Column(Integer, nullable=True, default=0)
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_delete = Column(Boolean, default=False)


class Contact(Base):
    __tablename__ = "contact"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String(150), nullable=False)
    email = Column(String(200), nullable=False, index=True)
    phone = Column(String(200), nullable=False)
    subject = Column(String(250), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())


class ContactBanner(Base):
    __tablename__ = "contact_banner"
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    banner_title = Column(String(255), nullable=False)
    banner_description = Column(Text, nullable=False)
    banner_image = Column(String(500), nullable=False)
    contact_info_email = Column(String(150), nullable=False)
    contact_info_phone = Column(String(150), nullable=False)
    contact_info_day = Column(String(250), nullable=False)
    contact_info_time = Column(String(150), nullable=False)
    contact_form_image = Column(String(500), nullable=False)
    contact_form_title = Column(String(100), nullable=False)
    contact_form_small_desc = Column(String(150), nullable=False)
    created_by = Column(Integer, ForeignKey('admin_users.id'))
    updated_by = Column(Integer, ForeignKey('admin_users.id'))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_delete = Column(Boolean, default=False)


class JobPosting(Base):
    __tablename__ = "job_posting"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)

    agency_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    agency = relationship("User", back_populates="job_postings")

    job_role = Column(String(255), nullable=False)
    description = Column(Text)
    project_type = Column(String(100))
    logo = Column(String(255), nullable=True)

    gender = Column(String(30), default="any")
    location = Column(String(255))

    pay_min = Column(Float)
    pay_max = Column(Float)
    pay_type = Column(String(50))
    pay_unit = Column(String(50), nullable=True)
    is_paid = Column(Boolean, default=True)

    qualifications = Column(Text, nullable=True)
    required_skills = Column(String(500), nullable=True)

    # 🔥 NAIVE DATETIMES ONLY
    date_from = Column(DateTime, nullable=True)
    date_to = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    deadline = Column(DateTime, nullable=True)

    requirements = Column(JSON)

    status = Column(String(50), default="open")
    visibility = Column(String(50), default="public")

    created_by = Column(Integer)
    updated_by = Column(Integer)

    is_delete = Column(Boolean, default=False)


class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)

    job_id = Column(Integer, ForeignKey("job_posting.id", ondelete="CASCADE"), nullable=False)
    model_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    status = Column(String(50), default="applied")  # applied / shortlisted / rejected / hired
    admin_notes = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    is_delete = Column(Boolean, default=False)

    # relationships
    job = relationship("JobPosting", backref="applications")
    model = relationship("User")

# -------------------------
# model filters
# -------------------------
class ModelFilter(Base):
    __tablename__ = "model_filters"

    id = Column(Integer, primary_key=True, index=True)
    gender = Column(String, index=True)
    height_min = Column(Float)
    height_max = Column(Float)
    eye_color = Column(String)
    hair_color = Column(String)
    age_range_min = Column(Integer)
    age_range_max = Column(Integer)
    body_type = Column(String)
    skin_tone = Column(String)
    availability = Column(JSON)


# -------------------------
# model_images_video
# -------------------------

class Image_Videos(Base):
    __tablename__ = "model_video"

    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)

    user_id = Column(Integer, index=True, nullable=False)

    video = Column(String, nullable=True)  # single video only
    video_url = Column(String, nullable=True)  # add video url

    created_at = Column(DateTime, server_default=func.now())


# ---- video child table
class ModelVideos(Base):
    __tablename__ = "model_videos"

    id = Column(Integer, primary_key=True)
    media_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey("model_video.uuid", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    video_index = Column(Integer, nullable=False)  # 0–1
    video_path = Column(String, nullable=False)

    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("media_uuid", "video_index"),
    )


class ModelImages(Base):
    __tablename__ = "model_images"

    id = Column(Integer, primary_key=True)  # INTERNAL ONLY
    media_uuid = Column(
        UUID(as_uuid=True),
        # ForeignKey("model_images_video.uuid", ondelete="CASCADE"),
        ForeignKey("model_video.uuid", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    image_index = Column(Integer, nullable=False)  # 0–4 / 0–9
    image_path = Column(String, nullable=False)

    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("media_uuid", "image_index"),
    )


# -------------------------
# model_profile_progress
# -------------------------
class ProfileStep(str, Enum):
    model_profile = "model_profile"
    model_professional = "model_professional"
    ModelImages = "model_images"
    Image_Videos = "model_video"
    user_social_links = "user_social_links"
    status = "true_or_false"
