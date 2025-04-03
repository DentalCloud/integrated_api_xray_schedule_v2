# 放置位置：utils.py（專案根目錄）

import os
import base64
import requests
from PIL import Image
from io import BytesIO
import torch
from torchvision import transforms, models
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
X_FOLDER_ID = os.getenv("X_FOLDER_ID")
INTRAORAL_FOLDER_ID = os.getenv("INTRAORAL_FOLDER_ID")
OTHERS_FOLDER_ID = os.getenv("OTHERS_FOLDER_ID")

model = None

def restore_model_from_b64():
    global model
    if model is not None:
        return

    with open("xray_classifier.pt.b64", "rb") as f:
        b64_data = f.read()
    binary_data = base64.b64decode(b64_data)
    with open("xray_classifier.pt", "wb") as f:
        f.write(binary_data)

    # 還原 MobileNetV2 架構
    model_base = models.mobilenet_v2(pretrained=False)
    model_base.classifier[1] = torch.nn.Linear(model_base.last_channel, 3)

    # 載入 state_dict 權重
    model_base.load_state_dict(torch.load("xray_classifier.pt", map_location=torch.device("cpu")))
    model_base.eval()
    model = model_base

def save_temp_image(message_id: str) -> str:
    headers = {"Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"}
    url = f"https://api-data.line.me/v2/bot/message/{message_id}/content"
    response = requests.get(url, headers=headers)

    image_path = f"/tmp/{message_id}.jpg"
    with open(image_path, "wb") as f:
        f.write(response.content)
    return image_path

def download_line_image(message_id: str) -> Image.Image:
    headers = {"Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"}
    url = f"https://api-data.line.me/v2/bot/message/{message_id}/content"
    response = requests.get(url, headers=headers)
    return Image.open(BytesIO(response.content)).convert("RGB")

def upload_image_to_drive(image_path: str, label: str) -> None:
    folder_map = {
        "xray": X_FOLDER_ID,
        "intraoral": INTRAORAL_FOLDER_ID,
        "others": OTHERS_FOLDER_ID
    }
    folder_id = folder_map.get(label, OTHERS_FOLDER_ID)

    creds = Credentials.from_service_account_file("credentials.json")
    service = build("drive", "v3", credentials=creds)

    file_metadata = {
        "name": os.path.basename(image_path),
        "parents": [folder_id]
    }
    media = MediaFileUpload(image_path, mimetype="image/jpeg")
    service.files().create(body=file_metadata, media_body=media).execute()
