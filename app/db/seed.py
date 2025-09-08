from sqlalchemy.orm import Session
from app.db.models.user import User, UserRole
from app.core.config import settings
from app.core.security import hash_password

def seed_admin(db: Session) -> None:
    existing = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
    if not existing:
        admin = User(
            name="Admin",
            email=settings.ADMIN_EMAIL,
            password_hash=hash_password(settings.ADMIN_PASSWORD),
            role=UserRole.admin,
        )
        db.add(admin)
        db.commit()
