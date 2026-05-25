const DATA_URL = "./data/dashboard.json";
const fallbackData = window.MAXNOW_DASHBOARD_DATA || {};

let dashboardData = fallbackData;
let activeTokenRange = "7d";

const qs = (selector) => document.querySelector(selector);
const qsa = (selector) => [...document.querySelectorAll(selector)];

const emptyTemplate = qs("#empty-template");
const refreshButton = qs("#refresh-button");
const viewTitle = qs("#view-title");

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
  article.innerHTML = `
    <span class="task-dot" aria-hidden="true"></span>
    <div>
      <p class="item-title"></p>
      <p class="item-copy"></p>
    </div>
    <span class="item-tag"></span>
  `;
  article.querySelector(".item-title").textContent = task.title || "未命名事项";
  article.querySelector(".item-copy").textContent = task.note || "";
  article.querySelector(".item-tag").textContent = task.label || "事项";
  return article;
}

function createFeed(feed) {
  const article = document.createElement("article");
  article.className = "feed-item";
  article.innerHTML = `
    <span class="item-tag"></span>
    <p class="item-title"></p>
    <p class="item-copy"></p>
  `;
  article.querySelector(".item-tag").textContent = feed.source || "Note";
  article.querySelector(".item-title").textContent = feed.title || "未命名信息";
  article.querySelector(".item-copy").textContent = feed.summary || "";

  if (feed.url) {
    const link = document.createElement("a");
    link.href = feed.url;
    link.target = "_blank";
    link.rel = "noreferrer";
    link.textContent = "打开";
    article.appendChild(link);
  }

  return article;
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
  li.querySelector(".item-title").textContent = item.title || "未命名时间点";
  li.querySelector(".item-copy").textContent = item.note || "";
  return li;
}

function getSystemItem(key) {
  return dashboardData.system?.find((item) => item.key === key) || {};
}

function getTokenRange(key = activeTokenRange) {
  const ranges = dashboardData.tokenUsage?.ranges || [];
  return ranges.find((range) => range.key === key) || ranges[0] || {};
}

function renderHome() {
  const tasks = dashboardData.tasks || [];
  const feeds = dashboardData.feeds || [];
  const server = getSystemItem("server");
  const token7d = getTokenRange("7d");
  const token24h = getTokenRange("24h");
  const token30d = getTokenRange("30d");

  setText("#daily-brief", dashboardData.brief || "等待 OpenClaw 写入今天的摘要。");
  setText("#operator-status", `OpenClaw ${dashboardData.automation?.status || "等待"}`);
  setText("#automation-summary", dashboardData.automation?.summary || "等待数据同步");
  setText("#feed-source", dashboardData.feedSource || "OpenClaw");

  setText("#metric-tasks", String(tasks.length));
  setText("#metric-tasks-note", `${tasks.length} 条事项`);
  setText("#metric-server", server.value || "--");
  setText("#metric-server-note", server.note || "等待检测");
  setText("#metric-token-total", formatToken(token7d.total));
  setText("#metric-token-note", `24小时 ${formatToken(token24h.total)}`);
  setText("#metric-automation", dashboardData.automation?.status || "--");
  setText("#metric-automation-note", dashboardData.automation?.lastRun || "等待同步");
  setText("#mini-token-24h", formatToken(token24h.total));
  setText("#mini-token-30d", formatToken(token30d.total));
  setText("#sidebar-token-total", formatToken(token7d.total));

  clearAndFill(qs("#task-list"), createTask, tasks);
  clearAndFill(qs("#feed-list"), createFeed, feeds);
  clearAndFill(qs("#timeline"), createTimelineItem, dashboardData.timeline || []);
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

  setText("#token-updated", usage.updatedAt ? `更新于 ${usage.updatedAt}` : "等待同步");
  setText("#token-total", formatToken(range.total));
  setText("#token-input", formatToken(range.input));
  setText("#token-output", formatToken(range.output));
  setText("#token-cost", Number.isFinite(range.cost) ? `$${range.cost.toFixed(2)}` : "--");
  setText("#token-note", range.note || "暂无说明。");

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

async function loadData() {
  try {
    const response = await fetch(`${DATA_URL}?t=${Date.now()}`, { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    dashboardData = await response.json();
  } catch (error) {
    dashboardData = window.MAXNOW_DASHBOARD_DATA || fallbackData;
  }

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
  if (viewTitle) viewTitle.textContent = nextView === "tokens" ? "Token 用量" : "今天";
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
