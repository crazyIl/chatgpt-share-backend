import base64
from datetime import datetime, timedelta
import json


def safe_b64decode(encoded_str):
    # 调整字符串长度以适应Base64的要求
    padding = len(encoded_str) % 4
    if padding != 0:
        encoded_str += "=" * (4 - padding)
    return base64.b64decode(encoded_str)


def open_ai_access_token_get_email(access_token):
    # access_token解析email
    email = ""
    if access_token is None:
        return email
    access_token_arr = access_token.split(".")
    if len(access_token_arr) == 3:
        # base64解码
        decoded_str = safe_b64decode(access_token_arr[1]).decode("utf-8")
        # 解析JSON数据
        data = json.loads(decoded_str)
        # 提取email字段
        email = data.get("https://api.openai.com/profile", {}).get("email", "")

    return email


def get_now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_after_days(days):
    return (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")


# 自定义 JSON 编码器，用于将 datetime 对象转换为字符串
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")  # 自定义时间格式
        return super().default(obj)
