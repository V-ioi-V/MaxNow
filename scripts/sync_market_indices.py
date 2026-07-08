import json
import http.client
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "dash" / "data" / "market-indices.json"
JS_PATH = ROOT / "dash" / "data" / "market-indices.js"
GLOBAL_NAME = "MAXNOW_MARKET_INDICES_DATA"

INDEXES = [
    {
        "key": "nasdaq100",
        "name": "纳指100",
        "symbol": "NDX",
        "displaySymbol": "NDX",
        "region": "US",
        "quoteCode": "usNDX",
        "currency": "USD",
    },
    {
        "key": "sp500",
        "name": "标普500",
        "symbol": "SPX",
        "displaySymbol": "SPX",
        "region": "US",
        "quoteCode": "usINX",
        "currency": "USD",
    },
    {
        "key": "shanghai",
        "name": "上证指数",
        "symbol": "000001",
        "displaySymbol": "SH000001",
        "region": "CN",
        "quoteCode": "sh000001",
        "currency": "CNY",
    },
    {
        "key": "shenzhen",
        "name": "深证成指",
        "symbol": "399001",
        "displaySymbol": "SZ399001",
        "region": "CN",
        "quoteCode": "sz399001",
        "currency": "CNY",
    },
    {
        "key": "chinext",
        "name": "创业板指",
        "symbol": "399006",
        "displaySymbol": "SZ399006",
        "region": "CN",
        "quoteCode": "sz399006",
        "currency": "CNY",
    },
]

QUOTE_PATTERN = re.compile(r'v_([^=]+)="([^"]*)";')
SOURCE_NAME = "Tencent Finance"


def now_text():
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M")


def read_existing():
    if not JSON_PATH.exists():
        return {}
    return json.loads(JSON_PATH.read_text(encoding="utf-8"))


def write_outputs(data):
    text = json.dumps(data, ensure_ascii=False, indent=2)
    JSON_PATH.write_text(text + "\n", encoding="utf-8")
    JS_PATH.write_text(f"window.{GLOBAL_NAME} = " + text + ";\n", encoding="utf-8")


def request_bytes(url):
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 MaxNow market sync",
            "Accept": "*/*",
            "Referer": "https://gu.qq.com/",
        },
    )
    with urllib.request.urlopen(request, timeout=12) as response:
        return response.read()


def request_text(url, encoding="utf-8"):
    return request_bytes(url).decode(encoding, errors="replace")


def request_json(url):
    return json.loads(request_text(url))


def to_number(value):
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str) and value.strip() not in {"", "-", "--"}:
        return float(value.strip().replace(",", ""))
    return None


def format_time_token(value):
    text = str(value or "").strip()
    if len(text) == 4 and text.isdigit():
        return f"{text[:2]}:{text[2:]}"
    return text[-5:]


def compact_trend(points, max_points=36):
    pairs = [(time_text, value) for time_text, value in points if time_text and isinstance(value, (int, float))]
    if len(pairs) <= max_points:
        selected = pairs
    else:
        selected = []
        for index in range(max_points):
            source_index = round(index * (len(pairs) - 1) / (max_points - 1))
            selected.append(pairs[source_index])

    return [
        {
            "time": format_time_token(time_text),
            "value": round(float(value), 4),
        }
        for time_text, value in selected
    ]


def quote_url():
    codes = ",".join(item["quoteCode"] for item in INDEXES)
    return f"https://qt.gtimg.cn/q={codes}"


def trend_url(quote_code):
    return f"https://web.ifzq.gtimg.cn/appstock/app/minute/query?code={quote_code}"


def fetch_quotes():
    url = quote_url()
    text = request_text(url, encoding="gb18030")
    quotes = {}
    for code, raw in QUOTE_PATTERN.findall(text):
        quotes[code] = raw.split("~")
    return quotes, url


def fetch_trend(quote_code):
    url = trend_url(quote_code)
    payload = request_json(url)
    quote_data = ((payload.get("data") or {}).get(quote_code) or {})
    trends = (((quote_data.get("data") or {}).get("data")) or [])
    points = []
    for line in trends:
        parts = str(line).split()
        if len(parts) < 2:
            continue
        value = to_number(parts[1])
        if value is None:
            continue
        points.append((parts[0], value))
    return compact_trend(points), url


def quote_field(fields, index):
    if index >= len(fields):
        return ""
    return fields[index]


def build_index(config, quote, source_url):
    price = to_number(quote_field(quote, 3))
    previous_close = to_number(quote_field(quote, 4))
    change = to_number(quote_field(quote, 31))
    change_percent = to_number(quote_field(quote, 32))

    if price is None or previous_close is None or change is None or change_percent is None:
        raise ValueError(f"{config['quoteCode']}: missing quote fields")

    trend = []
    trend_source_url = trend_url(config["quoteCode"])
    trend_error = ""
    try:
        trend, trend_source_url = fetch_trend(config["quoteCode"])
    except (urllib.error.URLError, http.client.RemoteDisconnected, TimeoutError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        trend_error = str(error)

    item = {
        **config,
        "currency": config["currency"],
        "price": round(price, 4),
        "previousClose": round(previous_close, 4),
        "change": round(change, 4),
        "changePercent": round(change_percent, 4),
        "updatedAt": now_text(),
        "marketState": "",
        "source": SOURCE_NAME,
        "sourceUrl": source_url,
        "trendSourceUrl": trend_source_url,
        "trend": trend,
    }
    if trend_error:
        item["trendError"] = trend_error
    return item


def fallback_item(config, existing_by_key, reason):
    item = existing_by_key.get(config["key"])
    if item:
        return {**item, "stale": True, "lastError": reason}
    return {
        **config,
        "currency": "",
        "price": None,
        "previousClose": None,
        "change": None,
        "changePercent": None,
        "updatedAt": "",
        "marketState": "unknown",
        "source": SOURCE_NAME,
        "sourceUrl": "",
        "trend": [],
        "stale": True,
        "lastError": reason,
    }


def main():
    existing = read_existing()
    existing_by_key = {
        item.get("key"): item
        for item in existing.get("indices", [])
        if item.get("key")
    }
    indices = []
    errors = []

    try:
        quotes, source_url = fetch_quotes()
    except (urllib.error.URLError, http.client.RemoteDisconnected, TimeoutError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        quotes = {}
        source_url = quote_url()
        errors.append(f"quotes: {error}")

    for config in INDEXES:
        try:
            quote = quotes.get(config["quoteCode"])
            if not quote:
                raise ValueError(f"{config['quoteCode']}: missing quote")
            item = build_index(config, quote, source_url)
            indices.append(item)
            print(f"[ok] fetched {config['symbol']} {item['changePercent']:.2f}%")
        except (urllib.error.URLError, http.client.RemoteDisconnected, TimeoutError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
            reason = str(error)
            errors.append(f"{config['symbol']}: {reason}")
            indices.append(fallback_item(config, existing_by_key, reason))
            print(f"[warn] kept fallback for {config['symbol']}: {reason}")

    fetched_count = sum(1 for item in indices if not item.get("stale"))
    if fetched_count == 0 and not existing_by_key:
        raise RuntimeError("; ".join(errors) or "no market data fetched")

    data = {
        "schemaVersion": 1,
        "updatedAt": now_text(),
        "source": SOURCE_NAME,
        "refreshIntervalMinutes": 10,
        "indices": indices,
    }
    if errors:
        data["errors"] = errors

    write_outputs(data)
    print(f"[ok] wrote {JSON_PATH.relative_to(ROOT)} with {fetched_count}/{len(INDEXES)} fresh indices")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"[fail] market index sync failed: {error}", file=sys.stderr)
        sys.exit(1)
