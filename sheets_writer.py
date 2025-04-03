# 放置位置：sheets_writer.py（專案根目錄）

import os
import gspread
from google.oauth2.service_account import Credentials
from calendar_sync import sync_sheet_to_calendar

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

SPREADSHEET_ID = "1IHl6XMlnN5ZsYGm1bEnwhgEvn_4TVVO4Useqxd04u7Y"

def write_to_sheet(data: list[list[str]]) -> None:
    creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1

    # 將每筆資料寫入新列
    for row in data:
        if len(row) >= 3:
            sheet.append_row(row)

    # 寫入完成後，同步至 Google Calendar
    sync_sheet_to_calendar()
