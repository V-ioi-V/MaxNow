const DATA_URL = "./data/dashboard.json";
const emptyTemplate = document.querySelector("#empty-template");

const fallbackData = {
  brief: "OpenClaw 暂时还没有生成今日摘要。页面已使用本地默认数据保持可用。",
  automation: {
    status: "待同步",
    summary: "把 OpenClaw 的输出写入 data/dashboard.json 后，这里会自动更新。",
    lastRun: "--",
  },
  tasks: [],
  timeline: [],
  feeds: [],
  projects: [],
  system: [],
};

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
    item.append(createElement("span", "item-tag", task.label || "Focus"));
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

function updateMetrics(data) {
  const pendingTasks = data.tasks.filter((task) => task.status !== "done").length;
  const serverMetric = data.system.find((item) => item.key === "server") || data.system[0];

  setText("#metric-tasks", pendingTasks);
  setText("#metric-tasks-note", `${data.tasks.length} 条事项已加载`);
  setText("#metric-feeds", data.feeds.length);
  setText("#metric-feeds-note", "来自 OpenClaw 汇总");
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
  updateMetrics(data);
  renderTasks(data.tasks || []);
  renderTimeline(data.timeline || []);
  renderFeeds(data.feeds || []);
  renderProjects(data.projects || []);
  renderSystem(data.system || []);
}

async function loadDashboard() {
  try {
    const response = await fetch(`${DATA_URL}?t=${Date.now()}`, { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    renderDashboard({ ...fallbackData, ...data });
  } catch (error) {
    renderDashboard(fallbackData);
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

document.querySelector('[data-action="refresh"]')?.addEventListener("click", loadDashboard);

updateClock();
loadDashboard();
window.setInterval(updateClock, 30_000);
