const DATA_URL = "./data/dashboard.json";
const LAST30_URL = "./data/last-30.json";
const WIKI_TODO_URL = "./data/wiki-todos.json";
const CHECKIN_URL = "./data/dounai_checkin.json";
const OPENCLAW_USAGE_URL = "./data/openclaw-usage.json";
const TOKEN_USAGE_URL = "./data/token-usage.json";
const MARKET_INDICES_URL = "./data/market-indices.json";
const PROJECT_META_URL = "./data/project-meta.json";
const PROJECT_STATUS_URL = "./data/project-status.json";
const RICKY_URL = "./data/ricky.json";
const LIFE_FOODS_URL = "./data/life-foods.json";
const LEAFLET_CSS_URL = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css";
const LEAFLET_JS_URL = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js";
const DATA_AUTO_REFRESH_INTERVAL_MS = 5 * 60 * 1000;

const fallbackData = window.MAXNOW_DASHBOARD_DATA || {};
const fallbackLast30 = window.MAXNOW_LAST30_DATA || {};
const fallbackWikiTodo = window.MAXNOW_WIKI_TODO_DATA || { tasks: [] };
const fallbackCheckin = {};
const fallbackOpenclawUsage = window.MAXNOW_OPENCLAW_USAGE_DATA || { days: [] };
const fallbackTokenUsage = window.MAXNOW_TOKEN_USAGE_DATA || { days: [] };
const fallbackMarketIndices = window.MAXNOW_MARKET_INDICES_DATA || { indices: [] };
const fallbackProjectMeta = window.MAXNOW_PROJECT_META_DATA || { recentUpdates: [] };
const fallbackProjectStatus = window.MAXNOW_PROJECT_STATUS_DATA || { mainlines: [], actions: [] };
const fallbackRicky = window.MAXNOW_RICKY_DATA || { stats: [], places: [], records: [] };
const fallbackLifeFoods = window.MAXNOW_LIFE_FOODS_DATA || { sections: [] };

let dashboardData = fallbackData;
let last30Data = fallbackLast30;
let wikiTodoData = fallbackWikiTodo;
let checkinData = fallbackCheckin;
let openclawUsageData = fallbackOpenclawUsage;
let tokenUsageData = fallbackTokenUsage;
let marketIndicesData = fallbackMarketIndices;
let projectMetaData = fallbackProjectMeta;
let projectStatusData = fallbackProjectStatus;
let rickyData = fallbackRicky;
let lifeFoodsData = fallbackLifeFoods;
let wikiTodoError = "";
let activeTokenRange = "1d";
let weatherMetaFitFrame = 0;
let rickyMap = null;
let rickyMarkerLayer = null;
let lifePickTimer = 0;
let lifeWheelAnimations = [];
let homeDataPromise = null;
let tokenDataPromise = null;
let rickyDataPromise = null;
let lifeDataPromise = null;
let leafletPromise = null;

const lifeFoodTones = ["cyan", "orange", "green", "purple", "blue"];

const qs = (selector) => document.querySelector(selector);
const qsa = (selector) => [...document.querySelectorAll(selector)];

const emptyTemplate = qs("#empty-template");
const refreshButton = qs("#refresh-button");
const viewTitle = qs("#view-title");

const weatherIcons = {
  sun: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.5v2.2M12 19.3v2.2M4.6 4.6l1.6 1.6M17.8 17.8l1.6 1.6M2.5 12h2.2M19.3 12h2.2M4.6 19.4l1.6-1.6M17.8 6.2l1.6-1.6"/></svg>',
  cloud: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M17.5 18H8a4.5 4.5 0 1 1 .9-8.9 6 6 0 0 1 11.4 2.6A3.2 3.2 0 0 1 17.5 18Z"/></svg>',
  rain: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M17.5 15H8a4.5 4.5 0 1 1 .9-8.9 6 6 0 0 1 11.4 2.6A3.2 3.2 0 0 1 17.5 15Z"/><path d="M8 19l-1 2M13 18l-1 2M18 19l-1 2"/></svg>',
  storm: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M17.5 14.8H8a4.5 4.5 0 1 1 .9-8.9 6 6 0 0 1 11.4 2.6A3.2 3.2 0 0 1 17.5 14.8Z"/><path d="m12.5 14-2.2 4h3l-1.8 3.5"/></svg>',
  snow: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M17.5 15H8a4.5 4.5 0 1 1 .9-8.9 6 6 0 0 1 11.4 2.6A3.2 3.2 0 0 1 17.5 15Z"/><path d="M8 20h.01M12 19h.01M16 20h.01"/></svg>',
  fog: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M17.5 14H8a4.5 4.5 0 1 1 .9-8.9 6 6 0 0 1 11.4 2.6A3.2 3.2 0 0 1 17.5 14Z"/><path d="M4 18h16M6 21h12"/></svg>',
};

const copy = {
  unnamedTask: "\u672a\u547d\u540d\u4e8b\u9879",
  unnamedInfo: "\u672a\u547d\u540d\u4fe1\u606f",
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
  noHoliday: "\u4eca\u65e5\u65e0\u8282\u65e5",
  updatedAt: "\u66f4\u65b0\u4e8e",
  ledgerMergedAt: "\u603b\u8d26\u5408\u5e76\u4e8e",
  noNote: "\u6682\u65e0\u8bf4\u660e\u3002",
  tokenTitle: "Token \u7528\u91cf",
  dounaiTitle: "\u8c46\u5976",
  cloudTitle: "\u4e91\u670d\u52a1",
  rickyTitle: "\u6211\u548c Ricky",
  lifeTitle: "\u751f\u6d3b",
  today: "\u4eca\u5929",
  energy: "\u8282\u594f",
  focus: "\u7126\u70b9",
  updatedAtShort: "\u66f4\u65b0",
  statusSnapshot: "\u72b6\u6001\u5feb\u7167",
  todayEvents: "\u6700\u65b0\u4fe1\u53f7",
  weekEvents: "\u672c\u5468\u89c2\u5bdf",
  last30Mainlines: "\u8fd1 30 \u5929\u4e3b\u7ebf",
  wikiTodoReady: "\u5df2\u8bfb\u53d6",
  wikiTodoFailed: "\u8bfb\u53d6\u5931\u8d25",
  wikiTodoEmpty: "\u6682\u65e0\u672a\u5b8c\u6210\u5f85\u529e",
  todayTodoEmpty: "\u4eca\u5929\u6682\u65e0\u660e\u786e\u6267\u884c\u65e5\u671f\u7684\u5f85\u529e",
  noTodayExecution: "\u6682\u65e0\u660e\u786e\u6267\u884c\u65e5\u671f",
  dueAt: "\u622a\u6b62",
  rickyEmptyPlaces: "\u8fd8\u6ca1\u6709\u5199\u5165\u5730\u70b9\u3002",
  rickyEmptyRecords: "\u8fd8\u6ca1\u6709\u5199\u5165\u65c5\u884c\u8bb0\u5f55\u3002",
  lifeNoFoods: "\u8fd8\u6ca1\u6709\u5199\u5165\u5019\u9009\u83dc\u54c1\u3002",
  lifePickFirst: "\u5148\u9009\u4e00\u70b9\u5403\u7684",
  lifePickEmpty: "\u5148\u52fe\u9009\u81f3\u5c11\u4e00\u4e2a\u5019\u9009",
};

function formatToken(value) {
  if (!Number.isFinite(value)) return "--";
  if (value >= 1000000000) return `${(value / 1000000000).toFixed(value >= 10000000000 ? 1 : 2)}B`;
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

function formatPercent(value) {
  if (!Number.isFinite(value)) return "--";
  if (value >= 99.5) return `${value.toFixed(0)}%`;
  if (value >= 10) return `${value.toFixed(1)}%`;
  return `${value.toFixed(2)}%`;
}

function localDateKey(date = new Date()) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function recentLocalDateKeys(count) {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return Array.from({ length: count }, (_, index) => {
    const date = new Date(today);
    date.setDate(today.getDate() - index);
    return localDateKey(date);
  });
}

function cloneLocalDate(date) {
  const next = new Date(date);
  next.setHours(0, 0, 0, 0);
  return next;
}

function addLocalDays(date, days) {
  const next = cloneLocalDate(date);
  next.setDate(next.getDate() + days);
  return next;
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

function formatDailyTraffic(value) {
  const amount = Number(value);
  if (!Number.isFinite(amount)) return "--";
  if (amount >= 1024 * 1024) return `${(amount / 1024 / 1024).toFixed(2)} TB`;
  if (amount >= 1024) return `${(amount / 1024).toFixed(2)} GB`;
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

function formatActiveDuration(value) {
  const seconds = Math.max(0, Number(value || 0));
  if (!Number.isFinite(seconds)) return "--";
  if (seconds < 60) return `${Math.round(seconds)}s`;
  const minutes = Math.round(seconds / 60);
  if (minutes < 60) return `${minutes}m`;
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  return remainingMinutes ? `${hours}h ${remainingMinutes}m` : `${hours}h`;
}

function formatDateShort(date = "") {
  return date.slice(5) || "--";
}

function formatTimeShort(value = "") {
  const match = String(value).match(/(\d{1,2}:\d{2})/);
  return match ? match[1] : "";
}

function parseLocalDateTime(value = "") {
  const match = String(value).match(/^(\d{4})-(\d{2})-(\d{2})(?:[ T](\d{1,2}):(\d{2}))?/);
  if (!match) return null;
  const [, year, month, day, hour = "0", minute = "0"] = match;
  const date = new Date(Number(year), Number(month) - 1, Number(day), Number(hour), Number(minute));
  return Number.isNaN(date.getTime()) ? null : date;
}

function isTodayDateTime(value, now = new Date()) {
  const date = parseLocalDateTime(value);
  return Boolean(date && localDateKey(date) === localDateKey(now));
}

function getDayPhase(now = new Date()) {
  const minutes = now.getHours() * 60 + now.getMinutes();
  const phases = [
    { until: 360, label: "\u6df1\u591c\u6536\u675f", note: "\u8f7b\u91cf\u8bb0\u5f55\uff0c\u522b\u786c\u625b" },
    { until: 540, label: "\u65e9\u95f4\u542f\u52a8", note: "\u786e\u8ba4\u4eca\u65e5\u5224\u65ad" },
    { until: 720, label: "\u4e0a\u5348\u63a8\u8fdb", note: "\u9002\u5408\u5904\u7406\u4e3b\u7ebf" },
    { until: 840, label: "\u5348\u95f4\u7f13\u51b2", note: "\u964d\u4f4e\u5207\u6362\u6210\u672c" },
    { until: 1080, label: "\u4e0b\u5348\u63a8\u8fdb", note: "\u7ee7\u7eed\u843d\u5730\u4e8b\u9879" },
    { until: 1320, label: "\u665a\u95f4\u590d\u76d8", note: "\u6536\u675f\u8bb0\u5f55\u548c\u660e\u65e5\u5165\u53e3" },
    { until: 1440, label: "\u591c\u95f4\u6536\u5c3e", note: "\u4fdd\u7559\u4e0a\u4e0b\u6587" },
  ];
  const phase = phases.find((item) => minutes < item.until) || phases[phases.length - 1];
  return {
    ...phase,
    progress: Math.max(4, Math.min(100, Math.round((minutes / 1440) * 100))),
  };
}

function updateTodaySource(source) {
  const card = qs("#overview");
  if (card) card.dataset.freshness = source.state;
  setText("#today-freshness", source.label);
  setText("#today-updated", source.detail);
  return source;
}

function updateTodayPhase() {
  const phase = getDayPhase();
  const progress = qs("#today-pulse-progress");
  const now = new Date();
  const nowText = `${String(now.getHours()).padStart(2, "0")}:${String(now.getMinutes()).padStart(2, "0")}`;
  const progressPercent = `${phase.progress}%`;
  const progressRatio = String(phase.progress / 100);
  setText("#today-phase", phase.label);
  setText("#today-phase-note", phase.note);
  setText("#today-pulse-now", nowText);
  const meter = qs(".summary-live-meter");
  if (meter) {
    meter.style.setProperty("--today-progress", progressPercent);
    meter.style.setProperty("--today-progress-ratio", progressRatio);
    meter.title = `今日进度 ${nowText} / ${phase.progress}%`;
    meter.setAttribute("aria-label", `今日进度 ${nowText}`);
  }
  if (progress) progress.style.removeProperty("height");
  return phase;
}

function setText(selector, value) {
  const element = qs(selector);
  if (element) element.textContent = value ?? "";
}

function setTitle(selector, value) {
  const element = qs(selector);
  if (element) element.title = value ?? "";
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
  const article = document.createElement(item.url ? "a" : "article");
  article.className = "last30-item";
  article.dataset.tone = getTone(item.status || item.confidence || item.source || item.title);
  if (item.url) {
    article.href = item.url;
    article.target = "_blank";
    article.rel = "noreferrer";
    article.setAttribute("aria-label", `${copy.open} ${item.title || copy.unnamedInfo}`);
  }
  article.innerHTML = `
    <div class="last30-item-head">
      <p class="item-title"></p>
      <span class="item-tag"></span>
    </div>
    <p class="item-copy"></p>
    <div class="last30-meta" aria-label="signal metadata">
      <span data-role="source"></span>
      <span data-role="confidence"></span>
    </div>
  `;
  article.querySelector(".item-title").textContent = item.title || copy.unnamedInfo;
  article.querySelector(".item-copy").textContent = item.summary || item.note || "";
  article.querySelector(".item-tag").textContent = item.needsOwnerConfirm
    ? "\u5f85\u786e\u8ba4"
    : item.date || item.status || item.source || copy.item;
  article.querySelector('[data-role="source"]').textContent = item.sourceType || item.source || item.status || copy.item;
  article.querySelector('[data-role="confidence"]').textContent = formatSignalConfidence(item);
  return article;
}

function formatSignalConfidence(item) {
  if (item.needsOwnerConfirm) return "\u9700 Owner \u786e\u8ba4";
  const value = String(item.confidence || "").toLowerCase();
  if (value === "high") return "\u6765\u6e90\u8f83\u7a33";
  if (value === "medium") return "\u81ea\u52a8\u89c2\u5bdf";
  if (value === "low") return "\u5f85\u6838\u5b9e";
  return item.confidence || "\u5df2\u7eb3\u5165\u89c2\u5bdf";
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
  return article;
}

function formatTodayTodoDue(task) {
  const dueDate = String(task.due_at || "").slice(0, 10);
  if (!dueDate) return task.status || copy.item;
  return dueDate === localDateKey() ? "\u4eca\u5929" : `${copy.dueAt} ${dueDate}`;
}

function createTodayTodoItem(task) {
  const article = createWikiTodoItem(task);
  article.classList.add("today-todo-item");
  article.dataset.tone = getTone(task.module || task.status || task.title);
  article.querySelector(".item-tag").textContent = formatTodayTodoDue(task);
  return article;
}

function createProjectUpdateItem(item) {
  const article = document.createElement("article");
  article.className = "project-update-item";
  article.innerHTML = `
    <div>
      <p class="item-title"></p>
      <p class="item-copy"></p>
    </div>
    <span class="item-tag"></span>
  `;
  article.querySelector(".item-title").textContent = item.title || copy.unnamedInfo;
  article.querySelector(".item-copy").textContent = item.summary || "";
  article.querySelector(".item-tag").textContent = item.date || "Update";
  return article;
}

function formatMarketPrice(value) {
  const amount = Number(value);
  if (!Number.isFinite(amount)) return "--";
  return amount.toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

function formatMarketSigned(value, digits = 2) {
  const amount = Number(value);
  if (!Number.isFinite(amount)) return "--";
  const sign = amount > 0 ? "+" : "";
  return `${sign}${amount.toFixed(digits)}`;
}

function marketDirection(item) {
  const percent = Number(item.changePercent);
  if (percent > 0) return "up";
  if (percent < 0) return "down";
  return "flat";
}

function createMarketSparkline(item) {
  const trend = Array.isArray(item.trend) ? item.trend : [];
  const values = trend.map((point) => Number(point.value)).filter(Number.isFinite);
  const previousClose = Number(item.previousClose);
  if (values.length < 2) {
    return '<svg class="market-sparkline-svg" viewBox="0 0 150 44" role="img" aria-label="暂无走势"><line class="market-baseline" x1="4" y1="22" x2="146" y2="22" /></svg>';
  }

  const width = 150;
  const height = 44;
  const padding = 4;
  const min = Math.min(...values, Number.isFinite(previousClose) ? previousClose : values[0]);
  const max = Math.max(...values, Number.isFinite(previousClose) ? previousClose : values[0]);
  const range = max - min || 1;
  const yFor = (value) => padding + (height - padding * 2) - ((value - min) / range) * (height - padding * 2);
  const points = values.map((value, index) => {
    const x = padding + (values.length <= 1 ? 0 : (index / (values.length - 1)) * (width - padding * 2));
    return { x, y: yFor(value) };
  });
  const linePath = points.map((point, index) => `${index === 0 ? "M" : "L"} ${point.x.toFixed(1)} ${point.y.toFixed(1)}`).join(" ");
  const areaPath = `${linePath} L ${points[points.length - 1].x.toFixed(1)} ${height - padding} L ${points[0].x.toFixed(1)} ${height - padding} Z`;
  const baselineY = Number.isFinite(previousClose) ? yFor(previousClose) : height / 2;
  const direction = marketDirection(item);

  return `
    <svg class="market-sparkline-svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="指数走势">
      <line class="market-baseline" x1="${padding}" y1="${baselineY.toFixed(1)}" x2="${width - padding}" y2="${baselineY.toFixed(1)}" />
      <path class="market-sparkline-fill" data-direction="${direction}" d="${areaPath}" />
      <path class="market-sparkline-line" data-direction="${direction}" d="${linePath}" />
    </svg>
  `;
}

function createMarketIndexItem(item) {
  const article = document.createElement("article");
  const direction = marketDirection(item);
  article.className = "market-item";
  article.dataset.direction = direction;
  article.title = [item.source || "", item.updatedAt ? `${copy.updatedAtShort} ${item.updatedAt}` : "", item.stale ? item.lastError || "stale" : ""]
    .filter(Boolean)
    .join(" · ");
  article.innerHTML = `
    <div class="market-name">
      <strong></strong>
      <small></small>
    </div>
    <div class="market-sparkline"></div>
    <div class="market-value">
      <strong></strong>
      <small></small>
    </div>
  `;
  article.querySelector(".market-name strong").textContent = item.name || copy.item;
  article.querySelector(".market-name small").textContent = item.displaySymbol || item.symbol || "--";
  article.querySelector(".market-sparkline").innerHTML = createMarketSparkline(item);
  article.querySelector(".market-value strong").textContent = `${formatMarketSigned(item.changePercent)}%`;
  article.querySelector(".market-value small").textContent = formatMarketPrice(item.price);
  return article;
}

function renderMarketIndices() {
  const indices = Array.isArray(marketIndicesData.indices) ? marketIndicesData.indices : [];
  setText("#market-updated", marketIndicesData.updatedAt ? `${formatTimeShort(marketIndicesData.updatedAt)} 更新` : copy.syncWaiting);
  clearAndFill(qs("#market-list"), createMarketIndexItem, indices);
}

function createRickyStatItem(item) {
  const article = document.createElement("article");
  article.innerHTML = `
    <span></span>
    <strong></strong>
    <small></small>
  `;
  article.querySelector("span").textContent = item.label || copy.item;
  article.querySelector("strong").textContent = item.value ?? "--";
  article.querySelector("small").textContent = item.unit || "";
  return article;
}

function createRickyPlaceItem(place) {
  const article = document.createElement("article");
  article.className = "ricky-place-item";
  article.dataset.tone = getTone(place.tone || place.country || place.city || place.name);
  article.innerHTML = `
    <div class="item-head">
      <p class="item-title"></p>
      <span class="item-tag"></span>
    </div>
    <p class="item-copy"></p>
  `;
  article.querySelector(".item-title").textContent = place.name || place.city || copy.unnamedInfo;
  article.querySelector(".item-tag").textContent = place.date || place.country || copy.item;
  article.querySelector(".item-copy").textContent = place.note || [place.city, place.country].filter(Boolean).join(" · ");
  appendLink(article, place.url || place.photoUrl);
  return article;
}

function createRickyRecordItem(record) {
  const article = document.createElement("article");
  article.className = "ricky-record-item";
  article.dataset.tone = getTone(record.tone || record.type || record.title);
  article.innerHTML = `
    <div class="item-head">
      <p class="item-title"></p>
      <span class="item-tag"></span>
    </div>
    <p class="item-copy"></p>
  `;
  article.querySelector(".item-title").textContent = record.title || copy.unnamedInfo;
  article.querySelector(".item-tag").textContent = record.date || record.type || copy.item;
  article.querySelector(".item-copy").textContent = record.summary || record.note || "";
  appendLink(article, record.url || record.photoUrl);
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

function createCloudSystemItem(item) {
  const displayItem = { ...item };
  if (String(displayItem.key || displayItem.name || "").toLowerCase() === "nginx") {
    displayItem.note = "";
  }
  return createSystemItem(displayItem);
}

function getSystemPercent(item) {
  const text = String(item.value || "").trim();
  if (!text.endsWith("%")) return null;
  const value = Number.parseInt(text, 10);
  if (!Number.isFinite(value)) return null;
  return Math.max(0, Math.min(100, value));
}

function formatSystemNote(item) {
  if (item.key === "deploy") return "";
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

function getAutomationHealth(status = "") {
  const text = String(status).toLowerCase();
  if (text.includes("异常") || text.includes("fail") || text.includes("error")) return "bad";
  if (text.includes("注意") || text.includes("unknown") || text.includes("pending")) return "unknown";
  return "ok";
}

function getDataSyncStatus() {
  const sources = [
    { label: "Wiki", updatedAt: wikiTodoData.synced_at || wikiTodoData.updated_at, staleAfterHours: 72 },
    { label: "Token", updatedAt: getTokenUsage().updatedAt, staleAfterHours: 72 },
    { label: "\u5929\u6c14", updatedAt: dashboardData.weather?.updatedAt, staleAfterHours: 72 },
    { label: "\u5e02\u573a", updatedAt: marketIndicesData.updatedAt, staleAfterHours: 72 },
    { label: "Last-30", updatedAt: last30Data.updatedAt, staleAfterHours: 168 },
    { label: "\u7248\u672c", updatedAt: projectMetaData.updatedAt, staleAfterHours: 72 },
    {
      label: "Roadmap",
      updatedAt: projectStatusData.generatedAt,
      staleAfterHours: Number(projectStatusData.staleAfterHours || 168),
    },
  ];
  const now = new Date();
  const items = sources.map((source) => {
    const date = parseLocalDateTime(normalizeSourceUpdatedAt(source.updatedAt));
    const ageHours = date ? (now.getTime() - date.getTime()) / (60 * 60 * 1000) : Infinity;
    const fresh = Number.isFinite(ageHours) && ageHours <= source.staleAfterHours;
    return { ...source, ageHours, fresh };
  });
  const stale = items.filter((item) => !item.fresh);
  const okCount = items.length - stale.length;
  const oldestStale = stale[0];
  const label = stale.length ? `${stale.length} \u4e2a\u8fc7\u671f` : `${okCount}/${items.length} \u6b63\u5e38`;
  const note = stale.length
    ? `${oldestStale.label} ${oldestStale.updatedAt ? formatSourceUpdatedAt(oldestStale.updatedAt) : copy.syncWaiting}`
    : "\u5173\u952e\u6765\u6e90\u5df2\u5237\u65b0";
  return { label, note, health: stale.length ? "unknown" : "ok", items };
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

function updateSidebarTokenSummary(key = activeTokenRange) {
  setText("#sidebar-token-total", "\u7528\u91cf\u6982\u89c8");
}

function normalizeUsageDay(day) {
  return {
    ...day,
    input: Number(day.inputTokens || day.input || 0),
    output: Number(day.outputTokens || day.output || 0),
    cacheRead: Number(day.cacheReadTokens || day.cacheRead || 0),
    cacheBase: Number(day.cacheBaseTokens || day.cacheBase || Math.max(day.inputTokens || day.input || 0, day.cacheReadTokens || day.cacheRead || 0)),
    total: Number(day.totalTokens || day.total || 0),
    cost: Number(day.estimatedCostUsd || day.cost || 0),
    activeSeconds: Number(day.activeSeconds || 0),
    completedTurns: Number(day.completedTurns || 0),
  };
}

function sumUsage(days) {
  const summary = days.reduce(
    (sum, day) => ({
      input: sum.input + Number(day.input || 0),
      output: sum.output + Number(day.output || 0),
      cacheRead: sum.cacheRead + Number(day.cacheRead || 0),
      cacheBase: sum.cacheBase + Number(day.cacheBase || 0),
      total: sum.total + Number(day.total || 0),
      cost: sum.cost + Number(day.cost || 0),
      runs: sum.runs + Number(day.runs || 0),
      activeSeconds: sum.activeSeconds + Number(day.activeSeconds || 0),
      completedTurns: sum.completedTurns + Number(day.completedTurns || 0),
    }),
    { input: 0, output: 0, cacheRead: 0, cacheBase: 0, total: 0, cost: 0, runs: 0, activeSeconds: 0, completedTurns: 0 },
  );
  summary.cacheHitRate = summary.cacheBase > 0 ? (summary.cacheRead / summary.cacheBase) * 100 : NaN;
  return summary;
}

function formatDateLabel(dateText) {
  const parts = String(dateText || "").split("-");
  return parts.length === 3 ? `${Number(parts[1])}/${Number(parts[2])}` : dateText || "";
}

function formatMonthLabel(date) {
  return `${date.getMonth() + 1}\u6708`;
}

function emptyUsageDay(date) {
  return normalizeUsageDay({
    date,
    sources: [],
    bySource: [],
    byModel: [],
    byTask: [],
    inputTokens: 0,
    outputTokens: 0,
    cacheReadTokens: 0,
    cacheBaseTokens: 0,
    totalTokens: 0,
    estimatedCostUsd: 0,
    runs: 0,
    activeSeconds: 0,
    completedTurns: 0,
  });
}

function buildTokenActivityThresholds(values) {
  const sorted = values.filter((value) => value > 0).sort((a, b) => a - b);
  if (!sorted.length) return [];
  return [0.2, 0.4, 0.6, 0.8].map((ratio) => sorted[Math.min(sorted.length - 1, Math.floor((sorted.length - 1) * ratio))]);
}

function getTokenActivityLevel(value, thresholds) {
  if (!value || value <= 0) return 0;
  let level = 1;
  thresholds.forEach((threshold) => {
    if (value > threshold) level += 1;
  });
  return Math.min(level, 5);
}

function buildTokenActivity(dayByDate, options = {}) {
  const dayCount = Math.max(1, Number(options.dayCount || 60));
  const rowCount = Math.max(1, Number(options.rows || 7));
  const today = cloneLocalDate(new Date());
  const firstDay = addLocalDays(today, -(dayCount - 1));
  const todayKey = localDateKey(today);
  const cells = Array.from({ length: dayCount }, (_, index) => {
    const date = addLocalDays(firstDay, index);
    const dateKey = localDateKey(date);
    const existing = dayByDate.get(dateKey);
    const day = existing || emptyUsageDay(dateKey);
    const total = Number(day.total || 0);
    return {
      date: dateKey,
      column: Math.floor(index / rowCount),
      row: index % rowCount,
      isEmpty: !existing,
      isToday: dateKey === todayKey,
      total,
      runs: Number(day.runs || 0),
      value: total,
    };
  });

  const thresholds = buildTokenActivityThresholds(cells.filter((cell) => !cell.isEmpty).map((cell) => cell.value));
  const monthsByLabel = new Map();
  cells.forEach((cell) => {
    const [year, month, day] = cell.date.split("-").map(Number);
    const label = formatMonthLabel(new Date(year, month - 1, day));
    const column = cell.column + 1;
    const current = monthsByLabel.get(label) || { label, start: column, end: column };
    current.start = Math.min(current.start, column);
    current.end = Math.max(current.end, column);
    monthsByLabel.set(label, current);
  });

  return {
    columnCount: Math.ceil(dayCount / rowCount),
    rowCount,
    dayCount,
    months: Array.from(monthsByLabel.values()).map((month) => ({
      label: month.label,
      start: month.start,
      span: Math.max(1, month.end - month.start + 1),
    })),
    cells: cells.map((cell) => ({
      ...cell,
      level: getTokenActivityLevel(cell.value, thresholds),
    })),
  };
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

function buildTaskBreakdown(days) {
  const byTask = new Map();
  days.forEach((day) => {
    (day.byTask || []).forEach((task) => {
      const label = task.label || task.kind || "OpenClaw session";
      const model = task.model || "";
      const key = `${task.kind || ""}:${label}:${model}`;
      const current = byTask.get(key) || { label, model, kind: task.kind || "", total: 0, cost: 0, runs: 0, activeSeconds: 0 };
      current.total += Number(task.totalTokens || task.total || 0);
      current.cost += Number(task.estimatedCostUsd || task.cost || 0);
      current.runs += Number(task.runs || 0);
      current.activeSeconds += Number(task.activeSeconds || 0);
      byTask.set(key, current);
    });
  });
  return [...byTask.values()].sort((a, b) => b.total - a.total);
}

function buildSessionBreakdown(selectedDays) {
  const selectedDates = new Set(selectedDays.map((day) => day.date));
  const usage = getTokenLedgerData();
  const runs = Array.isArray(usage.recentRuns) ? usage.recentRuns : [];
  const sessions = runs
    .filter((run) => !selectedDates.size || selectedDates.has(run.date))
    .map((run) => ({
      label: run.label || run.kind || "Token session",
      model: run.model || run.openrouterModel || "",
      kind: run.kind || "",
      runId: run.runId || "",
      total: Number(run.totalTokens || run.total || 0),
      input: Number(run.inputTokens || run.input || 0),
      output: Number(run.outputTokens || run.output || 0),
      cacheRead: Number(run.cacheReadTokens || run.cacheRead || 0),
      cost: Number(run.estimatedCostUsd || run.cost || 0),
      timestamp: run.timestamp || run.date || "",
      runs: 1,
      activeSeconds: Number(run.activeSeconds || 0),
    }))
    .sort((a, b) => b.total - a.total);

  return sessions.length ? sessions : buildTaskBreakdown(selectedDays);
}

function sourceDisplayName(source) {
  const key = String(source.key || source.source || "").toLowerCase();
  if (key === "openclaw") return "OpenClaw";
  if (key === "codex-local" || key === "codex-windows" || key === "codex-win") return "Codex Windows";
  if (key === "codex-macos" || key === "codex-mac") return "Codex macOS";
  if (key === "codex-linux") return "Codex Linux";
  if (key === "codex-server") return "Codex server";
  return source.label || source.key || key || "Source";
}

function sourceTone(source) {
  const key = String(source.key || source.source || "").toLowerCase();
  if (key.includes("server")) return "green";
  if (key.includes("local") || key.includes("windows") || key.includes("mac")) return "purple";
  if (key.includes("openclaw")) return "orange";
  return "blue";
}

function usageFromSource(source) {
  return {
    total: Number(source.totalTokens || source.total || 0),
    cost: Number(source.estimatedCostUsd || source.cost || 0),
    runs: Number(source.runs || 0),
    activeSeconds: Number(source.activeSeconds || 0),
  };
}

function addSourceUsage(map, source, usage) {
  const key = source.key || source.source || source.label || "source";
  const current = map.get(key) || {
    key,
    label: sourceDisplayName({ ...source, key }),
    total: 0,
    cost: 0,
    runs: 0,
    activeSeconds: 0,
    tone: sourceTone({ ...source, key }),
  };
  current.total += Number(usage.total || 0);
  current.cost += Number(usage.cost || 0);
  current.runs += Number(usage.runs || 0);
  current.activeSeconds += Number(usage.activeSeconds || 0);
  map.set(key, current);
}

function buildSourceBreakdown(selectedDays = []) {
  const bySource = new Map();

  selectedDays.forEach((day) => {
    const detailedSources = Array.isArray(day.bySource) ? day.bySource : [];
    if (detailedSources.length) {
      detailedSources.forEach((source) => addSourceUsage(bySource, source, usageFromSource(source)));
      return;
    }

    const sourceKeys = Array.isArray(day.sources) ? day.sources.filter(Boolean) : [];
    if (sourceKeys.length === 1) {
      addSourceUsage(bySource, { key: sourceKeys[0] }, day);
    }
  });

  if (bySource.size) {
    return [...bySource.values()]
      .filter((source) => source.total > 0 || source.runs > 0 || source.cost > 0 || source.activeSeconds > 0)
      .sort((a, b) => b.total - a.total);
  }

  if (selectedDays.length) return [];

  const ledger = getTokenLedgerData();
  const sources = Array.isArray(ledger.sources) ? ledger.sources : [];
  return sources
    .map((source) => ({
      key: source.key || source.source || source.label || "source",
      label: sourceDisplayName(source),
      ...usageFromSource(source),
      tone: sourceTone(source),
    }))
    .filter((source) => source.total > 0 || source.runs > 0 || source.cost > 0 || source.activeSeconds > 0)
    .sort((a, b) => b.total - a.total);
}

function getTokenLedgerData() {
  return Array.isArray(tokenUsageData.days) && tokenUsageData.days.length ? tokenUsageData : openclawUsageData;
}

function sourceUpdatedAt(source, ledger) {
  return source.updatedAt || source.lastUpdatedAt || source.syncedAt || ledger.updatedAt || "";
}

function buildSourceUpdateItems(ledger) {
  const sources = Array.isArray(ledger.sources) ? ledger.sources : [];
  return sources
    .map((source) => ({
      key: source.key || source.source || source.label || "source",
      label: sourceDisplayName(source),
      updatedAt: sourceUpdatedAt(source, ledger),
      tone: sourceTone(source),
    }))
    .filter((source) => source.updatedAt)
    .sort((a, b) => String(b.updatedAt).localeCompare(String(a.updatedAt)));
}

function getOpenclawTokenUsage() {
  const ledger = getTokenLedgerData();
  const rawDays = Array.isArray(ledger.days) ? ledger.days : [];
  if (!rawDays.length) return null;

  const days = rawDays.map(normalizeUsageDay).sort((a, b) => String(b.date).localeCompare(String(a.date)));
  const dayByDate = new Map(days.map((day) => [day.date, day]));
  const rangeDefs = [
    { key: "1d", label: "1d", count: 1 },
    { key: "7d", label: "7d", count: 7 },
    { key: "30d", label: "30d", count: 30 },
    { key: "all", label: "all", count: Infinity },
  ];
  const ranges = rangeDefs.map((range) => {
    const selected = Number.isFinite(range.count)
      ? recentLocalDateKeys(range.count).map((date) => dayByDate.get(date) || emptyUsageDay(date))
      : days;
    const summary = sumUsage(selected);
    return {
      key: range.key,
      label: range.label,
      ...summary,
      selectedDays: selected,
    };
  });

  const active = ranges.find((range) => range.key === activeTokenRange) || ranges[1] || ranges[0];
  const chartDays = recentLocalDateKeys(30).reverse().map((date) => dayByDate.get(date) || emptyUsageDay(date));
  return {
    updatedAt: ledger.updatedAt,
    ranges,
    models: buildModelBreakdown(active.selectedDays || []),
    sessions: buildSessionBreakdown(active.selectedDays || []).slice(0, 8),
    sources: buildSourceBreakdown(active.selectedDays || []),
    sourceUpdates: buildSourceUpdateItems(ledger),
    activity: buildTokenActivity(dayByDate, { dayCount: 90, rows: 3 }),
    daily: chartDays.map((day) => ({
      date: day.date,
      label: formatDateLabel(day.date),
      total: day.total,
      cost: day.cost,
    })),
    sourceSummary: "Token usage ledger",
  };
}

function getTokenUsage() {
  return getOpenclawTokenUsage() || {};
}

function shouldRenderRangeTabs(container, ranges) {
  const buttons = Array.from(container.querySelectorAll(".range-tab"));
  if (buttons.length !== ranges.length) return true;
  return buttons.some((button, index) => {
    const range = ranges[index] || {};
    return button.dataset.range !== String(range.key || "") || button.textContent !== String(range.label || "");
  });
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
  const itemLimit = key === "mainlines" ? 5 : 4;
  setText(titleSelector, group.title || fallbackTitle);
  setText(summarySelector, group.summary || "");
  clearAndFill(qs(listSelector), createLast30Item, getLast30Items(key).slice(0, itemLimit));
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

function getTodayWikiTodos(openTodos = getOpenWikiTodos()) {
  const todayKey = localDateKey();
  return openTodos.filter((task) => {
    const dueDate = String(task.due_at || "").slice(0, 10);
    return dueDate === todayKey;
  });
}

function renderTodayTodos(openTodos) {
  const todayTodos = getTodayWikiTodos(openTodos).slice(0, 5);
  const updatedAt = wikiTodoData.synced_at
    ? `\u540c\u6b65 ${wikiTodoData.synced_at}`
    : wikiTodoData.updated_at
      ? `\u66f4\u65b0 ${wikiTodoData.updated_at}`
      : wikiTodoData.source_file || "todo.json";

  setText("#today-todo-status", wikiTodoError ? copy.wikiTodoFailed : `${todayTodos.length} \u4e2a`);
  setText("#today-todo-updated", wikiTodoError || updatedAt);
  clearAndFill(qs("#today-todo-list"), createTodayTodoItem, todayTodos);

  if (!todayTodos.length && !wikiTodoError) {
    setText("#today-todo-list .empty-state", copy.todayTodoEmpty);
  }
}

function renderWikiTodos(openTodos = getOpenWikiTodos()) {
  const status = wikiTodoError ? copy.wikiTodoFailed : `${copy.wikiTodoReady} ${openTodos.length}`;
  const updatedAt = wikiTodoData.synced_at
    ? `同步 ${wikiTodoData.synced_at}`
    : wikiTodoData.updated_at
      ? `更新 ${wikiTodoData.updated_at}`
      : wikiTodoData.source_file || "todo.json";

  setText("#wiki-todo-status", status);
  setText("#wiki-todo-updated", wikiTodoError || updatedAt);
  clearAndFill(qs("#wiki-todo-list"), createWikiTodoItem, openTodos.slice(0, 4));

  if (!openTodos.length && !wikiTodoError) {
    setText("#wiki-todo-list .empty-state", copy.wikiTodoEmpty);
  }

  renderTodayTodos(openTodos);
}

function renderRicky() {
  const stats = Array.isArray(rickyData.stats) ? rickyData.stats : [];
  const places = Array.isArray(rickyData.places) ? rickyData.places : [];
  const records = Array.isArray(rickyData.records) ? rickyData.records : [];
  const pins = qs("#ricky-map-pins");

  setText("#ricky-title", rickyData.title || copy.rickyTitle);
  setText("#ricky-summary", rickyData.summary || rickyData.subtitle || "");
  setText("#ricky-updated", rickyData.updated_at ? `更新 ${rickyData.updated_at}` : copy.syncWaiting);
  setText("#ricky-map-count", `${places.length} 个地点`);
  clearAndFill(qs("#ricky-stats"), createRickyStatItem, stats);

  renderRickyLeaflet(places);
  if (!pins) return;
  pins.replaceChildren();
  if (!places.length) {
    const empty = document.createElement("p");
    empty.className = "ricky-map-empty";
    empty.textContent = copy.rickyEmptyPlaces;
    pins.appendChild(empty);
    return;
  }

  places.forEach((place, index) => {
    const x = Math.max(0, Math.min(100, Number(place.x ?? place.mapX ?? 50)));
    const y = Math.max(0, Math.min(100, Number(place.y ?? place.mapY ?? 50)));
    const pin = document.createElement("span");
    pin.className = "ricky-pin";
    pin.tabIndex = 0;
    pin.title = [place.name || place.city || copy.item, place.note || ""].filter(Boolean).join(" - ");
    pin.style.left = `${x}%`;
    pin.style.top = `${y}%`;
    pin.style.setProperty("--pin-color", index % 3 === 1 ? "var(--accent-strong)" : index % 3 === 2 ? "var(--orange)" : "var(--pink)");
    pin.innerHTML = `
      <span class="ricky-pin-label"></span>
      <span class="ricky-pin-dot" aria-hidden="true"></span>
    `;
    pin.querySelector(".ricky-pin-label").textContent = place.name || place.city || copy.item;
    pins.appendChild(pin);
  });
}

function getLifeFoodSection() {
  const sections = Array.isArray(lifeFoodsData.sections) ? lifeFoodsData.sections : [];
  return sections.find((section) => section.id === "food-picker") || sections[0] || { items: [] };
}

function createLifeFoodOption(item, index) {
  const label = document.createElement("label");
  label.className = "life-food-option";
  const tone = lifeFoodTones[index % lifeFoodTones.length];
  label.dataset.tone = tone;
  label.innerHTML = `
    <input type="checkbox" data-life-food checked />
    <span></span>
  `;
  const input = label.querySelector("input");
  input.value = item.id || item.name || `food-${index + 1}`;
  input.dataset.name = item.name || copy.item;
  input.dataset.tone = tone;
  label.querySelector("span").textContent = item.name || copy.item;
  return label;
}

function getSelectedLifeFoods() {
  return qsa("[data-life-food]")
    .filter((input) => input.checked)
    .map((input) => ({ id: input.value, name: input.dataset.name || input.value, tone: input.dataset.tone || "cyan" }));
}

function shuffleItems(items) {
  const next = [...items];
  for (let index = next.length - 1; index > 0; index -= 1) {
    const randomIndex = randomIndexBelow(index + 1);
    [next[index], next[randomIndex]] = [next[randomIndex], next[index]];
  }
  return next;
}

function randomIndexBelow(max) {
  if (window.crypto?.getRandomValues && max > 0) {
    const values = new Uint32Array(1);
    window.crypto.getRandomValues(values);
    return values[0] % max;
  }
  return Math.floor(Math.random() * max);
}

function setLifeResult(resultText, noteText = "") {
  const result = qs("#life-food-result");
  if (!result) return;
  result.querySelector(".life-result-text").textContent = resultText;
  result.querySelector(".life-result-label").textContent = noteText || "\u4eca\u665a\u5403";
}

function setLifeWheelPlaceholder(text) {
  const track = qs("#life-food-wheel-track");
  if (!track) return;
  track.style.setProperty("--life-wheel-count", "1");
  track.replaceChildren(createLifeWheelLane({ name: text, tone: "gray" }));
  track.style.transform = "translateY(0)";
}

function clearLifeWheelAnimations() {
  lifeWheelAnimations.forEach((handle) => {
    if (handle?.type === "raf") {
      cancelAnimationFrame(handle.id);
      return;
    }
    if (typeof handle === "number") {
      clearInterval(handle);
      return;
    }
    handle?.cancel?.();
  });
  lifeWheelAnimations = [];
}

function setLifePickingState(isPicking) {
  const result = qs("#life-food-result");
  const button = qs("#life-food-pick");
  result?.classList.toggle("is-picking", isPicking);
  result?.classList.remove("is-settled");
  if (button) {
    button.disabled = isPicking;
    button.dataset.state = isPicking ? "rolling" : "";
  }
}

function clampLifeFoodCount() {
  const selected = getSelectedLifeFoods();
  const countInput = qs("#life-food-count-input");
  if (!countInput) return Math.max(1, Math.min(1, selected.length || 1));
  const max = Math.max(selected.length, 1);
  const value = Math.min(Math.max(Number.parseInt(countInput.value || "1", 10) || 1, 1), max);
  countInput.max = String(max);
  countInput.value = String(value);
  return value;
}

function changeLifeFoodCount(delta) {
  const countInput = qs("#life-food-count-input");
  if (!countInput) return;
  countInput.value = String((Number.parseInt(countInput.value || "1", 10) || 1) + delta);
  clampLifeFoodCount();
}

function createLifeWheelItem(item) {
  const node = document.createElement("span");
  node.className = "life-wheel-item";
  node.dataset.tone = item.tone || "cyan";
  node.textContent = item.name;
  return node;
}

function createLifeWheelLane(item) {
  const lane = document.createElement("div");
  lane.className = "life-wheel-lane";
  const strip = document.createElement("div");
  strip.className = "life-wheel-strip";
  strip.appendChild(createLifeWheelItem(item));
  lane.appendChild(strip);
  return lane;
}

function setLifeWheelLaneItems(lane, items) {
  const strip = lane.querySelector(".life-wheel-strip") || document.createElement("div");
  strip.className = "life-wheel-strip";
  strip.style.transform = "translate3d(0, 0, 0)";
  strip.replaceChildren(...items.map((item) => createLifeWheelItem(item)));
  lane.replaceChildren(strip);
  return strip;
}

function randomLifeFood(items, avoidItem) {
  const pool = items.length > 1 && avoidItem ? items.filter((item) => item.id !== avoidItem.id) : items;
  return pool[randomIndexBelow(pool.length)] || items[0];
}

function createLifeWheelSequence(items, finalItem, length) {
  const sequence = [];
  let previousItem = finalItem;
  while (sequence.length < length - 1) {
    previousItem = randomLifeFood(items, previousItem);
    sequence.push(previousItem);
  }
  sequence.push(finalItem);
  return sequence;
}

function easeLifeWheel(progress) {
  const clamped = Math.min(Math.max(progress, 0), 1);
  return 1 - ((1 - clamped) ** 4);
}

function animateLifeWheelStrip(strip, distance, duration) {
  return new Promise((resolve) => {
    const startedAt = performance.now();
    const handle = { type: "raf", id: 0 };
    const step = (now) => {
      const progress = (now - startedAt) / duration;
      const eased = easeLifeWheel(progress);
      strip.style.transform = `translate3d(0, ${-distance * eased}px, 0)`;
      if (progress < 1) {
        handle.id = requestAnimationFrame(step);
        return;
      }
      strip.style.transform = `translate3d(0, ${-distance}px, 0)`;
      lifeWheelAnimations = lifeWheelAnimations.filter((item) => item !== handle);
      resolve();
    };
    handle.id = requestAnimationFrame(step);
    lifeWheelAnimations.push(handle);
  });
}

function animateLifeWheel(items, finalItems) {
  const wheel = qs("#life-food-wheel");
  const track = qs("#life-food-wheel-track");
  if (!wheel || !track || !items.length || !finalItems.length) return Promise.resolve();

  clearLifeWheelAnimations();
  track.replaceChildren();
  track.style.transform = "translateY(0)";
  track.style.setProperty("--life-wheel-count", String(finalItems.length));
  const lanes = finalItems.map((item) => {
    const lane = createLifeWheelLane(randomLifeFood(items, item));
    track.appendChild(lane);
    return lane;
  });
  wheel.classList.add("is-rolling");

  const lanePromises = lanes.map((lane, laneIndex) => new Promise((resolve) => {
    const sequence = createLifeWheelSequence(items, finalItems[laneIndex], 14 + laneIndex * 3);
    const strip = setLifeWheelLaneItems(lane, sequence);
    const laneHeight = lane.getBoundingClientRect().height || 340;
    lane.style.setProperty("--life-wheel-lane-height", `${laneHeight}px`);
    strip.style.transform = "translate3d(0, 0, 0)";
    const distance = (sequence.length - 1) * laneHeight;
    animateLifeWheelStrip(strip, distance, 2400 + laneIndex * 360).then(() => {
      setLifeWheelLaneItems(lane, [finalItems[laneIndex]]);
      lane.classList.add("is-final");
      resolve();
    });
  }));

  return Promise.all(lanePromises).then(() => {
    wheel.classList.remove("is-rolling");
    lifeWheelAnimations = [];
  });
}

async function pickLifeFoods() {
  const selected = getSelectedLifeFoods();
  if (!selected.length) {
    setLifeResult(copy.lifePickEmpty, "\u7ed3\u679c");
    return;
  }
  const count = clampLifeFoodCount();
  const pickedItems = shuffleItems(selected).slice(0, count);
  const picked = pickedItems.map((item) => item.name);
  clearInterval(lifePickTimer);
  setLifePickingState(true);
  setLifeResult("\u8f6c\u8f6e\u542f\u52a8", "\u6b63\u5728\u6311");
  await animateLifeWheel(selected, pickedItems);
  setLifePickingState(false);
  setLifeResult(picked.join(" / "), `${count} / ${selected.length}`);
  qs("#life-food-result")?.classList.add("is-settled");
}

function renderLife() {
  const section = getLifeFoodSection();
  const items = Array.isArray(section.items) ? section.items : [];
  const options = qs("#life-food-options");
  const countInput = qs("#life-food-count-input");

  setText("#life-summary", section.summary || "\u4ece\u5019\u9009\u6e05\u5355\u91cc\u968f\u673a\u51b3\u5b9a\u4eca\u5929\u5403\u4ec0\u4e48\u3002");
  setText("#life-updated", lifeFoodsData.synced_at ? `\u540c\u6b65 ${lifeFoodsData.synced_at}` : copy.syncWaiting);
  setText("#life-food-count", `${items.length} \u4e2a\u5019\u9009`);
  if (countInput) {
    countInput.max = String(Math.max(items.length, 1));
    countInput.value = String(Math.min(Math.max(Number(section.defaultCount || 1), 1), Math.max(items.length, 1)));
  }
  if (!options) return;
  options.replaceChildren();
  if (!items.length) {
    const empty = document.createElement("p");
    empty.className = "empty-state";
    empty.textContent = copy.lifeNoFoods;
    options.appendChild(empty);
    setLifeResult(copy.lifeNoFoods);
    setLifeWheelPlaceholder(copy.lifeNoFoods);
    return;
  }
  items.forEach((item, index) => options.appendChild(createLifeFoodOption(item, index)));
  setLifeResult(copy.lifePickFirst);
  setLifeWheelPlaceholder(copy.lifePickFirst);
}

function getMappableRickyPlaces(places) {
  return places
    .map((place) => ({
      ...place,
      lat: Number(place.lat),
      lng: Number(place.lng),
    }))
    .filter((place) => Number.isFinite(place.lat) && Number.isFinite(place.lng));
}

function createRickyPopup(place) {
  const note = place.note ? `<p>${escapeHtml(place.note)}</p>` : "";
  const meta = [place.region, place.country, place.date].filter(Boolean).join(" · ");
  return `
    <strong>${escapeHtml(place.name || place.city || copy.item)}</strong>
    <small>${escapeHtml(meta)}</small>
    ${note}
  `;
}

function escapeHtml(value = "") {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderRickyLeaflet(places) {
  const mapNode = qs("#ricky-real-map");
  const mapShell = qs(".ricky-map");
  const mappable = getMappableRickyPlaces(places);
  if (!mapNode || !mapShell) return;

  if (!window.L || !mappable.length) {
    mapShell.classList.remove("has-real-map");
    return;
  }

  mapShell.classList.add("has-real-map");

  if (!rickyMap) {
    rickyMap = window.L.map(mapNode, {
      zoomControl: true,
      scrollWheelZoom: false,
      worldCopyJump: true,
    });
    window.L.tileLayer("https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png", {
      maxZoom: 18,
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
    }).addTo(rickyMap);
    rickyMarkerLayer = window.L.layerGroup().addTo(rickyMap);
  }

  rickyMarkerLayer.clearLayers();
  const bounds = [];
  mappable.forEach((place) => {
    const latLng = [place.lat, place.lng];
    bounds.push(latLng);
    window.L.marker(latLng, { icon: createRickyMapIcon(place) })
      .bindPopup(createRickyPopup(place), { maxWidth: 260 })
      .addTo(rickyMarkerLayer);
  });

  rickyMap.fitBounds(bounds, {
    padding: [16, 16],
    maxZoom: 3,
  });
  requestAnimationFrame(() => rickyMap.invalidateSize());
}

function createRickyMapIcon(place) {
  const isWaiting = place.dateStatus === "needs_confirmation";
  const color = isWaiting ? "#ff980f" : "#ff6fae";
  const label = escapeHtml(place.mapLabel || place.name || place.city || copy.item);
  return window.L.divIcon({
    className: "ricky-leaflet-marker",
    html: `<span style="--marker-color: ${color}"><strong>${label}</strong></span>`,
    iconSize: [48, 52],
    iconAnchor: [21, 44],
    popupAnchor: [0, -40],
  });
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

function getLocalDateKey() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function getTrafficUsageRecords(limit = 30) {
  const today = getLocalDateKey();
  const history = Array.isArray(checkinData.traffic_usage_history) ? checkinData.traffic_usage_history : [];
  return history
    .filter((record) => record?.date && record.date !== today && Number.isFinite(Number(record.used_mb)))
    .slice(0, limit)
    .reverse()
    .map((record) => ({
      ...record,
      used_gb: Number(record.used_mb) / 1024,
    }));
}

function getNiceStep(value) {
  const safeValue = Math.max(Number(value) || 0, Number.EPSILON);
  const magnitude = 10 ** Math.floor(Math.log10(safeValue));
  const normalized = safeValue / magnitude;
  const niceNormalized = normalized < 1.5 ? 1 : normalized < 3 ? 2 : normalized < 7 ? 5 : 10;
  return niceNormalized * magnitude;
}

function getChartScale(values, tickCount = 5) {
  const cleanValues = values.map((value) => Number(value)).filter(Number.isFinite);
  const rawMin = cleanValues.length ? Math.min(...cleanValues) : 0;
  const rawMax = Math.max(...cleanValues, 1);
  const spread = rawMax - rawMin;
  const useTightScale = rawMin > 0 && rawMax > 0 && spread / rawMax <= 0.25;
  const scaleMin = useTightScale ? rawMin - Math.max(spread * 0.1, rawMax * 0.005) : 0;
  const scaleMax = useTightScale ? rawMax + Math.max(spread * 0.1, rawMax * 0.005) : rawMax;
  let step = getNiceStep((scaleMax - scaleMin) / Math.max(tickCount - 1, 1));
  let min = 0;
  let max = step;
  let ticks = [];
  for (let attempt = 0; attempt < 4; attempt += 1) {
    min = useTightScale ? Math.max(0, Math.floor(scaleMin / step) * step) : 0;
    max = Math.max(step, Math.ceil(scaleMax / step) * step);
    ticks = [];
    for (let value = min; value <= max + step / 2; value += step) {
      ticks.push(value);
    }
    if (ticks.length <= tickCount + 1) break;
    step *= 2;
  }
  return { min, max, ticks };
}

function getIntegerChartScale(values) {
  const cleanValues = values.map((value) => Number(value)).filter(Number.isFinite);
  const rawMin = cleanValues.length ? Math.min(...cleanValues) : 0;
  const rawMax = Math.max(...cleanValues, 1);
  const min = Math.max(0, Math.floor(rawMin));
  const max = Math.max(min + 1, Math.ceil(rawMax));
  const ticks = Array.from({ length: max - min + 1 }, (_, index) => min + index);
  return { min, max, ticks };
}

function getChartRenderWidth(container) {
  const width = container?.clientWidth || 0;
  return Math.max(920, Math.floor(width));
}

function createLineChart(records, options) {
  const { key, unit, formatter, stroke } = options;
  const yFormatter = options.yFormatter || ((value) => `${Math.round(value)}${unit}`);
  const width = options.width || Math.max(920, records.length * 46 + 96);
  const height = 340;
  const padding = { top: 28, right: 26, bottom: 64, left: 56 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;
  const values = records.map((record) => Number(record[key]) || 0);
  const yScale = options.integerYScale ? getIntegerChartScale(values) : getChartScale(values);
  const yRange = yScale.max - yScale.min || 1;
  const points = records.map((record, index) => {
    const x = padding.left + (records.length <= 1 ? 0 : (index / (records.length - 1)) * chartWidth);
    const y = padding.top + chartHeight - (((Number(record[key]) || 0) - yScale.min) / yRange) * chartHeight;
    return { record, value: Number(record[key]) || 0, x, y };
  });
  const linePath = points.map((point, index) => `${index === 0 ? "M" : "L"} ${point.x.toFixed(1)} ${point.y.toFixed(1)}`).join(" ");
  const yTicks = yScale.ticks.map((value) => {
    const y = padding.top + chartHeight - ((value - yScale.min) / yRange) * chartHeight;
    return { value, y };
  });
  const labelInterval = 5;
  const xLabelIndexes = new Set();
  records.forEach((_, index) => {
    if (index % labelInterval === 0) xLabelIndexes.add(index);
  });
  if (records.length > 0) {
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
            <text class="chart-y-label" x="${padding.left - 10}" y="${tick.y + 4}" text-anchor="end">${yFormatter(tick.value)}</text>
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
  setText("#sidebar-dounai-flow", "\u7b7e\u5230\u72b6\u6001");
}

function renderDounai() {
  const today = checkinData.today || {};
  const total = checkinData.total || {};
  const account = checkinData.account || {};
  const records = getCheckinRecords(30);
  const accountHistory = getAccountHistoryRecords(30);
  const trafficUsageRecords = getTrafficUsageRecords(30);
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
  setText("#dounai-daily-flow", Number.isFinite(dailyAvailable) ? `${formatDailyTraffic(dailyAvailable)}/d` : "--");

  const usageChart = qs("#dounai-usage-chart");
  if (usageChart) {
    usageChart.innerHTML = createLineChart(trafficUsageRecords, {
      key: "used_gb",
      title: "近 30 天实际使用流量",
      unit: "GB",
      stroke: "#00a6c8",
      width: getChartRenderWidth(usageChart),
      formatter: (value) => `${value.toFixed(2)} GB`,
      yFormatter: (value) => `${Math.round(value)}GB`,
      integerYScale: true,
    });
  }

  const dailyBudgetChart = qs("#dounai-daily-budget-chart");
  if (dailyBudgetChart) {
    dailyBudgetChart.innerHTML = createLineChart(accountHistory, {
      key: "daily_available_gb",
      title: "近 30 天日均可用流量",
      unit: "GB",
      stroke: "#7c3aed",
      width: getChartRenderWidth(dailyBudgetChart),
      formatter: (value) => `${value.toFixed(2)} GB`,
      yFormatter: (value) => `${Math.round(value)}GB`,
      integerYScale: true,
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

function normalizeTaskTitle(value) {
  return String(value || "")
    .trim()
    .replace(/\s+/g, " ")
    .toLowerCase();
}

function getHomeWorkItems() {
  const mainlines = projectStatusData.mainlines || [];
  const rawActions = projectStatusData.actions || [];
  const mainlineTitles = new Set(mainlines.map((item) => normalizeTaskTitle(item.title)).filter(Boolean));
  const actions = rawActions.filter((item) => !mainlineTitles.has(normalizeTaskTitle(item.title)));
  return { mainlines, actions, freshness: getProjectStatusFreshness() };
}

function getProjectStatusFreshness(now = new Date()) {
  const generatedAt = parseLocalDateTime(projectStatusData.generatedAt);
  const staleAfterHours = Number(projectStatusData.staleAfterHours || 168);
  const ageHours = generatedAt ? (now.getTime() - generatedAt.getTime()) / (60 * 60 * 1000) : Infinity;
  const hasItems = Boolean((projectStatusData.mainlines || []).length || (projectStatusData.actions || []).length);
  const stale = !hasItems || !Number.isFinite(ageHours) || ageHours > staleAfterHours;
  return {
    stale,
    ageHours,
    label: stale ? "\u5f85\u5237\u65b0" : "\u8def\u7ebf\u56fe\u5df2\u540c\u6b65",
    detail: projectStatusData.sourceUpdatedAt
      ? `ROADMAP ${formatSourceUpdatedAt(projectStatusData.sourceUpdatedAt)}`
      : "\u7b49\u5f85 ROADMAP \u540c\u6b65",
  };
}

function renderProjectStatusFreshness(freshness) {
  const node = qs("#project-status-freshness");
  if (!node) return;
  node.textContent = freshness.label;
  node.dataset.state = freshness.stale ? "stale" : "fresh";
  node.title = freshness.detail;
  qs("#actions")?.setAttribute("data-health", freshness.stale ? "unknown" : "ok");
}

function setSummaryLiveTone(selector, tone) {
  const element = qs(selector);
  if (element) element.dataset.tone = tone;
}

function getTodayOverride(today = dashboardData.today || {}) {
  if (!isTodayDateTime(today.updatedAt)) return null;
  if (!today.modeLabel && !today.summary && !today.focus && !today.energy) return null;
  return today;
}

function isAutomationConcern(status = "") {
  const text = String(status).toLowerCase();
  return ["failure", "failed", "fail", "error", "check"].some((key) => text.includes(key))
    || ["异常", "失败", "错误", "不可用", "待检查"].some((key) => text.includes(key));
}

function makeTodaySource(state, label, detail) {
  return { state, label, detail };
}

function deriveTodayStatus({ mainlines, actions, todayTodos, token1d, token7d, automation, phase }) {
  const today = dashboardData.today || {};
  const override = getTodayOverride(today);
  const tokenToday = Number(token1d.total || 0);
  const tokenWeek = Number(token7d.total || 0);
  const automationStatus = automation.status || copy.waiting;
  const topTodo = todayTodos[0];
  const topAction = actions[0];
  const topMainline = mainlines[0];
  const primaryWork = topAction || topMainline;
  const phaseLabel = phase?.label || "\u4eca\u65e5";
  const isEvening = ["\u6df1\u591c", "\u665a\u95f4", "\u591c\u95f4"].some((key) => phaseLabel.includes(key));

  if (override) {
    const focus = override.focus || primaryWork?.title || topTodo?.title || "--";
    return {
      mode: override.modeLabel || "\u4eca\u65e5\u786e\u8ba4",
      summary: override.summary || (focus !== "--" ? `\u4eca\u5929\u4f18\u5148\u63a8\u8fdb\uff1a${focus}\u3002` : "\u4eca\u5929\u72b6\u6001\u5df2\u624b\u52a8\u786e\u8ba4\u3002"),
      rhythm: override.energy ? `\u4eba\u5de5 ${override.energy}` : "\u4eba\u5de5\u786e\u8ba4",
      focus,
      source: makeTodaySource("fresh", "\u4eca\u65e5\u786e\u8ba4", `${copy.updatedAtShort} ${override.updatedAt}`),
    };
  }

  if (isAutomationConcern(automationStatus)) {
    return {
      mode: "\u5de1\u68c0\u6a21\u5f0f",
      summary: `\u7cfb\u7edf\u81ea\u52a8\u5316\u663e\u793a\u201c${automationStatus}\u201d\uff0c\u5148\u770b\u4e91\u670d\u52a1\u548c\u540c\u6b65\u65e5\u5fd7\u3002`,
      rhythm: "\u9700\u8981\u68c0\u67e5",
      focus: "\u68c0\u67e5\u81ea\u52a8\u5316",
      source: makeTodaySource("danger", "\u81ea\u52a8\u5de1\u68c0", automation.lastRun || automation.summary || copy.sync),
    };
  }

  if (todayTodos.length) {
    return {
      mode: "\u6267\u884c\u6a21\u5f0f",
      summary: `\u4eca\u5929\u6709 ${todayTodos.length} \u4e2a\u660e\u786e\u5f85\u529e\uff0c\u4f18\u5148\u5904\u7406\uff1a${topTodo.title}\u3002`,
      rhythm: todayTodos.length > 1 ? "\u5f85\u529e\u96c6\u4e2d" : "\u5f85\u529e\u660e\u786e",
      focus: topTodo.title,
      source: makeTodaySource("attention", "\u81ea\u52a8\u751f\u6210", "\u57fa\u4e8e\u4eca\u65e5 TODO"),
    };
  }

  if (isEvening) {
    const focus = primaryWork?.title || (tokenToday > 0 ? "\u6c89\u6dc0 AI \u534f\u4f5c" : "\u7ed9\u660e\u5929\u7559\u5165\u53e3");
    return {
      mode: "\u590d\u76d8\u6a21\u5f0f",
      summary: primaryWork
        ? `\u665a\u4e0a\u9002\u5408\u6536\u675f\uff1a\u8bb0\u5f55\u201c${focus}\u201d\u7684\u8fdb\u5c55\uff0c\u5e76\u7ed9\u660e\u5929\u7559\u5165\u53e3\u3002`
        : "\u665a\u4e0a\u9002\u5408\u8f7b\u91cf\u590d\u76d8\uff0c\u628a\u4eca\u5929\u7684\u5224\u65ad\u6536\u675f\u6210\u8bb0\u5f55\u3002",
      rhythm: "\u665a\u95f4\u6536\u675f",
      focus,
      source: makeTodaySource("auto", "\u81ea\u52a8\u751f\u6210", "\u57fa\u4e8e\u5f53\u524d\u65f6\u6bb5"),
    };
  }

  if (actions.length) {
    return {
      mode: "\u63a8\u8fdb\u6a21\u5f0f",
      summary: `\u4eca\u5929\u6ca1\u6709\u660e\u786e\u65e5\u671f TODO\uff0c\u5efa\u8bae\u63a8\u8fdb ROADMAP\uff1a${topAction.title}\u3002`,
      rhythm: "\u8def\u7ebf\u63a8\u8fdb",
      focus: topAction.title,
      source: makeTodaySource("attention", "\u81ea\u52a8\u751f\u6210", "\u57fa\u4e8e ROADMAP"),
    };
  }

  if (mainlines.length) {
    return {
      mode: "\u4e3b\u7ebf\u6a21\u5f0f",
      summary: `\u5f53\u524d\u4e3b\u7ebf\u662f\u201c${topMainline.title}\u201d\uff0c\u4eca\u5929\u53ef\u4ee5\u5148\u4fdd\u6301\u4e00\u4e2a\u63a8\u8fdb\u53e3\u3002`,
      rhythm: "\u4e3b\u7ebf\u5c31\u4f4d",
      focus: topMainline.title,
      source: makeTodaySource("auto", "\u81ea\u52a8\u751f\u6210", "\u57fa\u4e8e ROADMAP"),
    };
  }

  if (tokenToday > 0 || tokenWeek > 0) {
    return {
      mode: "\u63a2\u7d22\u6a21\u5f0f",
      summary: tokenToday > 0
        ? `\u4eca\u5929\u5df2\u6709 ${formatToken(tokenToday)} Token \u6d3b\u8dc3\uff0c\u9002\u5408\u628a\u63a2\u7d22\u7ed3\u679c\u6c89\u6dc0\u6210\u5f85\u529e\u6216\u8bb0\u5f55\u3002`
        : `\u8fd1 7 \u5929\u6709 ${formatToken(tokenWeek)} Token \u6d3b\u8dc3\uff0c\u4eca\u5929\u53ef\u4ee5\u4ece\u5df2\u6709\u63a2\u7d22\u91cc\u63d0\u4e00\u4e2a\u5165\u53e3\u3002`,
      rhythm: tokenToday > 0 ? "AI \u534f\u4f5c\u6d3b\u8dc3" : "\u8f7b\u91cf\u63a2\u7d22",
      focus: "\u6c89\u6dc0\u63a2\u7d22\u7ed3\u8bba",
      source: makeTodaySource("auto", "\u81ea\u52a8\u751f\u6210", "\u57fa\u4e8e Token \u6d3b\u8dc3"),
    };
  }

  return {
    mode: "\u5f85\u786e\u8ba4",
    summary: "\u4eca\u5929\u8fd8\u6ca1\u6709\u660e\u786e\u5f85\u529e\u6216\u4e3b\u7ebf\u4fe1\u53f7\uff0c\u53ef\u4ee5\u5148\u7ed9 personal-wiki \u6216 ROADMAP \u7559\u4e00\u4e2a\u5165\u53e3\u3002",
    rhythm: phaseLabel,
    focus: "\u7b49\u5f85\u4eca\u65e5\u5165\u53e3",
    source: makeTodaySource("missing", "\u7b49\u5f85\u4fe1\u53f7", "\u6682\u65e0\u4eca\u65e5 TODO / ROADMAP / Token"),
  };
}

function renderTodayStatus(mainlines, actions, todayTodos, token1d, token7d, automation) {
  const tokenToday = Number(token1d.total || 0);
  const tokenWeek = Number(token7d.total || 0);
  const automationStatus = automation.status || copy.waiting;
  const topMainline = mainlines[0]?.title || actions[0]?.title || "--";
  const phase = updateTodayPhase();
  const status = deriveTodayStatus({ mainlines, actions, todayTodos, token1d, token7d, automation, phase });

  setText("#today-mode", status.mode);
  setText("#daily-brief", status.summary || dashboardData.brief || copy.waitBrief);
  setText("#today-energy", `${copy.energy} ${status.rhythm || "--"}`);
  setText("#today-focus", `${copy.focus} ${status.focus || "--"}`);
  updateTodaySource(status.source);

  setText(
    "#today-action-signal",
    todayTodos.length
      ? `${todayTodos.length} \u4e2a\u4eca\u65e5\u5f85\u529e`
      : actions.length ? `${actions.length} \u4e2a\u5f85\u63a8\u8fdb` : mainlines.length ? "\u4e3b\u7ebf\u5df2\u5c31\u4f4d" : "\u7b49\u5f85\u8def\u7ebf\u56fe",
  );
  setText(
    "#today-action-note",
    todayTodos[0]?.title || (topMainline && topMainline !== "--" ? `\u4e3b\u7ebf ${topMainline}` : "\u7b49\u5f85 ROADMAP \u5199\u5165"),
  );
  setSummaryLiveTone("#today-action-row", todayTodos.length || actions.length ? "orange" : "blue");

  if (tokenToday > 0) {
    setText("#today-token-signal", `\u4eca\u65e5 ${formatToken(tokenToday)}`);
    setText("#today-token-note", tokenWeek > 0 ? `7\u5929 ${formatToken(tokenWeek)}` : "\u7b49\u5f85\u603b\u8d26");
  } else if (tokenWeek > 0) {
    setText("#today-token-signal", `7\u5929 ${formatToken(tokenWeek)}`);
    setText("#today-token-note", "\u4eca\u65e5\u6682\u65e0\u65b0\u589e");
  } else {
    setText("#today-token-signal", "\u7b49\u5f85\u603b\u8d26");
    setText("#today-token-note", "Token \u6570\u636e\u540c\u6b65\u540e\u66f4\u65b0");
  }

  setText("#today-automation-signal", automationStatus);
  setText("#today-automation-note", automation.lastRun || automation.summary || copy.sync);
  setSummaryLiveTone("#today-automation-row", getTone(automationStatus));
}

function renderHome() {
  const { mainlines, actions, freshness: projectFreshness } = getHomeWorkItems();
  const trustedMainlines = projectFreshness.stale ? [] : mainlines;
  const trustedActions = projectFreshness.stale ? [] : actions;
  const openTodos = getOpenWikiTodos();
  const todayTodos = getTodayWikiTodos(openTodos);
  const token7d = getTokenRange("7d");
  const token1d = getTokenRange("1d");
  const tokenAll = getTokenRange("all");
  const automation = dashboardData.automation || {};

  renderTodayStatus(trustedMainlines, trustedActions, todayTodos, token1d, token7d, automation);
  renderProjectStatusFreshness(projectFreshness);
  const automationStatus = automation.status || copy.waiting;
  const automationTitle = automation.summary
    ? `系统自动化：${automation.summary}`
    : "系统自动化状态：nginx、证书、部署、cron、失败日志和资源快照";
  setText("#last30-source", last30Data.sourceSummary || last30Data.updatedAt || copy.syncWaiting);
  renderWeather();

  const syncStatus = getDataSyncStatus();
  setText("#metric-today-execution", `${todayTodos.length} \u4e2a`);
  setText("#metric-today-execution-note", todayTodos[0]?.title || copy.noTodayExecution);
  setText("#metric-sync", syncStatus.label);
  setText("#metric-sync-note", syncStatus.note);
  qs(".metric-sync")?.setAttribute("data-health", syncStatus.health);
  setText("#metric-token-total", formatToken(token7d.total));
  setText("#metric-token-note", `${copy.day1} ${formatToken(token1d.total)}`);
  setText("#metric-automation", automationStatus || "--");
  setText("#metric-automation-note", automation.lastRun || copy.sync);
  setTitle(".metric-data", automationTitle);
  const automationHealth = getAutomationHealth(automationStatus);
  qs(".metric-data")?.setAttribute("data-health", automationHealth);
  qs("#system-panel")?.setAttribute("data-health", automationHealth);
  renderMarketIndices();
  setText("#mini-token-1d", formatToken(token1d.total));
  setText("#mini-token-7d", formatToken(token7d.total));
  setText("#mini-token-all", formatToken(tokenAll.total));
  setText("#mini-token-updated", getTokenUsage().updatedAt ? `${copy.updatedAtShort} ${getTokenUsage().updatedAt}` : copy.syncWaiting);
  setText(
    "#home-token-activity-updated",
    getTokenUsage().updatedAt ? `${copy.updatedAtShort} ${getTokenUsage().updatedAt}` : copy.syncWaiting,
  );
  const homeActivityChart = qs("#home-token-activity-chart");
  if (homeActivityChart) {
    homeActivityChart.replaceChildren(createTokenActivityChart(getTokenUsage().activity));
  }
  updateSidebarTokenSummary("7d");

  clearAndFill(qs("#action-list"), createTask, actions);
  const systemItems = dashboardData.system || [];
  const cloudSystemItems = [
    {
      key: "host",
      name: "Host",
      value: "43.160.240.244",
      note: "ubuntu / Tencent Cloud Singapore",
    },
    {
      key: "site",
      name: "站点",
      value: "dash / blog",
      note: "dash.maxnow.cn / blog.maxnow.cn",
    },
    ...systemItems,
  ];
  clearAndFill(qs("#system-list"), createSystemItem, systemItems);
  clearAndFill(qs("#cloud-system-list"), createCloudSystemItem, cloudSystemItems);
  setText("#project-version", projectMetaData.versionLabel || "v--");
  setText("#project-version-note", projectMetaData.deployNote || projectMetaData.updatedAt || copy.sync);
  clearAndFill(qs("#project-update-list"), createProjectUpdateItem, (projectMetaData.recentUpdates || []).slice(0, 4));
  renderCheckin();
  renderWikiTodos(openTodos);
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
  if (rangeTabs && shouldRenderRangeTabs(rangeTabs, ranges)) {
    rangeTabs.replaceChildren(...ranges.map(createRangeButton));
  }

  qsa(".range-tab").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.range === range.key);
  });
  if (qs("#tokens-view")?.classList.contains("is-active")) {
    updateSidebarTokenSummary(range.key);
  }

  setText("#token-updated", usage.updatedAt ? `${copy.ledgerMergedAt} ${usage.updatedAt}` : copy.sync);
  renderSourceUpdates(usage.sourceUpdates || []);
  setText("#token-total", formatToken(range.total));
  setText("#token-input", formatToken(range.input));
  setText("#token-output", formatToken(range.output));
  setText("#token-cache", formatToken(range.cacheRead));
  setText("#token-cache-hit", formatPercent(range.cacheHitRate));
  setText("#token-cost", formatCost(range.cost));
  setText("#token-active-time", formatActiveDuration(range.activeSeconds));

  clearAndFill(qs("#token-sources"), createSourceItem, usage.sources || []);
  clearAndFill(qs("#token-models"), createModelItem, usage.models || []);
  clearAndFill(qs("#token-sessions"), createSessionItem, usage.sessions || []);

  const trendChart = qs("#token-trend-chart");
  if (trendChart) {
    trendChart.innerHTML = createLineChart(usage.daily || [], {
      key: "total",
      title: "最近 30 天 Token 用量",
      unit: "",
      stroke: "#2688e8",
      width: getChartRenderWidth(trendChart),
      formatter: formatToken,
      yFormatter: formatToken,
    });
  }
}

function tokenActivityCellTitle(cell) {
  const dateLabel = formatDateLabel(cell.date);
  if (cell.isEmpty) return `${dateLabel} ${copy.noData}`;
  const runs = cell.runs ? ` / ${cell.runs} runs` : "";
  return `${dateLabel} ${formatToken(cell.total)}${runs}`;
}

function createTokenActivityChart(activity = {}, options = {}) {
  if (!activity.cells?.length) {
    const empty = document.createElement("p");
    empty.className = "empty-state";
    empty.textContent = copy.noData;
    return empty;
  }

  const chart = document.createElement("div");
  chart.className = "token-activity-scroll";
  if (options.compact) chart.classList.add("is-compact");
  chart.style.setProperty("--activity-column-count", String(activity.columnCount || 1));
  chart.style.setProperty("--activity-row-count", String(activity.rowCount || 7));

  const months = document.createElement("div");
  months.className = "token-activity-months";
  (activity.months || []).forEach((month) => {
    const label = document.createElement("span");
    label.textContent = month.label;
    label.style.gridColumn = `${month.start} / span ${month.span}`;
    label.style.gridRow = "1";
    months.appendChild(label);
  });

  const grid = document.createElement("div");
  grid.className = "token-activity-grid";
  grid.setAttribute("role", "img");
  grid.setAttribute("aria-label", "Token activity by day");
  activity.cells.forEach((cell) => {
    const block = document.createElement("span");
    const title = tokenActivityCellTitle(cell);
    block.className = "token-activity-cell";
    block.dataset.level = String(cell.level || 0);
    block.style.gridColumn = String((cell.column || 0) + 1);
    block.style.gridRow = String((cell.row || 0) + 1);
    block.title = title;
    block.setAttribute("aria-label", title);
    if (cell.isEmpty) block.dataset.empty = "true";
    if (cell.isToday) block.classList.add("is-today");
    grid.appendChild(block);
  });

  chart.append(months, grid);
  return chart;
}

function normalizeSourceUpdatedAt(value) {
  const text = String(value || "").replace("T", " ").replace(/\+\d{2}:\d{2}$/, "").trim();
  return text ? text.slice(0, 16) : "";
}

function formatSourceUpdatedAt(value) {
  const text = normalizeSourceUpdatedAt(value);
  return text || copy.syncWaiting;
}

function sourceUpdatedAtFreshness(value, now = new Date()) {
  const date = parseLocalDateTime(normalizeSourceUpdatedAt(value));
  if (!date) return "unknown";
  const diffHours = (now.getTime() - date.getTime()) / (60 * 60 * 1000);
  if (diffHours < 0 || diffHours <= 2) return "fresh";
  if (diffHours <= 24) return "today";
  if (diffHours <= 72) return "stale";
  return "old";
}

function createSourceUpdateItem(source) {
  const item = document.createElement("div");
  item.className = "token-source-update-item";
  item.dataset.tone = source.tone || "blue";
  item.dataset.freshness = sourceUpdatedAtFreshness(source.updatedAt);
  const fullTime = normalizeSourceUpdatedAt(source.updatedAt);
  if (fullTime) item.title = `${source.label || "Source"} \u6700\u540e\u540c\u6b65 ${fullTime}`;

  const label = document.createElement("span");
  label.textContent = source.label || "Source";
  const time = document.createElement("strong");
  time.textContent = formatSourceUpdatedAt(source.updatedAt);
  if (fullTime) time.setAttribute("aria-label", `\u6700\u540e\u540c\u6b65 ${fullTime}`);

  item.append(label, time);
  return item;
}

function renderSourceUpdates(items) {
  const container = qs("#token-source-updates");
  if (!container) return;
  container.replaceChildren();
  if (!items.length) {
    const empty = document.createElement("div");
    empty.className = "token-source-update-item is-empty";
    empty.textContent = copy.syncWaiting;
    container.appendChild(empty);
    return;
  }
  items.forEach((item) => container.appendChild(createSourceUpdateItem(item)));
}

function createModelItem(model) {
  const article = document.createElement("article");
  article.className = "model-item";
  article.dataset.tone = getTone(model.name || "model");
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

function createSourceItem(source) {
  const article = document.createElement("article");
  article.className = "token-source-item";
  article.dataset.tone = source.tone || "blue";
  article.innerHTML = `
    <div>
      <span></span>
      <strong></strong>
    </div>
    <small></small>
  `;
  article.querySelector("span").textContent = source.label || "Source";
  article.querySelector("strong").textContent = formatToken(source.total);
  const sourceDuration = source.activeSeconds ? ` / ${formatActiveDuration(source.activeSeconds)}` : "";
  article.querySelector("small").textContent = `${formatCost(source.cost)} / ${source.runs || 0} runs${sourceDuration}`;
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

function createSessionItem(session) {
  const article = document.createElement("article");
  article.className = "session-item";
  article.dataset.tone = getTone(session.model || session.label || "session");
  const timestamp = String(session.timestamp || "");
  const timeLabel = timestamp.includes("T") ? timestamp.slice(5, 16).replace("T", " ") : timestamp.slice(5, 16);
  const title = session.runs > 1 || !timeLabel ? session.label || "OpenClaw session" : `${session.label || "OpenClaw"} ${timeLabel}`;
  article.innerHTML = `
    <div class="session-main">
      <strong></strong>
      <small></small>
    </div>
    <div class="session-meta">
      <span></span>
      <strong></strong>
    </div>
  `;
  article.querySelector(".session-main strong").textContent = title;
  article.querySelector(".session-main small").textContent = [session.model, session.runId ? `#${String(session.runId).slice(0, 8)}` : ""].filter(Boolean).join(" · ");
  const duration = session.activeSeconds ? formatActiveDuration(session.activeSeconds) : "";
  article.querySelector(".session-meta span").textContent = session.runs > 1
    ? [`${session.runs} runs`, duration].filter(Boolean).join(" · ")
    : [formatCost(session.cost || 0), duration].filter(Boolean).join(" · ");
  article.querySelector(".session-meta strong").textContent = formatToken(session.total);
  return article;
}

async function readJson(url, fallback) {
  try {
    const response = await fetch(url, { cache: "no-cache" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    return fallback;
  }
}

async function readWikiTodo() {
  try {
    const response = await fetch(WIKI_TODO_URL, { cache: "no-cache" });
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

function getActiveView() {
  return document.body.dataset.view || "home";
}

function renderActiveView() {
  const view = getActiveView();
  if (view === "home" || view === "cloud") renderHome();
  if (view === "dounai") renderDounai();
  if (view === "tokens") renderTokens();
  if (view === "ricky") renderRicky();
  if (view === "life") renderLife();
}

async function loadHomeData({ force = false } = {}) {
  if (!force && homeDataPromise) return homeDataPromise;

  homeDataPromise = Promise.all([
    readJson(DATA_URL, window.MAXNOW_DASHBOARD_DATA || fallbackData),
    readJson(LAST30_URL, window.MAXNOW_LAST30_DATA || fallbackLast30),
    readWikiTodo(),
    readJson(CHECKIN_URL, fallbackCheckin),
    readJson(MARKET_INDICES_URL, window.MAXNOW_MARKET_INDICES_DATA || fallbackMarketIndices),
    readJson(PROJECT_META_URL, window.MAXNOW_PROJECT_META_DATA || fallbackProjectMeta),
    readJson(PROJECT_STATUS_URL, window.MAXNOW_PROJECT_STATUS_DATA || fallbackProjectStatus),
  ]).then(([dashboard, last30, wikiTodo, checkin, marketIndices, projectMeta, projectStatus]) => {
    dashboardData = dashboard;
    last30Data = last30;
    wikiTodoData = wikiTodo;
    checkinData = checkin;
    marketIndicesData = marketIndices;
    projectMetaData = projectMeta;
    projectStatusData = projectStatus;
    renderHome();
    if (getActiveView() === "dounai") renderDounai();
  });

  return homeDataPromise;
}

async function loadTokenData({ force = false } = {}) {
  if (!force && tokenDataPromise) return tokenDataPromise;

  tokenDataPromise = readJson(TOKEN_USAGE_URL, window.MAXNOW_TOKEN_USAGE_DATA || fallbackTokenUsage)
    .then(async (tokenUsage) => {
      tokenUsageData = tokenUsage;
      if (!Array.isArray(tokenUsageData.days) || !tokenUsageData.days.length) {
        openclawUsageData = await readJson(OPENCLAW_USAGE_URL, window.MAXNOW_OPENCLAW_USAGE_DATA || fallbackOpenclawUsage);
      }
      if (getActiveView() === "tokens") renderTokens();
      if (getActiveView() === "home") renderHome();
      if (getActiveView() !== "tokens") updateSidebarTokenSummary("7d");
    });

  return tokenDataPromise;
}

function loadStylesheetOnce(id, url) {
  if (document.getElementById(id)) return Promise.resolve();
  return new Promise((resolve) => {
    const link = document.createElement("link");
    link.id = id;
    link.rel = "stylesheet";
    link.href = url;
    link.onload = resolve;
    link.onerror = resolve;
    document.head.appendChild(link);
  });
}

function loadScriptOnce(id, url) {
  if (document.getElementById(id)) return Promise.resolve();
  return new Promise((resolve) => {
    const script = document.createElement("script");
    script.id = id;
    script.src = url;
    script.onload = resolve;
    script.onerror = resolve;
    document.body.appendChild(script);
  });
}

async function ensureRickyMapAssets() {
  if (window.L) return window.L;
  if (!leafletPromise) {
    leafletPromise = Promise.all([
      loadStylesheetOnce("leaflet-css", LEAFLET_CSS_URL),
      loadScriptOnce("leaflet-js", LEAFLET_JS_URL),
    ]).then(() => window.L || null);
  }
  return leafletPromise;
}

async function loadRickyData({ force = false } = {}) {
  if (!force && rickyDataPromise) return rickyDataPromise;

  rickyDataPromise = readJson(RICKY_URL, window.MAXNOW_RICKY_DATA || fallbackRicky)
    .then(async (ricky) => {
      rickyData = ricky;
      renderRicky();
      if (getMappableRickyPlaces(rickyData.places || []).length) {
        await ensureRickyMapAssets();
        renderRicky();
      }
    });

  return rickyDataPromise;
}

async function loadLifeData({ force = false } = {}) {
  if (!force && lifeDataPromise) return lifeDataPromise;

  lifeDataPromise = readJson(LIFE_FOODS_URL, window.MAXNOW_LIFE_FOODS_DATA || fallbackLifeFoods)
    .then((lifeFoods) => {
      lifeFoodsData = lifeFoods;
      renderLife();
    });

  return lifeDataPromise;
}

async function loadViewData(view = getActiveView(), options = {}) {
  if (view === "tokens") return loadTokenData(options);
  if (view === "ricky") return loadRickyData(options);
  if (view === "life") return loadLifeData(options);
  return loadHomeData(options);
}

async function loadData(options = {}) {
  const view = getActiveView();
  await loadHomeData(options);
  if (view === "tokens") await loadTokenData(options);
  if (view === "ricky") await loadRickyData(options);
  if (view === "life") await loadLifeData(options);
  if (view === "home") await loadTokenData(options);
  renderActiveView();
}

function setView(view) {
  const nextView = ["home", "ricky", "life", "tokens", "cloud", "dounai"].includes(view) ? view : "home";
  document.body.dataset.view = nextView;
  qsa("[data-view-panel]").forEach((panel) => {
    panel.classList.toggle("is-active", panel.dataset.viewPanel === nextView);
  });
  qsa("[data-view]").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.view === nextView);
  });
  if (viewTitle) {
    viewTitle.textContent =
      nextView === "tokens"
        ? copy.tokenTitle
        : nextView === "ricky"
          ? copy.rickyTitle
          : nextView === "life"
            ? copy.lifeTitle
            : nextView === "cloud"
              ? copy.cloudTitle
              : nextView === "dounai"
                ? copy.dounaiTitle
                : copy.today;
  }
  if (nextView === "home" || nextView === "cloud") requestAnimationFrame(renderHome);
  if (nextView === "dounai") requestAnimationFrame(renderDounai);
  if (nextView === "ricky") requestAnimationFrame(renderRicky);
  if (nextView === "life") requestAnimationFrame(renderLife);
  if (nextView === "tokens") requestAnimationFrame(() => requestAnimationFrame(renderTokens));
  loadViewData(nextView);
  if (nextView === "home") loadTokenData();
  if (nextView !== "tokens") updateSidebarTokenSummary("7d");
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

function getSpecialDateLabels(date) {
  const specialDates = Array.isArray(dashboardData.specialDates) ? dashboardData.specialDates : [];
  const year = date.getFullYear();
  const month = date.getMonth() + 1;
  const day = date.getDate();
  const dateKey = `${year}-${String(month).padStart(2, "0")}-${String(day).padStart(2, "0")}`;

  return specialDates
    .filter((item) => {
      if (item.date) return String(item.date).slice(0, 10) === dateKey;
      return Number(item.month) === month && Number(item.day) === day;
    })
    .map((item) => {
      const title = item.title || item.label || item.name || "";
      if (!title) return "";
      const startYear = Number(item.startYear || item.year);
      if (Number.isFinite(startYear) && startYear > 0 && year > startYear) {
        const years = year - startYear;
        return `${title} ${years}\u5468\u5e74`;
      }
      return title;
    })
    .filter(Boolean);
}

function renderWeather() {
  const weather = dashboardData.weather || {};
  const location = weather.district || weather.location || "\u6d77\u6dc0";
  const condition = weather.condition || weather.summary || "--";
  const icon = weatherIcons[weather.icon] ? weather.icon : "cloud";
  const current = Number(weather.tempC);
  const high = Number(weather.highC);
  const low = Number(weather.lowC);
  const currentLabel = Number.isFinite(current) ? `${Math.round(current)}\u00b0C` : "--\u00b0C";
  const rangeLabel =
    Number.isFinite(high) && Number.isFinite(low) ? `${Math.round(low)}\u00b0/${Math.round(high)}\u00b0` : "--";
  const updatedLabel = formatTimeShort(weather.updatedAt);
  const card = qs(".summary-weather");
  const iconNode = qs("#weather-icon");

  if (card) card.dataset.weather = icon;
  if (iconNode) iconNode.innerHTML = weatherIcons[icon];
  setText("#weather-location", location);
  setText("#weather-temp", currentLabel);
  setText("#weather-condition", condition);
  setText("#weather-range", rangeLabel);
  setText("#weather-updated", updatedLabel ? `${updatedLabel} \u66f4\u65b0` : copy.syncWaiting);
  scheduleWeatherMetaFit();
}

function scheduleWeatherMetaFit() {
  cancelAnimationFrame(weatherMetaFitFrame);
  weatherMetaFitFrame = requestAnimationFrame(fitWeatherMeta);
}

function fitWeatherMeta() {
  const meta = qs(".weather-meta");
  const card = qs(".summary-weather");
  if (!meta || !card) return;

  const baseSize = 14;
  const minSize = 10;
  meta.style.setProperty("--weather-meta-font-size", `${baseSize}px`);

  const cardStyle = getComputedStyle(card);
  const available =
    card.clientWidth -
    Number.parseFloat(cardStyle.paddingLeft || "0") -
    Number.parseFloat(cardStyle.paddingRight || "0");
  if (!Number.isFinite(available) || available <= 0 || meta.scrollWidth <= available) return;

  const estimatedSize = Math.max(minSize, Math.floor((available / meta.scrollWidth) * baseSize * 10) / 10);
  for (let size = estimatedSize; size >= minSize; size -= 0.2) {
    meta.style.setProperty("--weather-meta-font-size", `${size.toFixed(1)}px`);
    if (meta.scrollWidth <= available) return;
  }
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
  const labels = [...getHolidayLabels(now), ...getSpecialDateLabels(now)];
  setText("#holiday-label", labels.length ? [...new Set(labels)].join(" \u00b7 ") : copy.noHoliday);
  updateTodayPhase();
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

qs("#system-panel")?.addEventListener("click", () => setView("cloud"));
qs("#system-panel")?.addEventListener("keydown", (event) => {
  if (event.key === "Enter" || event.key === " ") {
    event.preventDefault();
    setView("cloud");
  }
});

qs("#life-food-pick")?.addEventListener("click", pickLifeFoods);

qs("#life-food-count-minus")?.addEventListener("click", () => changeLifeFoodCount(-1));
qs("#life-food-count-plus")?.addEventListener("click", () => changeLifeFoodCount(1));
qs("#life-food-count-input")?.addEventListener("change", clampLifeFoodCount);

qs("#life-food-select-all")?.addEventListener("click", () => {
  qsa("[data-life-food]").forEach((input) => {
    input.checked = true;
  });
  clampLifeFoodCount();
  setLifeResult(copy.lifePickFirst);
  setLifeWheelPlaceholder(copy.lifePickFirst);
});

qs("#life-food-clear")?.addEventListener("click", () => {
  qsa("[data-life-food]").forEach((input) => {
    input.checked = false;
  });
  clampLifeFoodCount();
  setLifeResult(copy.lifePickEmpty);
  setLifeWheelPlaceholder(copy.lifePickEmpty);
});

qs("#life-food-options")?.addEventListener("change", () => {
  const selected = getSelectedLifeFoods();
  clampLifeFoodCount();
  setLifeResult(selected.length ? copy.lifePickFirst : copy.lifePickEmpty);
  setLifeWheelPlaceholder(selected.length ? copy.lifePickFirst : copy.lifePickEmpty);
});

refreshButton?.addEventListener("click", async () => {
  refreshButton.disabled = true;
  refreshButton.dataset.state = "loading";
  await loadData({ force: true });
  refreshButton.dataset.state = "success";
  refreshButton.disabled = false;
  setTimeout(() => refreshButton.removeAttribute("data-state"), 900);
});

window.addEventListener("hashchange", () => {
  setView(location.hash.replace("#", ""));
});

let resizeTimer = 0;
window.addEventListener("resize", () => {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => {
    scheduleWeatherMetaFit();
    if (qs("#dounai-view")?.classList.contains("is-active")) renderDounai();
    if (qs("#tokens-view")?.classList.contains("is-active")) renderTokens();
  }, 120);
});

updateClock();
setInterval(updateClock, 30000);
loadHomeData().then(() => setView(location.hash.replace("#", "")));
setInterval(() => loadData({ force: true }), DATA_AUTO_REFRESH_INTERVAL_MS);
