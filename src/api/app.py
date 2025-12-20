from fastapi import FastAPI

from src.api.admin import router as admin_router
from src.api.predict import predict_captcha, set_model_cache
from src.db.models import init_db
from src.ml.captcha_model import load_captcha_model


def create_app(model_path: str = "resources/captcha_cnn.pth") -> FastAPI:
    """创建并配置 FastAPI 应用"""
    app = FastAPI(title="验证码识别API")
    
    # 注册管理员路由
    app.include_router(admin_router)
    
    # 注册预测路由
    app.post("/predict")(predict_captcha)

    @app.on_event("startup")
    async def startup():
        """应用启动时初始化"""
        # 初始化数据库
        init_db()
        print("数据库已初始化")
        
        # 加载模型
        model, device, transform = load_captcha_model(model_path)
        set_model_cache(model, device, transform)
        print(f"模型已加载，使用设备: {device}")

    @app.get("/")
    async def root():
        """根路径，返回API信息"""
        return {
            "message": "验证码识别API",
            "endpoints": {
                "/predict": "POST - 上传验证码图片进行识别（需要 API Key 鉴权）",
                "/admin/login": "POST - 管理员登录",
                "/admin/apikeys": "GET - 列出所有 API keys（需要 JWT 鉴权）",
                "/admin/apikeys/create": "POST - 创建新的 API key（需要 JWT 鉴权）",
                "/admin/apikeys/delete": "POST - 删除 API key（需要 JWT 鉴权）",
                "/docs": "GET - API文档"
            }
        }

    return app

