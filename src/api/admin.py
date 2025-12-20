from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.db.models import Admin, get_db
from src.services.apikey_service import create_apikey, delete_apikey, list_apikeys
from src.services.auth_service import authenticate_admin, create_admin, get_admin
from src.utils.jwt_utils import create_access_token, verify_token

router = APIRouter(prefix="/admin", tags=["admin"])
security = HTTPBearer()


# Pydantic 模型
class LoginRequest(BaseModel):
    username: str
    password: str


class CreateAPIKeyRequest(BaseModel):
    name: str | None = None


class DeleteAPIKeyRequest(BaseModel):
    key: str


class CreateAdminRequest(BaseModel):
    username: str
    password: str


# JWT 鉴权依赖
async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """验证 JWT token 并返回当前管理员"""
    token = credentials.credentials
    payload = verify_token(token)
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="无效的 token")
    
    admin = get_admin(db, username)
    if admin is None:
        raise HTTPException(status_code=401, detail="用户不存在")
    return admin


# 登录端点（不需要鉴权）
@router.post("/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """管理员登录"""
    admin = authenticate_admin(db, request.username, request.password)
    if not admin:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    access_token = create_access_token(data={"sub": admin.username})
    return {
        "success": True,
        "access_token": access_token,
        "token_type": "bearer",
        "username": admin.username
    }


# 创建管理员端点（首次使用时需要，后续可以移除或添加额外保护）
@router.post("/create-admin")
async def create_admin_user(
    request: CreateAdminRequest,
    db: Session = Depends(get_db)
):
    """创建管理员用户（首次设置）"""
    existing = get_admin(db, request.username)
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    admin = create_admin(db, request.username, request.password)
    return {
        "success": True,
        "message": "管理员创建成功",
        "username": admin.username
    }


# 需要鉴权的管理员端点
@router.get("/apikeys")
async def list_all_apikeys(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """列出所有 API keys（需要管理员权限）"""
    apikeys = list_apikeys(db)
    return {
        "success": True,
        "count": len(apikeys),
        "apikeys": [apikey.to_dict() for apikey in apikeys]
    }


@router.post("/apikeys/create")
async def create_new_apikey(
    request: CreateAPIKeyRequest,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """创建新的 API key（需要管理员权限）"""
    try:
        apikey = create_apikey(db, name=request.name)
        return {
            "success": True,
            "message": "API key 创建成功",
            "apikey": apikey.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建 API key 失败: {str(e)}")


@router.post("/apikeys/delete")
async def remove_apikey(
    request: DeleteAPIKeyRequest,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """删除 API key（需要管理员权限）"""
    success = delete_apikey(db, request.key)
    if not success:
        raise HTTPException(status_code=404, detail="API key 不存在")
    return {
        "success": True,
        "message": "API key 已删除"
    }

