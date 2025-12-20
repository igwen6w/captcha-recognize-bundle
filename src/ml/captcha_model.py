from pathlib import Path

from PIL import Image

import torch
import torch.nn as nn
import torchvision.transforms as T


NUM_DIGITS = 4
NUM_CLASSES = 10

# 训练参数
IMAGE_HEIGHT = 60
IMAGE_WIDTH = 160


class SimpleCaptchaCNN(nn.Module):
    """1500 4 位数字验证码 CNN 模型"""

    def __init__(self):
        super().__init__()
        self.feature_extractor = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=3, padding=1),
            nn.BatchNorm2d(16),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),

            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),

            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
        )

        feat_h = IMAGE_HEIGHT // 8
        feat_w = IMAGE_WIDTH // 8
        feat_dim = 64 * feat_h * feat_w

        self.classifier = nn.Sequential(
            nn.Linear(feat_dim, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.4),
            nn.Linear(256, NUM_DIGITS * NUM_CLASSES),
        )

    def forward(self, x):
        feat = self.feature_extractor(x)
        feat = feat.view(feat.size(0), -1)
        logits = self.classifier(feat)  # (B, 4*10)
        logits = logits.view(-1, NUM_DIGITS, NUM_CLASSES)  # (B, 4, 10)
        return logits


def _build_transform():
    return T.Compose(
        [
            T.Resize((IMAGE_HEIGHT, IMAGE_WIDTH)),
            T.ToTensor(),
            T.Normalize(mean=[0.5], std=[0.5]),
        ]
    )


def load_captcha_model(model_path: str = "resources/captcha_cnn.pth"):
    """
    加载训练好的验证码模型，返回 (model, device, transform)。
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = SimpleCaptchaCNN().to(device)
    # 这里直接使用传入的路径，相对于"当前工作目录"来查找模型文件
    state_dict = torch.load(model_path, map_location=device)
    model.load_state_dict(state_dict)
    model.eval()

    transform = _build_transform()
    return model, device, transform


def predict_captcha_image(
    img_path: str,
    model_path: str = "resources/captcha_cnn.pth",
) -> str:
    """
    对单张验证码图片进行预测，返回 4 位数字字符串。
    """
    model, device, transform = load_captcha_model(model_path)

    img = Image.open(img_path).convert("L")
    x = transform(img).unsqueeze(0).to(device)  # (1,1,H,W)

    with torch.no_grad():
        logits = model(x)  # (1,4,10)
        probs = torch.softmax(logits, dim=-1)  # (1,4,10)
        preds = probs.argmax(dim=-1).squeeze(0)  # (4,)

    digits = "".join(str(int(d)) for d in preds)
    return digits

