import streamlit as st
import requests
import time
import json
import os
import math

# Streamlit Cloud는 st.secrets, 로컬은 .env 파일 사용
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def get_secret(key):
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key)

DATA_GO_KR_KEY    = get_secret("DATA_GO_KR_KEY")
ANTHROPIC_API_KEY = get_secret("ANTHROPIC_API_KEY")

st.set_page_config(
    page_title="SkyWatch",
    page_icon="✈️",
    layout="wide"
)

# ── 전체 스타일 ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1b2a 50%, #0a0e1a 100%);
    color: #e0e6f0;
}
.sky-header {
    background: linear-gradient(90deg, #0d1b2a, #1a3a5c);
    border-bottom: 1px solid #1e3a5f;
    padding: 20px 30px;
    margin: -1rem -1rem 2rem -1rem;
    display: flex;
    align-items: center;
    gap: 15px;
}
.sky-header h1 {
    font-size: 2rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0;
    letter-spacing: 2px;
}
.sky-header span {
    font-size: 0.9rem;
    color: #7ab3d4;
    margin: 0;
}
.metric-card {
    background: linear-gradient(135deg, #0f2237, #1a3a5c);
    border: 1px solid #1e4976;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0,100,200,0.15);
}
.metric-card .metric-value {
    font-size: 2.2rem;
    font-weight: 700;
    color: #4fc3f7;
    line-height: 1;
}
.metric-card .metric-label {
    font-size: 0.8rem;
    color: #7ab3d4;
    margin-top: 6px;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.alert-banner {
    background: linear-gradient(90deg, #2d1b00, #3d2600);
    border: 1px solid #f39c12;
    border-left: 4px solid #f39c12;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 6px 0;
    color: #f9ca74;
    font-size: 0.88rem;
}
.search-section {
    background: linear-gradient(135deg, #0f2237, #1a3a5c);
    border: 1px solid #1e4976;
    border-radius: 14px;
    padding: 24px;
    margin: 20px 0;
}
.search-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #4fc3f7;
    margin-bottom: 14px;
    letter-spacing: 1px;
}
.result-card {
    background: linear-gradient(135deg, #0a1929, #0f2a3d);
    border: 1px solid #1e4976;
    border-radius: 10px;
    padding: 16px;
    margin: 10px 0;
}
.result-card .result-title {
    font-size: 1rem;
    font-weight: 600;
    color: #81d4fa;
    margin-bottom: 10px;
}
.result-metric {
    display: inline-block;
    background: #0d2137;
    border: 1px solid #1e4976;
    border-radius: 8px;
    padding: 8px 14px;
    margin: 4px;
    text-align: center;
}
.result-metric .rm-val { font-size: 1.2rem; font-weight: 700; color: #4fc3f7; }
.result-metric .rm-label { font-size: 0.7rem; color: #7ab3d4; }
.section-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #4fc3f7;
    letter-spacing: 1px;
    padding: 8px 0;
    border-bottom: 1px solid #1e4976;
    margin-bottom: 16px;
}
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #0f2237, #1a3a5c);
    border: 1px solid #1e4976;
    border-radius: 12px;
    padding: 16px;
}
div[data-testid="stMetricValue"] { color: #4fc3f7 !important; }
div[data-testid="stMetricLabel"] { color: #7ab3d4 !important; }
input[type="text"] {
    background: #0a1929 !important;
    border: 1px solid #1e4976 !important;
    color: #e0e6f0 !important;
    border-radius: 8px !important;
}
.stButton button {
    background: linear-gradient(90deg, #1565c0, #1976d2) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
}
.stButton button:hover {
    background: linear-gradient(90deg, #1976d2, #1e88e5) !important;
}
hr { border-color: #1e3a5f !important; }
.click-hint {
    background: rgba(79,195,247,0.08);
    border: 1px solid #1e4976;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 0.8rem;
    color: #7ab3d4;
    text-align: center;
    margin-bottom: 10px;
}
.progress-card {
    background: linear-gradient(135deg, #0a1929, #0f2a3d);
    border: 1px solid #1e4976;
    border-radius: 12px;
    padding: 18px;
    margin: 10px 0;
}
.progress-bar-wrap {
    background: #0a1929;
    border-radius: 20px;
    height: 16px;
    margin: 10px 0 6px 0;
    overflow: visible;
    border: 1px solid #1e4976;
    position: relative;
}
.progress-bar-fill {
    height: 100%;
    border-radius: 20px;
    background: linear-gradient(90deg, #1565c0, #4fc3f7);
    position: relative;
    min-width: 18px;
}
.airport-badge {
    display: inline-block;
    background: #0d2137;
    border: 1px solid #1e4976;
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 0.85rem;
    font-weight: 700;
    color: #4fc3f7;
}
.eta-big {
    font-size: 1.5rem;
    font-weight: 700;
    color: #4fc3f7;
    text-align: center;
}
.eta-label {
    font-size: 0.75rem;
    color: #7ab3d4;
    text-align: center;
}
.arrival-alert {
    background: linear-gradient(90deg, #0d2200, #1a3300);
    border: 2px solid #76c442;
    border-left: 5px solid #76c442;
    border-radius: 10px;
    padding: 14px 16px;
    margin: 8px 0;
    animation: pulse-green 2s infinite;
}
.arrival-alert-warn {
    background: linear-gradient(90deg, #2d1b00, #3d2600);
    border: 2px solid #ffa726;
    border-left: 5px solid #ffa726;
    border-radius: 10px;
    padding: 14px 16px;
    margin: 8px 0;
}
@keyframes pulse-green {
    0%, 100% { box-shadow: 0 0 0 0 rgba(118,196,66,0.4); }
    50% { box-shadow: 0 0 12px rgba(118,196,66,0.3); }
}
.forecast-row {
    display: flex;
    gap: 5px;
    margin-top: 10px;
    flex-wrap: wrap;
}
.forecast-cell {
    flex: 1;
    background: #0d2137;
    border: 1px solid #1e4976;
    border-radius: 8px;
    padding: 8px 4px;
    text-align: center;
    min-width: 50px;
}
.forecast-cell .fc-time { font-size: 0.68rem; color: #7ab3d4; }
.forecast-cell .fc-icon { font-size: 1.1rem; line-height: 1.4; }
.forecast-cell .fc-temp { font-size: 0.82rem; font-weight: 700; color: #4fc3f7; }
</style>
""", unsafe_allow_html=True)

# ── 상수 ──
KOREA_BOUNDS = {
    "lamin": 24.0, "lomin": 115.0,   # 중국 동부 해안선 포함
    "lamax": 45.0, "lomax": 145.0    # 일본 동부 + 만주 포함
}

WEATHER_STATIONS = [
    {"name": "서울",  "nx": 60, "ny": 127, "lat": 37.5665, "lon": 126.9780},
    {"name": "강릉",  "nx": 92, "ny": 131, "lat": 37.7519, "lon": 128.8761},
    {"name": "대전",  "nx": 67, "ny": 100, "lat": 36.3504, "lon": 127.3845},
    {"name": "대구",  "nx": 89, "ny": 90,  "lat": 35.8714, "lon": 128.6014},
    {"name": "부산",  "nx": 98, "ny": 76,  "lat": 35.1796, "lon": 129.0756},
    {"name": "광주",  "nx": 58, "ny": 74,  "lat": 35.1595, "lon": 126.8526},
    {"name": "제주",  "nx": 52, "ny": 38,  "lat": 33.4996, "lon": 126.5312},
    {"name": "전주",  "nx": 63, "ny": 89,  "lat": 35.8242, "lon": 127.1479},
    {"name": "울산",  "nx": 102,"ny": 84,  "lat": 35.5384, "lon": 129.3114},
]

# 주요 공항 데이터
AIRPORTS = [
    {"name": "인천국제공항",   "iata": "ICN", "lat": 37.4602, "lon": 126.4407, "nx": 55, "ny": 124, "keyword": "인천"},
    {"name": "김포국제공항",   "iata": "GMP", "lat": 37.5583, "lon": 126.7906, "nx": 57, "ny": 126, "keyword": "김포"},
    {"name": "제주국제공항",   "iata": "CJU", "lat": 33.5113, "lon": 126.4928, "nx": 52, "ny": 38,  "keyword": "제주"},
    {"name": "김해국제공항",   "iata": "PUS", "lat": 35.1795, "lon": 128.9381, "nx": 97, "ny": 74,  "keyword": "부산"},
    {"name": "대구국제공항",   "iata": "TAE", "lat": 35.8964, "lon": 128.6586, "nx": 89, "ny": 91,  "keyword": "대구"},
    {"name": "광주공항",       "iata": "KWJ", "lat": 35.1264, "lon": 126.8088, "nx": 58, "ny": 74,  "keyword": "광주"},
    {"name": "청주국제공항",   "iata": "CJJ", "lat": 36.7166, "lon": 127.4987, "nx": 69, "ny": 107, "keyword": "청주"},
    {"name": "양양국제공항",   "iata": "YNY", "lat": 38.0613, "lon": 128.6693, "nx": 93, "ny": 137, "keyword": "양양"},
    {"name": "무안국제공항",   "iata": "MWX", "lat": 34.9913, "lon": 126.3828, "nx": 55, "ny": 72,  "keyword": "무안"},
    {"name": "울산공항",       "iata": "USN", "lat": 35.5935, "lon": 129.3522, "nx": 102,"ny": 84,  "keyword": "울산"},
    {"name": "여수공항",       "iata": "RSU", "lat": 34.8423, "lon": 127.6167, "nx": 73, "ny": 66,  "keyword": "여수"},
    {"name": "포항경주공항",   "iata": "KPO", "lat": 35.9880, "lon": 129.4200, "nx": 103,"ny": 94,  "keyword": "포항"},
    {"name": "원주공항",       "iata": "WJU", "lat": 37.4380, "lon": 127.9596, "nx": 83, "ny": 121, "keyword": "원주"},
    {"name": "군산공항",       "iata": "KUV", "lat": 35.9038, "lon": 126.6159, "nx": 60, "ny": 90,  "keyword": "군산"},
    {"name": "사천공항",       "iata": "HIN", "lat": 35.0883, "lon": 128.0706, "nx": 80, "ny": 75,  "keyword": "사천"},
]

# 국가코드 → 한글 국가명
COUNTRY_KO = {
    "Republic of Korea": "대한민국",
    "South Korea": "대한민국",
    "Korea": "대한민국",
    "United States": "미국",
    "Japan": "일본",
    "China": "중국",
    "Taiwan": "대만",
    "Hong Kong": "홍콩",
    "Macao": "마카오",
    "Germany": "독일",
    "France": "프랑스",
    "United Kingdom": "영국",
    "Netherlands": "네덜란드",
    "Switzerland": "스위스",
    "Austria": "오스트리아",
    "Belgium": "벨기에",
    "Italy": "이탈리아",
    "Spain": "스페인",
    "Portugal": "포르투갈",
    "Sweden": "스웨덴",
    "Norway": "노르웨이",
    "Denmark": "덴마크",
    "Finland": "핀란드",
    "Poland": "폴란드",
    "Russia": "러시아",
    "Ukraine": "우크라이나",
    "Turkey": "튀르키예",
    "Canada": "캐나다",
    "Mexico": "멕시코",
    "Brazil": "브라질",
    "Argentina": "아르헨티나",
    "Australia": "호주",
    "New Zealand": "뉴질랜드",
    "Singapore": "싱가포르",
    "Malaysia": "말레이시아",
    "Thailand": "태국",
    "Vietnam": "베트남",
    "Philippines": "필리핀",
    "Indonesia": "인도네시아",
    "India": "인도",
    "Pakistan": "파키스탄",
    "Saudi Arabia": "사우디아라비아",
    "United Arab Emirates": "아랍에미리트",
    "Qatar": "카타르",
    "Kuwait": "쿠웨이트",
    "Iran": "이란",
    "Iraq": "이라크",
    "Israel": "이스라엘",
    "Egypt": "이집트",
    "South Africa": "남아프리카공화국",
    "Ethiopia": "에티오피아",
    "Kenya": "케냐",
    "Nigeria": "나이지리아",
    "Ghana": "가나",
    "Mongolia": "몽골",
    "Kazakhstan": "카자흐스탄",
    "Uzbekistan": "우즈베키스탄",
    "Myanmar": "미얀마",
    "Cambodia": "캄보디아",
    "Laos": "라오스",
    "Bangladesh": "방글라데시",
    "Nepal": "네팔",
    "Sri Lanka": "스리랑카",
    "Maldives": "몰디브",
    "Czech Republic": "체코",
    "Slovakia": "슬로바키아",
    "Hungary": "헝가리",
    "Romania": "루마니아",
    "Bulgaria": "불가리아",
    "Greece": "그리스",
    "Croatia": "크로아티아",
    "Serbia": "세르비아",
    "Luxembourg": "룩셈부르크",
    "Ireland": "아일랜드",
    "Iceland": "아이슬란드",
    "Panama": "파나마",
    "Cayman Islands": "케이맨 제도",
    "Bermuda": "버뮤다",
    "Unknown": "알 수 없음",
    "": "미확인",
}

def country_ko(name):
    if not name:
        return "미확인"
    for key, val in COUNTRY_KO.items():
        if key.lower() in name.lower():
            return val
    return name

def dist_km(lat1, lon1, lat2, lon2):
    """두 좌표 사이 거리(km) 계산 - Haversine"""
    if None in (lat1, lon1, lat2, lon2):
        return 9999
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon/2)**2
    return R * 2 * math.asin(math.sqrt(a))

# ── API 함수 ──
@st.cache_data(ttl=60)
def get_flights():
    """airplanes.live + OpenSky Network 두 API 병합, ICAO hex로 중복 제거"""
    seen = {}   # icao24 → 데이터 (중복 제거용)

    # ── 1. airplanes.live (반경 500nm로 확대) ──
    try:
        r = requests.get(
            "https://api.airplanes.live/v2/point/35.0/125.0/500",
            headers={"User-Agent": "SkyWatch/3.0 (Korea Air Traffic Monitor)"},
            timeout=15
        )
        if r.status_code == 200:
            for ac in r.json().get("ac", []):
                lat = ac.get("lat")
                lon = ac.get("lon")
                if lat is None or lon is None:
                    continue
                alt_raw = ac.get("alt_baro", 0)
                on_ground = alt_raw == "ground"
                alt_m = 0 if on_ground else (float(alt_raw) * 0.3048 if alt_raw else 0)
                gs = ac.get("gs", 0)
                icao = ac.get("hex", "").lower()
                seen[icao] = [
                    icao,                              # 0: ICAO hex
                    ac.get("flight", "").strip(),      # 1: 편명
                    country_ko(ac.get("r", "")),       # 2: 국가명(한글)
                    None, None,                        # 3,4: 미사용
                    float(lon), float(lat),            # 5,6: 경도/위도
                    alt_m,                             # 7: 고도(m)
                    on_ground,                         # 8: 지상여부
                    float(gs) * 0.514444 if gs else 0, # 9: 속도(m/s)
                    ac.get("track", 0) or 0,           # 10: 방향
                    ac.get("desc", ""),                # 11: 기종
                    ac.get("r", ""),                   # 12: 등록국코드
                    ac.get("orig", "") or ac.get("from", ""),  # 13: 출발공항 IATA
                    ac.get("dest", "") or ac.get("to", ""),    # 14: 도착공항 IATA
                ]
    except Exception as e:
        print("airplanes.live 오류:", e)

    # ── 2. OpenSky Network (한반도 bbox) ──
    try:
        r2 = requests.get(
            "https://opensky-network.org/api/states/all"
            "?lamin=24&lomin=115&lamax=45&lomax=145",
            headers={"User-Agent": "SkyWatch/3.0 (Korea Air Traffic Monitor)"},
            timeout=15
        )
        if r2.status_code == 200:
            for s in (r2.json().get("states") or []):
                if not s or len(s) < 11:
                    continue
                icao = (s[0] or "").lower()
                lon  = s[5]
                lat  = s[6]
                if lat is None or lon is None:
                    continue
                # airplanes.live에 이미 있으면 스킵 (더 정확한 데이터 우선)
                if icao in seen:
                    continue
                # 지도 관심 영역 밖이면 스킵 (너무 먼 데이터 제외)
                if not (24 <= float(lat) <= 45 and 115 <= float(lon) <= 145):
                    continue
                alt_m     = s[7] or 0          # baro_altitude (이미 m 단위)
                on_ground = bool(s[8])
                speed_ms  = s[9] or 0          # m/s → m/s (그대로)
                heading   = s[10] or 0
                callsign  = (s[1] or "").strip()
                country   = country_ko(s[2] or "")
                seen[icao] = [
                    icao,
                    callsign,
                    country,
                    None, None,
                    float(lon), float(lat),
                    float(alt_m),
                    on_ground,
                    float(speed_ms),
                    float(heading),
                    "",        # desc 없음
                    s[2] or "",
                    "",        # orig (OpenSky 미제공)
                    "",        # dest (OpenSky 미제공)
                ]
    except Exception as e:
        print("OpenSky 오류:", e)

    return list(seen.values())

def get_weather_data():
    now = time.localtime()
    base_date = time.strftime("%Y%m%d", now)
    hour = now.tm_hour - (1 if now.tm_min < 10 else 0)
    if hour < 0: hour = 23
    base_time = f"{hour:02d}00"
    results = []
    for station in WEATHER_STATIONS:
        params = {
            "serviceKey": DATA_GO_KR_KEY, "pageNo": 1, "numOfRows": 10,
            "dataType": "JSON", "base_date": base_date, "base_time": base_time,
            "nx": station["nx"], "ny": station["ny"]
        }
        try:
            r = requests.get("http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst",
                             params=params, timeout=5)
            items = r.json().get("response", {}).get("body", {}).get("items", {}).get("item", [])
            w = {"name": station["name"], "lat": station["lat"], "lon": station["lon"],
                 "temp": None, "rain": None, "wind_speed": None, "wind_dir": None, "humidity": None, "sky": None}
            for item in items:
                cat, val = item.get("category"), item.get("obsrValue")
                if cat == "T1H": w["temp"] = float(val)
                elif cat == "RN1": w["rain"] = float(val)
                elif cat == "WSD": w["wind_speed"] = float(val)
                elif cat == "VEC": w["wind_dir"] = float(val)
                elif cat == "REH": w["humidity"] = float(val)
                elif cat == "PTY": w["sky"] = int(float(val))
            results.append(w)
        except:
            results.append({"name": station["name"], "lat": station["lat"], "lon": station["lon"],
                            "temp": None, "rain": None, "wind_speed": None, "wind_dir": None, "humidity": None, "sky": None})
    return results

def get_airport_weather(nx, ny):
    now = time.localtime()
    base_date = time.strftime("%Y%m%d", now)
    hour = now.tm_hour - (1 if now.tm_min < 10 else 0)
    if hour < 0: hour = 23
    base_time = f"{hour:02d}00"
    params = {
        "serviceKey": DATA_GO_KR_KEY, "pageNo": 1, "numOfRows": 10,
        "dataType": "JSON", "base_date": base_date, "base_time": base_time,
        "nx": nx, "ny": ny
    }
    try:
        r = requests.get("http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst",
                         params=params, timeout=5)
        items = r.json().get("response", {}).get("body", {}).get("items", {}).get("item", [])
        w = {"temp": None, "rain": None, "wind_speed": None, "wind_dir": None, "humidity": None, "sky": None}
        for item in items:
            cat, val = item.get("category"), item.get("obsrValue")
            if cat == "T1H": w["temp"] = float(val)
            elif cat == "RN1": w["rain"] = float(val)
            elif cat == "WSD": w["wind_speed"] = float(val)
            elif cat == "VEC": w["wind_dir"] = float(val)
            elif cat == "REH": w["humidity"] = float(val)
            elif cat == "PTY": w["sky"] = int(float(val))
        return w
    except:
        return {"temp": None, "rain": None, "wind_speed": None, "wind_dir": None, "humidity": None, "sky": None}

def get_weather_alerts():
    params = {"serviceKey": DATA_GO_KR_KEY, "pageNo": 1, "numOfRows": 20, "dataType": "JSON", "stnId": "108"}
    try:
        r = requests.get("http://apis.data.go.kr/1360000/WthrWrnInfoService/getWthrWrnMsg", params=params, timeout=5)
        items = r.json().get("response", {}).get("body", {}).get("items", {})
        if items:
            item_list = items.get("item", [])
            return [item_list] if isinstance(item_list, dict) else item_list
        return []
    except:
        return []

# ── TAGO 국내항공운항정보 API ──
# 문서 기준 정확한 공항ID (NAARK + ICAO코드)
TAGO_AIRPORT_ID = {
    "GMP": "NAARKSS", "ICN": "NAARKSI", "CJU": "NAARKPC",
    "PUS": "NAARKPK", "TAE": "NAARKTG", "CJJ": "NAARKJJ",
    "RSU": "NAARKNY", "YNY": "NAARKYY", "USN": "NAARKUL",
    "WJU": "NAARKWR", "KPO": "NAARKPO", "HIN": "NAARKJH",
    "MWX": "NAARKMU", "KUV": "NAARKKU",
}
TAGO_URL = "http://apis.data.go.kr/1613000/DmstcFlightNvgInfo/GetFlightOpratInfoList"

@st.cache_data(ttl=300)
def _load_tago_flights_cache():
    """TAGO 국내항공운항정보 - 주요 노선 조회 후 vihicleId 딕셔너리로 캐시
    
    API 명세 (문서 p.4):
      필수: depAirportId, arrAirportId, depPlandTime(YYYYMMDD)
      응답: vihicleId(편명), depAirportNm, arrAirportNm,
            depPlandTime(YYYYMMDDHHmm), arrPlandTime, airlineNm
    """
    today = time.strftime("%Y%m%d")
    result = {}

    # 주요 국내선 노선 (양방향, 수요 순)
    routes = [
        ("NAARKSS","NAARKPC"), ("NAARKPC","NAARKSS"),  # GMP↔CJU 최다
        ("NAARKSI","NAARKPC"), ("NAARKPC","NAARKSI"),  # ICN↔CJU
        ("NAARKSS","NAARKPK"), ("NAARKPK","NAARKSS"),  # GMP↔PUS
        ("NAARKSI","NAARKPK"), ("NAARKPK","NAARKSI"),  # ICN↔PUS
        ("NAARKSS","NAARKTG"), ("NAARKTG","NAARKSS"),  # GMP↔TAE
        ("NAARKSS","NAARKJJ"), ("NAARKJJ","NAARKSS"),  # GMP↔CJJ(청주)
        ("NAARKSS","NAARKNY"), ("NAARKNY","NAARKSS"),  # GMP↔RSU(여수)
        ("NAARKSS","NAARKUL"), ("NAARKUL","NAARKSS"),  # GMP↔USN(울산)
        ("NAARKPC","NAARKPK"), ("NAARKPK","NAARKPC"),  # CJU↔PUS
        ("NAARKSI","NAARKTG"), ("NAARKTG","NAARKSI"),  # ICN↔TAE
    ]

    for dep_id, arr_id in routes:
        try:
            r = requests.get(TAGO_URL, params={
                "serviceKey":  DATA_GO_KR_KEY,
                "numOfRows":   100,
                "pageNo":      1,
                "_type":       "json",
                "depAirportId": dep_id,
                "arrAirportId": arr_id,
                "depPlandTime": today,   # 문서 기준: 출발일 YYYYMMDD
            }, timeout=10)

            text = r.text.strip()
            if not text:
                continue

            # 공공데이터포털 에러 XML 처리 (에러코드 32=IP미등록 등)
            if text.startswith("<OpenAPI"):
                import xml.etree.ElementTree as ET
                try:
                    root = ET.fromstring(text)
                    code = root.findtext(".//returnReasonCode", "")
                    msg  = root.findtext(".//returnAuthMsg", "")
                    if code == "32":
                        pass  # IP 미등록 - 로컬에서는 정상
                    elif code:
                        print(f"[TAGO] {dep_id}→{arr_id}: 에러{code}({msg})")
                except:
                    pass
                continue

            data  = r.json()
            body  = data.get("response", {}).get("body", {})
            total = int(body.get("totalCount", 0) or 0)
            if total == 0:
                continue

            items = body.get("items", {}).get("item", [])
            if isinstance(items, dict):
                items = [items]

            for it in (items or []):
                # 문서 기준 응답 필드: vihicleId (편명)
                vid = (it.get("vihicleId") or "").strip().upper()
                if vid and vid not in result:
                    result[vid] = it

        except Exception:
            continue

    if result:
        first = next(iter(result.values()))
        print(f"[TAGO] 총 {len(result)}편 로딩 완료")
        print(f"[TAGO] 응답 필드: {list(first.keys())}")
    else:
        print("[TAGO] 0편 - 로컬 실행 시 정상 작동 예정")
    return result

def search_flight_info(callsign):
    """편명(vihicleId)으로 TAGO 캐시 검색"""
    cache = _load_tago_flights_cache()
    item  = cache.get(callsign.strip().upper())
    return [item] if item else []


def get_airport_delays(airport_keyword):
    """특정 공항의 지연·결항 편 조회
    ※ 한국공항공사 B551177 API 사용
    ※ 현재 작동 중 - 기상 악화 시 지연·결항 정보 제공
    """
    results = []
    today = time.strftime("%Y%m%d")
    urls = [
        ("http://apis.data.go.kr/B551177/StatusOfPassengerFlightsOdp/getPassengerDeparturesDump", "출발"),
        ("http://apis.data.go.kr/B551177/StatusOfPassengerFlightsOdp/getPassengerArrivalsDump", "도착"),
    ]
    for url, direction in urls:
        params = {
            "serviceKey": DATA_GO_KR_KEY,
            "pageNo": 1, "numOfRows": 100,
            "type": "json", "date": today
        }
        try:
            r = requests.get(url, params=params, timeout=8)
            if not r.text or not r.text.strip():
                continue
            try:
                data = r.json()
            except Exception:
                continue
            items = data.get("response", {}).get("body", {}).get("items", {})
            if not items:
                continue
            item_list = items.get("item", [])
            if not item_list:
                continue
            if isinstance(item_list, dict):
                item_list = [item_list]
            for item in item_list:
                remark = item.get("remark", "") or item.get("remarkKorean", "") or ""
                airport = item.get("airport", "") or item.get("airportKorean", "") or ""
                if airport_keyword and airport_keyword not in airport:
                    continue
                if any(kw in str(remark) for kw in ["지연", "결항", "Delay", "Cancel", "취소"]):
                    results.append({
                        "direction": direction,
                        "flight_id": item.get("flightId", ""),
                        "airline": item.get("airline", "") or item.get("airlineKorean", ""),
                        "airport": airport,
                        "sched": item.get("scheduleDateTime", "") or item.get("std", ""),
                        "remark": remark
                    })
        except Exception:
            pass  # 조용히 실패
    return results

def get_delayed_flights():
    """전체 지연·결항 조회"""
    return get_airport_delays("")

def calc_flight_progress(cur_lat, cur_lon, dep_airport, arr_airport, speed_kmh):
    """현재 위치 기준 비행 진행률(%), 남은 거리, ETA 계산"""
    if not dep_airport or not arr_airport:
        return None
    total = dist_km(dep_airport["lat"], dep_airport["lon"],
                    arr_airport["lat"], arr_airport["lon"])
    remain = dist_km(cur_lat, cur_lon, arr_airport["lat"], arr_airport["lon"])
    if total <= 0:
        return None
    progress = max(0.0, min(100.0, (1 - remain / total) * 100))
    eta_min = int(remain / speed_kmh * 60) if speed_kmh > 50 else None
    eta_time = None
    if eta_min is not None:
        eta_ts = time.localtime(time.time() + eta_min * 60)
        eta_time = time.strftime("%H:%M", eta_ts)
    return {
        "progress": round(progress, 1),
        "total_km": round(total),
        "remain_km": round(remain),
        "eta_min": eta_min,
        "eta_time": eta_time,
    }

def analyze_flight_weather_ai(flight_info: dict, weather_info: dict, delay_info: list) -> str:
    """
    Claude API를 이용한 기상·운항 통합 AI 분석 코멘트 생성
    flight_info  : 편명, 출발지, 목적지, 고도, 속도, ETA 등
    weather_info : 목적지 공항 현재 날씨 (기온, 풍속, 강수, 하늘상태)
    delay_info   : 목적지 공항 지연·결항 편 리스트
    """
    if not ANTHROPIC_API_KEY:
        return "⚠️ AI 분석을 사용하려면 .env 파일에 ANTHROPIC_API_KEY를 설정해주세요."

    # 프롬프트 구성
    delay_text = ""
    if delay_info:
        delay_text = "\n".join(
            f"  - {d.get('flight','?')} ({d.get('airline','?')}) : {d.get('remark','지연')}"
            for d in delay_info[:5]
        )
    else:
        delay_text = "  현재 지연·결항 편 없음"

    sky_map = {1: "맑음", 2: "구름조금", 3: "구름많음", 4: "흐림"}
    sky_str = sky_map.get(weather_info.get("sky"), "알 수 없음")
    pty_map = {0: "없음", 1: "비", 2: "비/눈", 3: "눈", 4: "소나기"}
    pty_str = pty_map.get(weather_info.get("pty", 0), "없음")

    prompt = f"""당신은 항공 기상 전문 AI 어시스턴트입니다.
아래 데이터를 분석하여 공항에서 가족을 마중 나가는 일반 시민이 이해하기 쉬운 한국어로 3~4문장의 종합 분석 코멘트를 작성해주세요.
전문 용어는 쉽게 풀어서 설명하고, 실용적인 조언을 포함해주세요.

[항공편 정보]
- 편명: {flight_info.get('callsign', '알 수 없음')}
- 출발지: {flight_info.get('dep', '알 수 없음')}
- 목적지: {flight_info.get('arr', '알 수 없음')}
- 현재 고도: {flight_info.get('alt', '알 수 없음')} ft
- 현재 속도: {flight_info.get('speed', '알 수 없음')} km/h
- 예상 도착: {flight_info.get('eta', '계산 중')}

[목적지 공항 현재 날씨]
- 기온: {weather_info.get('temp', '알 수 없음')}°C
- 하늘상태: {sky_str}
- 강수형태: {pty_str}
- 풍속: {weather_info.get('wind_speed', '알 수 없음')} m/s
- 습도: {weather_info.get('humidity', '알 수 없음')}%

[공항 지연·결항 현황]
{delay_text}

위 데이터를 바탕으로 기상이 항공편에 미치는 영향, 현재 운항 상태, 마중 나가는 분들을 위한 실용적인 조언을 포함하여 분석해주세요."""

    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 400,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=15
        )
        result = resp.json()
        if "content" in result and result["content"]:
            return result["content"][0]["text"]
        return "⚠️ AI 분석 결과를 가져오지 못했습니다."
    except Exception as e:
        return f"⚠️ AI 분석 오류: {str(e)}"


def get_weather_forecast(nx, ny):
    """기상청 초단기예보 - 향후 6시간"""
    now = time.localtime()
    base_date = time.strftime("%Y%m%d", now)
    hour = now.tm_hour
    minute = now.tm_min
    if minute < 30:
        hour -= 1
        if hour < 0:
            hour = 23
    base_time = f"{hour:02d}30"
    params = {
        "serviceKey": DATA_GO_KR_KEY, "pageNo": 1, "numOfRows": 60,
        "dataType": "JSON", "base_date": base_date, "base_time": base_time,
        "nx": nx, "ny": ny
    }
    forecasts = {}
    try:
        r = requests.get(
            "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst",
            params=params, timeout=6
        )
        items = r.json().get("response", {}).get("body", {}).get("items", {}).get("item", [])
        for item in items:
            t = item.get("fcstTime", "")
            cat = item.get("category", "")
            val = item.get("fcstValue", "")
            if t not in forecasts:
                forecasts[t] = {"time": t}
            if cat == "T1H":   forecasts[t]["temp"] = float(val)
            elif cat == "PTY": forecasts[t]["pty"]  = int(float(val))
            elif cat == "SKY": forecasts[t]["sky"]  = int(float(val))
            elif cat == "RN1": forecasts[t]["rain"] = float(val)
            elif cat == "WSD": forecasts[t]["wind"] = float(val)
    except:
        pass
    return sorted(forecasts.values(), key=lambda x: x["time"])[:6]

def forecast_sky_icon(pty, sky):
    if pty == 1: return "🌧️"
    if pty == 2: return "🌨️"
    if pty == 3: return "❄️"
    if pty == 4: return "🌦️"
    if sky is None: return "🌤️"
    if sky <= 5:  return "☀️"
    if sky <= 8:  return "⛅"
    return "☁️"

# ── 헬퍼 ──
def sky_icon(pty, rain, wind_speed):
    if pty == 1: return "🌧️"
    if pty == 2: return "🌨️"
    if pty == 3: return "❄️"
    if pty == 4: return "🌦️"
    if rain and rain > 0: return "🌧️"
    if wind_speed and wind_speed > 10: return "💨"
    return "☀️"

def wind_arrow(deg):
    if deg is None: return "?"
    return ["↓", "↙", "←", "↖", "↑", "↗", "→", "↘"][round(deg / 45) % 8]

# ── 데이터 로딩 ──
with st.spinner(""):
    flights = get_flights()
    weather_data = get_weather_data()
    alerts = get_weather_alerts()

# fragment 안에서 접근할 수 있도록 session_state에 캐시
st.session_state["_flights_cache"] = flights

# ── 세션 초기화 ──
if "callsign_input" not in st.session_state:
    st.session_state.callsign_input = ""
if "dest_airport" not in st.session_state:
    st.session_state.dest_airport = None
if "show_3d_flight" not in st.session_state:
    st.session_state.show_3d_flight = None
if "clicked_flight" not in st.session_state:
    st.session_state.clicked_flight = ""

# ── 헤더 ──
airborne    = [f for f in flights if len(f) > 8 and not f[8]]
on_ground   = [f for f in flights if len(f) > 8 and f[8]]
identified  = [f for f in flights if f[1] and f[1].strip()]
intl        = [f for f in flights if f[1] and (f[1][:2] not in ["KE","OZ","7C","BX","TW","RS","ZE","YP","4V","KJ","LJ","RF","석"])]

# 평균 고도·속도 계산
if airborne:
    avg_alt = sum((f[7] or 0) for f in airborne) / len(airborne)
    avg_spd = sum(((f[9] or 0)*3.6) for f in airborne) / len(airborne)
else:
    avg_alt = avg_spd = 0

now_str = time.strftime('%Y.%m.%d %H:%M')

st.markdown(f"""
<div class="sky-header">
    <div style="font-size:2.2rem;filter:drop-shadow(0 0 8px #4fc3f7);">✈️</div>
    <div style="flex:1;">
        <h1>SKYWATCH</h1>
        <span>한반도 실시간 항공·기상 통합 모니터링 &nbsp;|&nbsp; {now_str} KST</span>
    </div>
    <div style="background:rgba(79,195,247,0.1);border:1px solid #1e4976;border-radius:8px;padding:6px 14px;text-align:center;">
        <div style="font-size:0.65rem;color:#7ab3d4;letter-spacing:1px;">DATA SOURCE</div>
        <div style="font-size:0.72rem;color:#4fc3f7;">airplanes.live · OpenSky · 기상청 · 국토부</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── 전문 지표 대시보드 ──
st.markdown("""
<style>
.dash-grid {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 10px;
    margin: 0 0 16px 0;
}
.dash-card {
    background: linear-gradient(135deg, #0c1e33, #0f2840);
    border: 1px solid #1a3a5c;
    border-radius: 10px;
    padding: 14px 12px;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.dash-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--accent, #4fc3f7);
}
.dash-card .dv { font-size: 1.6rem; font-weight: 700; color: var(--accent, #4fc3f7); line-height: 1.1; }
.dash-card .dl { font-size: 0.62rem; color: #5a8aaa; text-transform: uppercase; letter-spacing: 0.8px; margin-top: 4px; }
.dash-card .ds { font-size: 0.7rem; color: #7ab3d4; margin-top: 2px; }
.dash-divider { border: none; border-top: 1px solid #1a3a5c; margin: 0 0 14px 0; }
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="dash-grid">
    <div class="dash-card" style="--accent:#4fc3f7;">
        <div class="dv">{len(flights)}</div>
        <div class="dl">총 추적</div>
        <div class="ds">airplanes.live + OpenSky</div>
    </div>
    <div class="dash-card" style="--accent:#81c784;">
        <div class="dv">{len(airborne)}</div>
        <div class="dl">공중 비행</div>
        <div class="ds">현재 비행 중</div>
    </div>
    <div class="dash-card" style="--accent:#ffb74d;">
        <div class="dv">{len(on_ground)}</div>
        <div class="dl">지상 대기</div>
        <div class="ds">공항 계류 중</div>
    </div>
    <div class="dash-card" style="--accent:#ce93d8;">
        <div class="dv">{len(identified)}</div>
        <div class="dl">편명 식별</div>
        <div class="ds">ADS-B 수신</div>
    </div>
    <div class="dash-card" style="--accent:#80cbc4;">
        <div class="dv">{avg_alt:,.0f}m</div>
        <div class="dl">평균 고도</div>
        <div class="ds">{avg_alt*3.28084:,.0f} ft</div>
    </div>
    <div class="dash-card" style="--accent:#f48fb1;">
        <div class="dv">{avg_spd:.0f}</div>
        <div class="dl">평균 속도</div>
        <div class="ds">km/h</div>
    </div>
</div>
""", unsafe_allow_html=True)

# 기상 특보 배너 제거됨

st.markdown('<hr class="dash-divider">', unsafe_allow_html=True)

# ── 지도 ──
st.markdown('<div class="section-title">🗺️ 실시간 항공 레이더 &nbsp;<span style="font-size:0.72rem;color:#5a8aaa;font-weight:400;">Korea Air Traffic Monitor</span></div>', unsafe_allow_html=True)

col_t1, col_t2 = st.columns(2)
show_weather = False   # 기상 라벨 지도에서 제거
show_alert_toggle = False
with col_t1: show_wind = st.toggle("💨 바람 흐름", value=True)
with col_t2: show_rain = st.toggle("🌧️ 강수 구역", value=True)

# JS → Python 클릭 감지용 query param
clicked_from_url = st.query_params.get("flight", "")
if clicked_from_url and clicked_from_url != st.session_state.clicked_flight:
    st.session_state.clicked_flight = clicked_from_url
    st.session_state.callsign_input = clicked_from_url

# 공항 코드 → 한글명 (flights_js 변환에서 사용)
AIRPORT_KO = {
    "GMP": "김포", "ICN": "인천", "PUS": "김해", "CJU": "제주",
    "TAE": "대구", "CJJ": "청주", "KWJ": "광주", "RSU": "여수",
    "YNY": "양양", "USN": "울산", "WJU": "원주", "KPO": "포항",
    "HIN": "사천", "SHO": "속초", "MPK": "목포", "KUV": "군산",
    "MWX": "무안",
}
AIRPORT_COORDS = {a["iata"]: {"lat": a["lat"], "lon": a["lon"], "name": a["name"]}
                  for a in AIRPORTS}
DOMESTIC_IATA = set(AIRPORT_COORDS.keys())

def apt_ko(code):
    return AIRPORT_KO.get(str(code).upper(), code or "")

flights_js = []
for f in flights:
    try:
        lat, lon = f[6], f[5]
        if lat is None or lon is None: continue
        orig_iata = (f[13] if len(f) > 13 else "") or ""
        dest_iata = (f[14] if len(f) > 14 else "") or ""
        orig_info = AIRPORT_COORDS.get(orig_iata.upper(), {})
        dest_info = AIRPORT_COORDS.get(dest_iata.upper(), {})
        flights_js.append({
            "callsign": f[1].strip() if f[1] else "미확인",
            "country": f[2] if f[2] else "알 수 없음",
            "lat": lat, "lon": lon,
            "altitude": f[7] if f[7] else 0,
            "speed": round((f[9] or 0) * 3.6),
            "heading": f[10] if f[10] else 0,
            "on_ground": f[8] if f[8] is not None else False,
            "desc": f[11] if len(f) > 11 else "",
            "icao": f[0] if f[0] else "",
            "reg": f[12] if len(f) > 12 else "",
            # ADS-B 출발/도착 공항 (airplanes.live orig/dest 필드)
            "orig": orig_iata.upper(),
            "dest": dest_iata.upper(),
            "origName": apt_ko(orig_iata.upper()) if orig_iata else "",
            "destName": apt_ko(dest_iata.upper()) if dest_iata else "",
            "origLat": orig_info.get("lat"),
            "origLon": orig_info.get("lon"),
            "destLat": dest_info.get("lat"),
            "destLon": dest_info.get("lon"),
        })
    except:
        pass

weather_js = []
for w in weather_data:
    if w["temp"] is None: continue
    weather_js.append({
        "name": w["name"], "lat": w["lat"], "lon": w["lon"],
        "temp": w["temp"], "rain": w["rain"] or 0,
        "wind_speed": w["wind_speed"] or 0, "wind_dir": w["wind_dir"] or 0,
        "humidity": w["humidity"] or 0,
        "icon": sky_icon(w.get("sky"), w.get("rain"), w.get("wind_speed")),
        "arrow": wind_arrow(w["wind_dir"]) if w["wind_dir"] is not None else "?"
    })

airports_js = [{"name": a["name"], "iata": a["iata"], "lat": a["lat"], "lon": a["lon"]} for a in AIRPORTS]

# 경로선용: 검색된 편명의 출발/도착 공항
tracked = st.session_state.get("tracked_flight_info", {})
route_json = json.dumps(tracked, ensure_ascii=False)

flights_json = json.dumps(flights_js, ensure_ascii=False)
weather_json = json.dumps(weather_js, ensure_ascii=False)
airports_json = json.dumps(airports_js, ensure_ascii=False)

# ── 국토부 항공편 정보 미리 로딩 ──

def is_domestic(dep_code, arr_code):
    """출발/도착 모두 국내공항이면 True"""
    return (dep_code.upper() in DOMESTIC_IATA and
            arr_code.upper() in DOMESTIC_IATA)

@st.cache_data(ttl=120)
def get_all_flight_schedule(callsigns):
    """편명별 출도착 정보 조회
    ※ 현재: search_flight_info가 빈 dict 반환 (ADS-B 방향 분석으로 대체)
    ※ 향후: TAGO/공항공사 API 활성화 시 정확한 데이터 제공
    """
    result = {}
    first_logged = False
    for cs in callsigns[:30]:
        try:
            items = search_flight_info(cs)
            if not items:
                continue
            item = items[0] if isinstance(items, list) else items

            if not first_logged:
                print(f"[SCHEDULE] {cs} 응답 필드: {list(item.keys())}")
                first_logged = True

            # 문서(p.5) TAGO 정확한 응답 필드
            dep_nm   = (item.get("depAirportNm") or "").strip()  # 출발공항 한글명
            arr_nm   = (item.get("arrAirportNm") or "").strip()  # 도착공항 한글명
            airline  = (item.get("airlineNm")    or "").strip()  # 항공사명
            dep_plan = (item.get("depPlandTime") or "").strip()  # 출발시간 YYYYMMDDHHmm
            arr_plan = (item.get("arrPlandTime") or "").strip()  # 도착시간 YYYYMMDDHHmm

            if not dep_nm and not arr_nm:
                continue

            # 한글 공항명 → IATA 코드 역탐색
            dep_code, arr_code = "", ""
            for iata, ko in AIRPORT_KO.items():
                if dep_nm and (ko == dep_nm or dep_nm in ko or ko in dep_nm):
                    dep_code = iata
                if arr_nm and (ko == arr_nm or arr_nm in ko or ko in arr_nm):
                    arr_code = iata

            dep_info = AIRPORT_COORDS.get(dep_code, {})
            arr_info = AIRPORT_COORDS.get(arr_code, {})

            result[cs] = {
                "depAirport":  dep_nm,
                "arrAirport":  arr_nm,
                "depCode":     dep_code,
                "arrCode":     arr_code,
                "depPlanTime": dep_plan,
                "arrPlanTime": arr_plan,
                "airline":     airline,
                "domestic":    True,  # TAGO는 국내선 전용
                "depLat":      dep_info.get("lat"),
                "depLon":      dep_info.get("lon"),
                "arrLat":      arr_info.get("lat"),
                "arrLon":      arr_info.get("lon"),
            }
            print(f"[TAGO-OK] {cs}: {dep_nm}({dep_code})→{arr_nm}({arr_code}) {airline}")
        except Exception as e:
            print(f"[ERR] schedule({cs}): {e}")

    return result

airborne_callsigns = [f[1].strip().upper() for f in flights if f[1] and f[1].strip() and not f[8]]
# TAGO vihicleId 샘플 출력으로 매칭 확인
_tago_cache = _load_tago_flights_cache()
if _tago_cache:
    _tago_sample = list(_tago_cache.keys())[:5]
    _cs_sample = airborne_callsigns[:5]
    print(f"[MATCH] TAGO 편명 샘플: {_tago_sample}")
    print(f"[MATCH] ADS-B 편명 샘플: {_cs_sample}")
flight_schedule = get_all_flight_schedule(tuple(airborne_callsigns))
flight_schedule_json = json.dumps(flight_schedule, ensure_ascii=False)

map_html = f"""
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body {{ margin:0; padding:0; background:#f5f7fa; }}
        #map {{ height:660px; width:100%; border-radius:12px; background:#e8ecf0; }}
        #weatherCanvas {{
            position:absolute; top:0; left:0;
            width:100%; height:100%;
            pointer-events:none;
            z-index:500;
            border-radius:12px;
        }}
        .map-wrap {{ position:relative; width:100%; height:660px; border-radius:12px; overflow:hidden; }}
        .weather-label {{
            background: rgba(255,255,255,0.88);
            border: 1px solid #b0c8e0;
            border-radius: 8px;
            padding: 5px 9px;
            font-size: 11px;
            font-family: Arial, sans-serif;
            color: #2c3e50;
            white-space: nowrap;
            box-shadow: 0 2px 6px rgba(0,0,0,0.15);
        }}
        .weather-label b {{ color: #1a5276; }}
        .airport-label {{
            background: rgba(13,27,42,0.8);
            border: 1px solid rgba(79,195,247,0.45);
            border-radius: 4px;
            padding: 2px 5px 2px 3px;
            font-size: 9px;
            font-family: Arial, sans-serif;
            color: #4fc3f7;
            white-space: nowrap;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 3px;
        }}
        .leaflet-popup-content-wrapper {{
            background: #fff !important;
            border: 1px solid #c5d8ea !important;
            color: #2c3e50 !important;
            border-radius: 10px !important;
            box-shadow: 0 4px 16px rgba(0,0,0,0.15) !important;
            padding: 0 !important;
        }}
        .leaflet-popup-content {{ margin: 0 !important; }}
        .leaflet-popup-tip {{ background: #fff !important; }}
        .leaflet-popup-close-button {{ color: #555 !important; top:8px !important; right:10px !important; font-size:18px !important; }}
        .legend-box {{
            position:absolute; bottom:10px; left:10px; z-index:1000;
            background:rgba(255,255,255,0.93); border:1px solid #cdd8e3;
            padding:10px 14px; border-radius:10px; font-size:11px; color:#2c3e50;
            box-shadow:0 2px 12px rgba(0,0,0,0.15);
            line-height: 1.8;
        }}
        .ctrl-box {{
            position:absolute; bottom:10px; right:10px; z-index:1000;
            background:rgba(255,255,255,0.93); border:1px solid #cdd8e3;
            padding:10px 14px; border-radius:10px; font-size:11px; color:#2c3e50;
            display:flex; flex-direction:column; gap:6px;
            box-shadow:0 2px 12px rgba(0,0,0,0.15);
        }}
        .ctrl-box label {{ display:flex; align-items:center; gap:7px; cursor:pointer; font-size:12px; color:#2c3e50; }}
        .ctrl-box input[type=checkbox] {{ accent-color:#1565c0; width:13px; height:13px; }}
        #clickNotice {{
            position:absolute; bottom:20px; right:20px; z-index:1000;
            background:rgba(21,101,192,0.9); border:1px solid #1565c0;
            padding:8px 14px; border-radius:10px; font-size:11px; color:#fff;
            display:none; animation: fadeout 3s forwards;
            box-shadow:0 2px 8px rgba(0,0,0,0.2);
        }}
        @keyframes fadeout {{ 0%{{opacity:1}} 70%{{opacity:1}} 100%{{opacity:0}} }}
        .plane-selected {{
            filter: drop-shadow(0 0 6px #4fc3f7) drop-shadow(0 0 12px #4fc3f7) !important;
        }}
    </style>
</head>
<body style="margin:0;padding:0;background:#0d1b2a;overflow:hidden;">
<div class="map-wrap">
    <div id="map"></div>
    <canvas id="weatherCanvas"></canvas>
    <div class="ctrl-box">
        <label><input type="checkbox" id="showRain" checked> 🌧️ 강수</label>
        <label><input type="checkbox" id="showWind" checked> 💨 바람</label>
        <label><input type="checkbox" id="showPlanes" checked> ✈️ 항공기</label>
        <label><input type="checkbox" id="showAirports" checked> 🗼 공항</label>
    </div>
    <div class="legend-box">
        <b style="color:#1565c0;letter-spacing:0.5px;">고도</b><br>
        <span style="color:#1565c0">✈</span> <span style="color:#444">8,000m+</span>&nbsp;&nbsp;
        <span style="color:#2e7d32">✈</span> <span style="color:#444">3~8km</span><br>
        <span style="color:#e65100">✈</span> <span style="color:#444">3,000m↓</span>&nbsp;
        <span style="color:#888">✈</span> <span style="color:#444">지상</span>
    </div>
    <div id="clickNotice">✈️ 편명 검색창에 자동 입력됩니다!</div>
</div>

<script>
var map = L.map('map', {{zoomControl:true}}).setView([36.5, 127.5], 7);

// ── 타일: OSM 표준 (가장 안정적) ──
L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 18,
    tileSize: 256,
    zoomOffset: 0
}}).addTo(map);

// 한국 경계선
fetch('https://raw.githubusercontent.com/southkorea/southkorea-maps/master/kostat/2018/json/skorea-provinces-2018-geo.json')
    .then(function(r) {{ return r.json(); }})
    .then(function(data) {{
        L.geoJSON(data, {{
            style: function() {{
                return {{ color:'#27ae60', weight:1.5, fillOpacity:0.03, fillColor:'#27ae60', opacity:0.8 }};
            }}
        }}).addTo(map);
    }}).catch(function(e) {{ console.log('GeoJSON 오류:', e); }});

var flightsData = {flights_json};
var weatherData = {weather_json};
var airportsData = {airports_json};
var flightSchedule = {flight_schedule_json};
var routeData = {route_json};
var showWeather = {'true' if show_weather else 'false'};
var planes = {{}};
var selectedCallsign = '';
var routeLayer = null;

// ── 비행 경로선 그리기 ──
function drawRoute(route) {{
    // 기존 항적 레이어 그룹 전체 제거
    if(routeLayer) {{ map.removeLayer(routeLayer); routeLayer = null; }}
    if(!route || !route.dep_lat || !route.arr_lat) return;

    var dep = [route.dep_lat, route.dep_lon];
    var arr = [route.arr_lat, route.arr_lon];
    var cur = route.cur_lat ? [route.cur_lat, route.cur_lon] : null;

    // LayerGroup으로 묶어서 한번에 삭제 가능하게
    routeLayer = L.layerGroup().addTo(map);

    // 지나온 경로 (회색 점선)
    if(cur) {{
        L.polyline([dep, cur], {{
            color:'#90a4ae', weight:3, dashArray:'6,5', opacity:0.75
        }}).addTo(routeLayer);
    }}
    // 남은 경로 (하늘색 실선)
    L.polyline([cur || dep, arr], {{
        color:'#4fc3f7', weight:3, dashArray:'10,6', opacity:0.9
    }}).addTo(routeLayer);

    // 출발 마커 🛫
    L.marker(dep, {{icon: L.divIcon({{
        className:'',
        html:'<div style="background:#1565c0;color:#fff;border-radius:50%;width:30px;height:30px;display:flex;align-items:center;justify-content:center;font-size:14px;box-shadow:0 2px 8px rgba(0,0,0,0.4);">🛫</div>',
        iconAnchor:[15,15]
    }})}}).bindTooltip('<b>' + (route.dep_name||'출발') + '</b>', {{permanent:true, direction:'top', className:''}}).addTo(routeLayer);

    // 도착 마커 🛬
    L.marker(arr, {{icon: L.divIcon({{
        className:'',
        html:'<div style="background:#c62828;color:#fff;border-radius:50%;width:30px;height:30px;display:flex;align-items:center;justify-content:center;font-size:14px;box-shadow:0 2px 8px rgba(0,0,0,0.4);">🛬</div>',
        iconAnchor:[15,15]
    }})}}).bindTooltip('<b>' + (route.arr_name||'도착') + '</b>', {{permanent:true, direction:'top', className:''}}).addTo(routeLayer);

    // 출발→목적지 전체가 보이도록 줌
    map.fitBounds([dep, arr], {{padding:[60,60]}});
}}

// 초기 로드 시 경로 그리기
if(routeData && routeData.dep_lat) {{
}}

// ── 공항 마커 ──
var airportMarkers = [];
airportsData.forEach(function(a) {{
    var icon = L.divIcon({{
        className: '',
        html: '<div class="airport-label"><svg width="14" height="14" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg" style="flex-shrink:0;"><rect x="38" y="55" width="12" height="35" fill="#4fc3f7"/><rect x="28" y="45" width="32" height="12" fill="#4fc3f7" rx="2"/><rect x="34" y="30" width="20" height="16" fill="#4fc3f7" rx="2"/><rect x="42" y="18" width="4" height="14" fill="#81c784"/><rect x="36" y="16" width="16" height="4" fill="#81c784" rx="1"/><path d="M58 62 L82 55 L85 58 L70 65 L85 72 L82 75 L58 68 Z" fill="#b0bec5"/></svg><span style="font-size:9px;font-weight:700;">' + a.iata + '</span></div>',
        iconAnchor: [20, 12]
    }});
    var m = L.marker([a.lat, a.lon], {{icon:icon}})
        .bindPopup(
            '<div style="font-family:Arial;color:#e0e6f0;min-width:140px;">' +
            '<b style="color:#4fc3f7">🏢 ' + a.name + '</b><br>' +
            '<span style="color:#7ab3d4">IATA: ' + a.iata + '</span>' +
            '</div>'
        ).addTo(map);
    airportMarkers.push(m);
}});

document.getElementById('showAirports').addEventListener('change', function() {{
    airportMarkers.forEach(function(m) {{
        if(this.checked) map.addLayer(m); else map.removeLayer(m);
    }}.bind(this));
}});

// ── 항공기 체크박스 ──
document.getElementById('showPlanes').addEventListener('change', function() {{
    var show = this.checked;
    Object.keys(planes).forEach(function(key) {{
        if(show) map.addLayer(planes[key].marker);
        else map.removeLayer(planes[key].marker);
    }});
}});

// ── 날씨(강수/바람) 체크박스 ──
document.getElementById('showRain').addEventListener('change', function() {{
    // clearRect로 즉시 지우고 다음 프레임에서 drawWeather가 알아서 처리
    if(!this.checked) {{
        drops.forEach(function(d) {{ d.alpha = 0; }});
    }} else {{
        drops.forEach(function(d) {{ d.alpha = 0.25 + Math.random()*0.3; }});
    }}
}});
document.getElementById('showWind').addEventListener('change', function() {{
    if(!this.checked) {{
        windParticles.forEach(function(p) {{ p.age = p.maxAge; }});
    }} else {{
        windParticles.forEach(function(p) {{ p.age = 0; }});
    }}
}});

// ── 항공기 ──
function getColor(alt, on_ground) {{
    if(on_ground) return '#9e9e9e';
    if(alt > 8000) return '#0d47a1';
    if(alt > 3000) return '#1b5e20';
    return '#bf360c';
}}

function getPlaneIcon(heading, color, isSelected, onGround) {{
    var glow = isSelected
        ? 'filter:drop-shadow(0 0 6px '+color+') drop-shadow(0 0 12px '+color+');'
        : 'filter:drop-shadow(1px 1px 2px rgba(0,0,0,0.5));';
    var size = isSelected ? '20px' : (onGround ? '14px' : '17px');
    var opacity = onGround ? '0.65' : '1';
    return L.divIcon({{
        className: '',
        html: '<div style="transform:rotate('+(heading-90)+'deg);font-size:'+size+';color:'+color+';opacity:'+opacity+';'+glow+'width:22px;height:22px;display:flex;align-items:center;justify-content:center;transition:all 0.3s;">✈</div>',
        iconSize: [22, 22], iconAnchor: [11, 11]
    }});
}}

function makePopup(f) {{
    var altFt = Math.round(f.altitude * 3.28084);
    var statusColor = f.on_ground ? '#757575' : '#2e7d32';
    var statusTxt   = f.on_ground ? '🛬 지상 대기' : '✈️ 비행 중';
    var descHtml = f.desc ? '<div style="font-size:11px;color:rgba(255,255,255,0.8);margin-top:2px;">' + f.desc + '</div>' : '';
    return [
        '<div style="font-family:Arial,sans-serif;min-width:200px;border-radius:10px;overflow:hidden;">',
        '<div style="background:linear-gradient(90deg,#1565c0,#1976d2);padding:10px 14px;">',
        '<div style="font-size:14px;font-weight:700;color:#fff;letter-spacing:1px;">✈ ' + f.callsign + '</div>',
        descHtml,
        '</div>',
        '<div style="padding:10px 12px;background:#fff;">',
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:8px;">',
        '<div style="background:#e3f2fd;border-radius:6px;padding:6px;text-align:center;">',
        '<div style="font-size:13px;font-weight:700;color:#1565c0;">' + Math.round(f.altitude) + 'm</div>',
        '<div style="font-size:9px;color:#5a8aaa;">' + altFt + ' ft</div>',
        '</div>',
        '<div style="background:#e8f5e9;border-radius:6px;padding:6px;text-align:center;">',
        '<div style="font-size:13px;font-weight:700;color:#2e7d32;">' + f.speed + ' km/h</div>',
        '<div style="font-size:9px;color:#5a8aaa;">속도</div>',
        '</div></div>',
        '<div style="font-size:11px;color:#555;line-height:1.8;border-top:1px solid #eee;padding-top:6px;">',
        '🌏 ' + f.country + '&nbsp;&nbsp;🧭 ' + Math.round(f.heading) + '°<br>',
        '<span style="color:' + statusColor + ';font-weight:600;">' + statusTxt + '</span>',
        '</div></div>',
        '<div style="padding:6px 12px 10px;background:#f8f9fa;border-top:1px solid #eee;text-align:center;">',
        '<div style="background:#1565c0;border-radius:6px;padding:6px;font-size:11px;color:#fff;cursor:pointer;font-weight:600;" title="' + f.callsign + '" onclick="window._selectFlight(this)">',
        '✅ 아래 검색창에 <b>' + f.callsign + '</b> 입력 후 검색</div></div></div>'
    ].join('');
}}

// 방향 기반 목적지 추정 함수 (개선버전)
function estimateDestination(f) {{
    if(!f || !f.lat || !f.lon || !f.heading) return null;

    // 고도 기반 최소 예상 거리 (순항 중이면 목적지가 멀다)
    var altM = f.altitude || 0;
    var minDist = altM > 6000 ? 150 : (altM > 3000 ? 80 : 30);
    var maxDist = 1500;
    var angleTol = altM > 6000 ? 35 : 50;  // 순항 중엔 방향이 더 정확

    var best = null, bestScore = 9999;
    airportsData.forEach(function(a) {{
        var dy = a.lat - f.lat, dx = a.lon - f.lon;
        var dist = Math.sqrt(dy*dy + dx*dx) * 111;
        if(dist < minDist || dist > maxDist) return;

        var angleTo = (Math.atan2(dx, dy) * 180 / Math.PI + 360) % 360;
        var diff = Math.abs(((angleTo - f.heading + 180) % 360) - 180);
        if(diff > angleTol) return;

        // 각도 오차 위주, 거리는 보조
        var score = diff * 2.0 + (dist / 100);
        if(score < bestScore) {{
            bestScore = score;
            best = a;
        }}
    }});
    return best;
}}

window._selectFlight = function(el) {{
    selectFlight(el.getAttribute('title') || '');
}};

function selectFlight(callsign) {{
    // 이전 선택 해제
    if(selectedCallsign && planes[selectedCallsign]) {{
        var old = planes[selectedCallsign];
        old.marker.setIcon(getPlaneIcon(old.heading, getColor(old.altitude, old.on_ground), false));
    }}
    selectedCallsign = callsign;
    if(planes[callsign]) {{
        var p = planes[callsign];
        p.marker.setIcon(getPlaneIcon(p.heading, getColor(p.altitude, p.on_ground), true));
    }}
    // Streamlit iframe 환경에서는 pushState 차단됨 → parent로만 전달
    try {{
        if(window.parent && window.parent !== window) {{
            window.parent.postMessage({{type:'streamlit:setComponentValue', value:callsign}}, '*');
        }}
    }} catch(e) {{}}
    var notice = document.getElementById('clickNotice');
    notice.innerHTML = '✈️ <b>' + callsign + '</b> 선택됨! 아래 검색창에 입력하세요';
    notice.style.display = 'block';
    notice.style.animation = 'none';
    notice.offsetHeight;
    notice.style.animation = 'fadeout 4s forwards';
    setTimeout(function(){{ notice.style.display='none'; }}, 4000);
}}

function predictPosition(lat, lon, speedKmh, headingDeg, seconds) {{
    var R = 6371, d = (speedKmh * seconds / 3600) / R, hdg = headingDeg * Math.PI / 180;
    var lat1 = lat * Math.PI / 180, lon1 = lon * Math.PI / 180;
    var lat2 = Math.asin(Math.sin(lat1) * Math.cos(d) + Math.cos(lat1) * Math.sin(d) * Math.cos(hdg));
    var lon2 = lon1 + Math.atan2(Math.sin(hdg) * Math.sin(d) * Math.cos(lat1), Math.cos(d) - Math.sin(lat1) * Math.sin(lat2));
    return {{lat: lat2 * 180 / Math.PI, lon: lon2 * 180 / Math.PI}};
}}

function updateFlights(data) {{
    var newKeys = new Set();
    data.forEach(function(f) {{
        if(!f.lat || !f.lon) return;
        var key = f.callsign; newKeys.add(key);
        var color = getColor(f.altitude, f.on_ground);
        var isSelected = (key === selectedCallsign);
        // var popup = makePopup(f); // 미니 패널 방식으로 대체
        if(planes[key]) {{
            planes[key].lat = f.lat; planes[key].lon = f.lon;
            planes[key].speed = f.speed; planes[key].heading = f.heading;
            planes[key].altitude = f.altitude; planes[key].on_ground = f.on_ground;
            planes[key].marker.setIcon(getPlaneIcon(f.heading, color, isSelected, f.on_ground));
            // popup 업데이트 없음 (미니 패널 방식 사용)
        }} else {{
            var marker = L.marker([f.lat, f.lon], {{icon: getPlaneIcon(f.heading, color, isSelected, f.on_ground)}})
                .bindTooltip('<b style="color:#4fc3f7">' + f.callsign + '</b>', {{direction:'top', className:''}});
            // 클릭 이벤트: 편명 자동 검색
            marker.on('click', function() {{
                selectFlight(key);
            }});
            if(document.getElementById('showPlanes').checked) marker.addTo(map);
            planes[key] = {{
                marker: marker,
                lat: f.lat, lon: f.lon, speed: f.speed,
                heading: f.heading, altitude: f.altitude, on_ground: f.on_ground
            }};
        }}
    }});
    Object.keys(planes).forEach(function(key) {{
        if(!newKeys.has(key)) {{ map.removeLayer(planes[key].marker); delete planes[key]; }}
    }});
}}

function tickMovement() {{
    if(!document.getElementById('showPlanes').checked) return;
    Object.keys(planes).forEach(function(key) {{
        var p = planes[key];
        if(p.on_ground || p.speed < 10) return;
        var next = predictPosition(p.lat, p.lon, p.speed, p.heading, 1);
        p.lat = next.lat; p.lon = next.lon;
        p.marker.setLatLng([p.lat, p.lon]);
    }});
}}

updateFlights(flightsData);
setInterval(tickMovement, 1000);

// 날씨 라벨 제거됨 (하단 패널에서 표시)

// ── 기상 애니메이션 Canvas ──
var cvs = document.getElementById('weatherCanvas');
var ctx = cvs.getContext('2d');

function resizeCanvas() {{ cvs.width = cvs.offsetWidth; cvs.height = cvs.offsetHeight; }}
resizeCanvas();

function latLonToXY(lat, lon) {{
    var point = map.latLngToContainerPoint([lat, lon]);
    return {{x: point.x, y: point.y}};
}}

var rainZones = weatherData.filter(function(w) {{
    return w.rain > 0 || w.wind_speed > 5;
}}).map(function(w) {{
    return {{lat:w.lat, lon:w.lon, intensity:Math.min(w.rain/5,1)+0.2, wind_speed:w.wind_speed, wind_dir:w.wind_dir}};
}});
if(rainZones.length === 0) {{
    rainZones = [
        {{lat:33.5,lon:126.5,intensity:0.3,wind_speed:3,wind_dir:315}},
        {{lat:34.8,lon:128.5,intensity:0.25,wind_speed:2.5,wind_dir:300}},
    ];
}}

var drops = [];
function initDrops() {{
    drops = [];
    rainZones.forEach(function(z) {{
        var xy = latLonToXY(z.lat, z.lon);
        var r = 80 + z.intensity * 60;
        var count = Math.floor(z.intensity * 80);
        for(var i=0; i<count; i++) {{
            var angle = Math.random()*Math.PI*2;
            var dist = Math.random()*r;
            drops.push({{
                x: xy.x + Math.cos(angle)*dist,
                y: Math.random()*cvs.height,
                speed: 2.5 + Math.random()*3,
                len: 8 + Math.random()*10,
                alpha: 0.2 + Math.random()*0.4,
                zone: z,
                radius: r
            }});
        }}
    }});
}}

var windParticles = [];
function initWind() {{
    windParticles = [];
    for(var i=0; i<120; i++) {{
        windParticles.push({{
            x: Math.random()*cvs.width,
            y: Math.random()*cvs.height,
            age: Math.floor(Math.random()*80),
            maxAge: 60 + Math.floor(Math.random()*50)
        }});
    }}
}}

var t = 0;
var avgWindDir = 315, avgWindSpd = 3;
if(weatherData.length > 0) {{
    var totalU=0, totalV=0;
    weatherData.forEach(function(w) {{
        var rad = w.wind_dir * Math.PI/180;
        totalU += Math.sin(rad)*w.wind_speed;
        totalV += Math.cos(rad)*w.wind_speed;
    }});
    avgWindDir = Math.atan2(totalU/weatherData.length, totalV/weatherData.length)*180/Math.PI;
    avgWindSpd = Math.sqrt(totalU*totalU+totalV*totalV)/weatherData.length;
}}

function windU(x,y,t) {{
    return (Math.sin(avgWindDir*Math.PI/180) + Math.sin(y*0.008+t*0.01)*0.3) * avgWindSpd * 0.15;
}}
function windV(x,y,t) {{
    return (Math.cos(avgWindDir*Math.PI/180) + Math.cos(x*0.006+t*0.008)*0.3) * avgWindSpd * 0.12;
}}

map.on('moveend zoomend', function() {{ resizeCanvas(); initDrops(); initWind(); }});
initDrops(); initWind();

function drawWeather() {{
    ctx.clearRect(0,0,cvs.width,cvs.height);
    var showRainCk = document.getElementById('showRain').checked;
    var showWindCk = document.getElementById('showWind').checked;

    if(showRainCk) {{
        rainZones.forEach(function(z) {{
            var xy = latLonToXY(z.lat, z.lon);
            var pulse = Math.sin(t*0.05)*0.12;
            var r = (80 + z.intensity*60)*(1+pulse);
            var grd = ctx.createRadialGradient(xy.x,xy.y,0,xy.x,xy.y,r);
            grd.addColorStop(0,'rgba(41,128,185,'+(z.intensity*0.18)+')');
            grd.addColorStop(0.5,'rgba(41,128,185,'+(z.intensity*0.07)+')');
            grd.addColorStop(1,'rgba(0,0,0,0)');
            ctx.beginPath(); ctx.arc(xy.x,xy.y,r,0,Math.PI*2);
            ctx.fillStyle=grd; ctx.fill();
        }});
        var u0=windU(cvs.width/2,cvs.height/2,t);
        var v0=windV(cvs.width/2,cvs.height/2,t);
        var rainAngle=Math.atan2(u0, Math.abs(v0)*2);
        drops.forEach(function(d) {{
            ctx.strokeStyle='rgba(100,181,246,'+d.alpha+')';
            ctx.lineWidth=0.9;
            ctx.beginPath(); ctx.moveTo(d.x,d.y);
            ctx.lineTo(d.x+Math.sin(rainAngle)*d.len, d.y+Math.cos(rainAngle)*d.len);
            ctx.stroke();
            d.x+=windU(d.x,d.y,t)*0.5; d.y+=d.speed;
            if(d.y > cvs.height+10) {{
                var angle=Math.random()*Math.PI*2;
                var dist=Math.random()*d.radius;
                var cxy=latLonToXY(d.zone.lat,d.zone.lon);
                d.x=cxy.x+Math.cos(angle)*dist; d.y=-10;
            }}
        }});
    }}

    if(showWindCk) {{
        windParticles.forEach(function(p) {{
            var u=windU(p.x,p.y,t), v=windV(p.x,p.y,t);
            var spd=Math.sqrt(u*u+v*v);
            var fadeIn=Math.min(p.age/15,1);
            var fadeOut=Math.max(0,1-(p.age-p.maxAge*0.6)/(p.maxAge*0.4));
            var alpha=fadeIn*fadeOut*0.45;
            ctx.strokeStyle='rgba('+(80+Math.round(spd*40))+','+(140+Math.round(spd*30))+',220,'+alpha.toFixed(2)+')';
            ctx.lineWidth=0.8+spd*0.2;
            ctx.beginPath(); ctx.moveTo(p.x,p.y);
            p.x+=u; p.y+=v; p.age++;
            ctx.lineTo(p.x,p.y); ctx.stroke();
            if(p.age>p.maxAge||p.x<0||p.x>cvs.width||p.y<0||p.y>cvs.height) {{
                p.x=Math.random()*cvs.width; p.y=Math.random()*cvs.height;
                p.age=0; p.maxAge=60+Math.floor(Math.random()*50);
            }}
        }});
    }}
    t++;
    requestAnimationFrame(drawWeather);
}}
drawWeather();

// ── 지도 내 미니 정보 패널 (클릭 시 즉시 표시) ──
var infoPanel = document.createElement('div');
infoPanel.id = 'infoPanel';
infoPanel.style.cssText = [
    'position:absolute',
    'top:10px',
    'right:10px',
    'z-index:2000',
    'background:#ffffff',
    'border:1px solid #dce8f5',
    'border-radius:12px',
    'padding:14px 16px',
    'width:268px',
    'max-width:268px',
    'display:none',
    'font-family:Arial,sans-serif',
    'box-shadow:0 4px 20px rgba(0,0,0,0.18)',
    'color:#263238',
    'overflow-y:auto',
    'max-height:640px'
].join(';');
document.querySelector('.map-wrap').appendChild(infoPanel);

function closeInfoPanel() {{
    document.getElementById('infoPanel').style.display = 'none';
    selectedCallsign = '';
}}

function fmtTime(t) {{
    // "20250504083000" → "08:30"
    if(!t || t.length < 12) return '';
    return t.substr(8,2) + ':' + t.substr(10,2);
}}

function squawkBadge(sq) {{
    if(!sq) return '';
    var color = '#555', label = sq;
    if(sq==='7700') {{ color='#c62828'; label='7700 긴급'; }}
    else if(sq==='7600') {{ color='#e65100'; label='7600 통신불능'; }}
    else if(sq==='7500') {{ color='#ad1457'; label='7500 하이재킹'; }}
    return '<span style="background:'+color+';color:#fff;font-size:9px;padding:2px 6px;border-radius:4px;margin-left:4px;">SQWK '+label+'</span>';
}}

function showInfoPanel(f, route) {{
    route = route || {{}};
    var altFt  = Math.round((f.altitude||0) * 3.28084);
    var spdKts = Math.round((f.speed||0) / 1.852);
    var altColor = f.on_ground ? '#757575'
        : (f.altitude > 8000 ? '#1565c0' : (f.altitude > 3000 ? '#2e7d32' : '#e65100'));

    var statusBg  = f.on_ground ? '#f5f5f5' : '#e8f5e9';
    var statusClr = f.on_ground ? '#757575' : '#2e7d32';
    var statusTxt = f.on_ground ? '🛬 지상' : '✈️ 비행중';

    var depCode = route.depCode || '';
    var arrCode = route.arrCode || '';
    var depName = route.depName || '';
    var arrName = route.arrName || '';
    var depT    = route.depT   || '';
    var arrT    = route.arrT   || '';
    var airline = route.airline || '';
    var src     = route.src    || '';
    var hasRoute = !!(depCode || arrCode);

    var routeHtml = '';
    if(hasRoute) {{
        routeHtml =
            '<div style="margin:8px 0;background:#f0f7ff;border:1px solid #bbdefb;border-radius:8px;padding:10px;">' +
            '<div style="display:flex;align-items:center;">' +
            '<div style="flex:1;text-align:center;">' +
            '<div style="font-size:20px;font-weight:900;color:#1565c0;">' + (depCode||'—') + '</div>' +
            '<div style="font-size:10px;color:#5a7fa0;">' + (depName||'') + '</div>' +
            (depT ? '<div style="font-size:9px;color:#90a4ae;">예정 <b style="color:#546e7a">' + depT + '</b></div>' : '') +
            '</div>' +
            '<div style="padding:0 8px;color:#90caf9;font-size:22px;font-weight:900;">→</div>' +
            '<div style="flex:1;text-align:center;">' +
            '<div style="font-size:20px;font-weight:900;color:#1565c0;">' + (arrCode||'—') + '</div>' +
            '<div style="font-size:10px;color:#5a7fa0;">' + (arrName||'') + '</div>' +
            (arrT ? '<div style="font-size:9px;color:#90a4ae;">예정 <b style="color:#546e7a">' + arrT + '</b></div>' : '') +
            '</div>' +
            '</div>' +
            (airline ? '<div style="margin-top:5px;border-top:1px solid #bbdefb;padding-top:4px;font-size:9px;color:#90a4ae;display:flex;justify-content:space-between;"><span>' + airline + '</span>' + (src ? '<span style="color:#26a69a;">📡 ' + src + '</span>' : '') + '</div>' : '') +
            '</div>';
    }}

    var html =
        // 헤더
        '<div style="display:flex;align-items:center;justify-content:space-between;padding-bottom:8px;border-bottom:1px solid #e3eaf0;margin-bottom:8px;">' +
        '<span style="font-size:18px;font-weight:900;color:#1a237e;letter-spacing:1px;">' + (f.callsign||'미확인') + '</span>' +
        '<div style="display:flex;align-items:center;gap:6px;">' +
        '<span style="background:' + statusBg + ';color:' + statusClr + ';font-size:10px;padding:2px 9px;border-radius:12px;border:1px solid ' + statusClr + '44;font-weight:600;">' + statusTxt + '</span>' +
        '<span style="cursor:pointer;color:#9e9e9e;font-size:18px;line-height:1;" onclick="closeInfoPanel()">✕</span>' +
        '</div></div>' +
        // 기종/등록
        '<div style="display:flex;flex-wrap:wrap;gap:4px;margin-bottom:8px;">' +
        (f.desc ? '<span style="background:#e3f2fd;border:1px solid #90caf9;color:#1565c0;font-size:10px;padding:2px 8px;border-radius:4px;font-weight:600;">✈ ' + f.desc + '</span>' : '') +
        (f.reg  ? '<span style="background:#e8eaf6;border:1px solid #9fa8da;color:#283593;font-size:10px;padding:2px 8px;border-radius:4px;">' + f.reg + '</span>' : '') +
        '<span style="background:#f3f3f3;border:1px solid #ddd;color:#555;font-size:10px;padding:2px 8px;border-radius:4px;">🌏 ' + (f.country||'미확인') + '</span>' +
        '</div>' +
        routeHtml +
        // 수치 3칸
        '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:5px;margin-bottom:8px;">' +
        '<div style="text-align:center;background:#e3f2fd;border-radius:8px;padding:8px 4px;">' +
        '<div style="font-size:14px;font-weight:700;color:' + altColor + ';">' + Math.round(f.altitude||0) + 'm</div>' +
        '<div style="font-size:8px;color:#78909c;margin-top:2px;">고도</div>' +
        '<div style="font-size:8px;color:#b0bec5;">' + altFt + 'ft</div>' +
        '</div>' +
        '<div style="text-align:center;background:#e8f5e9;border-radius:8px;padding:8px 4px;">' +
        '<div style="font-size:14px;font-weight:700;color:#2e7d32;">' + (f.speed||0) + '<span style="font-size:8px">km/h</span></div>' +
        '<div style="font-size:8px;color:#78909c;margin-top:2px;">속도</div>' +
        '<div style="font-size:8px;color:#b0bec5;">' + spdKts + 'kts</div>' +
        '</div>' +
        '<div style="text-align:center;background:#f3e5f5;border-radius:8px;padding:8px 4px;">' +
        '<div style="font-size:14px;font-weight:700;color:#6a1b9a;">' + Math.round(f.heading||0) + '°</div>' +
        '<div style="font-size:8px;color:#78909c;margin-top:2px;">방향</div>' +
        '<div style="font-size:8px;color:#b0bec5;">&nbsp;</div>' +
        '</div>' +
        '</div>' +
        // ICAO/좌표
        '<div style="font-size:9px;color:#b0bec5;display:flex;justify-content:space-between;border-top:1px solid #eceff1;padding-top:5px;">' +
        '<span style="color:#90a4ae;">ICAO <b style="color:#1565c0">' + (f.icao||'').toUpperCase() + '</b></span>' +
        '<span>📍 ' + (f.lat||0).toFixed(3) + ', ' + (f.lon||0).toFixed(3) + '</span>' +
        '</div>';

    infoPanel.innerHTML = html;
    infoPanel.style.display = 'block';
}}

// ── selectFlight 확장: 패널 + ADS-B 기반 항적 ──
var _origSelectFlight = selectFlight;
selectFlight = function(callsign) {{
    // 같은 편명 재클릭 시에도 패널 다시 열기
    _origSelectFlight(callsign);
    var fd = flightsData.find(function(f) {{ return f.callsign === callsign; }});
    if(!fd) return;

    // ── 출도착 정보 계산 (팝업 + 항적 공통 사용) ──
    var sch = flightSchedule[callsign] || {{}};
    console.log('[SKYWATCH] callsign:', callsign, 'sch:', JSON.stringify(sch));
    var depCode, arrCode, depName, arrName, routeSrc;

    if(fd.origLat && fd.destLat) {{
        // 1순위: ADS-B orig/dest
        depLat = fd.origLat; depLon = fd.origLon;
        arrLat = fd.destLat; arrLon = fd.destLon;
        depCode = fd.orig; arrCode = fd.dest;
        depName = fd.origName || fd.orig;
        arrName = fd.destName || fd.dest;
        routeSrc = 'ADS-B';
    }} else if(sch.arrAirport || sch.depAirport) {{
        // 2순위: TAGO 공공API
        depCode = sch.depCode || sch.depAirport || '';
        arrCode = sch.arrCode || sch.arrAirport || '';
        depName = sch.depAirport || '';
        arrName = sch.arrAirport || '';
        routeSrc = '공공API';
    }}

    // 팝업에 출도착 정보 전달 후 표시
    showInfoPanel(fd, {{
        depCode: depCode, depName: depName,
        arrCode: arrCode, arrName: arrName,
        depT: fmtTime(sch.depPlanTime),
        arrT: fmtTime(sch.arrPlanTime),
        airline: sch.airline || '',
        src: routeSrc || ''
    }});

}};
</script>
</body>
</html>
"""
st.components.v1.html(map_html, height=700, scrolling=False)

# ── 지도 클릭 → 편명 자동 입력 처리 ──
# query_params에서 클릭된 편명 감지
url_flight = st.query_params.get("flight", "")
if url_flight:
    st.session_state.callsign_input = url_flight

st.markdown("---")

# ── 하단 4칸: @st.fragment로 분리 → 검색 시 지도 영역 재렌더링 없음 ──
@st.fragment
def bottom_panel():
    # flights 데이터는 fragment 안에서도 session_state 경유로 접근
    flights = st.session_state.get("_flights_cache", [])

    col_l, col_ml, col_mr, col_r = st.columns([1, 1, 1, 1])

    with col_l:
        st.markdown('<div class="section-title">🔍 편명 검색</div>', unsafe_allow_html=True)
        st.markdown('<div class="click-hint">💡 지도에서 항공기를 클릭하면 자동 입력돼요</div>', unsafe_allow_html=True)

        callsign_input = st.text_input(
            "편명 입력",
            placeholder="✈️ 편명 입력 (예: KAL017, AAR101)",
            value=st.session_state.callsign_input,
            key="callsign_text",
            label_visibility="collapsed"
        )
        search_btn = st.button("🔍 검색", use_container_width=True)

        # 엔터키(입력값 변경) 또는 버튼 클릭 모두 검색 실행
        do_search = search_btn or (
            callsign_input and
            callsign_input != st.session_state.get("_last_searched", "")
        )

        if do_search and callsign_input:
            st.session_state["_last_searched"] = callsign_input
            with st.spinner("검색 중..."):
                _fl = st.session_state.get("_flights_cache", [])
                current_flight = next(
                    (f for f in _fl if f[1] and f[1].strip().upper() == callsign_input.strip().upper()),
                    None
                )
                if current_flight:
                    alt = current_flight[7] or 0
                    spd = (current_flight[9] or 0) * 3.6
                    hdg = current_flight[10] or 0
                    cty = current_flight[2] or "알 수 없음"
                    desc = current_flight[11] if len(current_flight) > 11 else ""
                    cur_lat, cur_lon = current_flight[6], current_flight[5]

                    st.markdown(f"""
                    <div class="result-card">
                        <div class="result-title">✈️ {callsign_input.upper()} {("— "+desc) if desc else ""}</div>
                        <div>
                            <div class="result-metric"><div class="rm-val">{alt:.0f}m</div><div class="rm-label">고도</div></div>
                            <div class="result-metric"><div class="rm-val">{spd:.0f}km/h</div><div class="rm-label">속도</div></div>
                            <div class="result-metric"><div class="rm-val">{hdg:.0f}°</div><div class="rm-label">방향</div></div>
                            <div class="result-metric"><div class="rm-val">{cty}</div><div class="rm-label">등록국</div></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # 공항 근접 체크
                    nearest = min(AIRPORTS, key=lambda a: dist_km(cur_lat, cur_lon, a["lat"], a["lon"]))
                    d_near = dist_km(cur_lat, cur_lon, nearest["lat"], nearest["lon"])
                    if d_near < 80 and alt < 5000:
                        st.markdown(f"""
                        <div class="arrival-alert">
                            🛬 <b style="color:#76c442">{nearest["name"]} ({nearest["iata"]}) 근접!</b><br>
                            <span style="font-size:0.8rem;color:#b8e986;">거리 {d_near:.0f}km | 고도 {alt:.0f}m</span>
                        </div>
                        """, unsafe_allow_html=True)
                    st.session_state.show_3d_flight = current_flight
                else:
                    st.warning(f"현재 상공에서 **{callsign_input.upper()}** 를 찾을 수 없어요.")
                    st.session_state.show_3d_flight = None
                    current_flight = None
                    cur_lat = cur_lon = None

                # 국내선 운항 정보 (공공API)
                domestic = search_flight_info(callsign_input)
                found_dep = None
                found_dest = None
                sched_dep_t = ""
                sched_arr_t = ""

                if domestic:
                    item = domestic[0]
                    dep_nm  = item.get("depAirportNm", "")
                    arr_nm  = item.get("arrAirportNm", "")
                    dep_t   = str(item.get("depPlandTime", ""))
                    arr_t   = str(item.get("arrPlandTime", ""))
                    airline = item.get("airlineNm", "")
                    sched_dep_t = f"{dep_t[8:10]}:{dep_t[10:12]}" if len(dep_t) >= 12 else dep_t
                    sched_arr_t = f"{arr_t[8:10]}:{arr_t[10:12]}" if len(arr_t) >= 12 else arr_t

                    st.markdown(f"""
                    <div class="result-card">
                        <div class="result-title">🛫 국내선 운항정보</div>
                        <div style="color:#b0c4d8;font-size:0.88rem;">
                            {airline}<br>
                            <b style="color:#4fc3f7">{dep_nm}</b> {sched_dep_t}
                            &nbsp;→&nbsp;
                            <b style="color:#ffa726">{arr_nm}</b> {sched_arr_t}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    for a in AIRPORTS:
                        if dep_nm and (a["keyword"] in dep_nm or dep_nm in a["name"]):
                            found_dep = a
                        if arr_nm and (a["keyword"] in arr_nm or arr_nm in a["name"]):
                            found_dest = a

                # fallback: 방향+위치로 목적지 추론
                if not found_dest and current_flight:
                    lat, lon = current_flight[6], current_flight[5]
                    hdg = current_flight[10] or 0
                    candidates = []
                    for a in AIRPORTS:
                        d = dist_km(lat, lon, a["lat"], a["lon"])
                        if d < 5: continue
                        dy = a["lat"] - lat
                        dx = a["lon"] - lon
                        angle_to = (math.degrees(math.atan2(dx, dy)) + 360) % 360
                        angle_diff = abs(((angle_to - hdg + 180) % 360) - 180)
                        candidates.append((angle_diff, d, a))
                    if candidates:
                        candidates.sort(key=lambda x: x[0] * 0.5 + x[1] * 0.1)
                        best_angle, best_dist, best_airport = candidates[0]
                        if best_angle < 90:
                            found_dest = best_airport
                            st.markdown(f"""
                            <div class="result-card" style="border-color:#1565c0;">
                                <div style="font-size:0.78rem;color:#7ab3d4;">📡 추정 목적지 (방향 분석)</div>
                                <b style="color:#4fc3f7">→ {best_airport["name"]} ({best_airport["iata"]})</b>
                                <div style="font-size:0.75rem;color:#888;">{best_dist:.0f}km | 편차 {best_angle:.0f}°</div>
                            </div>
                            """, unsafe_allow_html=True)

                # tracked_flight_info 저장 (지도 경로선용)
                tracked = {}
                if current_flight:
                    tracked["cur_lat"] = current_flight[6]
                    tracked["cur_lon"] = current_flight[5]
                if found_dep:
                    tracked["dep_lat"] = found_dep["lat"]
                    tracked["dep_lon"] = found_dep["lon"]
                    tracked["dep_name"] = found_dep["name"]
                if found_dest:
                    tracked["arr_lat"] = found_dest["lat"]
                    tracked["arr_lon"] = found_dest["lon"]
                    tracked["arr_name"] = found_dest["name"]
                st.session_state.tracked_flight_info = tracked
                st.session_state.dest_airport = found_dest
                st.session_state.dep_airport  = found_dep
                st.session_state.current_flight = current_flight
                st.session_state.flight_spd = (current_flight[9] or 0) * 3.6 if current_flight else 0

                # ── AI 분석용 데이터 저장 ──
                spd_kmh = (current_flight[9] or 0) * 3.6 if current_flight else 0
                prog_ai = None
                if current_flight and found_dep and found_dest:
                    prog_ai = calc_flight_progress(
                        current_flight[6], current_flight[5],
                        found_dep, found_dest, spd_kmh
                    )
                st.session_state["searched_callsign"] = callsign_input
                st.session_state["ai_callsign"] = current_flight[1] if current_flight else callsign_input
                st.session_state["ai_dep"]   = found_dep["name"]  if found_dep  else "알 수 없음"
                st.session_state["ai_arr"]   = found_dest["name"] if found_dest else "알 수 없음"
                st.session_state["ai_alt"]   = current_flight[7]  if current_flight else "알 수 없음"
                st.session_state["ai_speed"] = round(spd_kmh)     if spd_kmh else "알 수 없음"
                st.session_state["ai_eta"]   = prog_ai["eta_time"] if prog_ai and prog_ai.get("eta_time") else "계산 중"
                if found_dest:
                    st.session_state["ai_weather"] = get_airport_weather(found_dest["nx"], found_dest["ny"])
                    st.session_state["ai_delays"]  = get_airport_delays(found_dest["keyword"])
                else:
                    st.session_state["ai_weather"] = {}
                    st.session_state["ai_delays"]  = []

    dest_airport   = st.session_state.get("dest_airport")
    dep_airport    = st.session_state.get("dep_airport")
    current_flight = st.session_state.get("current_flight")
    flight_spd     = st.session_state.get("flight_spd", 0)

    # ── col_ml: 비행 진행률 + ETA + 도착 임박 알림 ──
    with col_ml:
        st.markdown('<div class="section-title">📊 비행 진행률</div>', unsafe_allow_html=True)

        if current_flight and dest_airport:
            cur_lat = current_flight[6]
            cur_lon = current_flight[5]
            # dep_airport 없으면 현재위치에서 가장 먼 공항을 출발지로 추정
            eff_dep = dep_airport
            if not eff_dep:
                eff_dep = max(AIRPORTS, key=lambda a: dist_km(cur_lat, cur_lon, a["lat"], a["lon"]))
            # 출발지와 목적지가 같으면 진행률 계산 불가
            if eff_dep and eff_dep["iata"] == dest_airport["iata"]:
                eff_dep = None
            prog = calc_flight_progress(cur_lat, cur_lon, eff_dep, dest_airport, flight_spd)

            if prog:
                pct = prog["progress"]
                eta_min = prog["eta_min"]
                eta_time = prog["eta_time"]
                remain_km = prog["remain_km"]
                total_km = prog["total_km"]

                dep_label = eff_dep["iata"] if eff_dep else "출발"
                arr_label = dest_airport["iata"]

                # 진행률 바
                st.markdown(f"""
                <div class="progress-card">
                    <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                        <span class="airport-badge">🛫 {dep_label}</span>
                        <span style="font-size:0.85rem;color:#4fc3f7;font-weight:700;">{pct:.0f}%</span>
                        <span class="airport-badge">🛬 {arr_label}</span>
                    </div>
                    <div class="progress-bar-wrap">
                        <div class="progress-bar-fill" style="width:{pct}%;">
                            <span style="position:absolute;right:-10px;top:50%;transform:translateY(-50%);font-size:16px;">✈️</span>
                        </div>
                    </div>
                    <div style="display:flex;justify-content:space-between;font-size:0.72rem;color:#7ab3d4;margin-top:4px;">
                        <span>총 {total_km}km</span>
                        <span>남은거리 {remain_km}km</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # ETA 카드
                if eta_time:
                    st.markdown(f"""
                    <div class="result-card" style="text-align:center;padding:14px;">
                        <div style="font-size:0.75rem;color:#7ab3d4;margin-bottom:4px;">예상 도착 시각 (KST)</div>
                        <div class="eta-big">🕐 {eta_time}</div>
                        <div class="eta-label">약 {eta_min}분 후</div>
                    </div>
                    """, unsafe_allow_html=True)

                # 도착 임박 알림
                if eta_min is not None and eta_min <= 20:
                    st.markdown(f"""
                    <div class="arrival-alert">
                        🔔 <b style="color:#76c442">도착 임박!</b><br>
                        <span style="font-size:0.85rem;color:#b8e986;">
                            {dest_airport["name"]}까지<br>
                            약 <b>{eta_min}분</b> 남았어요
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                elif eta_min is not None and eta_min <= 45:
                    st.markdown(f"""
                    <div class="arrival-alert-warn">
                        ⏰ <b style="color:#ffa726">곧 도착</b><br>
                        <span style="font-size:0.85rem;color:#ffe0b2;">약 {eta_min}분 후 도착 예정</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert-banner" style="border-color:#4a6080;color:#7ab3d4;">경로 정보를 계산하는 중이에요</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-banner" style="border-color:#4a6080;color:#7ab3d4;">✈️ 편명 검색하면 진행률이 표시돼요</div>', unsafe_allow_html=True)

        # 지연·결항 (접어서)
        if dest_airport:
            st.markdown(f'<div class="section-title" style="margin-top:14px;">🚨 지연·결항</div>', unsafe_allow_html=True)
            airport_delays = get_airport_delays(dest_airport["keyword"])
            if airport_delays:
                for d in airport_delays[:3]:
                    sched = str(d["sched"])
                    sched_fmt = f"{sched[8:10]}:{sched[10:12]}" if len(sched) >= 12 else sched
                    is_cancel = any(kw in str(d["remark"]) for kw in ["결항","Cancel","취소"])
                    card_color = "#c0392b" if is_cancel else "#e67e22"
                    status_icon = "🚫 결항" if is_cancel else "🕐 지연"
                    st.markdown(f"""
                    <div class="alert-banner" style="border-color:{card_color};margin:3px 0;padding:8px 12px;">
                        <span style="color:{card_color};font-weight:600;">{status_icon}</span>
                        &nbsp;<b style="color:#fff">{d["flight_id"]}</b> {d["airline"]}<br>
                        <span style="font-size:0.75rem;color:#cd8888;">{sched_fmt} | {d["remark"]}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert-banner" style="border-color:#27ae60;color:#7ecba1;padding:8px 12px;">✅ 지연·결항 없음</div>', unsafe_allow_html=True)

    # ── col_mr: 목적지 날씨 + 시간대별 예보 ──
    with col_mr:
        if dest_airport:
            st.markdown(f'<div class="section-title">🌤️ {dest_airport["name"]} 날씨</div>', unsafe_allow_html=True)
            apt_weather = get_airport_weather(dest_airport["nx"], dest_airport["ny"])
            if apt_weather and apt_weather["temp"] is not None:
                w = apt_weather
                sky_i   = sky_icon(w.get("sky"), w.get("rain"), w.get("wind_speed"))
                w_arrow = wind_arrow(w["wind_dir"])
                rain_val = w["rain"] or 0
                rain_html = f'<div style="margin-top:8px;padding:6px 10px;background:#2d1800;border-radius:6px;color:#ffa726;font-size:0.82rem;">⚠️ 강수 {rain_val}mm</div>' if rain_val > 0 else '<div style="margin-top:8px;padding:6px 10px;background:#0d2200;border-radius:6px;color:#76c442;font-size:0.82rem;">✅ 맑음 · 강수 없음</div>'
                st.markdown(f"""
                <div class="result-card">
                    <div style="display:flex;align-items:center;gap:12px;">
                        <div style="font-size:2.4rem;">{sky_i}</div>
                        <div>
                            <div style="font-size:1.8rem;font-weight:700;color:#4fc3f7;">{w["temp"]}°C</div>
                            <div style="font-size:0.78rem;color:#7ab3d4;">습도 {w["humidity"] or 0}% &nbsp;|&nbsp; 💨{w_arrow} {w["wind_speed"] or 0}m/s</div>
                        </div>
                    </div>
                    {rain_html}
                </div>
                """, unsafe_allow_html=True)

            # 시간대별 예보 (도착 시간대)
            st.markdown('<div style="font-size:0.8rem;color:#4fc3f7;margin:10px 0 4px 0;">⏱️ 시간대별 예보</div>', unsafe_allow_html=True)
            forecasts = get_weather_forecast(dest_airport["nx"], dest_airport["ny"])
            if forecasts:
                cells = ""
                for fc in forecasts:
                    t = fc.get("time", "")
                    t_fmt = (t[:2] + ":" + t[2:]) if len(t) == 4 else t
                    icon = forecast_sky_icon(fc.get("pty", 0), fc.get("sky"))
                    temp = fc.get("temp", "—")
                    rain = fc.get("rain", 0) or 0
                    rain_html = ('<div style="font-size:0.62rem;color:#64b5f6;">' + str(rain) + "mm</div>") if rain > 0 else ""
                    cells += (
                        '<div class="forecast-cell">'
                        + '<div class="fc-time">' + str(t_fmt) + "</div>"
                        + '<div class="fc-icon">' + str(icon) + "</div>"
                        + '<div class="fc-temp">' + str(temp) + "°</div>"
                        + rain_html
                        + "</div>"
                    )
                st.markdown('<div class="forecast-row">' + cells + "</div>", unsafe_allow_html=True)
            else:
                st.markdown('<div style="font-size:0.8rem;color:#4a6080;">예보 데이터 없음</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="section-title">🌤️ 목적지 날씨</div>', unsafe_allow_html=True)
            st.markdown('<div class="alert-banner" style="border-color:#4a6080;color:#7ab3d4;">✈️ 편명 검색하면 목적지 날씨 + 예보가 표시돼요</div>', unsafe_allow_html=True)

    # ── col_r: 공항 정보 + 도착 안내 ──
    with col_r:
        st.markdown('<div class="section-title">🏢 공항 안내</div>', unsafe_allow_html=True)
        if dest_airport:
            iata = dest_airport["iata"]
            terminal_info = {
                "ICN": "T1 (동편·서편) / 탑승동 / T2",
                "GMP": "국내선터미널 / 국제선터미널",
                "CJU": "단일터미널",
                "PUS": "국내선 / 국제선",
                "TAE": "단일터미널",
            }.get(iata, "단일터미널")

            st.markdown(f"""
            <div class="result-card">
                <div class="result-title">🏢 {dest_airport["name"]}</div>
                <div style="font-size:0.82rem;color:#b0c4d8;line-height:1.8;">
                    📍 IATA: <b style="color:#4fc3f7">{iata}</b><br>
                    🏗️ 터미널: {terminal_info}<br>
                    📡 실시간 게이트: 공항 FIDS 확인
                </div>
            </div>
            """, unsafe_allow_html=True)

            # 도착 안내 체크리스트
            eta_min = None
            if current_flight and dest_airport and dep_airport:
                prog = calc_flight_progress(
                    current_flight[6], current_flight[5],
                    dep_airport, dest_airport, flight_spd
                )
                if prog: eta_min = prog["eta_min"]

            if eta_min is not None:
                checklist = []
                if eta_min > 60:
                    checklist = [("✅","비행 중 (순항)"),("⬜","착륙 준비"),("⬜","수하물 수취"),("⬜","입국심사")]
                elif eta_min > 20:
                    checklist = [("✅","비행 중 (순항)"),("🔄","착륙 준비 중"),("⬜","수하물 수취"),("⬜","입국심사")]
                else:
                    checklist = [("✅","비행 중"),("✅","착륙 임박"),("🔄","수하물 수취 예정"),("⬜","입국심사")]

                st.markdown('<div style="font-size:0.8rem;color:#4fc3f7;margin:10px 0 4px 0;">📋 도착 단계</div>', unsafe_allow_html=True)
                items_html = "".join(
                    f'<div style="font-size:0.82rem;color:#b0c4d8;padding:3px 0;">{icon} {label}</div>'
                    for icon, label in checklist
                )
                st.markdown(f'<div class="result-card" style="padding:12px;">{items_html}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-banner" style="border-color:#4a6080;color:#7ab3d4;">✈️ 편명 검색하면 공항 안내가 표시돼요</div>', unsafe_allow_html=True)

# ── fragment 종료 + 호출 ──
bottom_panel()

# ── AI 기상·운항 종합 분석 패널 ──
st.markdown("---")
st.markdown('<div class="section-title">🤖 AI 기상·운항 종합 분석</div>', unsafe_allow_html=True)

ai_col1, ai_col2 = st.columns([3, 1])
with ai_col1:
    st.markdown(
        '<div style="font-size:0.82rem;color:#7ab3d4;">편명을 검색한 뒤 아래 버튼을 누르면 Claude AI가 기상·운항 데이터를 종합 분석해드립니다.</div>',
        unsafe_allow_html=True
    )
with ai_col2:
    run_ai = st.button("✨ AI 분석 실행", use_container_width=True)

if run_ai:
    # 세션에서 현재 편명 검색 결과 수집
    searched = st.session_state.get("searched_callsign", "")
    if not searched:
        st.warning("먼저 상단에서 편명을 검색해주세요.")
    else:
        with st.spinner("🤖 Claude AI가 분석 중입니다..."):
            # flight_info 구성
            f_info = {
                "callsign": st.session_state.get("ai_callsign", searched),
                "dep":      st.session_state.get("ai_dep", "알 수 없음"),
                "arr":      st.session_state.get("ai_arr", "알 수 없음"),
                "alt":      st.session_state.get("ai_alt", "알 수 없음"),
                "speed":    st.session_state.get("ai_speed", "알 수 없음"),
                "eta":      st.session_state.get("ai_eta", "계산 중"),
            }
            # weather_info 구성
            w_info = st.session_state.get("ai_weather", {})
            # delay_info 구성
            d_info = st.session_state.get("ai_delays", [])

            analysis = analyze_flight_weather_ai(f_info, w_info, d_info)

        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #0d2137, #1a3a5c);
            border: 1px solid #2E75B6;
            border-left: 5px solid #4fc3f7;
            border-radius: 12px;
            padding: 18px 20px;
            margin-top: 10px;
            font-size: 0.88rem;
            color: #e0e6f0;
            line-height: 1.8;
        ">
            <div style="font-size:0.75rem;color:#4fc3f7;margin-bottom:8px;">🤖 Claude AI 종합 분석 결과</div>
            {analysis}
        </div>
        """, unsafe_allow_html=True)

# ── 푸터 ──
st.markdown("---")
st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;font-size:0.72rem;color:#4a6080;padding:4px 0;">
    <div>✈️ 항공: <a href="https://airplanes.live" style="color:#4a6080;">airplanes.live</a> &nbsp;|&nbsp; 🌤️ 기상청 초단기예보 &nbsp;|&nbsp; 🛫 국토교통부 공공데이터 &nbsp;|&nbsp; 🏢 인천·한국공항공사</div>
    <div>🕐 {time.strftime("%H:%M:%S")} KST &nbsp;|&nbsp; SkyWatch v3.0</div>
</div>
""", unsafe_allow_html=True)
