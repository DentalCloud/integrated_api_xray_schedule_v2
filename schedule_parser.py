# 放置位置：schedule_parser.py（專案根目錄）

import re
from datetime import datetime

WEEKDAY_MAP = {
    "星期一": 0,
    "星期二": 1,
    "星期三": 2,
    "星期四": 3,
    "星期五": 4,
    "星期六": 5,
    "星期日": 6,
    "星期天": 6
}

SHIFT_TYPE_MAP = {
    ("早", "午", "晚"): "早午晚班",
    ("早", "午"): "早午班",
    ("午", "晚"): "午晚班",
    ("早",): "早班",
    ("午",): "午班",
    ("晚",): "晚班"
}

def parse_schedule_text(text: str) -> list[list[str]]:
    lines = text.strip().splitlines()
    results = []

    current_month = None
    current_location = None

    for line in lines:
        line = line.strip()
        if match := re.match(r"(\d+)月(.+?)班表", line):
            current_month = int(match.group(1))
            current_location = match.group(2)
        elif "星期" in line and "：" in line:
            weekday_str, shift_days_str = line.split("：", 1)
            weekday = WEEKDAY_MAP.get(weekday_str.strip())
            shift_codes = re.findall(r"[早午晚]", weekday_str)

            shift_type = SHIFT_TYPE_MAP.get(tuple(sorted(set(shift_codes))), "未知班別")
            days = [int(d) for d in re.findall(r"\d+", shift_days_str)]

            year = datetime.now().year
            for day in days:
                try:
                    date = datetime(year, current_month, day)
                    if date.weekday() == weekday:
                        results.append([
                            date.strftime("%Y/%m/%d"),
                            current_location,
                            shift_type
                        ])
                except ValueError:
                    continue
    return results
