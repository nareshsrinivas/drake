from sqlalchemy.orm import Session
from models import ModelPortfolio

def upload_portfolio(db: Session, user_id: int, media_type: str, url: str):
    item = ModelPortfolio(
        user_id=user_id,
        media_type=media_type,
        file_url=url
    )

    db.add(item)
    db.commit()
    db.refresh(item)
    return item

def list_portfolio(db: Session, user_id: int):
    return db.query(ModelPortfolio).filter_by(user_id=user_id).all()

def get_portfolio(db: Session, uuid: str):
    return db.query(ModelPortfolio).filter_by(uuid=uuid).first()

def delete_portfolio(db: Session, uuid: str, user_id: int):
    item = db.query(ModelPortfolio).filter_by(uuid=uuid).first()
    if not item: return None
    if item.user_id != user_id: return "unauthorized"

    db.delete(item)
    db.commit()
    return True
