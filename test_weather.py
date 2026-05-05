import requests
import os
from dotenv import load_dotenv
import time

load_dotenv()
KEY = os.getenv("DATA_GO_KR_KEY")

now = time.localtime()
base_date = time.strftime("%Y%m%d", now)

# 현재 시각에서 1시간 전으로 설정 (데이터 생성 시간 보장)
hour = now.tm_hour
if now.tm_min < 10:
    hour = hour - 1
if hour < 0:
    hour = 23
base_time = f"{hour:02d}00"

print(f"날짜: {base_date}, 시간: {base_time}")
print(f"API KEY: {KEY[:10]}...")

url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"
params = {
    "serviceKey": KEY,
    "pageNo": 1,
    "numOfRows": 10,
    "dataType": "JSON",
    "base_date": base_date,
    "base_time": base_time,
    "nx": 60,
    "ny": 127
}

response = requests.get(url, params=params, timeout=10)
print("상태코드:", response.status_code)
print("응답 텍스트 앞부분:", response.text[:300])