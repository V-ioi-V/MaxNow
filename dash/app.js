const DATA_URL = "./data/dashboard.json";
const AI_NEWS_URL = "./data/ai-news.json";
const LAST30_URL = "./data/last-30.json";
const WIKI_TODO_URL = "./data/wiki-todos.json";
const CHECKIN_URL = "./data/dounai_checkin.json";
const OPENCLAW_USAGE_URL = "./data/openclaw-usage.json";
const WIKI_TODO_SOURCE_URL = "https://github.com/V-ioi-V/personal-wiki/blob/main/wiki/tasks/todo.json";
const WIKI_TASK_BASE_URL = "https://github.com/V-ioi-V/personal-wiki/blob/main/wiki/tasks/";

const fallbackData = window.MAXNOW_DASHBOARD_DATA || {};
const fallbackAiNews = window.MAXNOW_AI_NEWS_DATA || { items: [] };
const fallbackLast30 = window.MAXNOW_LAST30_DATA || {};
const fallbackWikiTodo = window.MAXNOW_WIKI_TODO_DATA || { tasks: [] };
const fallbackCheckin = {};
const fallbackOpenclawUsage = window.MAXNOW_OPENCLAW_USAGE_DATA || { days: [] };

let dashboardData = fallbackData;
let aiNewsData = fallbackAiNews;
let last30Data = fallbackLast30;
let wikiTodoData = fallbackWikiTodo;
let checkinData = fallbackCheckin;
let openclawUsageData = fallbackOpenclawUsage;
let wikiTodoError = "";
let activeTokenRange = "7d";

const qs = (selector) => document.querySelector(selector);
const qsa = (selector) => [...document.querySelectorAll(selector)];

const emptyTemplate = qs("#empty-template");
const refreshButton = qs("#refresh-button");
const viewTitle = qs("#view-title");

const copy = {
  unnamedTask: "\u672a\u547d\u540d\u4e8b\u9879",
  unnamedInfo: "\u672a\u547d\u540d\u4fe1\u606f",
  unnamedTime: "\u672a\u547d\u540d\u65f6\u95f4\u70b9",
  item: "\u4e8b\u9879",
  open: "\u6253\u5f00",
  waitBrief: "\u7b49\u5f85 OpenClaw \u5199\u5165\u4eca\u5929\u7684\u6458\u8981\u3002",
  waiting: "\u7b49\u5f85",
  syncWaiting: "\u7b49\u5f85\u6570\u636e\u540c\u6b65",
  noData: "\u6682\u65e0\u6570\u636e",
  taskCount: "\u6761\u4e8b\u9879",
  checkWaiting: "\u7b49\u5f85\u68c0\u6d4b",
  sync: "\u7b49\u5f85\u540c\u6b65",
  hour24: "24\u5c0f\u65f6",
  day1: "1d",
  updatedAt: "\u66f4\u65b0\u4e8e",
  noNote: "\u6682\u65e0\u8bf4\u660e\u3002",
  tokenTitle: "Token \u7528\u91cf",
  dounaiTitle: "\u8c46\u5976",
  today: "\u4eca\u5929",
  energy: "\u80fd\u91cf",
  focus: "\u4e3b\u7ebf",
  updatedAtShort: "\u66f4\u65b0",
  statusSnapshot: "\u72b6\u6001\u5feb\u7167",
  todayEvents: "\u4eca\u65e5\u5927\u4e8b",
  weekEvents: "\u672c\u5468\u5927\u4e8b",
  last30Mainlines: "\u8fd1 30 \u5929\u4e3b\u7ebf",
  wikiTodoReady: "\u5df2\u8bfb\u53d6",
  wikiTodoFailed: "\u8bfb\u53d6\u5931\u8d25",
  wikiTodoEmpty: "\u6682\u65e0\u672a\u5b8c\u6210\u5f85\u529e",
  dueAt: "\u622a\u6b62",
};

function formatToken(value) {
  if (!Number.isFinite(value)) return "--";
  if (value >= 1000000) return `${(value / 1000000).toFixed(value >= 10000000 ? 0 : 1)}M`;
  if (value >= 1000) return `${Math.round(value / 1000)}K`;
  return String(value);
}

function formatCost(value) {
  if (!Number.isFinite(value)) return "--";
  if (value >= 1) return `$${value.toFixed(2)}`;
  if (value >= 0.01) return `$${value.toFixed(3)}`;
  if (value > 0) return `$${value.toFixed(4)}`;
  return "$0";
}

function formatFlow(value, unit = "auto") {
  const amount = Number(value);
  if (!Number.isFinite(amount)) return "--";
  if (unit === "mb") return `${Math.round(amount)} MB`;
  if (unit === "gb" || amount >= 1024) return `${(amount / 1024).toFixed(1)} GB`;
  return `${Math.round(amount)} MB`;
}

function formatTraffic(value) {
  const amount = Number(value);
  if (!Number.isFinite(amount)) return "--";
  if (amount >= 1024 * 1024) return `${(amount / 1024 / 1024).toFixed(2)} TB`;
  if (amount >= 1024) return `${(amount / 1024).toFixed(1)} GB`;
  return `${Math.round(amount)} MB`;
}

function parseTrafficLabel(label) {
  const match = String(label || "").trim().match(/^([\d.]+)\s*(TB|GB|MB|B)$/i);
  if (!match) return NaN;
  const amount = Number(match[1]);
  if (!Number.isFinite(amount)) return NaN;
  const unit = match[2].toUpperCase();
  if (unit === "TB") return amount * 1024 * 1024;
  if (unit === "GB") return amount * 1024;
  if (unit === "MB") return amount;
  return amount / 1024 / 1024;
}

function parseDounaiDate(value) {
  if (!value) return null;
  const normalized = String(value).trim().replace(" ", "T");
  const date = new Date(`${normalized}+08:00`);
  return Number.isNaN(date.getTime()) ? null : date;
}

function formatDateOnly(value) {
  const dateText = String(value || "").trim();
  return dateText ? dateText.slice(0, 10) : "--";
}

function getDaysRemaining(value) {
  const date = parseDounaiDate(value);
  if (!date) return NaN;
  return Math.max(0, Math.ceil((date.getTime() - Date.now()) / 86400000));
}

function formatHours(value) {
  const amount = Number(value);
  if (!Number.isFinite(amount)) return "--";
  return `${amount.toFixed(amount >= 10 ? 1 : 2)}h`;
}

function formatDuration(value) {
  const amount = Number(value);
  if (!Number.isFinite(amount)) return "--";
  let days = Math.floor(amount / 24);
  let hours = Math.round(amount - days * 24);
  if (hours === 24) {
    days += 1;
    hours = 0;
  }
  if (days > 0 && hours > 0) return `${days}d ${hours}h`;
  if (days > 0) return `${days}d`;
  return `${hours}h`;
}

function formatDateShort(date = "") {
  return date.slice(5) || "--";
}

function setText(selector, value) {
  const element = qs(selector);
  if (element) element.textContent = value ?? "";
}

function clearAndFill(container, builder, items) {
  if (!container) return;
  container.replaceChildren();

  if (!items?.length) {
    container.appendChild(emptyTemplate.content.cloneNode(true));
    return;
  }

  items.forEach((item) => container.appendChild(builder(item)));
}

function createTask(task) {
  const article = document.createElement("article");
  article.className = "task-item";
  article.dataset.status = task.status || "active";
  article.dataset.tone = getTone(task.label || task.status || task.title);
  article.innerHTML = `
    <span class="task-dot" aria-hidden="true"></span>
    <div>
      <p class="item-title"></p>
      <p class="item-copy"></p>
    </div>
    <span class="item-tag"></span>
  `;
  article.querySelector(".item-title").textContent = task.title || copy.unnamedTask;
  article.querySelector(".item-copy").textContent = task.note || "";
  article.querySelector(".item-tag").textContent = task.label || copy.item;
  return article;
}

function createFeed(feed) {
  const article = document.createElement("article");
  article.className = "feed-item";
  article.dataset.tone = getTone(feed.source || feed.title);
  article.innerHTML = `
    <div class="item-head">
      <p class="item-title"></p>
      <span class="item-tag"></span>
    </div>
    <p class="item-copy"></p>
  `;
  article.querySelector(".item-tag").textContent = feed.source || "Note";
  article.querySelector(".item-title").textContent = feed.title || copy.unnamedInfo;
  article.querySelector(".item-copy").textContent = feed.summary || "";
  appendLink(article, feed.url);
  return article;
}

function createAiNewsItem(item) {
  const article = document.createElement("article");
  article.className = "ai-news-item";
  article.dataset.tone = getTone(item.signal || item.source);
  article.innerHTML = `
    <div class="item-head">
      <p class="item-title"></p>
      <div class="item-head-meta">
        <span class="item-tag"></span>
        <time></time>
      </div>
    </div>
    <p class="item-copy"></p>
  `;
  article.querySelector(".item-tag").textContent = item.source || "AI";
  article.querySelector("time").textContent = item.publishedAt || "";
  article.querySelector(".item-title").textContent = item.title || copy.unnamedInfo;
  article.querySelector(".item-copy").textContent = item.summary || "";
  appendLink(article, item.url);
  return article;
}

function createLast30Item(item) {
  const article = document.createElement("article");
  article.className = "last30-item";
  article.dataset.tone = getTone(item.status || item.confidence || item.source || item.title);
  article.innerHTML = `
    <div class="last30-item-head">
      <p class="item-title"></p>
      <span class="item-tag"></span>
    </div>
    <p class="item-copy"></p>
  `;
  article.querySelector(".item-title").textContent = item.title || copy.unnamedInfo;
  article.querySelector(".item-copy").textContent = item.summary || item.note || "";
  article.querySelector(".item-tag").textContent = item.needsOwnerConfirm
    ? "\u5f85\u786e\u8ba4"
    : item.date || item.status || item.source || copy.item;
  appendLink(article, item.url);
  return article;
}

function createWikiTodoItem(task) {
  const article = document.createElement("article");
  article.className = "wiki-todo-item";
  article.dataset.tone = getTone(task.module || task.status || task.title);
  article.innerHTML = `
    <div>
      <p class="item-title"></p>
      <p class="item-copy"></p>
    </div>
    <span class="item-tag"></span>
  `;

  const dueText = task.due_at ? `${copy.dueAt} ${task.due_at}` : task.status || copy.item;
  article.querySelector(".item-title").textContent = task.title || copy.unnamedTask;
  article.querySelector(".item-copy").textContent = task.module || task.source_file || "";
  article.querySelector(".item-tag").textContent = dueText;

  const link = getWikiTodoLink(task);
  if (link) appendLink(article, link);
  return article;
}

function appendLink(container, url) {
  if (!url) return;
  const link = document.createElement("a");
  link.href = url;
  link.target = "_blank";
  link.rel = "noreferrer";
  link.textContent = copy.open;
  container.appendChild(link);
}

function getWikiTodoLink(task) {
  const firstLink = task.links?.[0]?.href;
  if (!firstLink) return WIKI_TODO_SOURCE_URL;
  try {
    return new URL(firstLink, WIKI_TASK_BASE_URL).href;
  } catch (error) {
    return WIKI_TODO_SOURCE_URL;
  }
}

function createTimelineItem(item) {
  const li = document.createElement("li");
  li.innerHTML = `
    <time></time>
    <div>
      <p class="item-title"></p>
      <p class="item-copy"></p>
    </div>
  `;
  li.querySelector("time").textContent = item.time || "--:--";
  li.querySelector(".item-title").textContent = item.title || copy.unnamedTime;
  li.querySelector(".item-copy").textContent = item.note || "";
  return li;
}

function createSystemItem(item) {
  const article = document.createElement("article");
  article.className = "system-item";
  article.dataset.tone = getTone(item.key || item.value || item.name);
  const percent = getSystemPercent(item);
  if (percent !== null) article.classList.add("has-ring");
  article.dataset.health = getSystemHealth(item);
  article.innerHTML = `
    <div>
      <p class="item-title"></p>
      <p class="item-copy"></p>
    </div>
    <span class="system-value"></span>
  `;
  article.querySelector(".item-title").textContent = item.name || item.key || "System";
  article.querySelector(".item-copy").textContent = formatSystemNote(item);
  const value = article.querySelector(".system-value");
  if (percent !== null) {
    value.classList.add("system-ring");
    value.style.setProperty("--value", `${percent}%`);
    value.dataset.level = percent >= 85 ? "high" : percent >= 65 ? "medium" : "low";
    value.innerHTML = `<span>${percent}%</span>`;
  } else {
    value.textContent = item.value || "--";
  }
  return article;
}

function getSystemPercent(item) {
  const text = String(item.value || "").trim();
  if (!text.endsWith("%")) return null;
  const value = Number.parseInt(text, 10);
  if (!Number.isFinite(value)) return null;
  return Math.max(0, Math.min(100, value));
}

function formatSystemNote(item) {
  const note = item.note || "";
  if (item.key === "cpu") {
    return note
      .replace("cores;", "核；")
      .replace("1/5/15 min load", "1/5/15 分钟负载")
      .replace("load", "负载");
  }
  if (item.key === "disk" || item.key === "memory") {
    return note.replace("available on", "可用，挂载点").replace("available", "可用");
  }
  return note;
}

function getSystemHealth(item) {
  const value = String(item.value || "").toLowerCase();
  const note = String(item.note || "").toLowerCase();
  if (["fail", "failed", "check", "not set"].includes(value)) return "bad";
  if (value === "unknown" || value === "pending") return "unknown";
  if (item.key === "failure-log" && note.includes("[fail]")) return "bad";
  return "ok";
}

function getTone(value = "") {
  const text = String(value).toLowerCase();
  if (text.includes("failure") || text.includes("fail") || text.includes("check")) return "red";
  if (text.includes("token") || text.includes("data") || text.includes("github")) return "blue";
  if (text.includes("auto") || text.includes("openclaw") || text.includes("skill")) return "cyan";
  if (text.includes("server") || text.includes("deploy") || text.includes("\u90e8\u7f72")) return "orange";
  if (text.includes("https") || text.includes("certificate") || text.includes("cron") || text.includes("timer")) return "green";
  if (text.includes("ai") || text.includes("official") || text.includes("openai")) return "purple";
  if (text.includes("wait") || text.includes("pending") || text.includes("\u7b49")) return "gray";
  if (text.includes("done") || text.includes("online") || text.includes("\u6b63\u5e38")) return "green";
  return "blue";
}

function getSystemItem(key) {
  return dashboardData.system?.find((item) => item.key === key) || {};
}

function getTokenRange(key = activeTokenRange) {
  const usage = getTokenUsage();
  const ranges = usage.ranges || [];
  return ranges.find((range) => range.key === key) || ranges[0] || {};
}

function normalizeUsageDay(day) {
  return {
    ...day,
    input: Number(day.inputTokens || day.input || 0),
    output: Number(day.outputTokens || day.output || 0),
    cacheRead: Number(day.cacheReadTokens || day.cacheRead || 0),
    total: Number(day.totalTokens || day.total || 0),
    cost: Number(day.estimatedCostUsd || day.cost || 0),
  };
}

function sumUsage(days) {
  return days.reduce(
    (sum, day) => ({
      input: sum.input + Number(day.input || 0),
      output: sum.output + Number(day.output || 0),
      cacheRead: sum.cacheRead + Number(day.cacheRead || 0),
      total: sum.total + Number(day.total || 0),
      cost: sum.cost + Number(day.cost || 0),
      runs: sum.runs + Number(day.runs || 0),
    }),
    { input: 0, output: 0, cacheRead: 0, total: 0, cost: 0, runs: 0 },
  );
}

function formatDateLabel(dateText) {
  const parts = String(dateText || "").split("-");
  return parts.length === 3 ? `${Number(parts[1])}/${Number(parts[2])}` : dateText || "";
}

function buildModelBreakdown(days) {
  const byModel = new Map();
  days.forEach((day) => {
    (day.byModel || []).forEach((model) => {
      const name = model.model || model.name || "Model";
      const current = byModel.get(name) || { name, total: 0, cost: 0 };
      current.total += Number(model.totalTokens || model.total || 0);
      current.cost += Number(model.estimatedCostUsd || model.cost || 0);
      byModel.set(name, current);
    });
  });
  const models = [...byModel.values()].sort((a, b) => b.total - a.total);
  const total = models.reduce((sum, model) => sum + model.total, 0) || 1;
  return models.map((model) => ({
    ...model,
    share: Math.round((model.total / total) * 100),
  }));
}

function getOpenclawTokenUsage() {
  const rawDays = Array.isArray(openclawUsageData.days) ? openclawUsageData.days : [];
  if (!rawDays.length) return null;

  const days = rawDays.map(normalizeUsageDay).sort((a, b) => String(b.date).localeCompare(String(a.date)));
  const rangeDefs = [
    { key: "1d", label: "1d", count: 1 },
    { key: "7d", label: "7d", count: 7 },
    { key: "30d", label: "30d", count: 30 },
    { key: "all", label: "all", count: Infinity },
  ];
  const ranges = rangeDefs.map((range) => {
    const selected = Number.isFinite(range.count) ? days.slice(0, range.count) : days;
    const summary = sumUsage(selected);
    const sourceLabel = openclawUsageData.pricingBasis === "openrouter-equivalent" ? "OpenRouter 等价估算" : "估算";
    return {
      key: range.key,
      label: range.label,
      ...summary,
      note: `OpenClaw ${range.label} 用量，费用为 ${sourceLabel}，不是实际扣费账单。`,
      selectedDays: selected,
    };
  });

  const active = ranges.find((range) => range.key === activeTokenRange) || ranges[1] || ranges[0];
  const chartDays = [...days].reverse().slice(-30);
  return {
    updatedAt: openclawUsageData.updatedAt,
    ranges,
    models: buildModelBreakdown(active.selectedDays || []),
    daily: chartDays.map((day) => ({
      date: day.date,
      label: formatDateLabel(day.date),
      total: day.total,
      cost: day.cost,
    })),
    sourceSummary: "OpenClaw usage ledger",
  };
}

function getTokenUsage() {
  return getOpenclawTokenUsage() || dashboardData.tokenUsage || {};
}

function getLast30Group(key) {
  if (key === "mainlines") return last30Data.last30 || {};
  return last30Data[key] || {};
}

function getLast30Items(key) {
  const group = getLast30Group(key);
  if (key === "mainlines") return group.mainlines || group.items || [];
  return group.items || [];
}

function renderLast30Column(key, titleSelector, summarySelector, listSelector, fallbackTitle) {
  const group = getLast30Group(key);
  setText(titleSelector, group.title || fallbackTitle);
  setText(summarySelector, group.summary || "");
  clearAndFill(qs(listSelector), createLast30Item, getLast30Items(key).slice(0, 3));
}

function getOpenWikiTodos() {
  const tasks = Array.isArray(wikiTodoData.tasks) ? wikiTodoData.tasks : [];
  return tasks
    .filter((task) => !task.completed_at && !["done", "completed", "closed"].includes(String(task.status || "").toLowerCase()))
    .sort((a, b) => {
      const left = a.due_at || "9999-12-31";
      const right = b.due_at || "9999-12-31";
      return left.localeCompare(right);
    });
}

function renderWikiTodos() {
  const openTodos = getOpenWikiTodos();
  const status = wikiTodoError ? copy.wikiTodoFailed : `${copy.wikiTodoReady} ${openTodos.length}`;
  const updatedAt = wikiTodoData.synced_at
    ? `同步 ${wikiTodoData.synced_at}`
    : wikiTodoData.updated_at
      ? `更新 ${wikiTodoData.updated_at}`
      : wikiTodoData.source_file || "todo.json";

  setText("#wiki-todo-status", status);
  setText("#wiki-todo-updated", wikiTodoError || updatedAt);
  clearAndFill(qs("#wiki-todo-list"), createWikiTodoItem, openTodos);

  if (!openTodos.length && !wikiTodoError) {
    setText("#wiki-todo-list .empty-state", copy.wikiTodoEmpty);
  }
}

function getCheckinRecords(limit = 30) {
  return Array.isArray(checkinData.records) ? checkinData.records.slice(0, limit).reverse() : [];
}

function getAccountHistoryRecords(limit = 30) {
  const history = Array.isArray(checkinData.account_history) ? checkinData.account_history : [];
  const records = history
    .filter((record) => Number.isFinite(Number(record.daily_available_mb)))
    .slice(0, limit)
    .reverse()
    .map((record) => ({
      ...record,
      daily_available_gb: Number(record.daily_available_mb) / 1024,
    }));

  if (records.length || !Number.isFinite(Number(checkinData.account?.daily_available_mb))) return records;

  const syncedAt = checkinData.account?.synced_at || checkinData.updatedAt || "";
  return [
    {
      date: syncedAt.slice(0, 10) || copy.today,
      daily_available_mb: Number(checkinData.account.daily_available_mb),
      daily_available_gb: Number(checkinData.account.daily_available_mb) / 1024,
    },
  ];
}

function getNiceMax(values) {
  const max = Math.max(...values.map((value) => Number(value) || 0), 1);
  const magnitude = 10 ** Math.floor(Math.log10(max));
  return Math.ceil(max / magnitude) * magnitude;
}

function getChartRenderWidth(container) {
  const width = container?.clientWidth || 0;
  return Math.max(920, Math.floor(width));
}

function createLineChart(records, options) {
  const { key, unit, formatter, stroke } = options;
  const width = options.width || Math.max(920, records.length * 46 + 96);
  const height = 340;
  const padding = { top: 28, right: 26, bottom: 64, left: 56 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;
  const values = records.map((record) => Number(record[key]) || 0);
  const yMax = getNiceMax(values);
  const points = records.map((record, index) => {
    const x = padding.left + (records.length <= 1 ? 0 : (index / (records.length - 1)) * chartWidth);
    const y = padding.top + chartHeight - ((Number(record[key]) || 0) / yMax) * chartHeight;
    return { record, value: Number(record[key]) || 0, x, y };
  });
  const linePath = points.map((point, index) => `${index === 0 ? "M" : "L"} ${point.x.toFixed(1)} ${point.y.toFixed(1)}`).join(" ");
  const yTicks = Array.from({ length: 5 }, (_, index) => {
    const value = (yMax / 4) * index;
    const y = padding.top + chartHeight - (value / yMax) * chartHeight;
    return { value, y };
  });
  const labelInterval = 5;
  const xLabelIndexes = new Set();
  records.forEach((_, index) => {
    if (index % labelInterval === 0) xLabelIndexes.add(index);
  });
  if (records.length > 0 && records.length - 1 - Math.max(...xLabelIndexes) >= 3) {
    xLabelIndexes.add(records.length - 1);
  }

  if (!records.length) return `<p class="empty-state">${copy.noData}</p>`;

  return `
    <svg class="line-chart-svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" role="img" aria-label="${options.title}">
      <line class="chart-axis" x1="${padding.left}" y1="${padding.top}" x2="${padding.left}" y2="${padding.top + chartHeight}" />
      <line class="chart-axis" x1="${padding.left}" y1="${padding.top + chartHeight}" x2="${padding.left + chartWidth}" y2="${padding.top + chartHeight}" />
      ${yTicks
        .map(
          (tick) => `
            <line class="chart-grid-line" x1="${padding.left}" y1="${tick.y.toFixed(1)}" x2="${padding.left + chartWidth}" y2="${tick.y.toFixed(1)}" />
            <text class="chart-y-label" x="${padding.left - 10}" y="${tick.y + 4}" text-anchor="end">${Math.round(tick.value)}${unit}</text>
          `,
        )
        .join("")}
      <path class="chart-line" d="${linePath}" style="--chart-stroke: ${stroke}" />
      ${points
        .map(
          (point, index) => `
            <g class="chart-point-group">
              <circle class="chart-point" cx="${point.x.toFixed(1)}" cy="${point.y.toFixed(1)}" r="4">
                <title>${point.record.date}: ${formatter(point.value)}</title>
              </circle>
              <text class="chart-value-label" x="${point.x.toFixed(1)}" y="${Math.max(12, point.y - 9).toFixed(1)}" text-anchor="middle">${formatter(point.value)}</text>
              ${
                xLabelIndexes.has(index)
                  ? `<text class="chart-x-label" x="${point.x.toFixed(1)}" y="${padding.top + chartHeight + 24}" text-anchor="middle">${formatDateShort(point.record.date)}</text>`
                  : ""
              }
            </g>
          `,
        )
        .join("")}
    </svg>
  `;
}

function renderCheckin() {
  const today = checkinData.today || {};
  const total = checkinData.total || {};

  setText("#checkin-today", Number.isFinite(Number(today.flow_mb)) ? formatFlow(today.flow_mb, "mb") : "--");
  setText("#checkin-today-beans", Number.isFinite(Number(today.beans)) ? `${today.beans}` : "--");
  setText("#checkin-today-hours", formatHours(today.hours));
  setText("#checkin-days", Number.isFinite(Number(total.days)) ? `${total.days}d` : "--");
  setText("#checkin-total-flow", Number.isFinite(Number(total.flow_mb)) ? formatFlow(total.flow_mb, "gb") : "--");
  setText("#checkin-total-hours", formatDuration(total.hours));
  setText("#checkin-updated", checkinData.updatedAt ? `更新 ${checkinData.updatedAt}` : copy.syncWaiting);
  setText("#sidebar-dounai-flow", Number.isFinite(Number(today.flow_mb)) ? formatFlow(today.flow_mb, "mb") : "--");
}

function renderDounai() {
  const today = checkinData.today || {};
  const total = checkinData.total || {};
  const account = checkinData.account || {};
  const records = getCheckinRecords(30);
  const accountHistory = getAccountHistoryRecords(30);
  const remainingFlow = Number.isFinite(Number(account.remaining_flow_mb))
    ? Number(account.remaining_flow_mb)
    : parseTrafficLabel(account.remaining_flow_label || account.remaining_flow);
  const expiry = account.effective_expires_at || account.vip_expires_at || account.account_expires_at;
  const daysRemaining = Number.isFinite(Number(account.days_remaining))
    ? Number(account.days_remaining)
    : getDaysRemaining(expiry);
  const dailyAvailable = Number.isFinite(Number(account.daily_available_mb))
    ? Number(account.daily_available_mb)
    : Number.isFinite(remainingFlow) && Number.isFinite(daysRemaining) && daysRemaining > 0
      ? remainingFlow / daysRemaining
      : NaN;

  setText("#dounai-updated", checkinData.updatedAt ? `更新 ${checkinData.updatedAt}` : copy.syncWaiting);
  setText("#dounai-today-flow", Number.isFinite(Number(today.flow_mb)) ? formatFlow(today.flow_mb, "mb") : "--");
  setText("#dounai-today-beans", Number.isFinite(Number(today.beans)) ? `${today.beans}` : "--");
  setText("#dounai-today-hours", formatHours(today.hours));
  setText("#dounai-days", Number.isFinite(Number(total.days)) ? `${total.days}d` : "--");
  setText("#dounai-total-flow", Number.isFinite(Number(total.flow_mb)) ? formatFlow(total.flow_mb, "gb") : "--");
  setText("#dounai-total-hours", formatDuration(total.hours));
  setText("#dounai-remaining-flow", Number.isFinite(remainingFlow) ? formatTraffic(remainingFlow) : account.remaining_flow_label || "--");
  setText("#dounai-expiry", formatDateOnly(expiry));
  setText("#dounai-daily-flow", Number.isFinite(dailyAvailable) ? `${formatTraffic(dailyAvailable)}/d` : "--");

  const dailyBudgetChart = qs("#dounai-daily-budget-chart");
  if (dailyBudgetChart) {
    dailyBudgetChart.innerHTML = createLineChart(accountHistory, {
      key: "daily_available_gb",
      title: "近 30 天日均可用流量",
      unit: "GB",
      stroke: "#7c3aed",
      width: getChartRenderWidth(dailyBudgetChart),
      formatter: (value) => `${value.toFixed(1)} GB`,
    });
  }

  const flowChart = qs("#dounai-flow-chart");
  if (flowChart) {
    flowChart.innerHTML = createLineChart(records, {
      key: "flow_mb",
      title: "近 30 天获取流量",
      unit: "MB",
      stroke: "#2688e8",
      width: getChartRenderWidth(flowChart),
      formatter: (value) => `${Math.round(value)} MB`,
    });
  }

  const hoursChart = qs("#dounai-hours-chart");
  if (hoursChart) {
    hoursChart.innerHTML = createLineChart(records, {
      key: "hours",
      title: "近 30 天获取时长",
      unit: "h",
      stroke: "#00a6c8",
      width: getChartRenderWidth(hoursChart),
      formatter: (value) => `${value.toFixed(2)}h`,
    });
  }

}

function renderHome() {
  const mainlines = dashboardData.mainlines || dashboardData.projects || dashboardData.tasks || [];
  const actions = dashboardData.actions || dashboardData.tasks || [];
  const journal = dashboardData.journal || [];
  const feeds = dashboardData.feeds || [];
  const aiItems = (aiNewsData.items || []).slice(0, 3);
  const token7d = getTokenRange("7d");
  const token1d = getTokenRange("1d");
  const token30d = getTokenRange("30d");
  const today = dashboardData.today || {};

  setText("#today-mode", today.modeLabel || "\u4eca\u65e5\u72b6\u6001");
  setText("#daily-brief", today.summary || dashboardData.brief || copy.waitBrief);
  setText("#today-energy", `${copy.energy} ${today.energy || "--"}`);
  setText("#today-focus", `${copy.focus} ${today.focus || "--"}`);
  setText("#today-updated", today.updatedAt ? `${copy.updatedAtShort} ${today.updatedAt}` : "\u5f85\u786e\u8ba4");
  setText("#operator-status", `OpenClaw ${dashboardData.automation?.status || copy.waiting}`);
  setText("#feed-source", dashboardData.feedSource || "OpenClaw");
  setText("#journal-source", dashboardData.journalSource || copy.statusSnapshot);
  setText("#ai-news-source", aiNewsData.sourceSummary || "OpenClaw AI Daily");
  setText("#last30-source", last30Data.sourceSummary || last30Data.updatedAt || copy.syncWaiting);

  setText("#metric-mainlines", String(mainlines.length));
  setText("#metric-mainlines-note", `${mainlines.length} ${copy.taskCount}`);
  setText("#metric-actions", String(actions.length));
  setText("#metric-actions-note", `${actions.length} ${copy.taskCount}`);
  setText("#metric-token-total", formatToken(token7d.total));
  setText("#metric-token-note", `${copy.day1} ${formatToken(token1d.total)}`);
  setText("#metric-automation", dashboardData.automation?.status || "--");
  setText("#metric-automation-note", dashboardData.automation?.lastRun || copy.sync);
  setText("#mini-token-24h", formatToken(token1d.total));
  setText("#mini-token-30d", formatToken(token30d.total));
  setText("#sidebar-token-total", formatToken(token7d.total));

  clearAndFill(qs("#mainline-list"), createTask, mainlines);
  clearAndFill(qs("#action-list"), createTask, actions);
  clearAndFill(qs("#journal-list"), createFeed, journal);
  clearAndFill(qs("#ai-news-list"), createAiNewsItem, aiItems);
  clearAndFill(qs("#feed-list"), createFeed, feeds);
  clearAndFill(qs("#timeline"), createTimelineItem, dashboardData.timeline || []);
  clearAndFill(qs("#system-list"), createSystemItem, dashboardData.system || []);
  renderCheckin();
  renderDounai();
  renderWikiTodos();
  renderLast30Column("today", "#last30-today-title", "#last30-today-summary", "#last30-today-list", copy.todayEvents);
  renderLast30Column("week", "#last30-week-title", "#last30-week-summary", "#last30-week-list", copy.weekEvents);
  renderLast30Column(
    "mainlines",
    "#last30-mainline-title",
    "#last30-mainline-summary",
    "#last30-mainline-list",
    copy.last30Mainlines,
  );
}

function createRangeButton(range) {
  const button = document.createElement("button");
  button.className = "range-tab";
  button.type = "button";
  button.dataset.range = range.key;
  button.textContent = range.label;
  button.addEventListener("click", () => {
    activeTokenRange = range.key;
    renderTokens();
  });
  return button;
}

function renderTokens() {
  const usage = getTokenUsage();
  const ranges = usage.ranges || [];
  const range = getTokenRange();

  const rangeTabs = qs("#token-ranges");
  if (rangeTabs && rangeTabs.childElementCount !== ranges.length) {
    rangeTabs.replaceChildren(...ranges.map(createRangeButton));
  }

  qsa(".range-tab").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.range === range.key);
  });

  setText("#token-updated", usage.updatedAt ? `${copy.updatedAt} ${usage.updatedAt}` : copy.sync);
  setText("#token-total", formatToken(range.total));
  setText("#token-input", formatToken(range.input));
  setText("#token-output", formatToken(range.output));
  setText("#token-cost", formatCost(range.cost));
  setText("#token-note", range.note || copy.noNote);

  clearAndFill(qs("#token-models"), createModelItem, usage.models || []);
  clearAndFill(qs("#token-bars"), createDailyBar, usage.daily || []);
}

function createModelItem(model) {
  const article = document.createElement("article");
  article.className = "model-item";
  article.innerHTML = `
    <div class="model-row">
      <strong></strong>
      <span></span>
    </div>
    <div class="model-meter"><span></span></div>
  `;
  article.querySelector("strong").textContent = model.name || "Model";
  article.querySelector(".model-row span").textContent = formatToken(model.total);
  article.querySelector(".model-meter span").style.width = `${Math.min(model.share || 0, 100)}%`;
  return article;
}

function createDailyBar(day) {
  const article = document.createElement("article");
  article.className = "token-bar";
  const max = Math.max(...(getTokenUsage().daily || []).map((item) => item.total || 0), 1);
  article.innerHTML = `
    <span></span>
    <div class="bar-track"><span></span></div>
    <strong></strong>
  `;
  article.querySelector("span").textContent = day.label || day.date || "";
  article.querySelector(".bar-track span").style.width = `${Math.max(4, ((day.total || 0) / max) * 100)}%`;
  article.querySelector("strong").textContent = formatToken(day.total);
  return article;
}

function renderAll() {
  renderHome();
  renderTokens();
  renderDounai();
}

async function readJson(url, fallback) {
  try {
    const response = await fetch(`${url}?t=${Date.now()}`, { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    return fallback;
  }
}

async function readWikiTodo() {
  try {
    const response = await fetch(`${WIKI_TODO_URL}?t=${Date.now()}`, { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    wikiTodoError = "";
    return await response.json();
  } catch (error) {
    if ((fallbackWikiTodo.tasks || []).length) {
      wikiTodoError = "";
      return fallbackWikiTodo;
    }
    wikiTodoError = "\u8bf7\u5148\u8fd0\u884c scripts/sync_wiki_todos.py";
    return fallbackWikiTodo;
  }
}

async function loadData() {
  const [dashboard, aiNews, last30, wikiTodo, checkin, openclawUsage] = await Promise.all([
    readJson(DATA_URL, window.MAXNOW_DASHBOARD_DATA || fallbackData),
    readJson(AI_NEWS_URL, window.MAXNOW_AI_NEWS_DATA || fallbackAiNews),
    readJson(LAST30_URL, window.MAXNOW_LAST30_DATA || fallbackLast30),
    readWikiTodo(),
    readJson(CHECKIN_URL, fallbackCheckin),
    readJson(OPENCLAW_USAGE_URL, window.MAXNOW_OPENCLAW_USAGE_DATA || fallbackOpenclawUsage),
  ]);

  dashboardData = dashboard;
  aiNewsData = aiNews;
  last30Data = last30;
  wikiTodoData = wikiTodo;
  checkinData = checkin;
  openclawUsageData = openclawUsage;
  renderAll();
}

function setView(view) {
  const nextView = ["home", "tokens", "dounai"].includes(view) ? view : "home";
  qsa("[data-view-panel]").forEach((panel) => {
    panel.classList.toggle("is-active", panel.dataset.viewPanel === nextView);
  });
  qsa("[data-view]").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.view === nextView);
  });
  if (viewTitle) {
    viewTitle.textContent = nextView === "tokens" ? copy.tokenTitle : nextView === "dounai" ? copy.dounaiTitle : copy.today;
  }
  if (nextView === "dounai") requestAnimationFrame(renderDounai);
  if (location.hash !== `#${nextView}`) location.hash = nextView;
  window.scrollTo({ top: 0, behavior: "auto" });
}

const lunarMonths = [
  "\u6b63\u6708",
  "\u4e8c\u6708",
  "\u4e09\u6708",
  "\u56db\u6708",
  "\u4e94\u6708",
  "\u516d\u6708",
  "\u4e03\u6708",
  "\u516b\u6708",
  "\u4e5d\u6708",
  "\u5341\u6708",
  "\u51ac\u6708",
  "\u814a\u6708",
];

const lunarDays = [
  "",
  "\u521d\u4e00",
  "\u521d\u4e8c",
  "\u521d\u4e09",
  "\u521d\u56db",
  "\u521d\u4e94",
  "\u521d\u516d",
  "\u521d\u4e03",
  "\u521d\u516b",
  "\u521d\u4e5d",
  "\u521d\u5341",
  "\u5341\u4e00",
  "\u5341\u4e8c",
  "\u5341\u4e09",
  "\u5341\u56db",
  "\u5341\u4e94",
  "\u5341\u516d",
  "\u5341\u4e03",
  "\u5341\u516b",
  "\u5341\u4e5d",
  "\u4e8c\u5341",
  "\u5eff\u4e00",
  "\u5eff\u4e8c",
  "\u5eff\u4e09",
  "\u5eff\u56db",
  "\u5eff\u4e94",
  "\u5eff\u516d",
  "\u5eff\u4e03",
  "\u5eff\u516b",
  "\u5eff\u4e5d",
  "\u4e09\u5341",
];

const lunarHolidayMap = {
  "\u6b63\u6708-\u521d\u4e00": "\u6625\u8282",
  "\u6b63\u6708-\u5341\u4e94": "\u5143\u5bb5\u8282",
  "\u4e8c\u6708-\u521d\u4e8c": "\u9f99\u62ac\u5934",
  "\u4e94\u6708-\u521d\u4e94": "\u7aef\u5348\u8282",
  "\u4e03\u6708-\u521d\u4e03": "\u4e03\u5915",
  "\u516b\u6708-\u5341\u4e94": "\u4e2d\u79cb\u8282",
  "\u4e5d\u6708-\u521d\u4e5d": "\u91cd\u9633\u8282",
  "\u814a\u6708-\u521d\u516b": "\u814a\u516b\u8282",
};

function normalizeLunarMonth(value) {
  const text = String(value || "").replace(/^\u95f0/, "");
  const numeric = Number.parseInt(text, 10);
  return Number.isFinite(numeric) && lunarMonths[numeric - 1] ? lunarMonths[numeric - 1] : text;
}

function normalizeLunarDay(value) {
  const text = String(value || "");
  const numeric = Number.parseInt(text, 10);
  return Number.isFinite(numeric) && lunarDays[numeric] ? lunarDays[numeric] : text;
}

function getLunarParts(date) {
  try {
    const parts = new Intl.DateTimeFormat("zh-CN-u-ca-chinese", {
      month: "long",
      day: "numeric",
    }).formatToParts(date);
    return {
      month: normalizeLunarMonth(parts.find((part) => part.type === "month")?.value),
      day: normalizeLunarDay(parts.find((part) => part.type === "day")?.value),
    };
  } catch (error) {
    return { month: "", day: "" };
  }
}

function formatLunarDate(date) {
  const lunar = getLunarParts(date);
  return lunar.month && lunar.day ? `\u519c\u5386 ${lunar.month}${lunar.day}` : "\u519c\u5386 --";
}

function addDays(date, days) {
  const next = new Date(date);
  next.setDate(next.getDate() + days);
  return next;
}

function isSameDay(first, second) {
  return (
    first.getFullYear() === second.getFullYear() &&
    first.getMonth() === second.getMonth() &&
    first.getDate() === second.getDate()
  );
}

function getNthWeekdayOfMonth(year, monthIndex, weekday, nth) {
  const date = new Date(year, monthIndex, 1);
  const offset = (weekday - date.getDay() + 7) % 7;
  date.setDate(1 + offset + (nth - 1) * 7);
  return date;
}

function getHolidayLabels(date) {
  const labels = [];
  const month = date.getMonth() + 1;
  const day = date.getDate();
  const fixedHolidayMap = {
    "1-1": "\u5143\u65e6",
    "2-14": "\u60c5\u4eba\u8282",
    "3-8": "\u5987\u5973\u8282",
    "5-1": "\u52b3\u52a8\u8282",
    "6-1": "\u513f\u7ae5\u8282",
    "10-1": "\u56fd\u5e86\u8282",
    "12-25": "\u5723\u8bde\u8282",
  };
  const fixedHoliday = fixedHolidayMap[`${month}-${day}`];
  if (fixedHoliday) labels.push(fixedHoliday);

  const year = date.getFullYear();
  if (isSameDay(date, getNthWeekdayOfMonth(year, 4, 0, 2))) labels.push("\u6bcd\u4eb2\u8282");
  if (isSameDay(date, getNthWeekdayOfMonth(year, 5, 0, 3))) labels.push("\u7236\u4eb2\u8282");

  const lunar = getLunarParts(date);
  const lunarHoliday = lunarHolidayMap[`${lunar.month}-${lunar.day}`];
  if (lunarHoliday) labels.push(lunarHoliday);

  const tomorrowLunar = getLunarParts(addDays(date, 1));
  if (tomorrowLunar.month === "\u6b63\u6708" && tomorrowLunar.day === "\u521d\u4e00") {
    labels.push("\u9664\u5915");
  }

  return [...new Set(labels)];
}

function updateClock() {
  const now = new Date();
  const date = new Intl.DateTimeFormat("zh-CN", {
    month: "long",
    day: "numeric",
    weekday: "long",
  }).format(now);
  const time = new Intl.DateTimeFormat("zh-CN", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).format(now);

  setText("#today-label", date);
  setText("#clock-label", time);
  setText("#lunar-label", formatLunarDate(now));
  const holidays = getHolidayLabels(now);
  setText("#holiday-label", holidays.length ? holidays.join(" \u00b7 ") : "\u4eca\u65e5\u65e0\u8282\u65e5");
}

qsa("[data-view]").forEach((button) => {
  button.addEventListener("click", () => setView(button.dataset.view));
});

qs("#dounai-checkin")?.addEventListener("click", () => setView("dounai"));
qs("#dounai-checkin")?.addEventListener("keydown", (event) => {
  if (event.key === "Enter" || event.key === " ") {
    event.preventDefault();
    setView("dounai");
  }
});

refreshButton?.addEventListener("click", async () => {
  refreshButton.disabled = true;
  refreshButton.dataset.state = "loading";
  await loadData();
  refreshButton.dataset.state = "success";
  refreshButton.disabled = false;
  setTimeout(() => refreshButton.removeAttribute("data-state"), 900);
});

window.addEventListener("hashchange", () => {
  setView(location.hash.replace("#", ""));
});

let resizeTimer = 0;
window.addEventListener("resize", () => {
  if (!qs("#dounai-view")?.classList.contains("is-active")) return;
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(renderDounai, 120);
});

updateClock();
setInterval(updateClock, 30000);
loadData().then(() => setView(location.hash.replace("#", "")));
