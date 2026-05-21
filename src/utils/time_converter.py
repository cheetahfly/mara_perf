"""马拉松成绩时间格式转换工具"""

def parse_time(time_str: str) -> int:
    """将时间字符串转为秒数"""
    parts = time_str.strip().split(":")
    if len(parts) == 3:
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + int(s)
    elif len(parts) == 2:
        m, s = parts
        return int(m) * 60 + int(s)
    else:
        raise ValueError(f"Invalid time format: {time_str}")

def format_time(seconds: int) -> str:
    """将秒数转为 HH:MM:SS 格式"""
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h}:{m:02d}:{s:02d}"

def time_to_minutes(seconds: int) -> float:
    """秒数转为分钟（浮点）"""
    return seconds / 60.0

def minutes_to_time(minutes: float) -> str:
    """分钟浮点数转为时间字符串"""
    total_seconds = int(round(minutes * 60))
    return format_time(total_seconds)
