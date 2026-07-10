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

CORE_AI_TERMS = (
    "ai",
    "llm",
    "agent",
    "agents",
    "openai",
    "anthropic",
    "claude",
    "gemini",
    "deepmind",
    "mistral",
    "llama",
    "reasoning",
    "mcp",
    "model context protocol",
    "model",
    "models",
    "token",
    "tokens",
)

LOW_LEVEL_RELEASE_TERMS = (
    "chore",
    "chores",
    "bug fix",
    "bug fixes",
    "fixes",
    "patch",
    "dependencies",
    "updated packages",
)

SUBSTANTIVE_AI_TERMS = (
    "ai",
    "llm",
    "agent",
    "agents",
    "chatgpt",
    "claude",
    "gemini",
    "mistral",
    "llama",
    "model",
    "models",
    "reasoning",
    "mcp",
    "model context protocol",
    "api",
    "token",
    "tokens",
    "ocr",
    "multimodal",
    "benchmark",
)

OFFICIAL_LABS = {"OpenAI", "Anthropic", "Google AI", "DeepMind", "Mistral AI"}

CASE_STUDY_TERMS = (
    "case study",
    "customer story",
    "moves faster with",
    "aims to become ai-native",
    "uses claude",
    "with chatgpt and codex",
    "educators",
    "government and national security partnerships",
    "adoption has expanded",
    "partner to bring",
)

RELEASE_TERMS = (
    "introducing",
    "launching",
    "launched",
    "release",
    "released",
    "now available",
    "general availability",
    "previewing",
    "new capabilities",
    "new generation",
    "adds support",
    "is now the preferred model",
)

RESEARCH_TERMS = (
    "benchmark",
    "evaluation",
    "evaluations",
    "research",
    "system card",
)

PRODUCT_PATTERNS = (
    re.compile(r"\bGPT[-\s]?\d+(?:\.\d+)?(?:\s+(?:Sol|Terra|Luna|Instant Mini))?\b", re.I),
    re.compile(r"\bGPT[-\s]?Live\b", re.I),
    re.compile(r"\bChatGPT Work\b", re.I),
    re.compile(r"\bClaude(?:\s+[A-Za-z]+){0,2}\s+\d+(?:\.\d+)?\b", re.I),
    re.compile(r"\bClaude Science\b", re.I),
    re.compile(r"\bGemini(?:\s+API|\s+\d+(?:\.\d+)?(?:\s+[A-Za-z]+){0,2})\b", re.I),
    re.compile(r"\bMistral\s+(?:OCR|Medium|Small|Large)\s+\d+(?:\.\d+)?\b", re.I),
)

CURATED_EVENTS = {
    "/index/gpt-5-6": {
        "title": "OpenAI 正式发布 GPT-5.6",
        "summary": "GPT-5.6 Sol、Terra 和 Luna 已向 ChatGPT、Codex 与 API 全面开放，并新增 max / ultra 推理档位、多智能体测试版和程序化工具调用。",
        "kind": "model_release",
        "priority": 120,
        "topic": "gpt-5.6",
    },
    "/index/gpt-5-6-preferred-model-microsoft-365-copilot": {
        "title": "GPT-5.6 成为 Microsoft 365 Copilot 首选模型",
        "summary": "Microsoft 365 Copilot 已将 GPT-5.6 用于 Word、Excel、PowerPoint、Chat 和 Cowork 等工作场景。",
        "kind": "model_release",
        "priority": 92,
        "topic": "gpt-5.6",
    },
    "/index/chatgpt-for-your-most-ambitious-work": {
        "title": "OpenAI 发布 ChatGPT Work 长时任务 Agent",
        "summary": "ChatGPT Work 可跨应用和文件执行任务、持续工作数小时，并把目标整理成可交付成果。",
        "kind": "product_release",
        "priority": 108,
        "topic": "chatgpt-work",
    },
    "/index/introducing-gpt-live": {
        "title": "OpenAI 发布 GPT-Live 实时语音模型",
        "summary": "新一代实时语音模型已用于 ChatGPT Voice，重点改善自然对话、噪声处理和打断体验。",
        "kind": "model_release",
        "priority": 104,
        "topic": "gpt-live",
    },
    "/index/separating-signal-from-noise-coding-evaluations": {
        "title": "OpenAI 指出 SWE-Bench Pro 评测存在可靠性问题",
        "summary": "官方分析认为该编码基准的可靠性与准确性存在问题，比较编码模型时不能只看单一榜单。",
        "kind": "research",
        "priority": 82,
        "topic": "swe-bench-pro-reliability",
    },
    "/innovation-and-ai/technology/developers-tools/expanding-managed-agents-gemini-api": {
        "title": "Gemini API 增强托管 Agent：后台任务与远程 MCP",
        "summary": "Google 为 Gemini API 的托管 Agent 增加后台任务、远程 MCP 等能力，面向可持续运行的生产级 Agent。",
        "kind": "api_update",
        "priority": 98,
        "topic": "gemini-managed-agents",
    },
    "/news/reflect-with-claude": {
        "title": "Anthropic 为 Claude 增加使用回顾功能",
        "summary": "Claude 新增个人使用回顾入口，用于整理用户与 Claude 的协作方式和变化。",
        "kind": "product_release",
        "priority": 78,
        "topic": "claude-reflection",
    },
    "/news/claude-sonnet-5": {
        "title": "Anthropic 发布 Claude Sonnet 5",
        "summary": "Claude Sonnet 5 面向编码、Agent 和专业工作负载，是 Anthropic 新一代主力模型。",
        "kind": "model_release",
        "priority": 112,
        "topic": "claude-sonnet-5",
    },
    "/news/claude-science-ai-workbench": {
        "title": "Anthropic 发布 Claude Science 科研工作台",
        "summary": "Claude Science 集成科研常用工具、软件包和计算资源，并强调可审计的研究产物。",
        "kind": "product_release",
        "priority": 90,
        "topic": "claude-science",
    },
    "/news/redeploying-fable-5": {
        "title": "Claude Fable 5 与 Mythos 5 恢复全球开放",
        "summary": "Anthropic 在出口限制解除后恢复两款模型的全球访问，并同步更新越狱风险评估框架。",
        "kind": "model_release",
        "priority": 88,
        "topic": "claude-fable-5-access",
    },
    "/innovation-and-ai/models-and-research/google-research/amie-for-disease-management-in-nature": {
        "title": "Google AMIE 医疗 AI 完成复杂疾病管理研究",
        "summary": "Nature 研究显示，AMIE 对复杂疾病管理的表现接近初级保健医生，是医疗对话模型的重要进展。",
        "kind": "research",
        "priority": 72,
        "topic": "google-amie-disease-management",
    },
}


def has_term(text, term):
    escaped = re.escape(term)
    if " " in term:
        return re.search(rf"(?<!\w){escaped}(?!\w)", text) is not None
    return re.search(rf"\b{escaped}\b", text) is not None


def has_any_term(text, terms):
    return any(has_term(text, term) for term in terms)


def signal_subject_text(item):
    return f"{item.title} {item.summary or ''}".lower()


def event_path(item):
    return urllib.parse.urlparse(item.url or "").path.rstrip("/")


def curated_event(item):
    return CURATED_EVENTS.get(event_path(item))


def extract_product_label(text):
    for pattern in PRODUCT_PATTERNS:
        match = pattern.search(text or "")
        if match:
            return re.sub(r"\s+", " ", match.group(0)).strip()
    return ""


def event_kind(item):
    curated = curated_event(item)
    if curated:
        return curated["kind"]

    text = signal_subject_text(item)
    if re.fullmatch(r"v?\d+\.\d+\.\d+", item.title.strip(), re.I):
        return "noise"
    if has_any_term(text, CASE_STUDY_TERMS):
        return "noise"
    if "the latest ai news we announced" in text:
        return "noise"
    if item.signal == "github" and has_any_term(text, LOW_LEVEL_RELEASE_TERMS):
        return "noise"

    product = extract_product_label(text)
    if product and has_any_term(text, RELEASE_TERMS):
        return "model_release" if re.search(r"\d|gpt-live", product, re.I) else "product_release"
    if product and item.source in OFFICIAL_LABS:
        return "model_update"
    if has_any_term(text, RELEASE_TERMS) and has_any_term(text, ("agent", "mcp", "api", "tool use", "computer use")):
        return "api_update"
    if item.source in OFFICIAL_LABS and has_any_term(text, RESEARCH_TERMS) and has_any_term(text, SUBSTANTIVE_AI_TERMS):
        return "research"
    if item.signal == "github" and has_any_term(text, ("agent", "mcp", "model", "api")):
        return "developer_release"
    return "noise"


def topic_key(item):
    curated = curated_event(item)
    if curated:
        return curated["topic"]
    product = extract_product_label(signal_subject_text(item))
    if product:
        return re.sub(r"[^a-z0-9]+", "-", product.lower()).strip("-")
    path = event_path(item)
    return path.rsplit("/", 1)[-1] or re.sub(r"\W+", "-", item.title.lower()).strip("-")


def localized_signal(item):
    curated = curated_event(item)
    if curated:
        return curated["title"], curated["summary"]

    text = signal_subject_text(item)
    product = extract_product_label(text)
    kind = event_kind(item)
    if product:
        verb = "发布" if kind in {"model_release", "product_release"} else "更新"
        title = f"{item.source} {verb} {product}"
    elif "managed agents" in text or ("agent" in text and "api" in text):
        title = f"{item.source} 发布 Agent 与 API 能力更新"
    elif "mcp" in text:
        title = f"{item.source} 发布 MCP 开发者工具更新"
    elif has_any_term(text, RESEARCH_TERMS):
        title = f"{item.source} 发布 AI 评测与研究进展"
    else:
        title = f"{item.source} 发布 AI 前沿更新"

    if "background task" in text and "remote mcp" in text:
        summary = "官方新增后台任务和远程 MCP 等能力，面向可持续运行的生产级 Agent。"
    elif "voice" in text or "gpt-live" in text:
        summary = "官方发布实时语音能力更新，重点改善自然对话、噪声处理和打断体验。"
    elif "pricing" in text or "cost" in text or "token" in text:
        summary = "官方公告包含模型定价或 Token 成本变化，具体价格与开放范围已保留在原文。"
    elif has_any_term(text, RESEARCH_TERMS):
        summary = "官方发布新的模型评测或研究结果，可用于校准模型能力判断。"
    elif "agent" in text or "mcp" in text or "tool use" in text:
        summary = "官方更新 Agent 或工具调用能力，具体功能与开放范围已保留在原文。"
    else:
        summary = "官方发布模型或产品能力更新，具体功能、价格与开放范围已保留在原文。"
    return title, summary

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
    if source in OFFICIAL_LABS:
        score += 6
    if source in {"GitHub Blog"} and not has_any_term(text, CORE_AI_TERMS):
        score -= 8
    if re.match(r"^v?\d+\.\d+\.\d+$", title.strip(), re.I):
        score -= 4
    if "pricing" in text or "cost" in text or "token" in text:
        score += 4
    if re.search(r"\b(?:gpt|claude|gemini|mistral|llama)[-\s]?\d", text, re.I):
        score += 20
    if has_any_term(text, RELEASE_TERMS):
        score += 12
    if has_any_term(text, CASE_STUDY_TERMS):
        score -= 30
    return score


def is_ai_relevant(item):
    if curated_event(item):
        return True
    body = signal_subject_text(item)
    text = f"{body} {item.source}".lower()
    if item.source in OFFICIAL_LABS | {"arXiv"}:
        return has_any_term(body, SUBSTANTIVE_AI_TERMS)
    return has_any_term(text, CORE_AI_TERMS)


def is_major_ai_event(item):
    return event_kind(item) != "noise"


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
        summary=clean_text(summary),
        url=url,
        published_at=published_at,
        signal=signal,
        score=score,
    )


def fetch_hn():
    query = urllib.parse.quote("(AI OR LLM OR OpenAI OR Anthropic OR agent OR coding)")
    cutoff = int((now_local() - timedelta(days=30)).timestamp())
    url = (
        f"https://hn.algolia.com/api/v1/search_by_date?query={query}&tags=story&hitsPerPage=20"
        f"&numericFilters=created_at_i%3E{cutoff}"
    )
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
        return False
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
    title, summary = localized_signal(item)
    return {
        "source": item.source,
        "title": title,
        "summary": summary,
        "url": item.url,
        "publishedAt": item.published_at,
        "signal": item.signal,
        "originalTitle": item.title,
    }


def frontier_priority(item):
    curated = curated_event(item)
    if curated:
        return curated["priority"] + recency_bonus(item)
    kind_bonus = {
        "model_release": 70,
        "product_release": 58,
        "api_update": 54,
        "model_update": 48,
        "developer_release": 38,
        "research": 30,
    }
    return item.score + recency_bonus(item) + kind_bonus.get(event_kind(item), 0)


def select_frontier_events(signals, limit, excluded_topics=None):
    excluded = set(excluded_topics or [])
    selected = []
    seen_topics = set(excluded)
    candidates = sorted(
        (item for item in signals if is_major_ai_event(item)),
        key=lambda item: (frontier_priority(item), item.published_at),
        reverse=True,
    )
    for item in candidates:
        topic = topic_key(item)
        if topic in seen_topics:
            continue
        selected.append(item)
        seen_topics.add(topic)
        if len(selected) >= limit:
            break
    return selected


def update_ai_news(signals, failures):
    top = select_frontier_events([item for item in signals if within_days(item, 7)], 3)
    data = {
        "updatedAt": now_local().strftime("%Y-%m-%d %H:%M"),
        "sourceSummary": "AI 前沿简报 · 官方来源优先",
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
        return f"暂无新的{label}。"
    if label == "最新发布":
        return f"最近 3 天最重要的 {len(items)} 条模型与产品发布。"
    if label == "本周前沿":
        return f"本周其他 {len(items)} 条值得了解的模型、Agent 与评测更新。"
    return f"近 30 天值得补看的 {len(items)} 个正式发布与重要研究。"


def latest_signal_group(signals, today):
    recent = select_frontier_events([item for item in signals if within_days(item, 3)], 3)
    if len(recent) < 3:
        fallback = select_frontier_events(
            [item for item in signals if within_days(item, 7)],
            3 - len(recent),
            {topic_key(item) for item in recent},
        )
        recent.extend(fallback)
    latest_date = recent[0].published_at if recent else today.isoformat()
    return {
        "date": latest_date,
        "title": "最新发布",
        "summary": group_summary(recent, "最新发布"),
        "items": recent,
    }


def update_last30(signals, failures):
    today = now_local().date()
    latest_group = latest_signal_group(signals, today)
    latest_topics = {topic_key(item) for item in latest_group["items"]}
    week_items = select_frontier_events(
        [item for item in signals if within_days(item, 7)],
        4,
        latest_topics,
    )
    used_topics = latest_topics | {topic_key(item) for item in week_items}
    month_items = select_frontier_events(
        [item for item in signals if within_days(item, 30)],
        5,
        used_topics,
    )
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
        "sourceSummary": "AI 前沿简报 · 官方来源优先",
        "today": {
            "date": latest_group["date"],
            "title": latest_group["title"],
            "summary": latest_group["summary"],
            "items": [last30_item(item) for item in latest_group["items"]],
        },
        "week": {
            "range": f"{(today - timedelta(days=6)).isoformat()}/{today.isoformat()}",
            "title": "本周前沿",
            "summary": group_summary(week_items, "本周前沿"),
            "items": [last30_item(item) for item in week_items],
        },
        "last30": {
            "range": f"{(today - timedelta(days=29)).isoformat()}/{today.isoformat()}",
            "title": "近 30 天关键进展",
            "summary": group_summary(month_items, "近 30 天关键进展"),
            "mainlines": [last30_item(item) for item in month_items],
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
    title, summary = localized_signal(item)
    return {
        "date": item.published_at,
        "title": title,
        "summary": summary,
        "source": item.source,
        "sourceType": signal_source_type(item.signal),
        "confidence": "medium" if item.signal in {"community", "news", "research"} else "high",
        "needsOwnerConfirm": False,
        "url": item.url,
        "originalTitle": item.title,
    }


def signal_source_type(signal):
    labels = {
        "official": "官方发布",
        "github": "开发者发布",
        "community": "社区来源",
        "research": "研究来源",
        "news": "新闻索引",
    }
    return labels.get(signal, "公开来源")


def run_self_test():
    gpt = build_signal(
        "OpenAI",
        "GPT-5.6: Frontier intelligence that scales with your ambition",
        "More intelligence from every token and stronger performance per dollar.",
        "https://openai.com/index/gpt-5-6/",
        "2026-07-09",
        "official",
    )
    case_study = build_signal(
        "OpenAI",
        "Australian Payments Plus moves faster with ChatGPT and Codex",
        "A customer story about enterprise adoption.",
        "https://openai.com/index/australian-payments-plus/",
        "2026-07-07",
        "official",
    )
    gpt_followup = build_signal(
        "OpenAI",
        "GPT-5.6 is now the preferred model in Microsoft 365 Copilot",
        "GPT-5.6 powers Microsoft 365 Copilot.",
        "https://openai.com/index/gpt-5-6-preferred-model-microsoft-365-copilot/",
        "2026-07-09",
        "official",
    )
    assert is_major_ai_event(gpt)
    assert not is_major_ai_event(case_study)
    title, summary = localized_signal(gpt)
    assert title == "OpenAI 正式发布 GPT-5.6"
    assert "关注它" not in summary and re.search(r"[\u4e00-\u9fff]", summary)
    selected = select_frontier_events([gpt_followup, gpt], 3)
    assert len(selected) == 1 and topic_key(selected[0]) == "gpt-5.6"
    print("[ok] AI frontier ranking and Chinese brief self-test")


def main():
    signals, failures = collect_signals()
    signals = [item for item in dedupe(signals) if item.score > 0 and is_ai_relevant(item)]
    signals.sort(key=lambda item: (frontier_priority(item), item.published_at), reverse=True)
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
        if "--self-test" in sys.argv:
            run_self_test()
        else:
            main()
    except (urllib.error.URLError, RuntimeError, ET.ParseError, json.JSONDecodeError) as error:
        print(f"[fail] {error}", file=sys.stderr)
        sys.exit(1)
