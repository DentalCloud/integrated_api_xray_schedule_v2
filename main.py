from flask import Flask, request
import os
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, ImageMessage
from schedule_parser import parse_schedule_text
from sheets_writer import write_schedule_to_sheet
from xray_classifier import classify_image
from utils import save_temp_image, upload_image_to_drive, restore_model_from_b64
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
restore_model_from_b64()

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except Exception as e:
        return str(e), 400
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    schedule_text = event.message.text
    rows = parse_schedule_text(schedule_text)
    if rows:
        write_schedule_to_sheet(rows)

@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    message_id = event.message.id
    image_path = save_temp_image(message_id)
    label = classify_image(image_path)
    upload_image_to_drive(image_path, label)

@app.route("/", methods=["GET"])
def index():
    return "✅ DentalCloud API is running."

@app.route("/health", methods=["GET"])
def health():
    return "ok"

# ✅ 修正：綁定 Render 所指定的 PORT
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
