# 放置位置：calendar_sync.py（專案根目錄）

import os
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/calendar"
]

SPREADSHEET_ID = "1IHl6XMlnN5ZsYGm1bEnwhgEvn_4TVVO4Useqxd04u7Y"
CALENDAR_ID = "6e761a98705e1f702467b2726a58f09f8188a3f45ec7a8094c3d8efb39e34a55@group.calendar.google.com"

def sync_sheet_to_calendar():
    creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)

    # Sheets 讀取
    gc = gspread.authorize(creds)
    sheet = gc.open_by_key(SPREADSHEET_ID).sheet1
    rows = sheet.get_all_values()[1:]  # 跳過標題列

    # Calendar 初始化
    calendar = build("calendar", "v3", credentials=creds)

    for row in rows:
        if len(row) < 3:
            continue

        date_str, location, shift_type = row[:3]
        try:
            event_date = datetime.strptime(date_str, "%Y/%m/%d").date()
        except ValueError:
            continue

        title = f"{location}｜{shift_type}"
        date_iso = event_date.isoformat()

        # 查詢是否已有同標題事件
        existing = calendar.events().list(
            calendarId=CALENDAR_ID,
            timeMin=f"{date_iso}T00:00:00Z",
            timeMax=f"{date_iso}T23:59:59Z",
            singleEvents=True
        ).execute().get("items", [])

        if any(e.get("summary") == title for e in existing):
            continue

        event = {
            "summary": title,
            "start": {"date": date_iso},
            "end": {"date": date_iso}
        }
        calendar.events().insert(calendarId=CALENDAR_ID, body=event).execute()
