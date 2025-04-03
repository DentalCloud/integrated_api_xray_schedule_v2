# 放置位置：xray_classifier.py（專案根目錄）

import torch
from PIL import Image
from torchvision import transforms
from utils import restore_model_from_b64

LABELS = ["xray", "intraoral", "others"]

def classify_image(image_path: str) -> str:
    restore_model_from_b64()

    image = Image.open(image_path).convert("RGB")
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor()
    ])
    input_tensor = transform(image).unsqueeze(0)  # shape: [1, 3, 224, 224]

    with torch.no_grad():
        output = model(input_tensor)
        predicted = torch.argmax(output, dim=1).item()
        label = LABELS[predicted]

    return label
