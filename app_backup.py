import streamlit as st
import requests
import time
import json
import os
from dotenv import load_dotenv

load_dotenv()
DATA_GO_KR_KEY = os.getenv("DATA_GO_KR_KEY")

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

/* 배경 */
.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1b2a 50%, #0a0e1a 100%);
    color: #e0e6f0;
}

/* 헤더 */
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

/* 지표 카드 */
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

/* 특보 배너 */
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

/* 검색 섹션 */
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

/* 결과 카드 */
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

/* 섹션 타이틀 */
.section-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #4fc3f7;
    letter-spacing: 1px;
    padding: 8px 0;
    border-bottom: 1px solid #1e4976;
    margin-bottom: 16px;
}

/* 토글 레이블 */
.layer-toggle {
    background: #0f2237;
    border: 1px solid #1e4976;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 0.85rem;
    color: #7ab3d4;
}

/* streamlit 기본 요소 덮어쓰기 */
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
</style>
""", unsafe_allow_html=True)

KOREA_BOUNDS = {
    "lamin": 30.0, "lomin": 120.0,
    "lamax": 42.0, "lomax": 135.0
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

#def get_flights(): //인증 방식 OpenSky  무료 계정 한계 실시간에서 계속 Data 가 안옴 429 에러
#    try:
#        username = os.getenv("OPENSKY_USERNAME")
#       auth = (username, password) if username and password else None
#        r = requests.get("https://opensky-network.org/api/states/all", 
#                        params=KOREA_BOUNDS, auth=auth, timeout=10)
#        return r.json().get("states", [])
#    except:
#        return []
#@st.cache_data(ttl=60)
#def get_flights():
#    try:
#        username = os.getenv("OPENSKY_USERNAME")
#        password = os.getenv("OPENSKY_PASSWORD")
#        auth = (username, password) if username and password else None
#        r = requests.get(
#            "https://opensky-network.org/api/states/all",
#           params=KOREA_BOUNDS, auth=auth, timeout=15
#        )
#        if r.status_code == 200:
#            return r.json().get("states", [])
#        return []
#    except:
#        return []
@st.cache_data(ttl=60)
def get_flights():
    try:
        r = requests.get(
            "https://api.airplanes.live/v2/point/36.5/127.5/300",
            timeout=15
        )
        if r.status_code == 200:
            ac_list = r.json().get("ac", [])
            result = []
            for ac in ac_list:
                lat = ac.get("lat")
                lon = ac.get("lon")
                if lat is None or lon is None:
                    continue
                alt_raw = ac.get("alt_baro", 0)
                on_ground = alt_raw == "ground"
                alt_m = 0 if on_ground else (float(alt_raw) * 0.3048 if alt_raw else 0)
                gs = ac.get("gs", 0)
                result.append([
                    ac.get("hex",""),
                    ac.get("flight","").strip(),
                    ac.get("r",""),
                    None, None, lon, lat,
                    alt_m,
                    on_ground,
                    float(gs) * 0.514444 if gs else 0,
                    ac.get("track", 0),
                    ac.get("desc",""),
                ])
            return result
        return []
    except Exception as e:
        print("get_flights 오류:", e)
        return []

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
            r = requests.get("http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst", params=params, timeout=5)
            items = r.json().get("response",{}).get("body",{}).get("items",{}).get("item",[])
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

def get_weather_alerts():
    params = {"serviceKey": DATA_GO_KR_KEY, "pageNo": 1, "numOfRows": 20, "dataType": "JSON", "stnId": "108"}
    try:
        r = requests.get("http://apis.data.go.kr/1360000/WthrWrnInfoService/getWthrWrnMsg", params=params, timeout=5)
        items = r.json().get("response",{}).get("body",{}).get("items",{})
        if items:
            item_list = items.get("item", [])
            return [item_list] if isinstance(item_list, dict) else item_list
        return []
    except:
        return []

def search_flight_info(callsign):
    params = {"serviceKey": DATA_GO_KR_KEY, "pageNo": 1, "numOfRows": 10, "_type": "json", "flightId": callsign}
    try:
        r = requests.get("http://apis.data.go.kr/1613000/DmstcFlightNvgInfoService/getFlightOpratInfoList", params=params, timeout=10)
        items = r.json().get("response",{}).get("body",{}).get("items",{})
        if items:
            item_list = items.get("item", [])
            return [item_list] if isinstance(item_list, dict) else item_list
        return []
    except:
        return []

def get_delayed_flights():
    results = []
    now = time.localtime()
    today = time.strftime("%Y%m%d", now)
    urls = [
        ("http://apis.data.go.kr/B551177/StatusOfPassengerFlightsOdp/getPassengerDeparturesDump", "출발"),
        ("http://apis.data.go.kr/B551177/StatusOfPassengerFlightsOdp/getPassengerArrivalsDump", "도착"),
    ]
    for url, direction in urls:
        params = {
            "serviceKey": DATA_GO_KR_KEY,
            "pageNo": 1,
            "numOfRows": 100,
            "type": "json",
            "date": today
        }
        try:
            r = requests.get(url, params=params, timeout=8)
            data = r.json()
            items = data.get("response",{}).get("body",{}).get("items",{})
            if not items:
                continue
            item_list = items.get("item", [])
            if isinstance(item_list, dict):
                item_list = [item_list]
            for item in item_list:
                remark = item.get("remark","") or item.get("remarkKorean","") or ""
                if any(kw in str(remark) for kw in ["지연","결항","Delay","Cancel","취소"]):
                    results.append({
                        "direction": direction,
                        "flight_id": item.get("flightId",""),
                        "airline": item.get("airline","") or item.get("airlineKorean",""),
                        "airport": item.get("airport","") or item.get("airportKorean",""),
                        "sched": item.get("scheduleDateTime","") or item.get("std",""),
                        "remark": remark
                    })
        except Exception as e:
            print("지연 조회 오류:", e)
    return results

# ── 데이터 로딩 ──
with st.spinner(""):
    flights = get_flights()
    weather_data = get_weather_data()
    alerts = get_weather_alerts()

# ── 헤더 ──
st.markdown(f"""
<div class="sky-header">
    <div style="font-size:2rem">✈️</div>
    <div>
        <h1>SKYWATCH</h1>
        <span>한반도 실시간 항공 · 기상 통합 플랫폼 &nbsp;|&nbsp; {time.strftime('%Y.%m.%d %H:%M')} KST</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── 지표 (작게) ──
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("✈️ 비행 중", f"{len(flights)}대")
with col2:
    airborne = [f for f in flights if len(f) > 8 and not f[8]]
    st.metric("🛫 공중", f"{len(airborne)}대")
with col3:
    identified = [f for f in flights if f[1] and f[1].strip()]
    st.metric("📡 식별", f"{len(identified)}대")
with col4:
    st.metric("⚠️ 특보", f"{len(alerts)}건" if alerts else "없음")

st.markdown("---")

# ── 지도 (메인) ──
st.markdown('<div class="section-title">🗺️ 실시간 항공기 + 기상 지도</div>', unsafe_allow_html=True)

col_t1, col_t2, col_t3, col_t4 = st.columns(4)
with col_t1: show_weather = st.toggle("☁️ 날씨", value=True)
with col_t2: show_wind = st.toggle("💨 바람", value=True)
with col_t3: show_rain = st.toggle("🌧️ 강수량", value=True)
with col_t4: show_alert_toggle = st.toggle("⚠️ 특보", value=True)

def sky_icon(pty, rain, wind_speed):
    if pty == 1: return "🌧️"
    if pty == 2: return "🌨️"
    if pty == 3: return "❄️"
    if pty == 4: return "🌦️"
    if rain and rain > 0: return "🌧️"
    if wind_speed and wind_speed > 10: return "💨"
    return "☀️"

def wind_arrow(deg):
    return ["↓","↙","←","↖","↑","↗","→","↘"][round(deg/45)%8]

flights_js = []
for f in flights:
    try:
        lat, lon = f[6], f[5]
        if lat is None or lon is None: continue
        flights_js.append({
            "callsign": f[1].strip() if f[1] else "미확인",
            "country": f[2] if f[2] else "알 수 없음",
            "lat": lat, "lon": lon,
            "altitude": f[7] if f[7] else 0,
            "speed": round((f[9] or 0) * 3.6),
            "heading": f[10] if f[10] else 0,
            "on_ground": f[8] if f[8] is not None else False
        })
    except: pass

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

flights_json = json.dumps(flights_js)
weather_json = json.dumps(weather_js)

map_html = f"""
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body {{ margin:0; background:#f0f4f0; }}
        #map {{ height:660px; width:100%; border-radius:12px; }}
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
        .leaflet-popup-content-wrapper {{
            background: #fff;
            border: 1px solid #b0c8e0;
            color: #2c3e50;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        .legend-box {{
            position:absolute; bottom:20px; left:20px; z-index:1000;
            background:rgba(255,255,255,0.92); border:1px solid #ccc;
            padding:8px 12px; border-radius:10px; font-size:11px; color:#2c3e50;
        }}
        .ctrl-box {{
            position:absolute; top:10px; right:10px; z-index:1000;
            background:rgba(255,255,255,0.92); border:1px solid #ccc;
            padding:8px 12px; border-radius:10px; font-size:11px; color:#2c3e50;
            display:flex; flex-direction:column; gap:5px;
        }}
        .ctrl-box label {{ display:flex; align-items:center; gap:6px; cursor:pointer; }}
    </style>
</head>
<body>
<div class="map-wrap">
    <div id="map"></div>
    <canvas id="weatherCanvas"></canvas>

    <div class="ctrl-box">
        <label><input type="checkbox" id="showRain" checked> 🌧️ 강수</label>
        <label><input type="checkbox" id="showWind" checked> 💨 바람</label>
        <label><input type="checkbox" id="showPlanes" checked> ✈️ 항공기</label>
    </div>

    <div class="legend-box">
        <b style="color:#1a5276">고도</b><br>
        <span style="color:#1565c0">✈</span> 8,000m+&nbsp;
        <span style="color:#2e7d32">✈</span> 3,000~8,000m<br>
        <span style="color:#e65100">✈</span> 3,000m미만&nbsp;
        <span style="color:#888">✈</span> 지상
    </div>
</div>

<script>
var map = L.map('map', {{zoomControl:true}}).setView([36.5, 127.5], 7);
L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
    attribution:'© CartoDB'
}}).addTo(map);

L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_only_labels/{{z}}/{{x}}/{{y}}{{r}}.png', {{
    attribution:''
}}).addTo(map);

fetch('https://cdn.jsdelivr.net/npm/south-korea-geojson@1.0.1/skorea-provinces-geo.json')
    .then(function(r) {{ return r.json(); }})
    .then(function(data) {{
        L.geoJSON(data, {{
            style: function() {{
                return {{
                    color: '#27ae60',
                    weight: 2,
                    fillOpacity: 0.03,
                    fillColor: '#27ae60',
                    opacity: 0.9
                }};
            }}
        }}).addTo(map);
    }})
    .catch(function(e) {{
        console.log('GeoJSON 오류:', e);
    }});

var flightsData = {flights_json};
var weatherData = {weather_json};
var showWeather = {'true' if show_weather else 'false'};
var showWind = {'true' if show_wind else 'false'};
var showRain = {'true' if show_rain else 'false'};
var planes = {{}};

// 날씨 라벨
if(showWeather) {{
    weatherData.forEach(function(w) {{
        var lines = [];
        lines.push(w.icon + ' <b>' + w.temp + '°C</b> ' + w.humidity + '%');
        if(showWind) lines.push('💨 ' + w.arrow + ' ' + w.wind_speed + 'm/s');
        if(showRain && w.rain > 0) lines.push('🌧️ ' + w.rain + 'mm');
        var html = '<div class="weather-label"><b>' + w.name + '</b><br>' + lines.join('<br>') + '</div>';
        L.marker([w.lat, w.lon], {{
            icon: L.divIcon({{ className:'', html:html, iconAnchor:[-5,10] }})
        }}).bindPopup(
            '<b style="color:#1a5276">' + w.name + '</b><br>' +
            '🌡️ ' + w.temp + '°C &nbsp; 💧 ' + w.humidity + '%<br>' +
            '💨 ' + w.arrow + ' ' + w.wind_speed + 'm/s<br>' +
            '🌧️ ' + w.rain + 'mm'
        ).addTo(map);
    }});
}}

// ── 항공기 ──
function getColor(alt, on_ground) {{
    if(on_ground) return '#888';
    if(alt > 8000) return '#1565c0';
    if(alt > 3000) return '#2e7d32';
    return '#e65100';
}}
function getPlaneIcon(heading, color) {{
    return L.divIcon({{
        className:'',
        html:'<div style="transform:rotate('+(heading-90)+'deg);font-size:18px;color:'+color+';width:22px;height:22px;display:flex;align-items:center;justify-content:center;filter:drop-shadow(0 1px 3px rgba(0,0,0,0.3));">✈</div>',
        iconSize:[22,22], iconAnchor:[11,11]
    }});
}}
function predictPosition(lat,lon,speedKmh,headingDeg,seconds) {{
    var R=6371, d=(speedKmh*seconds/3600)/R, hdg=headingDeg*Math.PI/180;
    var lat1=lat*Math.PI/180, lon1=lon*Math.PI/180;
    var lat2=Math.asin(Math.sin(lat1)*Math.cos(d)+Math.cos(lat1)*Math.sin(d)*Math.cos(hdg));
    var lon2=lon1+Math.atan2(Math.sin(hdg)*Math.sin(d)*Math.cos(lat1),Math.cos(d)-Math.sin(lat1)*Math.sin(lat2));
    return {{lat:lat2*180/Math.PI, lon:lon2*180/Math.PI}};
}}
function updateFlights(data) {{
    var newKeys=new Set();
    data.forEach(function(f) {{
        if(!f.lat||!f.lon) return;
        var key=f.callsign; newKeys.add(key);
        var color=getColor(f.altitude,f.on_ground);
        var popup='<b style="color:#1a5276">✈ '+f.callsign+'</b><br>🌏 '+f.country+'<br>📡 '+Math.round(f.altitude)+'m<br>💨 '+f.speed+'km/h<br>🧭 '+Math.round(f.heading)+'°';
        if(planes[key]) {{
            planes[key].lat=f.lat; planes[key].lon=f.lon;
            planes[key].speed=f.speed; planes[key].heading=f.heading;
            planes[key].altitude=f.altitude; planes[key].on_ground=f.on_ground;
            planes[key].marker.setIcon(getPlaneIcon(f.heading,color));
            planes[key].marker.setPopupContent(popup);
        }} else {{
            planes[key]={{
                marker:L.marker([f.lat,f.lon],{{icon:getPlaneIcon(f.heading,color)}})
                    .bindPopup(popup)
                    .bindTooltip('<b>'+f.callsign+'</b>',{{direction:'top'}})
                    .addTo(map),
                lat:f.lat,lon:f.lon,speed:f.speed,
                heading:f.heading,altitude:f.altitude,on_ground:f.on_ground
            }};
        }}
    }});
    Object.keys(planes).forEach(function(key) {{
        if(!newKeys.has(key)) {{ map.removeLayer(planes[key].marker); delete planes[key]; }}
    }});
}};
function tickMovement() {{
    if(!document.getElementById('showPlanes').checked) return;
    Object.keys(planes).forEach(function(key) {{
        var p=planes[key];
        if(p.on_ground||p.speed<10) return;
        var next=predictPosition(p.lat,p.lon,p.speed,p.heading,1);
        p.lat=next.lat; p.lon=next.lon;
        p.marker.setLatLng([p.lat,p.lon]);
    }});
}}
updateFlights(flightsData);
setInterval(tickMovement,1000);
setInterval(function() {{
    fetch('https://opensky-network.org/api/states/all?lamin=30.0&lomin=120.0&lamax=42.0&lomax=135.0')
        .then(r=>r.json()).then(data=>{{
            updateFlights((data.states||[]).map(f=>({{
                callsign:(f[1]||'미확인').trim(),country:f[2]||'알 수 없음',
                lat:f[6],lon:f[5],altitude:f[7]||0,
                speed:Math.round((f[9]||0)*3.6),heading:f[10]||0,on_ground:f[8]||false
            }})).filter(f=>f.lat&&f.lon));
        }}).catch(e=>console.log(e));
}},60000); 

// ── 기상 애니메이션 Canvas ──
var cvs = document.getElementById('weatherCanvas');
var ctx = cvs.getContext('2d');

function resizeCanvas() {{
    cvs.width = cvs.offsetWidth;
    cvs.height = cvs.offsetHeight;
}}
resizeCanvas();

// 지도 좌표 → canvas 픽셀 변환
function latLonToXY(lat, lon) {{
    var point = map.latLngToContainerPoint([lat, lon]);
    return {{x: point.x, y: point.y}};
}}

// 실제 기상 데이터 기반 강수 구역
var rainZones = weatherData.filter(function(w) {{
    return w.rain > 0 || w.wind_speed > 5;
}}).map(function(w) {{
    return {{
        lat: w.lat, lon: w.lon,
        intensity: Math.min(w.rain / 5, 1) + 0.2,
        wind_speed: w.wind_speed,
        wind_dir: w.wind_dir
    }};
}});

// 강수가 없으면 기본 구역 (제주·남해안)
if(rainZones.length === 0) {{
    rainZones = [
        {{lat:33.5,lon:126.5,intensity:0.4,wind_speed:3,wind_dir:315}},
        {{lat:34.8,lon:128.5,intensity:0.3,wind_speed:2.5,wind_dir:300}},
    ];
}}

// 빗방울 생성
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
                alpha: 0.25 + Math.random()*0.45,
                zone: z,
                centerX: xy.x,
                centerY: xy.y,
                radius: r
            }});
        }}
    }});
}}

// 바람 파티클
var windParticles = [];
function initWind() {{
    windParticles = [];
    for(var i=0; i<120; i++) {{
        windParticles.push({{
            x: Math.random()*cvs.width,
            y: Math.random()*cvs.height,
            age: Math.floor(Math.random()*80),
            maxAge: 60+Math.floor(Math.random()*50)
        }});
    }}
}}

var t = 0;
var avgWindDir = 315;
var avgWindSpd = 3;
if(weatherData.length > 0) {{
    var totalU=0, totalV=0;
    weatherData.forEach(function(w) {{
        var rad = w.wind_dir * Math.PI/180;
        totalU += Math.sin(rad) * w.wind_speed;
        totalV += Math.cos(rad) * w.wind_speed;
    }});
    avgWindDir = Math.atan2(totalU/weatherData.length, totalV/weatherData.length) * 180/Math.PI;
    avgWindSpd = Math.sqrt(totalU*totalU+totalV*totalV)/weatherData.length;
}}

function windU(x,y,t) {{
    var base = Math.sin(avgWindDir*Math.PI/180);
    return (base + Math.sin(y*0.008+t*0.01)*0.3) * avgWindSpd * 0.15;
}}
function windV(x,y,t) {{
    var base = Math.cos(avgWindDir*Math.PI/180);
    return (base + Math.cos(x*0.006+t*0.008)*0.3) * avgWindSpd * 0.12;
}}

map.on('moveend zoomend', function() {{
    resizeCanvas();
    initDrops();
    initWind();
}});

initDrops();
initWind();

function drawWeather() {{
    ctx.clearRect(0,0,cvs.width,cvs.height);
    var showRainCk = document.getElementById('showRain').checked;
    var showWindCk = document.getElementById('showWind').checked;

    // 강수 헤일로 (맥박 효과)
    if(showRainCk) {{
        rainZones.forEach(function(z) {{
            var xy = latLonToXY(z.lat, z.lon);
            var pulse = Math.sin(t*0.05)*0.12;
            var r = (80 + z.intensity*60)*(1+pulse);
            var grd = ctx.createRadialGradient(xy.x,xy.y,0,xy.x,xy.y,r);
            grd.addColorStop(0,'rgba(41,128,185,'+(z.intensity*0.2)+')');
            grd.addColorStop(0.5,'rgba(41,128,185,'+(z.intensity*0.08)+')');
            grd.addColorStop(1,'rgba(0,0,0,0)');
            ctx.beginPath(); ctx.arc(xy.x,xy.y,r,0,Math.PI*2);
            ctx.fillStyle=grd; ctx.fill();
        }});

        // 빗방울 (바람 방향으로 기울어짐)
        var u0 = windU(cvs.width/2,cvs.height/2,t);
        var v0 = windV(cvs.width/2,cvs.height/2,t);
        var rainAngle = Math.atan2(u0, Math.abs(v0)*2);
        drops.forEach(function(d) {{
            ctx.strokeStyle='rgba(93,173,226,'+d.alpha+')';
            ctx.lineWidth=0.9;
            ctx.beginPath();
            ctx.moveTo(d.x, d.y);
            ctx.lineTo(d.x + Math.sin(rainAngle)*d.len, d.y + Math.cos(rainAngle)*d.len);
            ctx.stroke();
            d.x += windU(d.x,d.y,t)*0.5;
            d.y += d.speed;
            if(d.y > cvs.height + 10) {{
                var angle = Math.random()*Math.PI*2;
                var dist = Math.random()*d.radius;
                var cxy = latLonToXY(d.zone.lat, d.zone.lon);
                d.centerX = cxy.x; d.centerY = cxy.y;
                d.x = cxy.x + Math.cos(angle)*dist;
                d.y = -10;
            }}
        }});
    }}

    // 바람 흐름 파티클
    if(showWindCk) {{
        windParticles.forEach(function(p) {{
            var u=windU(p.x,p.y,t), v=windV(p.x,p.y,t);
            var spd=Math.sqrt(u*u+v*v);
            var fadeIn=Math.min(p.age/15,1);
            var fadeOut=Math.max(0,1-(p.age-p.maxAge*0.6)/(p.maxAge*0.4));
            var alpha=fadeIn*fadeOut*0.5;
            ctx.strokeStyle='rgba('+Math.round(80+spd*40)+','+Math.round(140+spd*30)+',200,'+alpha.toFixed(2)+')';
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
</script>
</body>
</html>
"""
st.components.v1.html(map_html, height=680)