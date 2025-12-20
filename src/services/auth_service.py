from datetime import datetime

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.db.models import Admin

# 密码加密上下文
pwd_context = CryptContext(schemes=["sha256_crypt"])


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    return pwd_context.hash(password)


def get_admin(db: Session, username: str) -> Admin | None:
    """获取管理员用户"""
    return db.query(Admin).filter(Admin.username == username).first()


def authenticate_admin(db: Session, username: str, password: str) -> Admin | None:
    """验证管理员用户名和密码"""
    admin = get_admin(db, username)
    if not admin:
        return None
    if not verify_password(password, admin.hashed_password):
        return None
    # 更新最后登录时间
    admin.last_login_at = datetime.utcnow()
    db.commit()
    return admin


def create_admin(db: Session, username: str, password: str) -> Admin:
    """创建管理员用户"""
    hashed_password = get_password_hash(password)
    admin = Admin(
        username=username,
        hashed_password=hashed_password,
        created_at=datetime.utcnow()
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin

