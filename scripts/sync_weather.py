import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_JSON = ROOT / "dash" / "data" / "dashboard.json"
DASHBOARD_JS = ROOT / "dash" / "data" / "dashboard.js"
GLOBAL_NAME = "MAXNOW_DASHBOARD_DATA"

LOCATION = {
    "city": "北京市",
    "district": "海淀",
    "location": "北京市海淀区",
    "latitude": 39.96,
    "longitude": 116.30,
}

WEATHER_CODES = {
    0: ("晴", "sun"),
    1: ("大部晴朗", "sun"),
    2: ("多云", "cloud"),
    3: ("阴", "cloud"),
    45: ("雾", "fog"),
    48: ("雾凇", "fog"),
    51: ("小毛毛雨", "rain"),
    53: ("毛毛雨", "rain"),
    55: ("大毛毛雨", "rain"),
    56: ("冻毛毛雨", "rain"),
    57: ("强冻毛毛雨", "rain"),
    61: ("小雨", "rain"),
    63: ("中雨", "rain"),
    65: ("大雨", "rain"),
    66: ("冻雨", "rain"),
    67: ("强冻雨", "rain"),
    71: ("小雪", "snow"),
    73: ("中雪", "snow"),
    75: ("大雪", "snow"),
    77: ("雪粒", "snow"),
    80: ("阵雨", "rain"),
    81: ("中阵雨", "rain"),
    82: ("强阵雨", "rain"),
    85: ("阵雪", "snow"),
    86: ("强阵雪", "snow"),
    95: ("雷阵雨", "storm"),
    96: ("雷阵雨伴冰雹", "storm"),
    99: ("强雷阵雨伴冰雹", "storm"),
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_dashboard(data):
    DASHBOARD_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    DASHBOARD_JS.write_text(
        f"window.{GLOBAL_NAME} = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )


def fetch_weather():
    params = {
        "latitude": LOCATION["latitude"],
        "longitude": LOCATION["longitude"],
        "current": "temperature_2m,weather_code,is_day",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min",
        "timezone": "Asia/Shanghai",
        "forecast_days": 1,
    }
    url = "https://api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"User-Agent": "MaxNow weather sync"})
    with urllib.request.urlopen(request, timeout=12) as response:
        payload = json.loads(response.read().decode("utf-8"))

    current = payload.get("current") or {}
    daily = payload.get("daily") or {}
    code = int(current.get("weather_code", daily.get("weather_code", [3])[0]))
    condition, icon = WEATHER_CODES.get(code, ("天气", "cloud"))
    daily_code = daily.get("weather_code", [code])[0]
    daily_condition, daily_icon = WEATHER_CODES.get(int(daily_code), (condition, icon))

    return {
        **LOCATION,
        "condition": condition,
        "summary": daily_condition,
        "icon": icon or daily_icon,
        "weatherCode": code,
        "dailyWeatherCode": int(daily_code),
        "tempC": current.get("temperature_2m"),
        "highC": (daily.get("temperature_2m_max") or [None])[0],
        "lowC": (daily.get("temperature_2m_min") or [None])[0],
        "isDay": bool(current.get("is_day", 1)),
        "updatedAt": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M"),
        "source": "Open-Meteo",
        "sourceUrl": url,
    }


def main():
    dashboard = read_json(DASHBOARD_JSON)
    dashboard["weather"] = fetch_weather()
    write_dashboard(dashboard)
    weather = dashboard["weather"]
    print(
        "[ok] updated weather "
        f"location=Beijing-Haidian code={weather['weatherCode']} icon={weather['icon']} "
        f"tempC={round(float(weather['tempC']))} "
        f"rangeC={round(float(weather['highC']))}/{round(float(weather['lowC']))}"
    )


if __name__ == "__main__":
    try:
        main()
    except (urllib.error.URLError, TimeoutError, ValueError, KeyError, TypeError) as error:
        print(f"[fail] weather sync failed: {error}", file=sys.stderr)
        sys.exit(1)
