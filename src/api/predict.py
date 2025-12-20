import os
import tempfile

import torch
from fastapi import Depends, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image

from src.api.auth import verify_apikey
from src.db.models import APIKey

# 最大文件大小：10KB
MAX_FILE_SIZE = 10 * 1024  # 10KB in bytes

# 全局变量存储模型，避免每次请求都加载
MODEL_CACHE = None
DEVICE_CACHE = None
TRANSFORM_CACHE = None


def set_model_cache(model, device, transform):
    """设置模型缓存"""
    global MODEL_CACHE, DEVICE_CACHE, TRANSFORM_CACHE
    MODEL_CACHE = model
    DEVICE_CACHE = device
    TRANSFORM_CACHE = transform


async def predict_captcha(
    file: UploadFile = File(...),
    apikey: APIKey = Depends(verify_apikey)
):
    """
    接收验证码图片，返回解析结果（需要 API Key 鉴权）

    - **file**: 上传的验证码图片文件（小于10KB）
    - **X-API-Key**: 请求头中的 API Key（必需）
    """
    # 验证文件类型
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="文件必须是图片格式")

    # 创建临时文件
    temp_file = None
    try:
        # 读取文件内容并检查大小
        contents = await file.read()
        file_size = len(contents)

        # 验证文件大小
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"文件大小超过限制：{file_size} bytes > {MAX_FILE_SIZE} bytes (10KB)"
            )

        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            temp_file = tmp.name
            tmp.write(contents)

        # 使用缓存的模型进行预测
        img = Image.open(temp_file).convert("L")
        x = TRANSFORM_CACHE(img).unsqueeze(0).to(DEVICE_CACHE)

        with torch.no_grad():
            logits = MODEL_CACHE(x)
            probs = torch.softmax(logits, dim=-1)
            preds = probs.argmax(dim=-1).squeeze(0)

        result = "".join(str(int(d)) for d in preds)

        return JSONResponse(content={
            "success": True,
            "captcha": result,
            "file_size": file_size
        })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理图片时出错: {str(e)}")

    finally:
        # 删除临时文件
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
            except Exception as e:
                print(f"删除临时文件失败: {e}")

