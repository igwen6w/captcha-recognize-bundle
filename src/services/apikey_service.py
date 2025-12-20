import secrets
from datetime import datetime

from sqlalchemy.orm import Session

from src.db.models import APIKey


def generate_apikey() -> str:
    """生成新的 API key"""
    # 生成 32 字节的随机 token，转换为 URL 安全的 base64 字符串
    return secrets.token_urlsafe(32)


def create_apikey(db: Session, name: str = None) -> APIKey:
    """创建新的 API key"""
    key = generate_apikey()
    apikey = APIKey(key=key, name=name, created_at=datetime.utcnow())
    db.add(apikey)
    db.commit()
    db.refresh(apikey)
    return apikey


def delete_apikey(db: Session, key: str) -> bool:
    """删除 API key"""
    apikey = db.query(APIKey).filter(APIKey.key == key).first()
    if not apikey:
        return False
    db.delete(apikey)
    db.commit()
    return True


def get_apikey(db: Session, key: str) -> APIKey | None:
    """获取 API key"""
    return db.query(APIKey).filter(APIKey.key == key).first()


def list_apikeys(db: Session) -> list[APIKey]:
    """列出所有 API keys"""
    return db.query(APIKey).order_by(APIKey.created_at.desc()).all()


def update_last_used(db: Session, key: str):
    """更新 API key 的最后使用时间"""
    apikey = db.query(APIKey).filter(APIKey.key == key).first()
    if apikey:
        apikey.last_used_at = datetime.utcnow()
        db.commit()

