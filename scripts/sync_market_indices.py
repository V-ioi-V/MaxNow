import json
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
        "symbol": "^NDX",
        "displaySymbol": "NDX",
        "region": "US",
    },
    {
        "key": "sp500",
        "name": "标普500",
        "symbol": "^GSPC",
        "displaySymbol": "SPX",
        "region": "US",
    },
    {
        "key": "shanghai",
        "name": "上证指数",
        "symbol": "000001.SS",
        "displaySymbol": "SH000001",
        "region": "CN",
    },
    {
        "key": "shenzhen",
        "name": "深证成指",
        "symbol": "399001.SZ",
        "displaySymbol": "SZ399001",
        "region": "CN",
    },
    {
        "key": "chinext",
        "name": "创业板指",
        "symbol": "399006.SZ",
        "displaySymbol": "SZ399006",
        "region": "CN",
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
            "User-Agent": "MaxNow market sync",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=12) as response:
        return json.loads(response.read().decode("utf-8"))


def compact_trend(timestamps, values, max_points=36):
    pairs = [
        (timestamp, value)
        for timestamp, value in zip(timestamps, values)
        if timestamp and isinstance(value, (int, float))
    ]
    if len(pairs) <= max_points:
        selected = pairs
    else:
        selected = []
        for index in range(max_points):
            source_index = round(index * (len(pairs) - 1) / (max_points - 1))
            selected.append(pairs[source_index])

    return [
        {
            "time": datetime.fromtimestamp(timestamp).astimezone().strftime("%H:%M"),
            "value": round(float(value), 4),
        }
        for timestamp, value in selected
    ]


def first_number(*values):
    for value in values:
        if isinstance(value, (int, float)):
            return float(value)
    return None


def fetch_index(config):
    params = urllib.parse.urlencode(
        {
            "range": "1d",
            "interval": "5m",
            "includePrePost": "false",
        }
    )
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(config['symbol'])}?{params}"
    payload = request_json(url)
    result = (payload.get("chart", {}).get("result") or [None])[0]
    if not result:
        error = payload.get("chart", {}).get("error") or "empty chart result"
        raise ValueError(f"{config['symbol']}: {error}")

    meta = result.get("meta") or {}
    quote = ((result.get("indicators") or {}).get("quote") or [{}])[0]
    timestamps = result.get("timestamp") or []
    closes = quote.get("close") or []
    clean_closes = [float(value) for value in closes if isinstance(value, (int, float))]
    price = first_number(meta.get("regularMarketPrice"), clean_closes[-1] if clean_closes else None)
    previous_close = first_number(meta.get("chartPreviousClose"), meta.get("previousClose"))

    if price is None or previous_close is None:
        raise ValueError(f"{config['symbol']}: missing price or previous close")

    change = price - previous_close
    change_percent = (change / previous_close * 100) if previous_close else 0
    market_time = meta.get("regularMarketTime")
    updated_at = (
        datetime.fromtimestamp(market_time).astimezone().strftime("%Y-%m-%d %H:%M")
        if isinstance(market_time, (int, float))
        else now_text()
    )

    return {
        **config,
        "currency": meta.get("currency", ""),
        "price": round(price, 4),
        "previousClose": round(previous_close, 4),
        "change": round(change, 4),
        "changePercent": round(change_percent, 4),
        "updatedAt": updated_at,
        "marketState": meta.get("marketState", ""),
        "source": "Yahoo Finance",
        "sourceUrl": url,
        "trend": compact_trend(timestamps, closes),
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
        "source": "Yahoo Finance",
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

    for config in INDEXES:
        try:
            item = fetch_index(config)
            indices.append(item)
            print(f"[ok] fetched {config['symbol']} {item['changePercent']:.2f}%")
        except (urllib.error.URLError, TimeoutError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
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
        "source": "Yahoo Finance",
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
