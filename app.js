const DATA_URL = "./data/dashboard.json";
const emptyTemplate = document.querySelector("#empty-template");
const refreshButton = document.querySelector("#refresh-button");
const viewTitle = document.querySelector("#view-title");

const fallbackData = {
  brief: "OpenClaw 还没有写入今天的摘要。",
  feedSource: "OpenClaw",
  automation: {
    status: "待同步",
    summary: "等待数据同步",
    lastRun: "--",
  },
  tasks: [],
  timeline: [],
  feeds: [],
  projects: [],
  system: [],
  tokenUsage: {
    updatedAt: "--",
    ranges: [],
    models: [],
    daily: [],
  },
};

let dashboardData = fallbackData;
let activeTokenRange = "7d";

function formatNumber(value) {
  return new Intl.NumberFormat("zh-CN").format(Math.round(Number(value) || 0));
}

function compactNumber(value) {
  const number = Number(value) || 0;
  if (number >= 1_000_000) return `${(number / 1_000_000).toFixed(1)}M`;
  if (number >= 10_000) return `${Math.round(number / 1000)}K`;
  return formatNumber(number);
}

function formatCost(value) {
  const number = Number(value) || 0;
  if (!number) return "--";
  return `$${number.toFixed(2)}`;
}

function setText(selector, value) {
  const node = document.querySelector(selector);
  if (node) node.textContent = value;
}

function renderEmpty(container) {
  container.append(emptyTemplate.content.cloneNode(true));
}

function createElement(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text) node.textContent = text;
  return node;
}

function setView(view) {
  const nextView = view === "tokens" ? "tokens" : "home";
  document.querySelectorAll("[data-view-panel]").forEach((panel) => {
    panel.classList.toggle("is-active", panel.dataset.viewPanel === nextView);
  });
  document.querySelectorAll("[data-view]").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.view === nextView);
  });
  if (viewTitle) viewTitle.textContent = nextView === "tokens" ? "Token 用量" : "今天";
  window.location.hash = nextView === "tokens" ? "tokens" : "home";
}

function renderTasks(tasks) {
  const container = document.querySelector("#task-list");
  container.replaceChildren();
  if (!tasks.length) return renderEmpty(container);

  tasks.forEach((task) => {
    const item = createElement("article", "task-item");
    item.dataset.status = task.status || "active";
    item.append(createElement("span", "task-dot"));

    const body = createElement("div");
    body.append(createElement("h3", "item-title", task.title));
    body.append(createElement("p", "item-copy", task.note));
    item.append(body);
    item.append(createElement("span", "item-tag", task.label || "事项"));
    container.append(item);
  });
}

function renderTimeline(items) {
  const container = document.querySelector("#timeline");
  container.replaceChildren();
  if (!items.length) return renderEmpty(container);

  items.forEach((entry) => {
    const item = createElement("li");
    item.append(createElement("time", "", entry.time));

    const body = createElement("div");
    body.append(createElement("h3", "item-title", entry.title));
    body.append(createElement("p", "item-meta", entry.note));
    item.append(body);
    container.append(item);
  });
}

function renderFeeds(feeds) {
  const container = document.querySelector("#feed-list");
  container.replaceChildren();
  if (!feeds.length) return renderEmpty(container);

  feeds.forEach((feed) => {
    const item = createElement("article", "feed-item");
    item.append(createElement("span", "item-tag", feed.source));
    item.append(createElement("h3", "item-title", feed.title));
    item.append(createElement("p", "item-copy", feed.summary));

    if (feed.url) {
      const link = createElement("a", "", "打开");
      link.href = feed.url;
      link.target = "_blank";
      link.rel = "noreferrer";
      item.append(link);
    }

    container.append(item);
  });
}

function renderProjects(projects) {
  const container = document.querySelector("#project-list");
  container.replaceChildren();
  if (!projects.length) return renderEmpty(container);

  projects.forEach((project) => {
    const item = createElement("article", "project-item");
    item.append(createElement("h3", "item-title", project.name));
    item.append(createElement("p", "item-copy", project.note));

    const progress = createElement("div", "project-progress");
    const bar = createElement("span");
    bar.style.width = `${Math.max(0, Math.min(100, project.progress || 0))}%`;
    progress.append(bar);
    item.append(progress);
    item.append(createElement("p", "item-meta", `${project.progress || 0}% · ${project.status}`));
    container.append(item);
  });
}

function renderSystem(metrics) {
  const container = document.querySelector("#system-list");
  container.replaceChildren();
  if (!metrics.length) return renderEmpty(container);

  metrics.forEach((metric) => {
    const item = createElement("article", "system-item");
    const body = createElement("div");
    body.append(createElement("h3", "item-title", metric.name));
    body.append(createElement("p", "item-meta", metric.note));
    item.append(body);
    item.append(createElement("span", "system-value", metric.value));
    container.append(item);
  });
}

function renderTokenRanges(usage) {
  const container = document.querySelector("#token-ranges");
  container.replaceChildren();

  const ranges = usage.ranges || [];
  if (!ranges.some((range) => range.key === activeTokenRange)) {
    activeTokenRange = ranges[0]?.key || "7d";
  }

  ranges.forEach((range) => {
    const button = createElement("button", "range-tab", range.label);
    button.type = "button";
    button.dataset.range = range.key;
    button.setAttribute("role", "tab");
    button.setAttribute("aria-selected", String(range.key === activeTokenRange));
    button.classList.toggle("is-active", range.key === activeTokenRange);
    button.addEventListener("click", () => {
      activeTokenRange = range.key;
      renderTokenUsage(dashboardData.tokenUsage || fallbackData.tokenUsage);
    });
    container.append(button);
  });
}

function renderTokenModels(models) {
  const container = document.querySelector("#token-models");
  container.replaceChildren();
  if (!models.length) return renderEmpty(container);

  models.forEach((model) => {
    const item = createElement("article", "model-item");
    const top = createElement("div", "model-row");
    top.append(createElement("strong", "", model.name));
    top.append(createElement("span", "", `${model.share || 0}%`));
    item.append(top);

    const meter = createElement("div", "model-meter");
    const fill = createElement("span");
    fill.style.width = `${Math.max(0, Math.min(100, model.share || 0))}%`;
    meter.append(fill);
    item.append(meter);
    item.append(createElement("p", "item-meta", `${formatNumber(model.total)} tokens`));
    container.append(item);
  });
}

function renderTokenBars(days) {
  const container = document.querySelector("#token-bars");
  container.replaceChildren();
  if (!days.length) return renderEmpty(container);

  const max = Math.max(...days.map((day) => Number(day.total) || 0), 1);
  days.forEach((day) => {
    const item = createElement("article", "token-bar");
    item.append(createElement("span", "", day.label || day.date));

    const track = createElement("div", "bar-track");
    const fill = createElement("span");
    fill.style.width = `${Math.max(4, ((Number(day.total) || 0) / max) * 100)}%`;
    track.append(fill);
    item.append(track);
    item.append(createElement("strong", "", formatNumber(day.total)));
    container.append(item);
  });
}

function getTokenRange(usage, key) {
  return (usage.ranges || []).find((range) => range.key === key);
}

function renderTokenUsage(usage) {
  const ranges = usage.ranges || [];
  const active = getTokenRange(usage, activeTokenRange) || ranges[0] || {};
  const hour = getTokenRange(usage, "1h") || {};
  const day = getTokenRange(usage, "24h") || {};
  const week = getTokenRange(usage, "7d") || active;
  const month = getTokenRange(usage, "30d") || {};

  setText("#sidebar-token-total", week.total ? compactNumber(week.total) : "--");
  setText("#metric-token-total", week.total ? compactNumber(week.total) : "--");
  setText("#metric-token-note", day.total ? `24小时 ${compactNumber(day.total)}` : "等待同步");
  setText("#mini-token-24h", day.total ? compactNumber(day.total) : "--");
  setText("#mini-token-30d", month.total ? compactNumber(month.total) : "--");
  setText("#token-updated", usage.updatedAt ? `更新于 ${usage.updatedAt}` : "等待同步");
  setText("#token-total", active.total ? formatNumber(active.total) : "--");
  setText("#token-input", active.input ? formatNumber(active.input) : "--");
  setText("#token-output", active.output ? formatNumber(active.output) : "--");
  setText("#token-cost", formatCost(active.cost));
  setText("#token-note", active.note || "暂无说明。");

  renderTokenRanges(usage);
  renderTokenModels(usage.models || []);
  renderTokenBars(usage.daily || []);
}

function updateMetrics(data) {
  const tasks = data.tasks || [];
  const feeds = data.feeds || [];
  const system = data.system || [];
  const serverMetric = system.find((item) => item.key === "server") || system[0];
  const pendingTasks = tasks.filter((task) => task.status !== "done").length;

  setText("#metric-tasks", pendingTasks);
  setText("#metric-tasks-note", `${tasks.length} 条事项`);
  setText("#metric-feeds", feeds.length);
  setText("#metric-feeds-note", data.feedSource || "OpenClaw");
  setText("#metric-server", serverMetric?.value || "--");
  setText("#metric-server-note", serverMetric?.note || "等待检测");
  setText("#metric-automation", data.automation.status);
  setText("#metric-automation-note", data.automation.lastRun);
  setText("#automation-summary", data.automation.summary);
  setText("#operator-status", `OpenClaw ${data.automation.status}`);
  setText("#daily-brief", data.brief);
  setText("#feed-source", data.feedSource || "OpenClaw");
}

function renderDashboard(data) {
  dashboardData = data;
  updateMetrics(data);
  renderTasks(data.tasks || []);
  renderTimeline(data.timeline || []);
  renderFeeds(data.feeds || []);
  renderProjects(data.projects || []);
  renderSystem(data.system || []);
  renderTokenUsage(data.tokenUsage || fallbackData.tokenUsage);
}

function setRefreshState(state) {
  if (!refreshButton) return;
  refreshButton.dataset.state = state;
  refreshButton.disabled = state === "loading";

  if (state === "loading") refreshButton.textContent = "...";
  if (state === "success") refreshButton.textContent = "✓";
  if (state === "error") refreshButton.textContent = "!";

  if (state !== "idle") {
    window.setTimeout(() => {
      refreshButton.dataset.state = "idle";
      refreshButton.disabled = false;
      refreshButton.textContent = "↻";
    }, 900);
  }
}

async function loadDashboard({ showState = false } = {}) {
  if (showState) setRefreshState("loading");

  try {
    const response = await fetch(`${DATA_URL}?t=${Date.now()}`, { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    renderDashboard({
      ...fallbackData,
      ...data,
      automation: { ...fallbackData.automation, ...data.automation },
      tokenUsage: { ...fallbackData.tokenUsage, ...data.tokenUsage },
    });
    if (showState) setRefreshState("success");
  } catch (error) {
    renderDashboard(fallbackData);
    if (showState) setRefreshState("error");
    console.warn("Failed to load dashboard data:", error);
  }
}

function updateClock() {
  const now = new Date();
  setText(
    "#today-label",
    new Intl.DateTimeFormat("zh-CN", {
      month: "long",
      day: "numeric",
      weekday: "long",
    }).format(now),
  );
  setText(
    "#clock-label",
    new Intl.DateTimeFormat("zh-CN", {
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    }).format(now),
  );
}

document.querySelectorAll("[data-view]").forEach((button) => {
  button.addEventListener("click", () => setView(button.dataset.view));
});
refreshButton?.addEventListener("click", () => loadDashboard({ showState: true }));

updateClock();
loadDashboard();
setView(window.location.hash === "#tokens" ? "tokens" : "home");
window.setInterval(updateClock, 30_000);
