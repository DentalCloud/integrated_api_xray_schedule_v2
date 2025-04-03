# 放置位置：main.py（專案根目錄）

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, ImageMessage
from linebot.exceptions import InvalidSignatureError
import os
from dotenv import load_dotenv

from schedule_parser import parse_schedule_text
from sheets_writer import write_to_sheet
from utils import download_line_image, save_temp_image, upload_image_to_drive
from xray_classifier import classify_image
from utils import restore_model_from_b64

# 初始化
load_dotenv()
restore_model_from_b64()

app = Flask(__name__)
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_text(event):
    text = event.message.text
    if "班表" in text:
        schedule_data = parse_schedule_text(text)
        write_to_sheet(schedule_data)
        reply = f"✅ 已成功匯入 {len(schedule_data)} 筆排班資料並同步行事曆"
    else:
        reply = "請輸入包含『班表』的文字來匯入排班"

    line_bot_api.reply_message(event.reply_token, TextMessage(text=reply))

@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    image_path = save_temp_image(event.message.id)
    label = classify_image(image_path)
    upload_image_to_drive(image_path, label)
    reply = f"✅ 圖片已分類為 {label} 並上傳"

    line_bot_api.reply_message(event.reply_token, TextMessage(text=reply))

@app.route("/", methods=["GET"])
def index():
    return "✅ DentalCloud API is running."

if __name__ == "__main__":
    app.run()
