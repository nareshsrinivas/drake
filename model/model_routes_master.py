# model/model_routes_master.py

from fastapi import APIRouter

from model.routes import router as user_router
from model.model_profile_routes import router as profile_router
from model.model_professional_routes import router as professional_router
from model.model_media_routes import router as media_router
from model.model_portfolio_routes import router as portfolio_router


from model.model_images_routes import router as images_routes
from model.model_filters_routes import router as filter_router
from model.model_info import router as model_info_router
# from model.model_video_routes import router as video_router
from model.model_images_routes import router as model_images_router
from model.model_videos_routes import router as model_videos_router
from model.model_social_link_routes import router as social_links_router
# from model.model_profile_progress_routes import router as profile_progress_router
from model.progress_routes import router as progress_router
from model.model_share_profile_routes import router as share_profile_router


router = APIRouter(prefix="/model", tags=["Model"])

router.include_router(share_profile_router)

router.include_router(user_router)
router.include_router(profile_router)
router.include_router(professional_router)
router.include_router(media_router)
router.include_router(portfolio_router)

# router.include_router(images_routes)
# router.include_router(video_router)
router.include_router(model_images_router)
router.include_router(model_videos_router)

router.include_router(filter_router)
router.include_router(model_info_router)
router.include_router(social_links_router)
# router.include_router(profile_progress_router)
router.include_router(progress_router)




