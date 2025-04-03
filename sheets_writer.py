# 放置位置：sheets_writer.py

import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

def write_schedule_to_sheet(rows: list) -> None:
    if not rows:
        return

    creds = Credentials.from_service_account_file("credentials.json")
    service = build("sheets", "v4", credentials=creds)

    sheet = service.spreadsheets()
    body = {"values": rows}

    # 寫入到第 1 個工作表（假設為 A:B 欄）
    result = sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range="A:B",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body=body
    ).execute()

    print(f"{result.get('updates').get('updatedCells')} cells appended.")
