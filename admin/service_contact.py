from sqlalchemy.orm import Session
from models import Contact
from admin.schema_contact import ContactCreate

async def create_contact(db: Session, data: ContactCreate):
    new_contact = Contact(
        name=data.name,
        email=data.email,
        phone=data.phone,
        subject=data.subject,
        message=data.message
    )
    db.add(new_contact)
    await db.commit()
    await db.refresh(new_contact)
    return new_contact
