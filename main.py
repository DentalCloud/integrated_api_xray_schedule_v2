from flask import Flask, request
import os
import threading
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, ImageMessage
from schedule_parser import parse_schedule_text
from sheets_writer import write_schedule_to_sheet
from async_worker import handle_image_async
from dotenv import load_dotenv
from utils import restore_model_from_b64
from linebot.exceptions import InvalidSignatureError

load_dotenv()

app = Flask(__name__)
restore_model_from_b64()

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

# 全域快取圖片訊息，供主線程 callback 判斷類型後轉背景處理
_image_message_ids = []

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        events = handler.parser.parse(body, signature)
        for event in events:
            if isinstance(event.message, ImageMessage):
                message_id = event.message.id
                threading.Thread(target=handle_image_async, args=(message_id,)).start()
            elif isinstance(event.message, TextMessage):
                schedule_text = event.message.text
                rows = parse_schedule_text(schedule_text)
                if rows:
                    write_schedule_to_sheet(rows)
    except InvalidSignatureError:
        return "Invalid signature", 400
    except Exception as e:
        return str(e), 400

    return "OK"

@app.route("/", methods=["GET"])
def index():
    return "✅ DentalCloud API is running."

@app.route("/health", methods=["GET"])
def health():
    return "ok"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
