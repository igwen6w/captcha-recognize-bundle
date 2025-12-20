from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session

from src.db.models import APIKey, get_db
from src.services.apikey_service import get_apikey, update_last_used


async def verify_apikey(
    x_api_key: str = Header(..., alias="X-API-Key", description="API Key"),
    db: Session = Depends(get_db)
) -> APIKey:
    """
    验证 API key 是否有效
    
    - **X-API-Key**: 从请求头获取的 API key（必需）
    """
    apikey = get_apikey(db, x_api_key)
    if not apikey:
        raise HTTPException(
            status_code=401,
            detail="无效的 API Key"
        )
    
    # 更新最后使用时间
    update_last_used(db, x_api_key)
    
    return apikey

