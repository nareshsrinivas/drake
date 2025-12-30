from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from utils.file_upload import save_file
from core.deps import get_current_user, get_db
import json
from model.model_portfolio_schema import PortfolioCreate
from model.model_portfolio_service import upload_portfolio, list_portfolio, get_portfolio, delete_portfolio

router = APIRouter(prefix="/portfolio", tags=["Model Portfolio"])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload(media_type: str, file: UploadFile = File(...), db: Session = Depends(get_db), user=Depends(get_current_user)):

    if media_type not in ["photo", "video"]:
        raise HTTPException(400, "Invalid media_type")

    url = await save_file(file,"portfolio")

    #social = json.loads(social_links) if social_links else None

    item = upload_portfolio(db, user.id, media_type, url)
    return item

@router.get("/")
def all(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return list_portfolio(db, user.id)

@router.get("/{uuid}")
def get_item(uuid: str, db: Session = Depends(get_db)):
    item = get_portfolio(db, uuid)
    if not item:
        raise HTTPException(404, "Not found")
    return item

@router.delete("/{uuid}")
def delete_item(uuid: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    result = delete_portfolio(db, uuid, user.id)
    if result == "unauthorized":
        raise HTTPException(403, "Not allowed")
    if not result:
        raise HTTPException(404, "Not found")
    return {"message": "Deleted"}