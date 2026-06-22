import json
import html
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AI_NEWS_JSON = ROOT / "dash/data/ai-news.json"
AI_NEWS_JS = ROOT / "dash/data/ai-news.js"
LAST30_JSON = ROOT / "dash/data/last-30.json"
LAST30_JS = ROOT / "dash/data/last-30.js"
USER_AGENT = "MaxNow/1.0 external-ai-signal-collector"
TZ = timezone(timedelta(hours=8))

KEYWORDS = {
    "agent": 9,
    "agents": 9,
    "codex": 10,
    "openai": 8,
    "anthropic": 8,
    "claude": 8,
    "gemini": 8,
    "deepmind": 7,
    "mistral": 7,
    "llama": 7,
    "reasoning": 7,
    "tool use": 7,
    "computer use": 7,
    "browser use": 6,
    "mcp": 8,
    "model context protocol": 8,
    "sdk": 5,
    "api": 5,
    "developer": 5,
    "coding": 6,
    "code": 4,
    "cost": 6,
    "pricing": 7,
    "tokens": 7,
    "open source": 5,
    "release": 4,
    "benchmark": 4,
    "multimodal": 5,
}

OFFICIAL_SOURCES = [
    ("OpenAI", "https://openai.com/news/rss.xml", "official"),
    ("Google AI", "https://blog.google/technology/ai/rss/", "official"),
    ("GitHub Blog", "https://github.blog/feed/", "official"),
]

HTML_SOURCES = [
    ("Anthropic", "https://www.anthropic.com/news", "https://www.anthropic.com", r"/(?:news|engineering|research)/[^\"'#?]+"),
    ("DeepMind", "https://deepmind.google/blog/", "https://deepmind.google", r"/blog/[^\"'#?]+"),
    ("Mistral AI", "https://mistral.ai/news/", "https://mistral.ai", r"/news/[^\"'#?]+"),
]

GITHUB_RELEASE_FEEDS = [
    ("OpenAI Python", "https://github.com/openai/openai-python/releases.atom"),
    ("OpenAI JS", "https://github.com/openai/openai-node/releases.atom"),
    ("Anthropic SDK", "https://github.com/anthropics/anthropic-sdk-python/releases.atom"),
    ("MCP", "https://github.com/modelcontextprotocol/servers/releases.atom"),
]


@dataclass
class Signal:
    source: str
    title: str
    summary: str
    url: str
    published_at: str
    signal: str
    score: int


def now_local():
    return datetime.now(TZ)


def fetch_text(url):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=8) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def clean_text(value):
    value = html.unescape(value or "")
    text = re.sub(r"<[^>]+>", " ", value or "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_date(value):
    if not value:
        return ""
    for fmt in ("%b %d, %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(value, fmt).replace(tzinfo=TZ).strftime("%Y-%m-%d")
        except Exception:
            pass
    try:
        return parsedate_to_datetime(value).astimezone(TZ).strftime("%Y-%m-%d")
    except Exception:
        pass
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(TZ).strftime("%Y-%m-%d")
    except Exception:
        return str(value)[:10]


def extract_date_from_text(value):
    match = re.search(
        r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\s+\d{1,2},\s+\d{4}\b",
        value or "",
        re.I,
    )
    return parse_date(match.group(0)) if match else ""


def clean_listing_title(value):
    text = clean_text(value)
    text = re.sub(
        r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\s+\d{1,2},\s+\d{4}\b",
        " ",
        text,
        flags=re.I,
    )
    text = re.sub(
        r"^(Product|Announcements?|Research|Engineering|Company|Safety|News|Blog)\b\s*",
        "",
        text,
        flags=re.I,
    )
    text = re.sub(r"\s+", " ", text).strip()
    text = re.split(r"\s+(?:An upgrade|A new|Our latest|Learn how|Read more)\b", text, maxsplit=1)[0].strip()
    return text[:120].rstrip()


def score_signal(title, summary, source):
    text = f"{title} {summary}".lower()
    score = 0
    for keyword, weight in KEYWORDS.items():
        if keyword in text:
            score += weight
    if source in {"OpenAI", "Anthropic", "Google AI", "DeepMind", "Mistral AI"}:
        score += 6
    if "pricing" in text or "cost" in text or "token" in text:
        score += 4
    return score


def make_summary(source, title, text, signal):
    cleaned = clean_text(text)
    if cleaned and cleaned.lower() != title.lower():
        base = cleaned[:130].rstrip()
    else:
        base = title
    reason = "可能影响模型选择、开发工具、agent 能力或使用成本。"
    if signal == "github":
        reason = "开发者工具或 SDK 更新，可能影响 MaxNow / OpenClaw 的实现选择。"
    if signal == "community":
        reason = "社区热度信号，适合观察是否值得后续跟进。"
    if signal == "research":
        reason = "研究信号，适合进入近 30 天观察池。"
    return f"{source}：{base}；{reason}"


def parse_rss(source, url, signal):
    text = fetch_text(url)
    root = ET.fromstring(text)
    items = []
    for item in root.findall(".//item")[:12]:
        title = clean_text(item.findtext("title"))
        link = clean_text(item.findtext("link"))
        description = clean_text(item.findtext("description"))
        published = parse_date(item.findtext("pubDate") or item.findtext("date"))
        if title and link:
            items.append(build_signal(source, title, description, link, published, signal))
    return items


def parse_atom(source, url, signal):
    text = fetch_text(url)
    root = ET.fromstring(text)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    items = []
    for entry in root.findall(".//atom:entry", ns)[:12]:
        title = clean_text(entry.findtext("atom:title", default="", namespaces=ns))
        summary = clean_text(
            entry.findtext("atom:summary", default="", namespaces=ns)
            or entry.findtext("atom:content", default="", namespaces=ns)
        )
        link = ""
        for node in entry.findall("atom:link", ns):
            if node.attrib.get("href"):
                link = node.attrib["href"]
                break
        published = parse_date(
            entry.findtext("atom:published", default="", namespaces=ns)
            or entry.findtext("atom:updated", default="", namespaces=ns)
        )
        if title and link:
            items.append(build_signal(source, title, summary, link, published, signal))
    return items


def parse_html_listing(source, url, base_url, href_pattern, signal):
    text = fetch_text(url)
    pattern = re.compile(rf'href=["\']({href_pattern})["\'][^>]*>(.*?)</a>', re.I | re.S)
    items = []
    for href, label in pattern.findall(text):
        published = extract_date_from_text(label)
        title = clean_listing_title(label)
        if not title or len(title) < 8:
            continue
        link = urllib.parse.urljoin(base_url, href)
        items.append(build_signal(source, title, "", link, published, signal))
        if len(items) >= 12:
            break
    return items


def build_signal(source, title, summary, url, published_at, signal):
    score = score_signal(title, summary, source)
    return Signal(
        source=source,
        title=title,
        summary=make_summary(source, title, summary, signal),
        url=url,
        published_at=published_at,
        signal=signal,
        score=score,
    )


def fetch_hn():
    query = urllib.parse.quote("(AI OR LLM OR OpenAI OR Anthropic OR agent OR coding)")
    url = f"https://hn.algolia.com/api/v1/search_by_date?query={query}&tags=story&hitsPerPage=20"
    data = json.loads(fetch_text(url))
    items = []
    for hit in data.get("hits", []):
        title = clean_text(hit.get("title") or hit.get("story_title"))
        link = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
        published = parse_date(hit.get("created_at", ""))
        if title and link:
            items.append(build_signal("Hacker News", title, "", link, published, "community"))
    return items


def fetch_gdelt():
    query = urllib.parse.quote('(AI OR "large language model" OR OpenAI OR Anthropic OR "AI agent")')
    url = (
        "https://api.gdeltproject.org/api/v2/doc/doc"
        f"?query={query}&mode=ArtList&format=json&maxrecords=20&sort=HybridRel"
    )
    data = json.loads(fetch_text(url))
    items = []
    for article in data.get("articles", []):
        title = clean_text(article.get("title"))
        link = article.get("url", "")
        source = clean_text(article.get("sourceCommonName")) or "GDELT"
        published = parse_date(article.get("seendate", ""))
        if title and link:
            items.append(build_signal(source, title, "", link, published, "news"))
    return items


def fetch_arxiv():
    query = urllib.parse.quote('cat:cs.AI OR cat:cs.CL OR cat:cs.LG')
    url = f"http://export.arxiv.org/api/query?search_query={query}&sortBy=submittedDate&sortOrder=descending&max_results=12"
    return parse_atom("arXiv", url, "research")


def collect_signals():
    signals = []
    failures = []
    jobs = []

    for source, url, signal in OFFICIAL_SOURCES:
        jobs.append((source, parse_rss, (source, url, signal)))

    for source, url, base_url, href_pattern in HTML_SOURCES:
        jobs.append((source, parse_html_listing, (source, url, base_url, href_pattern, "official")))

    for source, url in GITHUB_RELEASE_FEEDS:
        jobs.append((source, parse_atom, (source, url, "github")))

    for fetcher in [fetch_hn, fetch_gdelt, fetch_arxiv]:
        jobs.append((fetcher.__name__, fetcher, ()))

    with ThreadPoolExecutor(max_workers=8) as executor:
        future_map = {
            executor.submit(func, *args): name
            for name, func, args in jobs
        }
        for future in as_completed(future_map):
            name = future_map[future]
            try:
                signals.extend(future.result())
            except Exception as error:
                failures.append(f"{name}: {error}")

    return signals, failures


def dedupe(signals):
    seen = set()
    unique = []
    for item in signals:
        key = re.sub(r"\W+", " ", item.title.lower()).strip()
        if not key or key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def within_days(item, days):
    if not item.published_at:
        return True
    try:
        date = datetime.strptime(item.published_at, "%Y-%m-%d").replace(tzinfo=TZ)
    except ValueError:
        return True
    return date >= now_local() - timedelta(days=days)


def recency_bonus(item):
    if not item.published_at:
        return 0
    try:
        date = datetime.strptime(item.published_at, "%Y-%m-%d").replace(tzinfo=TZ)
    except ValueError:
        return 0
    age = now_local() - date
    if age <= timedelta(days=1):
        return 10
    if age <= timedelta(days=7):
        return 6
    if age <= timedelta(days=30):
        return 3
    return 0


def to_item(item):
    return {
        "source": item.source,
        "title": item.title,
        "summary": item.summary,
        "url": item.url,
        "publishedAt": item.published_at,
        "signal": item.signal,
    }


def select_diverse(signals, limit, max_per_source=2):
    selected = []
    counts = {}
    for item in signals:
        if counts.get(item.source, 0) >= max_per_source:
            continue
        selected.append(item)
        counts[item.source] = counts.get(item.source, 0) + 1
        if len(selected) >= limit:
            break
    if len(selected) < limit:
        for item in signals:
            if item in selected:
                continue
            selected.append(item)
            if len(selected) >= limit:
                break
    return selected


def update_ai_news(signals, failures):
    top = select_diverse(signals, 3, max_per_source=1)
    data = {
        "updatedAt": now_local().strftime("%Y-%m-%d %H:%M"),
        "sourceSummary": "免费 AI 外部信号",
        "items": [to_item(item) for item in top],
    }
    if failures:
        data["notes"] = {
            "partialFailures": failures[:5],
            "policy": "失败源不会清空已有页面；下一次同步会继续尝试。",
        }
    AI_NEWS_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    AI_NEWS_JS.write_text(
        "window.MAXNOW_AI_NEWS_DATA = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )


def group_summary(items, label):
    if not items:
        return f"暂无新的{label}，保留观察。"
    sources = []
    for item in items:
        if item.source not in sources:
            sources.append(item.source)
    return f"本次从 {', '.join(sources[:4])} 捕捉到 {len(items)} 条高相关 AI 信号。"


def update_last30(signals, failures):
    today = now_local().date()
    today_items = select_diverse([item for item in signals if item.published_at == today.isoformat()], 5)
    week_items = select_diverse([item for item in signals if within_days(item, 7)], 7)
    month_items = [item for item in signals if within_days(item, 30)][:12]
    mainlines = build_mainlines(month_items)
    waiting = []
    if failures:
        waiting.append({
            "title": "部分免费源抓取失败",
            "summary": "免费 RSS/API 偶尔会超时或限流，本次已保留其他来源结果，下一次同步继续尝试。",
            "source": "sync_ai_last30.py",
            "confidence": "medium",
            "needsOwnerConfirm": False,
        })

    data = {
        "updatedAt": now_local().strftime("%Y-%m-%d %H:%M"),
        "sourceSummary": "免费 AI 外部信号滚动记忆",
        "today": {
            "date": today.isoformat(),
            "title": "今日 AI 信号",
            "summary": group_summary(today_items, "今日 AI 信号"),
            "items": [last30_item(item) for item in today_items],
        },
        "week": {
            "range": f"{(today - timedelta(days=6)).isoformat()}/{today.isoformat()}",
            "title": "本周 AI 变化",
            "summary": group_summary(week_items, "本周 AI 变化"),
            "items": [last30_item(item) for item in week_items[:7]],
        },
        "last30": {
            "range": f"{(today - timedelta(days=29)).isoformat()}/{today.isoformat()}",
            "title": "近 30 天 AI 主线",
            "summary": "用免费公开源追踪模型、agent、开发者工具、成本和开源生态的持续变化。",
            "mainlines": mainlines,
            "decisions": [
                {
                    "date": today.isoformat(),
                    "title": "Last-30 先采用免费公开源",
                    "summary": "初版不接 X/Twitter 付费 API，优先使用官方 RSS、GitHub、HN、GDELT 和 arXiv。",
                    "source": "Owner direction",
                    "confidence": "high",
                    "needsOwnerConfirm": False,
                }
            ],
            "waiting": waiting,
        },
    }
    LAST30_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    LAST30_JS.write_text(
        "window.MAXNOW_LAST30_DATA = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )


def last30_item(item):
    return {
        "date": item.published_at,
        "title": item.title,
        "summary": item.summary,
        "source": item.source,
        "confidence": "medium" if item.signal in {"community", "news", "research"} else "high",
        "needsOwnerConfirm": False,
        "url": item.url,
    }


def build_mainlines(items):
    buckets = [
        ("模型与 API 更新", ["openai", "anthropic", "gemini", "mistral", "llama", "api", "model"]),
        ("Agent 与工具调用", ["agent", "tool use", "computer use", "browser use", "mcp"]),
        ("开发者工具与 SDK", ["github", "sdk", "coding", "code", "release"]),
        ("成本与 Token", ["cost", "pricing", "token"]),
        ("开源与研究", ["open source", "arxiv", "research", "benchmark"]),
    ]
    results = []
    for title, keywords in buckets:
        matched = []
        for item in items:
            text = f"{item.title} {item.summary} {item.source}".lower()
            if any(keyword in text for keyword in keywords):
                matched.append(item)
        if matched:
            results.append({
                "title": title,
                "summary": f"近 30 天捕捉到 {len(matched)} 条相关信号，代表来源包括 {', '.join(sorted({item.source for item in matched})[:3])}。",
                "status": "active",
                "source": "free external sources",
                "confidence": "medium",
                "needsOwnerConfirm": False,
            })
    return results[:5]


def main():
    signals, failures = collect_signals()
    signals = [item for item in dedupe(signals) if item.score > 0]
    signals.sort(key=lambda item: (item.score + recency_bonus(item), item.published_at), reverse=True)
    signals = signals[:40]

    if not signals:
        raise RuntimeError("no AI signals collected from free sources")

    update_ai_news(signals, failures)
    update_last30(signals, failures)
    print(f"[ok] collected {len(signals)} AI signals")
    if failures:
        print(f"[warn] partial failures: {len(failures)}")


if __name__ == "__main__":
    try:
        main()
    except (urllib.error.URLError, RuntimeError, ET.ParseError, json.JSONDecodeError) as error:
        print(f"[fail] {error}", file=sys.stderr)
        sys.exit(1)
