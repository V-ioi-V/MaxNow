import json
import http.client
import sys
import urllib.error
import urllib.parse
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
        "secid": "100.NDX",
        "currency": "USD",
    },
    {
        "key": "sp500",
        "name": "标普500",
        "symbol": "SPX",
        "displaySymbol": "SPX",
        "region": "US",
        "secid": "100.SPX",
        "currency": "USD",
    },
    {
        "key": "shanghai",
        "name": "上证指数",
        "symbol": "000001",
        "displaySymbol": "SH000001",
        "region": "CN",
        "secid": "1.000001",
        "currency": "CNY",
    },
    {
        "key": "shenzhen",
        "name": "深证成指",
        "symbol": "399001",
        "displaySymbol": "SZ399001",
        "region": "CN",
        "secid": "0.399001",
        "currency": "CNY",
    },
    {
        "key": "chinext",
        "name": "创业板指",
        "symbol": "399006",
        "displaySymbol": "SZ399006",
        "region": "CN",
        "secid": "0.399006",
        "currency": "CNY",
    },
]


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


def request_json(url):
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 MaxNow market sync",
            "Accept": "application/json",
            "Referer": "https://quote.eastmoney.com/",
        },
    )
    with urllib.request.urlopen(request, timeout=12) as response:
        return json.loads(response.read().decode("utf-8"))


def to_number(value):
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str) and value.strip() not in {"", "-", "--"}:
        return float(value)
    return None


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
            "time": time_text[-5:],
            "value": round(float(value), 4),
        }
        for time_text, value in selected
    ]


def quote_url():
    secids = ",".join(item["secid"] for item in INDEXES)
    params = urllib.parse.urlencode(
        {
            "fltt": 2,
            "secids": secids,
            "fields": "f12,f14,f2,f3,f4,f18,f13,f15,f16,f17",
        }
    )
    return f"https://push2.eastmoney.com/api/qt/ulist.np/get?{params}"


def trend_url(secid):
    params = urllib.parse.urlencode(
        {
            "secid": secid,
            "fields1": "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11",
            "fields2": "f51,f53",
            "iscr": 0,
            "iscca": 0,
            "ndays": 1,
        }
    )
    return f"https://push2his.eastmoney.com/api/qt/stock/trends2/get?{params}"


def fetch_quotes():
    url = quote_url()
    payload = request_json(url)
    diff = ((payload.get("data") or {}).get("diff") or [])
    quotes = {}
    for item in diff:
        secid = f"{item.get('f13')}.{item.get('f12')}"
        quotes[secid] = item
    return quotes, url


def fetch_trend(secid):
    url = trend_url(secid)
    payload = request_json(url)
    trends = ((payload.get("data") or {}).get("trends") or [])
    points = []
    for line in trends:
        parts = str(line).split(",")
        if len(parts) < 2:
            continue
        value = to_number(parts[1])
        if value is None:
            continue
        points.append((parts[0], value))
    return compact_trend(points), url


def build_index(config, quote, source_url):
    price = to_number(quote.get("f2"))
    previous_close = to_number(quote.get("f18"))
    change = to_number(quote.get("f4"))
    change_percent = to_number(quote.get("f3"))

    if price is None or previous_close is None or change is None or change_percent is None:
        raise ValueError(f"{config['secid']}: missing quote fields")

    trend, trend_source_url = fetch_trend(config["secid"])

    return {
        **config,
        "currency": config["currency"],
        "price": round(price, 4),
        "previousClose": round(previous_close, 4),
        "change": round(change, 4),
        "changePercent": round(change_percent, 4),
        "updatedAt": now_text(),
        "marketState": "",
        "source": "Eastmoney",
        "sourceUrl": source_url,
        "trendSourceUrl": trend_source_url,
        "trend": trend,
    }


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
        "source": "Eastmoney",
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
            quote = quotes.get(config["secid"])
            if not quote:
                raise ValueError(f"{config['secid']}: missing quote")
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
        "source": "Eastmoney",
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
