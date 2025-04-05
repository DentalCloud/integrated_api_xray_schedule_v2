import os
import io
import base64
import torch
from torchvision import models, transforms
from PIL import Image
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

_model = None  # 全域模型快取

def get_model():
    global _model
    if _model is None:
        restore_model_from_b64()
    return _model

def restore_model_from_b64():
    global _model
    if _model is not None:
        return

    with open("xray_classifier.pt.b64", "r") as f:
        b64data = f.read()

    buffer = io.BytesIO(base64.b64decode(b64data))
    state_dict = torch.load(buffer, map_location=torch.device("cpu"))

    model = models.mobilenet_v2(weights=None)
    model.classifier[1] = torch.nn.Linear(model.last_channel, 3)  # 修正分類輸出
    model.load_state_dict(state_dict)
    model.eval()
    _model = model

def classify_image(image_path):
    model = get_model()

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
    ])

    image = Image.open(image_path).convert("RGB")
    input_tensor = transform(image).unsqueeze(0)

    with torch.no_grad():
        outputs = model(input_tensor)
        predicted = torch.argmax(outputs, dim=1).item()

    labels = ["xray", "intraoral", "others"]
    return labels[predicted]

def save_temp_image(message_id):
    from linebot import LineBotApi
    line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))

    message_content = line_bot_api.get_message_content(message_id)
    temp_path = f"temp_{message_id}.jpg"
    with open(temp_path, "wb") as f:
        for chunk in message_content.iter_content():
            f.write(chunk)
    return temp_path

def upload_image_to_drive(image_path, label):
    folder_id = os.getenv(f"FOLDER_ID_{label.upper()}")
    creds = Credentials.from_service_account_file("credentials.json")
    service = build("drive", "v3", credentials=creds)

    file_metadata = {"name": os.path.basename(image_path), "parents": [folder_id]}
    media = MediaFileUpload(image_path, mimetype="image/jpeg")

    service.files().create(body=file_metadata, media_body=media, fields="id").execute()
