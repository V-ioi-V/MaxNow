const DATA_URL = "./data/dashboard.json";
const AI_NEWS_URL = "./data/ai-news.json";
const LAST30_URL = "./data/last-30.json";
const WIKI_TODO_URL = "./data/wiki-todos.json";
const WIKI_TODO_SOURCE_URL = "https://github.com/V-ioi-V/personal-wiki/blob/main/wiki/tasks/todo.json";
const WIKI_TASK_BASE_URL = "https://github.com/V-ioi-V/personal-wiki/blob/main/wiki/tasks/";

const fallbackData = window.MAXNOW_DASHBOARD_DATA || {};
const fallbackAiNews = window.MAXNOW_AI_NEWS_DATA || { items: [] };
const fallbackLast30 = window.MAXNOW_LAST30_DATA || {};
const fallbackWikiTodo = window.MAXNOW_WIKI_TODO_DATA || { tasks: [] };

let dashboardData = fallbackData;
let aiNewsData = fallbackAiNews;
let last30Data = fallbackLast30;
let wikiTodoData = fallbackWikiTodo;
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
  updatedAt: "\u66f4\u65b0\u4e8e",
  noNote: "\u6682\u65e0\u8bf4\u660e\u3002",
  tokenTitle: "Token \u7528\u91cf",
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
    <span class="item-tag"></span>
    <p class="item-title"></p>
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
    <div class="ai-news-meta">
      <span class="item-tag"></span>
      <time></time>
    </div>
    <p class="item-title"></p>
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
  article.innerHTML = `
    <div>
      <p class="item-title"></p>
      <p class="item-copy"></p>
    </div>
    <span class="system-value"></span>
  `;
  article.querySelector(".item-title").textContent = item.name || item.key || "System";
  article.querySelector(".item-copy").textContent = item.note || "";
  article.querySelector(".system-value").textContent = item.value || "--";
  return article;
}

function getTone(value = "") {
  const text = String(value).toLowerCase();
  if (text.includes("token") || text.includes("data") || text.includes("github")) return "blue";
  if (text.includes("auto") || text.includes("openclaw") || text.includes("skill")) return "cyan";
  if (text.includes("server") || text.includes("deploy") || text.includes("\u90e8\u7f72")) return "orange";
  if (text.includes("ai") || text.includes("official") || text.includes("openai")) return "purple";
  if (text.includes("wait") || text.includes("pending") || text.includes("\u7b49")) return "gray";
  if (text.includes("done") || text.includes("online") || text.includes("\u6b63\u5e38")) return "green";
  return "blue";
}

function getSystemItem(key) {
  return dashboardData.system?.find((item) => item.key === key) || {};
}

function getTokenRange(key = activeTokenRange) {
  const ranges = dashboardData.tokenUsage?.ranges || [];
  return ranges.find((range) => range.key === key) || ranges[0] || {};
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
  clearAndFill(qs("#wiki-todo-list"), createWikiTodoItem, openTodos.slice(0, 6));

  if (!openTodos.length && !wikiTodoError) {
    setText("#wiki-todo-list .empty-state", copy.wikiTodoEmpty);
  }
}

function renderHome() {
  const mainlines = dashboardData.mainlines || dashboardData.projects || dashboardData.tasks || [];
  const actions = dashboardData.actions || dashboardData.tasks || [];
  const journal = dashboardData.journal || [];
  const feeds = dashboardData.feeds || [];
  const aiItems = (aiNewsData.items || []).slice(0, 3);
  const token7d = getTokenRange("7d");
  const token24h = getTokenRange("24h");
  const token30d = getTokenRange("30d");
  const today = dashboardData.today || {};

  setText("#today-mode", today.modeLabel || "\u4eca\u65e5\u72b6\u6001");
  setText("#daily-brief", today.summary || dashboardData.brief || copy.waitBrief);
  setText("#today-energy", `${copy.energy} ${today.energy || "--"}`);
  setText("#today-focus", `${copy.focus} ${today.focus || "--"}`);
  setText("#today-updated", today.updatedAt ? `${copy.updatedAtShort} ${today.updatedAt}` : "\u5f85\u786e\u8ba4");
  setText("#operator-status", `OpenClaw ${dashboardData.automation?.status || copy.waiting}`);
  setText("#automation-summary", dashboardData.automation?.summary || copy.syncWaiting);
  setText("#feed-source", dashboardData.feedSource || "OpenClaw");
  setText("#journal-source", dashboardData.journalSource || copy.statusSnapshot);
  setText("#ai-news-source", aiNewsData.sourceSummary || "OpenClaw AI Daily");
  setText("#last30-source", last30Data.sourceSummary || last30Data.updatedAt || copy.syncWaiting);

  setText("#metric-mainlines", String(mainlines.length));
  setText("#metric-mainlines-note", `${mainlines.length} ${copy.taskCount}`);
  setText("#metric-actions", String(actions.length));
  setText("#metric-actions-note", `${actions.length} ${copy.taskCount}`);
  setText("#metric-token-total", formatToken(token7d.total));
  setText("#metric-token-note", `${copy.hour24} ${formatToken(token24h.total)}`);
  setText("#metric-automation", dashboardData.automation?.status || "--");
  setText("#metric-automation-note", dashboardData.automation?.lastRun || copy.sync);
  setText("#mini-token-24h", formatToken(token24h.total));
  setText("#mini-token-30d", formatToken(token30d.total));
  setText("#sidebar-token-total", formatToken(token7d.total));

  clearAndFill(qs("#mainline-list"), createTask, mainlines);
  clearAndFill(qs("#action-list"), createTask, actions);
  clearAndFill(qs("#journal-list"), createFeed, journal);
  clearAndFill(qs("#ai-news-list"), createAiNewsItem, aiItems);
  clearAndFill(qs("#feed-list"), createFeed, feeds);
  clearAndFill(qs("#timeline"), createTimelineItem, dashboardData.timeline || []);
  clearAndFill(qs("#system-list"), createSystemItem, dashboardData.system || []);
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
  const usage = dashboardData.tokenUsage || {};
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
  setText("#token-cost", Number.isFinite(range.cost) ? `$${range.cost.toFixed(2)}` : "--");
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
  const max = Math.max(...(dashboardData.tokenUsage?.daily || []).map((item) => item.total || 0), 1);
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
  const [dashboard, aiNews, last30, wikiTodo] = await Promise.all([
    readJson(DATA_URL, window.MAXNOW_DASHBOARD_DATA || fallbackData),
    readJson(AI_NEWS_URL, window.MAXNOW_AI_NEWS_DATA || fallbackAiNews),
    readJson(LAST30_URL, window.MAXNOW_LAST30_DATA || fallbackLast30),
    readWikiTodo(),
  ]);

  dashboardData = dashboard;
  aiNewsData = aiNews;
  last30Data = last30;
  wikiTodoData = wikiTodo;
  renderAll();
}

function setView(view) {
  const nextView = view === "tokens" ? "tokens" : "home";
  qsa("[data-view-panel]").forEach((panel) => {
    panel.classList.toggle("is-active", panel.dataset.viewPanel === nextView);
  });
  qsa("[data-view]").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.view === nextView);
  });
  if (viewTitle) viewTitle.textContent = nextView === "tokens" ? copy.tokenTitle : copy.today;
  if (location.hash !== `#${nextView}`) location.hash = nextView;
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
}

qsa("[data-view]").forEach((button) => {
  button.addEventListener("click", () => setView(button.dataset.view));
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

updateClock();
setInterval(updateClock, 30000);
loadData().then(() => setView(location.hash.replace("#", "")));
