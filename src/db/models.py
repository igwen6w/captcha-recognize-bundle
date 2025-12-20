import os
from datetime import datetime
from pathlib import Path

from sqlalchemy import Column, DateTime, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 数据库文件路径
DB_DIR = Path("data")
DB_DIR.mkdir(exist_ok=True)
DB_PATH = DB_DIR / "apikeys.db"

# 创建数据库引擎
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()


class APIKey(Base):
    """API Key 数据模型"""
    __tablename__ = "apikeys"

    key = Column(String(64), primary_key=True, index=True)
    name = Column(String(255), nullable=True)  # 可选的名称/描述
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_used_at = Column(DateTime, nullable=True)

    def to_dict(self):
        """转换为字典"""
        return {
            "key": self.key,
            "name": self.name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
        }


class Admin(Base):
    """管理员用户数据模型"""
    __tablename__ = "admins"

    username = Column(String(50), primary_key=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)

    def to_dict(self):
        """转换为字典（不包含密码）"""
        return {
            "username": self.username,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
        }


def init_db():
    """初始化数据库，创建表"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

