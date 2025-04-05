import threading
from xray_classifier import classify_image
from utils import save_temp_image, upload_image_to_drive

def handle_image_async(message_id):
    thread = threading.Thread(target=_process_image, args=(message_id,))
    thread.start()

def _process_image(message_id):
    try:
        image_path = save_temp_image(message_id)
        label = classify_image(image_path)
        upload_image_to_drive(image_path, label)
    except Exception as e:
        print(f"[async_worker] Error processing image: {e}")
