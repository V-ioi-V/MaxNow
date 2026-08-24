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
const BALLET_URL = "./data/ballet.json";
const BALLET_SESSION_URL = "./data/ballet-session.json";
const BALLET_BOOKING_FAST_URL = "./data/ballet-booking-fast.json";
const BALLET_WEEK_TEMPLATE_URL = "./assets/ballet-week-cover/template.json";
const BALLET_WEEK_FALLBACK_CONFIG = {
  templateVersion: "v1",
  briefTemplateVersion: "v3",
  briefTemplateFile: "brief-template-v1.webp",
  briefDataRefreshDelayMinutes: 10,
  briefGenerateDelayMinutes: 20,
  timezone: "Asia/Shanghai",
  anchorMonday: "2026-07-27",
  anchorWeek: 2,
};
const LEAFLET_CSS_URL = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css";
const LEAFLET_JS_URL = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js";
const DATA_AUTO_REFRESH_INTERVAL_MS = 5 * 60 * 1000;
const BALLET_WEEK_IMAGE_LOAD_TIMEOUT_MS = 20 * 1000;
const BALLET_SESSION_PUBLISH_STALE_MS = 15 * 60 * 1000;
const BALLET_SESSION_NEXT_RUN_INTERVAL_MINUTES = 20;
const DATA_CACHE_PREFIX = "maxnow:last-good:v1:";

const DATA_SOURCE_OPTIONS = {
  weather: {
    label: "天气",
    staleAfterHours: 72,
    updatedAt: (data) => data.weather?.updatedAt,
    hasData: (data) => Boolean(data.weather?.condition),
  },
  last30: {
    label: "Last-30",
    staleAfterHours: 168,
    updatedAt: (data) => data.updatedAt,
    hasData: (data) => hasEntries(data.today?.items) || hasEntries(data.week?.items) || hasEntries(data.last30?.mainlines),
  },
  wiki: {
    label: "Wiki",
    staleAfterHours: 72,
    updatedAt: (data) => data.synced_at || data.updated_at,
    hasData: (data) => Boolean((data.tasks || []).length),
  },
  dounai: {
    label: "豆奶",
    staleAfterHours: 36,
    updatedAt: (data) => data.updatedAt || data.account?.synced_at,
    hasData: (data) => Boolean(data.today || (data.records || []).length || data.account),
  },
  market: {
    label: "市场",
    staleAfterHours: 72,
    updatedAt: (data) => data.updatedAt,
    hasData: (data) => Boolean((data.indices || []).length),
  },
  version: {
    label: "版本",
    staleAfterHours: 72,
    updatedAt: (data) => data.updatedAt,
    hasData: (data) => Boolean(data.version),
  },
  roadmap: {
    label: "Roadmap",
    staleAfterHours: 168,
    updatedAt: (data) => data.generatedAt,
    hasData: (data) => Boolean((data.mainlines || []).length || (data.actions || []).length),
  },
  token: {
    label: "Token",
    staleAfterHours: 72,
    updatedAt: (data) => data.updatedAt,
    hasData: (data) => Boolean((data.days || []).length),
  },
  ricky: {
    label: "同行记",
    staleAfterHours: 72,
    updatedAt: (data) => data.synced_at || data.updated_at,
    hasData: (data) => Boolean((data.places || []).length || (data.records || []).length),
  },
  life: {
    label: "生活",
    staleAfterHours: 72,
    updatedAt: (data) => data.synced_at || data.updated_at,
    hasData: (data) => Boolean((data.sections || []).length),
  },
  ballet: {
    label: "芭蕾",
    staleAfterHours: 36,
    updatedAt: (data) => data.dataAsOf || data.sync?.lastSuccessAt,
    hasData: (data) =>
      Boolean(
        Number(data.summary?.classes ?? data.summary?.totalClasses ?? 0) ||
          (data.records || []).length ||
          (Array.isArray(data.upcoming) ? data.upcoming.length : (data.upcoming?.records || []).length) ||
          (data.timetable?.days || []).some((day) => (day.records || []).length) ||
          data.nextClass ||
          data.summary?.nextClass,
      ),
  },
};

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
const fallbackBallet = window.MAXNOW_BALLET_DATA || {
  sync: { cacheState: "unavailable", lastAttemptStatus: "waiting" },
  summary: {},
  aggregates: {},
  records: [],
  upcoming: { records: [] },
  timetable: { days: [] },
  week: {},
  membership: { cards: [] },
};
const fallbackBalletSession = window.MAXNOW_BALLET_SESSION_DATA || {
  schemaVersion: 1,
  timezone: "Asia/Shanghai",
  status: "unknown",
  refreshIntervalMinutes: 25,
};
const fallbackBalletBookingFast =
  window.MAXNOW_BALLET_BOOKING_FAST_DATA || {
    schemaVersion: 1,
    enabled: false,
    planMode: "weekly-rules",
    coursePriorityOrder: ["芭蕾 L1", "芭蕾 L1.5", "软开 / 软开课"],
    priorityOrder: ["周六", "周一", "周二", "周三", "周四", "周五"],
    prioritySummary: "芭蕾 L1 > 芭蕾 L1.5 > 软开 / 软开课；每类按周六 > 周一至周五李俊（老师空白按李俊）> 周一至周五其他老师；工作日仅 18:40 后、周六全天；软开严格排除软开专项 / 软开-胯",
    targets: [],
    lastStatus: "waiting",
  };

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
let balletData = fallbackBallet;
let balletSessionData = fallbackBalletSession;
let balletBookingFastData = fallbackBalletBookingFast;
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
let balletWeekConfigPromise = null;
let balletWeekCoverCache = null;
let balletWeekCoverPromise = null;
let balletWeekBriefCache = null;
let balletWeekBriefPromise = null;
let balletWeekWarmupHandle = 0;
let balletWeekBriefScheduleHandle = 0;
let balletWeekActiveSlide = "cover";
let balletWeekCarouselFrame = 0;
let balletPlanWeekOffset = 0;
const browserDataHealth = new Map();

const lifeFoodTones = ["cyan", "orange", "green", "purple", "blue"];
let activeBalletPeriod = "all";
let activeBalletMetric = "classes";

const qs = (selector) => document.querySelector(selector);
const qsa = (selector) => [...document.querySelectorAll(selector)];

const emptyTemplate = qs("#empty-template");
const refreshButton = qs("#refresh-button");
const viewTitle = qs("#view-title");

function dateKeyInTimeZone(date = new Date(), timeZone = "Asia/Shanghai") {
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).formatToParts(date);
  const value = Object.fromEntries(parts.map((part) => [part.type, part.value]));
  return `${value.year}-${value.month}-${value.day}`;
}

function utcDayFromDateKey(dateKey = "") {
  const match = String(dateKey).match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (!match) return Number.NaN;
  return Date.UTC(Number(match[1]), Number(match[2]) - 1, Number(match[3]));
}

function dateKeyFromUtcDay(utcDay) {
  const date = new Date(utcDay);
  return `${date.getUTCFullYear()}-${String(date.getUTCMonth() + 1).padStart(2, "0")}-${String(date.getUTCDate()).padStart(2, "0")}`;
}

function formatBalletWeekDate(dateKey = "") {
  const match = String(dateKey).match(/^\d{4}-(\d{2})-(\d{2})$/);
  return match ? `${Number(match[1])}月${Number(match[2])}日` : dateKey;
}

function getBalletWeekInfo(config = BALLET_WEEK_FALLBACK_CONFIG, date = new Date()) {
  const timezone = config.timezone || BALLET_WEEK_FALLBACK_CONFIG.timezone;
  const currentUtcDay = utcDayFromDateKey(dateKeyInTimeZone(date, timezone));
  const anchorUtcDay = utcDayFromDateKey(config.anchorMonday || BALLET_WEEK_FALLBACK_CONFIG.anchorMonday);
  const weekOffset = Math.floor((currentUtcDay - anchorUtcDay) / (7 * 86400000));
  const week = Math.max(1, Number(config.anchorWeek || BALLET_WEEK_FALLBACK_CONFIG.anchorWeek) + weekOffset);
  const mondayUtcDay = anchorUtcDay + weekOffset * 7 * 86400000;
  return {
    week,
    monday: dateKeyFromUtcDay(mondayUtcDay),
    sunday: dateKeyFromUtcDay(mondayUtcDay + 6 * 86400000),
  };
}

function timePartsInTimeZone(date = new Date(), timeZone = "Asia/Shanghai") {
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hourCycle: "h23",
  }).formatToParts(date);
  const values = Object.fromEntries(parts.map((part) => [part.type, part.value]));
  return {
    dateKey: `${values.year}-${values.month}-${values.day}`,
    hour: Number(values.hour),
    minute: Number(values.minute),
  };
}

function getBalletBriefCycles(config = BALLET_WEEK_FALLBACK_CONFIG) {
  const published = balletData.weeklyBrief?.cycles;
  if (Array.isArray(published) && published.length) return published;
  const refreshDelay = Number(config.briefDataRefreshDelayMinutes ?? 10);
  const generateDelay = Number(config.briefGenerateDelayMinutes ?? 20);
  const ends = new Map();
  const candidates = [
    ...(Array.isArray(balletData.records) ? balletData.records : []),
    ...(Array.isArray(balletData.upcoming?.records)
      ? balletData.upcoming.records.filter((record) => record.bookingStatus === "booked")
      : []),
  ];
  candidates.forEach((record) => {
    const dateKey = balletRecordDate(record);
    const endTime = balletEndTime(record);
    if (!/^\d{4}-\d{2}-\d{2}$/.test(dateKey) || !/^\d{2}:\d{2}$/.test(endTime)) return;
    const day = utcDayFromDateKey(dateKey);
    const weekday = new Date(day).getUTCDay() || 7;
    const monday = dateKeyFromUtcDay(day - (weekday - 1) * 86400000);
    const endAt = `${dateKey}T${endTime}:00+08:00`;
    if (!ends.has(monday) || Date.parse(endAt) > Date.parse(ends.get(monday))) ends.set(monday, endAt);
  });
  return [...ends.entries()].sort(([left], [right]) => left.localeCompare(right)).map(([monday, lastCourseEndAt]) => ({
    weekStart: monday,
    weekEnd: dateKeyFromUtcDay(utcDayFromDateKey(monday) + 6 * 86400000),
    lastCourseEndAt,
    refreshAt: new Date(Date.parse(lastCourseEndAt) + refreshDelay * 60000).toISOString(),
    generateAt: new Date(Date.parse(lastCourseEndAt) + generateDelay * 60000).toISOString(),
  }));
}

function getBalletBriefCycleInfo(cycle, config = BALLET_WEEK_FALLBACK_CONFIG) {
  const anchor = getBalletWeekInfo(config, new Date(`${cycle.weekStart}T12:00:00+08:00`));
  return {
    week: anchor.week,
    monday: cycle.weekStart,
    sunday: cycle.weekEnd,
    lastCourseEndAt: cycle.lastCourseEndAt,
    refreshAt: cycle.refreshAt,
    generateAt: cycle.generateAt,
    cutoff: Date.parse(cycle.lastCourseEndAt),
  };
}

function getBalletWeeklyBriefInfo(config = BALLET_WEEK_FALLBACK_CONFIG, date = new Date()) {
  const cycles = getBalletBriefCycles(config).filter((cycle) => Date.parse(cycle.generateAt) <= date.getTime());
  if (cycles.length) return getBalletBriefCycleInfo(cycles.at(-1), config);
  const current = getBalletWeekInfo(config, date);
  return { ...current, lastCourseEndAt: null, refreshAt: null, generateAt: null, cutoff: Number.NEGATIVE_INFINITY };
}

function getCurrentBalletBriefCycle(config = BALLET_WEEK_FALLBACK_CONFIG, date = new Date()) {
  const dateKey = timePartsInTimeZone(date, config.timezone || "Asia/Shanghai").dateKey;
  const cycle = getBalletBriefCycles(config).find((item) => item.weekStart <= dateKey && dateKey <= item.weekEnd);
  return cycle ? getBalletBriefCycleInfo(cycle, config) : null;
}

function formatBalletBriefSchedule(isoValue) {
  const parsed = new Date(isoValue);
  if (!Number.isFinite(parsed.getTime())) return "最后一节后 20 分钟生成";
  const parts = new Intl.DateTimeFormat("zh-CN", {
    timeZone: "Asia/Shanghai",
    weekday: "short",
    hour: "2-digit",
    minute: "2-digit",
    hourCycle: "h23",
  }).formatToParts(parsed);
  const values = Object.fromEntries(parts.map((part) => [part.type, part.value]));
  return `${values.weekday} ${values.hour}:${values.minute} 生成`;
}

function formatBalletBriefDateRange(info = {}) {
  const format = (dateKey) => {
    const match = String(dateKey || "").match(/^\d{4}-(\d{2})-(\d{2})$/);
    return match ? `${match[1]}.${match[2]}` : "";
  };
  return `${format(info.monday)}–${format(info.sunday)}`;
}

function updateBalletWeekDialogRange(config = BALLET_WEEK_FALLBACK_CONFIG) {
  const coverInfo = getBalletWeekInfo(config);
  const briefInfo = getBalletWeeklyBriefInfo(config);
  const range = balletWeekActiveSlide === "brief"
    ? `周简报 week ${briefInfo.week} · ${formatBalletWeekDate(briefInfo.monday)}–${formatBalletWeekDate(briefInfo.sunday)}`
    : `${formatBalletWeekDate(coverInfo.monday)}–${formatBalletWeekDate(coverInfo.sunday)} · 周一至周日`;
  setText("#ballet-week-dialog-range", range);
}

function updateBalletWeekTrigger(config = BALLET_WEEK_FALLBACK_CONFIG) {
  const info = getBalletWeekInfo(config);
  const briefInfo = getBalletWeeklyBriefInfo(config);
  const currentCycle = getCurrentBalletBriefCycle(config);
  if (balletWeekCoverCache && balletWeekCoverCache.week !== info.week) balletWeekCoverCache = null;
  if (balletWeekBriefCache && balletWeekBriefCache.week !== briefInfo.week) balletWeekBriefCache = null;
  setText("#ballet-week-trigger-number", info.week);
  setText("#ballet-week-dialog-number", info.week);
  setText("#ballet-week-tab-number", info.week);
  setText(
    "#ballet-week-brief-refresh",
    currentCycle
      ? `周简报 week ${currentCycle.week} · ${formatBalletBriefSchedule(currentCycle.generateAt)}`
      : "周简报 · 每周期最后一节后 20 分钟生成",
  );
  updateBalletWeekDialogRange(config);
  const trigger = qs("#ballet-week-trigger");
  if (trigger) trigger.setAttribute("aria-label", `打开芭蕾周记录 week ${info.week} 封面和周简报`);
  return info;
}

async function loadBalletWeekConfig({ force = false } = {}) {
  if (force) balletWeekConfigPromise = null;
  if (balletWeekConfigPromise) return balletWeekConfigPromise;
  balletWeekConfigPromise = fetch(BALLET_WEEK_TEMPLATE_URL, { cache: "no-cache" })
    .then((response) => {
      if (!response.ok) throw new Error(`模板配置请求失败 (${response.status})`);
      return response.json();
    })
    .then((config) => {
      if (
        !config.templateFile
        || !config.briefTemplateFile
        || !config.digitsManifest
        || !Number(config.width)
        || !Number(config.height)
      ) {
        throw new Error("模板配置不完整");
      }
      updateBalletWeekTrigger(config);
      return config;
    })
    .catch((error) => {
      balletWeekConfigPromise = null;
      throw error;
    });
  return balletWeekConfigPromise;
}

function loadBalletWeekImage(url) {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.decoding = "async";
    const timeout = window.setTimeout(() => {
      image.src = "";
      reject(new Error(`图片素材加载超时：${url.pathname.split("/").pop()}`));
    }, BALLET_WEEK_IMAGE_LOAD_TIMEOUT_MS);
    image.onload = () => {
      window.clearTimeout(timeout);
      resolve(image);
    };
    image.onerror = () => {
      window.clearTimeout(timeout);
      reject(new Error(`图片素材加载失败：${url.pathname.split("/").pop()}`));
    };
    image.src = url.href;
  });
}

function canvasToPngBlob(canvas) {
  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (blob) resolve(blob);
      else reject(new Error("PNG 生成失败"));
    }, "image/png");
  });
}

function setBalletWeekActionsDisabled(disabled) {
  [qs("#ballet-week-copy"), qs("#ballet-week-download")].forEach((button) => {
    if (button) button.disabled = disabled;
  });
}

function setBalletWeekStatus(type, message) {
  const status = qs("#ballet-week-status");
  if (status && balletWeekActiveSlide === type) status.textContent = message;
}

async function buildBalletWeekCover() {
  const canvas = qs("#ballet-week-canvas");
  if (!canvas) return null;
  setBalletWeekActionsDisabled(true);
  setBalletWeekStatus("cover", "正在加载本周封面素材…");

  try {
    const config = await loadBalletWeekConfig();
    const info = updateBalletWeekTrigger(config);
    const cacheKey = `${config.templateVersion}:${info.week}`;
    if (balletWeekCoverCache?.key === cacheKey) {
      setBalletWeekStatus("cover", "已从本页缓存读取 · 1280 × 1710 PNG");
      setBalletWeekActionsDisabled(false);
      return balletWeekCoverCache;
    }

    const configUrl = new URL(BALLET_WEEK_TEMPLATE_URL, window.location.href);
    const templateUrl = new URL(config.templateFile, configUrl);
    const digitsManifestUrl = new URL(config.digitsManifest, configUrl);
    const [templateImage, digitsResponse] = await Promise.all([
      loadBalletWeekImage(templateUrl),
      fetch(digitsManifestUrl, { cache: "force-cache" }),
    ]);
    if (!digitsResponse.ok) throw new Error(`手绘数字配置请求失败 (${digitsResponse.status})`);
    const digitsManifest = await digitsResponse.json();
    const digitText = String(info.week);
    const digitImages = await Promise.all(
      [...digitText].map((digit) => {
        const asset = digitsManifest.digits?.[digit];
        if (!asset?.file) throw new Error(`缺少手绘数字 ${digit}`);
        return loadBalletWeekImage(new URL(asset.file, digitsManifestUrl));
      }),
    );

    canvas.width = Number(config.width);
    canvas.height = Number(config.height);
    const context = canvas.getContext("2d", { alpha: false });
    if (!context) throw new Error("浏览器不支持图片合成");
    context.clearRect(0, 0, canvas.width, canvas.height);
    context.drawImage(templateImage, 0, 0, canvas.width, canvas.height);

    const scale = Number(config.digitScale || 0.4);
    const gap = Number(config.digitGap || 0);
    const widths = digitImages.map((image) => image.naturalWidth * scale);
    const totalWidth = widths.reduce((sum, width) => sum + width, 0) + Math.max(0, digitImages.length - 1) * gap;
    let x = Number(config.numberCenterX) - totalWidth / 2;
    const y = Number(config.numberBaselineY) - Number(digitsManifest.baseline) * scale;
    digitImages.forEach((image, index) => {
      context.drawImage(image, x, y, image.naturalWidth * scale, image.naturalHeight * scale);
      x += widths[index] + gap;
    });

    await new Promise((resolve) => requestAnimationFrame(resolve));
    const blob = await canvasToPngBlob(canvas);
    balletWeekCoverCache = {
      key: cacheKey,
      blob,
      week: info.week,
      filename: `芭蕾周记录-week-${info.week}.png`,
    };
    setBalletWeekStatus("cover", "已生成 · 1280 × 1710 PNG · 本周结果仅在当前页面缓存");
    setBalletWeekActionsDisabled(false);
    return balletWeekCoverCache;
  } catch (error) {
    balletWeekCoverCache = null;
    setBalletWeekStatus("cover", `生成失败：${error.message || error}`);
    setBalletWeekActionsDisabled(false);
    return null;
  }
}

function renderBalletWeekCover() {
  if (balletWeekCoverPromise) return balletWeekCoverPromise;
  balletWeekCoverPromise = buildBalletWeekCover().finally(() => {
    balletWeekCoverPromise = null;
  });
  return balletWeekCoverPromise;
}

function formatBalletBriefDuration(minutes = 0) {
  const safeMinutes = Math.max(0, Math.round(Number(minutes) || 0));
  const hours = Math.floor(safeMinutes / 60);
  return `${String(hours).padStart(2, "0")}:${String(safeMinutes % 60).padStart(2, "0")}`;
}

function drawBalletBriefText(context, value, x, y, maxWidth, fontSize, minFontSize = 32, options = {}) {
  const text = String(value || "暂无");
  let size = fontSize;
  const numeric = options.numeric === true;
  const fontFamily = numeric
    ? '"Segoe UI Variable Text", "Segoe UI", "Microsoft YaHei", sans-serif'
    : '"MaxNow Week Hand", "KaiTi", cursive';
  const fontWeight = 400;
  context.textAlign = "center";
  context.textBaseline = "alphabetic";
  context.fillStyle = "#6b202a";
  while (size > minFontSize) {
    context.font = `${fontWeight} ${size}px ${fontFamily}`;
    if (context.measureText(text).width <= maxWidth) break;
    size -= 2;
  }
  if (!numeric) {
    context.lineJoin = "round";
    context.lineWidth = Math.max(1, size * 0.018);
    context.strokeStyle = context.fillStyle;
    context.strokeText(text, x, y, maxWidth);
  }
  context.fillText(text, x, y, maxWidth);
}

async function buildBalletWeekBrief() {
  const canvas = qs("#ballet-week-brief-canvas");
  if (!canvas) return null;
  setBalletWeekActionsDisabled(true);
  setBalletWeekStatus("brief", "正在加载本周训练简报素材…");

  try {
    const config = await loadBalletWeekConfig();
    const summary = getBalletWeeklyBriefSummary(config);
    if (!summary.info.lastCourseEndAt) throw new Error("本周期还没有可结算课程");
    if (!summary.sourceReachedCutoff) throw new Error("等待本周期收尾刷新完成");
    const cacheKey = `${config.briefTemplateVersion}:${summary.info.week}:${summary.sourceAsOf}:${summary.completedRecords}`;
    if (balletWeekBriefCache?.key === cacheKey) {
      setBalletWeekStatus("brief", balletWeekBriefCache.statusMessage);
      setBalletWeekActionsDisabled(false);
      return balletWeekBriefCache;
    }

    const configUrl = new URL(BALLET_WEEK_TEMPLATE_URL, window.location.href);
    const templateUrl = new URL(config.briefTemplateFile, configUrl);
    const [templateImage] = await Promise.all([
      loadBalletWeekImage(templateUrl),
      document.fonts?.load?.('80px "MaxNow Week Hand"', "芭蕾周简报0123456789") || Promise.resolve(),
    ]);

    canvas.width = Number(config.width);
    canvas.height = Number(config.height);
    const context = canvas.getContext("2d", { alpha: false });
    if (!context) throw new Error("浏览器不支持图片合成");
    context.clearRect(0, 0, canvas.width, canvas.height);
    context.drawImage(templateImage, 0, 0, canvas.width, canvas.height);

    const columns = Array.isArray(config.briefColumnCenters) ? config.briefColumnCenters.map(Number) : [240, 632, 1030];
    const firstY = Number(config.briefFirstRowValueBaselineY || 846);
    const secondY = Number(config.briefSecondRowValueBaselineY || 1450);
    drawBalletBriefText(
      context,
      summary.info.week,
      Number(config.briefWeekNumberCenterX || 353),
      Number(config.briefWeekNumberBaselineY || 390),
      88,
      72,
      48,
      { numeric: true },
    );
    drawBalletBriefText(
      context,
      formatBalletBriefDateRange(summary.info),
      Number(config.briefDateCenterX || 704),
      Number(config.briefDateBaselineY || 377),
      440,
      38,
      28,
      { numeric: true },
    );
    drawBalletBriefText(context, String(summary.week.classes).padStart(2, "0"), columns[0], firstY, 250, 104, 72, { numeric: true });
    drawBalletBriefText(context, formatBalletBriefDuration(summary.week.minutes), columns[1], firstY, 300, 88, 58, { numeric: true });
    drawBalletBriefText(context, summary.week.favorite?.label || "暂无", columns[2], firstY, 300, 62, 38);
    drawBalletBriefText(context, String(summary.total.classes).padStart(2, "0"), columns[0], secondY, 250, 104, 72, { numeric: true });
    drawBalletBriefText(context, formatBalletBriefDuration(summary.total.minutes), columns[1], secondY, 300, 88, 58, { numeric: true });
    drawBalletBriefText(context, summary.total.favorite?.label || "暂无", columns[2], secondY, 300, 62, 38);

    await new Promise((resolve) => requestAnimationFrame(resolve));
    const blob = await canvasToPngBlob(canvas);
    const statusMessage = `已生成 · week ${summary.info.week} · 最后一节 ${formatBalletDateTime(summary.info.lastCourseEndAt)} · 数据已于 ${formatBalletDateTime(summary.info.refreshAt)} 后刷新`;
    balletWeekBriefCache = {
      key: cacheKey,
      blob,
      week: summary.info.week,
      sourceAsOf: summary.sourceAsOf,
      statusMessage,
      filename: `芭蕾周简报-week-${summary.info.week}.png`,
    };
    setBalletWeekStatus("brief", statusMessage);
    setBalletWeekActionsDisabled(false);
    return balletWeekBriefCache;
  } catch (error) {
    balletWeekBriefCache = null;
    setBalletWeekStatus("brief", `周简报生成失败：${error.message || error}`);
    setBalletWeekActionsDisabled(false);
    return null;
  }
}

function renderBalletWeekBrief() {
  if (balletWeekBriefPromise) return balletWeekBriefPromise;
  balletWeekBriefPromise = buildBalletWeekBrief().finally(() => {
    balletWeekBriefPromise = null;
  });
  return balletWeekBriefPromise;
}

function renderBalletWeekAsset(type = balletWeekActiveSlide) {
  return type === "brief" ? renderBalletWeekBrief() : renderBalletWeekCover();
}

function warmBalletWeekCover() {
  balletWeekWarmupHandle = 0;
  if (!balletWeekCoverCache && !balletWeekCoverPromise) renderBalletWeekCover();
}

function scheduleBalletWeekCoverWarmup() {
  if (balletWeekCoverCache || balletWeekCoverPromise || balletWeekWarmupHandle) return;
  if ("requestIdleCallback" in window) {
    balletWeekWarmupHandle = window.requestIdleCallback(warmBalletWeekCover, { timeout: 1200 });
    return;
  }
  balletWeekWarmupHandle = window.setTimeout(warmBalletWeekCover, 120);
}

function scheduleBalletWeeklyBriefGeneration() {
  if (balletWeekBriefScheduleHandle) window.clearTimeout(balletWeekBriefScheduleHandle);
  balletWeekBriefScheduleHandle = 0;
  loadBalletWeekConfig().then((config) => {
    const cycle = getCurrentBalletBriefCycle(config);
    if (!cycle?.generateAt) return;
    const delay = Date.parse(cycle.generateAt) - Date.now();
    if (delay > 0) {
      balletWeekBriefScheduleHandle = window.setTimeout(
        scheduleBalletWeeklyBriefGeneration,
        Math.min(delay + 250, 2147483000),
      );
      return;
    }
    const summary = getBalletWeeklyBriefSummary(config);
    if (summary.info.week !== cycle.week || !summary.sourceReachedCutoff) {
      balletWeekBriefScheduleHandle = window.setTimeout(
        scheduleBalletWeeklyBriefGeneration,
        DATA_AUTO_REFRESH_INTERVAL_MS,
      );
      return;
    }
    if (balletWeekBriefCache?.week === cycle.week && balletWeekBriefCache?.sourceAsOf === summary.sourceAsOf) return;
    balletWeekBriefScheduleHandle = window.setTimeout(() => {
      balletWeekBriefScheduleHandle = 0;
      renderBalletWeekBrief();
    }, 250);
  }).catch(() => {});
}

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
  noUpcomingSpecialDate: "\u6682\u65e0\u5f85\u5230\u7279\u6b8a\u65e5",
  updatedAt: "\u66f4\u65b0\u4e8e",
  ledgerMergedAt: "\u603b\u8d26\u5408\u5e76\u4e8e",
  noNote: "\u6682\u65e0\u8bf4\u660e\u3002",
  tokenTitle: "Token \u7528\u91cf",
  dounaiTitle: "\u8c46\u5976",
  cloudTitle: "\u4e91\u670d\u52a1",
  rickyTitle: "\u6211\u548c Ricky",
  lifeTitle: "\u751f\u6d3b",
  balletTitle: "\u82ad\u857e",
  today: "\u4eca\u5929",
  energy: "\u8282\u594f",
  focus: "\u7126\u70b9",
  updatedAtShort: "\u66f4\u65b0",
  statusSnapshot: "\u72b6\u6001\u5feb\u7167",
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

function hasEntries(value) {
  if (Array.isArray(value)) return value.length > 0;
  if (value && typeof value === "object") return Object.values(value).some(hasEntries);
  return Boolean(value);
}

function dataHealthStatus(options, data) {
  const updatedAt = options.updatedAt(data) || "";
  const updatedDate = parseLocalDateTime(normalizeSourceUpdatedAt(updatedAt));
  if (!updatedDate) return { status: "unsynced", statusLabel: "尚未同步", updatedAt };
  const ageHours = (Date.now() - updatedDate.getTime()) / (60 * 60 * 1000);
  if (!Number.isFinite(ageHours) || ageHours > options.staleAfterHours) {
    return { status: "stale", statusLabel: "数据过期", updatedAt };
  }
  if (!options.hasData(data)) return { status: "empty", statusLabel: "暂无记录", updatedAt };
  return { status: "fresh", statusLabel: "已同步", updatedAt };
}

function updateBrowserDataHealth(key, data, error = "") {
  const options = DATA_SOURCE_OPTIONS[key];
  if (!options) return;
  if (error) {
    const updatedAt = options.updatedAt(data) || "";
    browserDataHealth.set(key, {
      key,
      label: options.label,
      status: "failed",
      statusLabel: "请求失败",
      updatedAt,
      staleAfterHours: options.staleAfterHours,
      error,
    });
    return;
  }
  if (key === "ballet") {
    const attempt = String(data.sync?.lastAttemptStatus || "").toLowerCase();
    const updatedAt = options.updatedAt(data) || "";
    if (attempt === "auth_required") {
      browserDataHealth.set(key, {
        key,
        label: options.label,
        status: "failed",
        statusLabel: "需要重新登录",
        updatedAt,
        staleAfterHours: options.staleAfterHours,
        error: "auth_required",
      });
      return;
    }
    if (attempt && !["never", "success", "waiting", "pending", "idle"].includes(attempt)) {
      browserDataHealth.set(key, {
        key,
        label: options.label,
        status: "failed",
        statusLabel: "更新失败",
        updatedAt,
        staleAfterHours: options.staleAfterHours,
        error: "upstream_sync_failed",
      });
      return;
    }
  }
  browserDataHealth.set(key, {
    key,
    label: options.label,
    staleAfterHours: options.staleAfterHours,
    error: "",
    ...dataHealthStatus(options, data),
  });
}

function readLastGood(key) {
  try {
    const cached = JSON.parse(localStorage.getItem(`${DATA_CACHE_PREFIX}${key}`) || "null");
    return cached?.data || null;
  } catch (error) {
    return null;
  }
}

function saveLastGood(key, data) {
  try {
    localStorage.setItem(`${DATA_CACHE_PREFIX}${key}`, JSON.stringify({ savedAt: new Date().toISOString(), data }));
  } catch (error) {
    // The live response remains usable when browser storage is unavailable or full.
  }
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
    progress: Math.max(0, Math.min(100, Math.round((minutes / 1440) * 100))),
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
  const now = new Date();
  const nowText = `${String(now.getHours()).padStart(2, "0")}:${String(now.getMinutes()).padStart(2, "0")}`;
  const progressPercent = `${phase.progress}%`;
  const progressAngle = `${phase.progress * 3.6}deg`;
  setText("#today-phase", phase.label);
  setText("#today-phase-note", phase.note);
  setText("#today-pulse-now", nowText);
  setText("#today-pulse-percent", progressPercent);
  const meter = qs(".summary-live-meter");
  if (meter) {
    meter.style.setProperty("--today-progress-angle", progressAngle);
    meter.title = `今日进度 ${nowText} / ${phase.progress}%`;
    meter.setAttribute("aria-label", `当前时间 ${nowText}，今天已过去 ${phase.progress}%`);
  }
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
    article.rel = "noopener noreferrer";
    article.setAttribute("aria-label", `${copy.open} ${item.title || copy.unnamedInfo}`);
  }
  article.innerHTML = `
    <div class="last30-item-head">
      <p class="item-title"></p>
      <span class="item-tag"></span>
    </div>
    <p class="item-copy"></p>
    <div class="last30-meta" aria-label="来源">
      <span data-role="source"></span>
    </div>
  `;
  article.querySelector(".item-title").textContent = item.title || copy.unnamedInfo;
  article.querySelector(".item-copy").textContent = item.summary || item.note || "";
  article.querySelector(".item-tag").textContent = item.needsOwnerConfirm
    ? "\u5f85\u786e\u8ba4"
    : item.date || item.status || item.source || copy.item;
  article.querySelector('[data-role="source"]').textContent = [item.source, item.sourceType].filter(Boolean).join(" · ") || copy.item;
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
  if (["fail", "failed", "check", "alert", "not set"].includes(value)) return "bad";
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
  const serverSources = getSystemItem("data-health").sources || [];
  const merged = new Map(serverSources.map((source) => [source.key, source]));
  browserDataHealth.forEach((source, key) => merged.set(key, source));
  const items = [...merged.values()];
  const unhealthy = items.filter((item) => ["failed", "stale", "unsynced"].includes(item.status));
  const failed = unhealthy.filter((item) => item.status === "failed");
  const empty = items.filter((item) => item.status === "empty");
  const firstIssue = failed[0] || unhealthy[0];
  const label = unhealthy.length ? `${unhealthy.length} 个异常` : `${items.length}/${items.length} 正常`;
  const note = firstIssue
    ? `${firstIssue.label} ${firstIssue.statusLabel}${firstIssue.updatedAt ? ` · 保留 ${formatSourceUpdatedAt(firstIssue.updatedAt)}` : ""}`
    : empty.length
      ? `${empty[0].label} 暂无记录（同步正常）`
      : "关键数据源已刷新";
  return { label, note, health: failed.length ? "bad" : unhealthy.length ? "unknown" : "ok", items };
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

function renderLast30Column(key, listSelector) {
  const itemLimit = key === "mainlines" ? 5 : 4;
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

  renderTopbarDataStatus(
    "ricky",
    rickyData,
    rickyData.synced_at || rickyData.updated_at,
    "#ricky-updated",
    "#ricky-connection-status",
  );
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

  renderTopbarDataStatus(
    "life",
    lifeFoodsData,
    lifeFoodsData.synced_at || lifeFoodsData.updated_at,
    "#life-updated",
    "#life-connection-status",
  );
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
  const xFormatter = options.xFormatter || ((record) => formatDateShort(record.date));
  const width = options.width || Math.max(920, records.length * 46 + 96);
  const height = 340;
  const padding = { top: 28, right: 26, bottom: 64, left: 56 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;
  const values = records.map((record) => Number(record[key]) || 0);
  const yScale = options.integerYScale ? getIntegerChartScale(values) : getChartScale(values);
  const yRange = yScale.max - yScale.min || 1;
  const points = records.map((record, index) => {
    const x = records.length <= 1
      ? padding.left + chartWidth / 2
      : padding.left + (index / (records.length - 1)) * chartWidth;
    const y = padding.top + chartHeight - (((Number(record[key]) || 0) - yScale.min) / yRange) * chartHeight;
    return { record, value: Number(record[key]) || 0, x, y };
  });
  const linePath = points.map((point, index) => `${index === 0 ? "M" : "L"} ${point.x.toFixed(1)} ${point.y.toFixed(1)}`).join(" ");
  const yTicks = yScale.ticks.map((value) => {
    const y = padding.top + chartHeight - ((value - yScale.min) / yRange) * chartHeight;
    return { value, y };
  });
  const labelInterval = Math.max(1, Number(options.labelInterval) || 5);
  const xLabelIndexes = new Set();
  records.forEach((_, index) => {
    if (index % labelInterval === 0) xLabelIndexes.add(index);
  });
  if (records.length > 0) {
    xLabelIndexes.add(records.length - 1);
  }

  if (!records.length) return `<p class="empty-state">${copy.noData}</p>`;

  return `
    <svg class="line-chart-svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" role="img" aria-label="${escapeHtml(options.title)}">
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
                <title>${escapeHtml(xFormatter(point.record))}: ${escapeHtml(formatter(point.value))}</title>
              </circle>
              <text class="chart-value-label" x="${point.x.toFixed(1)}" y="${Math.max(12, point.y - 9).toFixed(1)}" text-anchor="middle">${escapeHtml(formatter(point.value))}</text>
              ${
                xLabelIndexes.has(index)
                  ? `<text class="chart-x-label" x="${point.x.toFixed(1)}" y="${padding.top + chartHeight + 24}" text-anchor="middle">${escapeHtml(xFormatter(point.record))}</text>`
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

const BALLET_COURSE_TYPE_LABELS = {
  ballet: "芭蕾",
  soft_open: "软开",
  flexibility: "软开",
  conditioning: "肌肉素质",
  muscle: "肌肉素质",
  technique: "技术技巧",
  other: "其他",
};

const BALLET_LEVEL_LABELS = {
  l1: "L1",
  "l1.5": "L1.5",
  l15: "L1.5",
  l2: "L2",
  l3: "L3",
  l4: "L4",
  l5: "L5",
  none: "无级别",
  no_level: "无级别",
  unknown: "无级别",
};

const BALLET_NO_LEVEL_KEYS = new Set(["", "none", "no_level", "unknown"]);

// Course path follows:
// personal-wiki/raw/relationship-ricky/docs/2026-07-20-lijun-ballet-course-guide.md
// Growth levels are MaxNow class-count milestones, not technical assessments.
const BALLET_PROMOTION_RULES = {
  L1: { next: "L1.5", regular: 8, intermittent: 15 },
  "L1.5": { next: "L2", regular: 15, intermittent: 25 },
  L2: { next: "L3", regular: 20, intermittent: 30 },
  L3: { next: "L4", regular: 30, intermittent: 40 },
  L4: { next: "L5", regular: 30, intermittent: 40 },
  L5: { next: null, regular: 30, intermittent: 40 },
};

const BALLET_LEVEL_ORDER = ["L1", "L1.5", "L2", "L3", "L4", "L5"];

const BALLET_GROWTH_LEVELS = [
  { level: 1, threshold: 0 },
  { level: 2, threshold: 10 },
  { level: 3, threshold: 25 },
  { level: 4, threshold: 45 },
  { level: 5, threshold: 70 },
  { level: 6, threshold: 95 },
  { level: 7, threshold: 120 },
  { level: 8, threshold: 145 },
  { level: 9, threshold: 170 },
  { level: 10, threshold: 200 },
];

function balletNumber(value, fallback = 0) {
  const number = Number(value);
  return Number.isFinite(number) ? number : fallback;
}

function balletMinutes(item = {}) {
  const minutes = item.minutes ?? item.durationMinutes ?? item.totalMinutes;
  return Number.isFinite(Number(minutes)) ? Math.max(0, Number(minutes)) : null;
}

function formatBalletHours(minutes) {
  if (!Number.isFinite(Number(minutes))) return "--";
  const hours = Math.max(0, Number(minutes)) / 60;
  return hours.toFixed(hours >= 100 ? 0 : hours >= 10 ? 1 : 2).replace(/\.?0+$/, "");
}

const BALLET_SESSION_STATES = {
  running: {
    label: "正常运行",
    tone: "success",
    message: "最近一次只读检查正常；这不代表 PHPSESSID 已实现自动续期。",
  },
  complete: {
    label: "实验完成",
    tone: "success",
    message: "持续活动寿命实验已结束，时长冻结在最后一次验证成功。",
  },
  auth_required: {
    label: "需要重新登录",
    tone: "auth",
    message: "会话授权已失效；请在电脑微信重新登录后刷新服务器凭据。",
  },
  delayed: {
    label: "检查延迟",
    tone: "stale",
    message: "最近一次自动检查未按计划完成；已确认有效时长保持不变。",
  },
  interrupted: {
    label: "实验中断",
    tone: "error",
    message: "只读探针已停止；已确认有效时长保持不变。",
  },
  unknown: {
    label: "等待状态",
    tone: "waiting",
    message: "等待服务器写入脱敏实验状态。",
  },
};

const BALLET_SESSION_ERROR_LABELS = {
  auth_required: "需要重新登录微信并刷新服务器凭据。",
  identity_expired: "会话身份已失效。",
  network_error: "最近一次检查遇到网络异常。",
  http_error: "最近一次检查返回异常 HTTP 状态。",
  unknown_response: "最近一次响应无法安全判断登录状态。",
  probe_delayed: "只读检查已超过预期时间，当前登录状态待确认。",
  probe_interrupted: "自动检查服务已停止，当前登录状态待确认。",
  probe_inconclusive: "连续检查无法确认登录状态，实验已安全停止。",
  source_config_mismatch: "实验配置与日志中的检查间隔不一致。",
  source_log_invalid: "实验状态日志暂时无法完整解析。",
  invalid_completion: "实验完成标记尚未通过完整性校验。",
  status_unknown: "暂时无法确认当前会话状态。",
  stopped_consecutive_unknown: "连续多次无法判断状态，探针已安全停止。",
  service_inactive: "只读探针当前未运行。",
};

function parseBalletSessionTimestamp(value) {
  const text = String(value || "").trim();
  if (!text) return null;
  const absolute = new Date(text);
  if (!Number.isNaN(absolute.getTime())) return absolute;
  return parseLocalDateTime(text);
}

function formatBalletSessionTimestamp(value) {
  const date = parseBalletSessionTimestamp(value);
  if (!date) return "--";
  try {
    const parts = Object.fromEntries(
      new Intl.DateTimeFormat("zh-CN", {
        timeZone: "Asia/Shanghai",
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        hourCycle: "h23",
      })
        .formatToParts(date)
        .filter((item) => item.type !== "literal")
        .map((item) => [item.type, item.value]),
    );
    return `${parts.year}-${parts.month}-${parts.day} ${parts.hour}:${parts.minute}`;
  } catch (error) {
    return normalizeSourceUpdatedAt(value) || "--";
  }
}

function getBalletVerifiedAliveSeconds(data = balletSessionData) {
  const explicit = data?.verifiedAliveSeconds;
  if (explicit !== null && explicit !== undefined && explicit !== "") {
    const seconds = Number(explicit);
    if (Number.isFinite(seconds) && seconds >= 0) return Math.floor(seconds);
  }
  const startedAt = parseBalletSessionTimestamp(data?.experimentStartedAt);
  const authenticatedAt = parseBalletSessionTimestamp(data?.lastAuthenticatedAt);
  if (!startedAt || !authenticatedAt || authenticatedAt < startedAt) return null;
  return Math.floor((authenticatedAt.getTime() - startedAt.getTime()) / 1000);
}

function formatBalletVerifiedDuration(seconds) {
  if (!Number.isFinite(Number(seconds)) || Number(seconds) < 0) return "--";
  const totalMinutes = Math.floor(Number(seconds) / 60);
  const days = Math.floor(totalMinutes / (24 * 60));
  const hours = Math.floor((totalMinutes % (24 * 60)) / 60);
  const minutes = totalMinutes % 60;
  return `${days}天 ${hours}小时 ${minutes}分`;
}

function isBalletSessionPublisherStale(data = balletSessionData, now = new Date()) {
  const updatedAt = parseBalletSessionTimestamp(data?.updatedAt);
  return !updatedAt || now.getTime() - updatedAt.getTime() > BALLET_SESSION_PUBLISH_STALE_MS;
}

function getBalletSessionState(now = new Date()) {
  const key = String(balletSessionData?.status || "unknown").trim().toLowerCase();
  if (key === "running" && isBalletSessionPublisherStale(balletSessionData, now)) {
    return {
      key: "delayed",
      ...BALLET_SESSION_STATES.delayed,
      message: "实验状态缓存已超过 15 分钟未更新；已确认有效时长保持不变。",
    };
  }
  return { key, ...(BALLET_SESSION_STATES[key] || BALLET_SESSION_STATES.unknown) };
}

function getBalletSessionErrorLabel() {
  const error = balletSessionData?.lastError;
  const rawCode = typeof error === "string" ? error : error?.code;
  const code = String(rawCode || "")
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9_-]/g, "")
    .slice(0, 48);
  if (!code) return "";
  return BALLET_SESSION_ERROR_LABELS[code] || "最近错误的详细信息已安全隐藏。";
}

function getBalletSessionResultLabel() {
  const result = balletSessionData?.lastResult;
  if (!result || typeof result !== "object") return "最近结果：待观察";
  const status = Number(result.httpStatus);
  const loginState = String(result.loginState || "").trim().toLowerCase();
  const loginLabels = {
    authenticated: "已登录",
    expired: "登录失效",
    identity_expired: "登录失效",
    unauthenticated: "未登录",
    network_error: "网络异常",
    redirect: "发生跳转",
    unknown: "待确认",
  };
  const parts = [
    Number.isInteger(status) && status >= 100 && status <= 599 ? `HTTP ${status}` : "",
    loginLabels[loginState] || "",
    result.networkError === true ? "网络异常" : "",
  ].filter(Boolean);
  return parts.length ? `最近结果：${parts.join(" · ")}` : "最近结果：待观察";
}

function formatBalletSessionCountdown(milliseconds) {
  const totalMinutes = Math.max(1, Math.ceil(milliseconds / 60000));
  const days = Math.floor(totalMinutes / (24 * 60));
  const hours = Math.floor((totalMinutes % (24 * 60)) / 60);
  const minutes = totalMinutes % 60;
  if (days) return `${days}天 ${hours}小时`;
  if (hours) return `${hours}小时 ${minutes}分`;
  return `${minutes}分`;
}

function renderBalletSessionCountdown(now = new Date()) {
  const target = parseBalletSessionTimestamp(balletSessionData?.nextProbeAt);
  if (!target) {
    setText("#ballet-session-next-probe", "--");
    return;
  }
  const scheduled = formatBalletSessionTimestamp(balletSessionData.nextProbeAt);
  const state = getBalletSessionState(now);
  if (!["running", "delayed"].includes(state.key)) {
    setText("#ballet-session-next-probe", scheduled);
    return;
  }
  const remaining = target.getTime() - now.getTime();
  setText(
    "#ballet-session-next-probe",
    remaining > 0
      ? `${scheduled} · ${formatBalletSessionCountdown(remaining)}后`
      : `${scheduled} · 等待本轮结果`,
  );
}

function renderBalletSessionExperiment(now = new Date()) {
  const state = getBalletSessionState(now);
  const status = qs("#ballet-session-status");
  const card = qs(".ballet-session-card");
  setText("#ballet-session-status", state.label);
  if (status) status.dataset.state = state.tone;
  if (card) card.dataset.state = state.key;

  setText(
    "#ballet-session-duration",
    formatBalletVerifiedDuration(getBalletVerifiedAliveSeconds()),
  );
  setText(
    "#ballet-session-started",
    formatBalletSessionTimestamp(balletSessionData?.experimentStartedAt),
  );
  setText(
    "#ballet-session-last-probe",
    formatBalletSessionTimestamp(balletSessionData?.lastProbeAt),
  );
  const interval = Number(balletSessionData?.refreshIntervalMinutes);
  setText(
    "#ballet-session-interval",
    Number.isFinite(interval) && interval > 0 ? `每 ${interval} 分钟` : "--",
  );
  const nextRunPlan = qs("#ballet-session-next-plan");
  const showNextRunPlan =
    ["auth_required", "interrupted", "complete"].includes(state.key) &&
    interval !== BALLET_SESSION_NEXT_RUN_INTERVAL_MINUTES;
  setText(
    "#ballet-session-next-plan",
    `新凭据后计划每 ${BALLET_SESSION_NEXT_RUN_INTERVAL_MINUTES} 分钟`,
  );
  if (nextRunPlan) nextRunPlan.hidden = !showNextRunPlan;
  renderBalletSessionCountdown(now);

  const errorLabel = getBalletSessionErrorLabel();
  setText(
    "#ballet-session-note",
    [state.message, errorLabel].filter(Boolean).join(" "),
  );
  setText(
    "#ballet-session-phase",
    `阶段起始 ${formatBalletSessionTimestamp(balletSessionData?.phaseStartedAt)}`,
  );
  const phaseSamples = Math.max(0, Math.floor(balletNumber(balletSessionData?.phaseSamples)));
  const totalSamples = Math.max(0, Math.floor(balletNumber(balletSessionData?.totalSamples)));
  setText("#ballet-session-samples", `本阶段 ${phaseSamples} 次 · 累计 ${totalSamples} 次`);
  const sessionChanged =
    typeof balletSessionData?.sessionChangedObserved === "boolean"
      ? `各阶段进程内会话变化：${balletSessionData.sessionChangedObserved ? "已观察到" : "未观察到"}`
      : "各阶段进程内会话变化：待观察";
  const setCookie =
    typeof balletSessionData?.setCookieObserved === "boolean"
      ? `Set-Cookie：${balletSessionData.setCookieObserved ? "已观察到" : "未观察到"}`
      : "Set-Cookie：待观察";
  setText(
    "#ballet-session-observations",
    `${getBalletSessionResultLabel()} · ${sessionChanged} · ${setCookie}`,
  );
}

const BALLET_BOOKING_FAST_STATUS = {
  waiting: { label: "等待首次执行", tone: "waiting" },
  success: { label: "运行正常", tone: "success" },
  partial: { label: "部分完成", tone: "stale" },
  completed_unverified: { label: "已提交，待核验", tone: "stale" },
  stopped: { label: "已安全停止", tone: "error" },
  auth_required: { label: "登录已失效", tone: "error" },
  outside_window: { label: "未到抢课时间", tone: "waiting" },
  configuration_error: { label: "配置异常", tone: "error" },
  source_changed: { label: "页面结构变化", tone: "error" },
  unknown_result: { label: "结果待确认", tone: "error" },
};

const BALLET_BOOKING_RECORD_STATUS = {
  booked: "已抢到",
  already_booked: "已预约",
  waitlisted: "已排队",
  already_waitlisted: "已在排队",
  ready: "可预约",
  ready_waitlist: "可排队",
  not_available: "不可预约",
  course_not_unique: "未找到唯一课程",
  card_not_open: "课程卡未开放",
  card_selection_required: "需选择课程卡",
  no_eligible_card: "无可用课程卡",
  rules_blocked: "规则未通过",
  full: "已满",
  stopped: "已停止预约",
  notopen: "尚未开放",
  unknown_result: "结果待确认",
  source_changed: "页面结构变化",
  auth_required: "登录已失效",
  not_attempted: "未继续",
};

function createBalletBookingFastTarget(target = {}, result = null) {
  const article = document.createElement("article");
  article.className = "ballet-booking-fast-target";
  if (result?.status) article.dataset.state = result.status;

  const time = document.createElement("time");
  const shortDate = String(target.date || "").slice(5).replace("-", "/");
  const timeRange = target.endTime
    ? `${target.startTime || "--"}–${target.endTime}`
    : target.startTime || "全天";
  time.textContent = [target.weekday, shortDate, timeRange]
    .filter(Boolean)
    .join(" · ");

  const main = document.createElement("div");
  const title = document.createElement("strong");
  title.textContent = target.course || "未命名课程";
  const meta = document.createElement("small");
  meta.textContent = [target.teacher, target.venue].filter(Boolean).join(" · ");
  main.append(title, meta);

  const status = document.createElement("span");
  status.className = "status-pill";
  status.textContent = result
    ? BALLET_BOOKING_RECORD_STATUS[result.status] || "状态待确认"
    : "计划中";
  if (result && Number(result.attempts) > 1) {
    status.textContent += ` · ${Number(result.attempts) - 1} 次重试`;
  }
  if (result && Number.isInteger(result.waitlistPosition) && result.waitlistPosition > 0) {
    status.textContent += ` · 第 ${result.waitlistPosition} 位`;
  }
  article.append(time, main, status);
  return article;
}

function createBalletBookingEmpty(message) {
  const paragraph = document.createElement("p");
  paragraph.className = "ballet-booking-empty";
  paragraph.textContent = message;
  return paragraph;
}

const BALLET_BOOKING_WEEKDAY_ORDER = {
  周一: 1,
  周二: 2,
  周三: 3,
  周四: 4,
  周五: 5,
  周六: 6,
  周日: 7,
};

function balletBookingTargetTone(target = {}) {
  const course = String(target.course || target.courseName || target.name || "")
    .replace(/\s+/g, "")
    .toLowerCase();
  if (course.includes("l1")) return "l1";
  if (course.includes("软开")) return "soft-open";
  return "other";
}

function balletBookingMiniStatusText(result = {}) {
  let label = BALLET_BOOKING_RECORD_STATUS[result.status] || "状态待确认";
  if (Number(result.attempts) > 1) label += ` · 重试 ${Number(result.attempts) - 1}`;
  if (Number.isInteger(result.waitlistPosition) && result.waitlistPosition > 0) {
    label += ` · 第 ${result.waitlistPosition} 位`;
  }
  return label;
}

function createBalletBookingMiniTimetable(targets = [], options = {}) {
  const mode = options.mode === "results" ? "results" : "targets";
  const timetable = document.createElement("div");
  timetable.className = `ballet-booking-mini-timetable is-${mode}`;
  timetable.setAttribute("role", "table");
  timetable.setAttribute(
    "aria-label",
    mode === "results" ? "本次抢课结果微型课表" : "每周自动抢课微型课表",
  );

  const grid = document.createElement("div");
  grid.className = "ballet-booking-mini-grid";
  grid.setAttribute("role", "row");
  const groups = new Map();
  targets.forEach((target) => {
    const key = `${target.weekday || ""}|${target.date || ""}`;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(target);
  });
  const sortedGroups = [...groups.values()].sort((left, right) => {
    if (mode === "results") {
      const dateDiff = String(left[0]?.date || "").localeCompare(String(right[0]?.date || ""));
      if (dateDiff) return dateDiff;
    }
    const weekdayDiff = (BALLET_BOOKING_WEEKDAY_ORDER[left[0]?.weekday] || 99)
      - (BALLET_BOOKING_WEEKDAY_ORDER[right[0]?.weekday] || 99);
    return weekdayDiff || String(left[0]?.date || "").localeCompare(String(right[0]?.date || ""));
  });
  timetable.classList.add(`has-${Math.min(sortedGroups.length, 6)}-days`);

  sortedGroups.forEach((dayTargets) => {
    const firstTarget = dayTargets[0] || {};
    const day = document.createElement("section");
    day.className = "ballet-booking-mini-day";
    day.dataset.priority = mode === "targets" && firstTarget.weekday === "周六" ? "first" : "standard";
    day.setAttribute("role", "cell");

    const header = document.createElement("header");
    const heading = document.createElement("div");
    const weekday = document.createElement("strong");
    weekday.textContent = firstTarget.weekday || "未定";
    const date = document.createElement("time");
    date.dateTime = firstTarget.date || "";
    date.textContent = String(firstTarget.date || "").slice(5).replace("-", "/");
    heading.append(weekday, date);
    header.appendChild(heading);
    if (mode === "targets" && firstTarget.weekday === "周六") {
      const priority = document.createElement("span");
      priority.className = "ballet-booking-mini-priority";
      priority.textContent = "周末优先";
      header.appendChild(priority);
    }

    const courses = document.createElement("div");
    courses.className = "ballet-booking-mini-courses";
    dayTargets
      .slice()
      .sort((left, right) => {
        if (mode === "results") {
          return String(left.startTime || "").localeCompare(String(right.startTime || ""));
        }
        const toneOrder = { l1: 0, "soft-open": 1, other: 2 };
        return toneOrder[balletBookingTargetTone(left)] - toneOrder[balletBookingTargetTone(right)];
      })
      .forEach((target) => {
        const course = document.createElement("article");
        course.className = "ballet-booking-mini-course";
        course.dataset.course = balletBookingTargetTone(target);
        const title = document.createElement("strong");
        title.textContent = target.course || "未命名课程";
        const time = document.createElement("span");
        time.textContent = target.endTime
          ? `${target.startTime || "--"}–${target.endTime}`
          : target.startTime || "全天";
        course.append(title, time);
        if (mode === "results") {
          course.dataset.state = target.status || "unknown_result";
          const status = document.createElement("small");
          status.className = "ballet-booking-mini-status";
          status.textContent = balletBookingMiniStatusText(target);
          course.appendChild(status);
        } else {
          const order = document.createElement("small");
          order.className = "ballet-booking-mini-order";
          order.textContent = `优先 ${String(targets.indexOf(target) + 1).padStart(2, "0")}`;
          course.appendChild(order);
        }
        courses.appendChild(course);
      });

    day.append(header, courses);
    grid.appendChild(day);
  });

  timetable.appendChild(grid);
  if (mode === "targets") {
    const legend = document.createElement("div");
    legend.className = "ballet-booking-mini-legend";
    legend.innerHTML = `
      <span><i data-course="l1"></i>L1</span>
      <span><i data-course="soft-open"></i>软开</span>
      <small>数字为执行优先级 · 不限老师 · 大教室优先</small>
    `;
    timetable.appendChild(legend);
  }
  return timetable;
}

function getBalletBookingTiming(lastRun = {}) {
  const records = Array.isArray(lastRun?.records) ? lastRun.records : [];
  const durations = records
    .map((record) => Number(record?.elapsedMilliseconds))
    .filter((duration) => Number.isFinite(duration) && duration > 0);
  const summedMilliseconds = durations.reduce((total, duration) => total + duration, 0);
  const criticalPathMilliseconds = Number(lastRun?.criticalPathMilliseconds);
  const totalMilliseconds = Number.isFinite(criticalPathMilliseconds) && criticalPathMilliseconds > 0
    ? Math.round(criticalPathMilliseconds)
    : durations.length
      ? Math.round(summedMilliseconds)
      : null;
  return {
    totalMilliseconds,
    averageMilliseconds: durations.length
      ? Math.round(summedMilliseconds / durations.length)
      : null,
    targetCount: durations.length,
  };
}

function formatBalletBookingDuration(milliseconds) {
  const duration = Number(milliseconds);
  if (!Number.isFinite(duration) || duration <= 0) return "--";
  if (duration < 1000) return `${Math.round(duration)} ms`;
  return `${(duration / 1000).toFixed(1)} s`;
}

const BALLET_PLAN_WEEKDAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"];

function getBalletPlanWeekStart(offset = balletPlanWeekOffset) {
  const date = new Date();
  date.setHours(12, 0, 0, 0);
  date.setDate(date.getDate() - ((date.getDay() + 6) % 7) + offset * 7);
  return date;
}

function getBalletPlanWeekDates(offset = balletPlanWeekOffset) {
  const start = getBalletPlanWeekStart(offset);
  return BALLET_PLAN_WEEKDAYS.map((weekday, index) => {
    const date = new Date(start);
    date.setDate(start.getDate() + index);
    return { date: localDateKey(date), weekday };
  });
}

function getBalletPlanRecordStatus(record = {}) {
  const bookingStatus = String(
    record.bookingStatus || record.status || record.availability || record.attendanceStatus || "",
  ).toLowerCase();
  const labels = {
    booked: "已预约",
    already_booked: "已预约",
    waitlisted: "候补中",
    already_waitlisted: "候补中",
    waitlist: "候补中",
    attended: "已上完",
  };
  if (labels[bookingStatus]) return { key: bookingStatus, label: labels[bookingStatus] };
  if (BALLET_BOOKING_RECORD_STATUS[bookingStatus]) {
    return { key: bookingStatus, label: BALLET_BOOKING_RECORD_STATUS[bookingStatus] };
  }
  return { key: bookingStatus || "planned", label: bookingStatus ? "待确认" : "已安排" };
}

function balletPlanCourseKey(record = {}) {
  const rawType = String(record.courseType || "").trim().toLowerCase();
  const rawLevel = String(record.level || "").replace(/\s+/g, "").toLowerCase();
  const targetTone = balletBookingTargetTone(record);
  const normalizedName = balletCourseName(record).replace(/\s+/g, "").toLowerCase();
  let courseIdentity = normalizedName;
  if (rawType === "ballet" || normalizedName.includes("芭蕾") || targetTone === "l1") {
    const level = rawLevel && rawLevel !== "none"
      ? rawLevel
      : normalizedName.includes("l1.5")
        ? "l1.5"
        : normalizedName.includes("l1")
          ? "l1"
          : "unknown";
    courseIdentity = `ballet:${level}`;
  } else if (rawType === "soft_open" || targetTone === "soft-open") {
    courseIdentity = "soft-open";
  } else if (rawType && rawType !== "other") {
    courseIdentity = rawType;
  }
  return [
    balletRecordDate(record),
    balletStartTime(record),
    balletEndTime(record),
    courseIdentity,
  ].join("|");
}

function getBalletPlanAvailability(record = {}) {
  const status = getBalletPlanRecordStatus(record).key;
  if (["booked", "already_booked"].includes(status)) return "booked";
  if (["waitlisted", "already_waitlisted", "waitlist"].includes(status)) return "waitlist";
  if (status === "attended") return "attended";
  return status || "available";
}

function getBalletBookingSnapshotRecords() {
  const records = [];
  const add = (record, source) => {
    const date = balletRecordDate(record);
    if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) return;
    records.push({ ...record, date, _planSource: source });
  };
  getBalletUpcomingRecords().forEach((record) => add(record, "upcoming"));
  const timetableDays = Array.isArray(balletData.timetable?.days) ? balletData.timetable.days : [];
  timetableDays.forEach((day) => {
    (Array.isArray(day.records) ? day.records : [])
      .filter((record) => ["booked", "waitlist"].includes(String(record.availability || "").toLowerCase()))
      .forEach((record) => add({
        ...record,
        date: day.date,
        bookingStatus: record.bookingStatus || record.availability,
      }, "timetable"));
  });

  const unique = new Map();
  const sourceOrder = { upcoming: 2, timetable: 1 };
  records.forEach((record) => {
    const key = balletPlanCourseKey(record);
    const current = unique.get(key);
    if (!current || sourceOrder[record._planSource] >= sourceOrder[current._planSource]) {
      unique.set(key, record);
    }
  });
  return [...unique.values()].sort((left, right) =>
    `${left.date}T${balletStartTime(left) || "00:00"}`.localeCompare(
      `${right.date}T${balletStartTime(right) || "00:00"}`,
    ),
  );
}

function getBalletPlanActualRecords() {
  const records = [];
  const add = (record, source) => {
    const date = balletRecordDate(record);
    if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) return;
    records.push({ ...record, date, _planSource: source });
  };
  (Array.isArray(balletData.records) ? balletData.records : []).forEach((record) => add(record, "history"));
  getBalletUpcomingRecords().forEach((record) => add(record, "upcoming"));
  const timetableDays = Array.isArray(balletData.timetable?.days) ? balletData.timetable.days : [];
  timetableDays.forEach((day) => {
    (Array.isArray(day.records) ? day.records : [])
      .filter((record) => ["booked", "waitlist", "attended"].includes(String(record.availability || "").toLowerCase()))
      .forEach((record) => add({ ...record, date: day.date }, "timetable"));
  });
  const lastRecords = Array.isArray(balletBookingFastData?.lastRun?.records)
    ? balletBookingFastData.lastRun.records
    : [];
  lastRecords.forEach((record) => add(record, "last-run"));

  const unique = new Map();
  records.forEach((record) => {
    const key = balletPlanCourseKey(record);
    const current = unique.get(key);
    const sourceOrder = { upcoming: 4, timetable: 3, history: 2, "last-run": 1 };
    if (!current || sourceOrder[record._planSource] >= sourceOrder[current._planSource]) {
      unique.set(key, record);
    }
  });
  return [...unique.values()];
}

function createBalletPlanWeekCourse(record = {}, options = {}) {
  if (!options.planned) {
    const interval = balletTimetableInterval(record);
    const course = createBalletTimetableCourse(
      {
        ...record,
        availability: getBalletPlanAvailability(record),
        durationMinutes: record.durationMinutes || (interval ? interval.end - interval.start : undefined),
      },
      false,
      { includeVenue: false, includeCounts: false },
    );
    course.classList.add("is-plan");
    return course;
  }
  const article = document.createElement("article");
  article.className = "ballet-plan-week-course";
  article.dataset.course = balletBookingTargetTone(record);
  article.dataset.kind = options.planned ? "planned" : "actual";
  const status = options.planned
    ? { key: "planned", label: "准备抢" }
    : getBalletPlanRecordStatus(record);
  article.dataset.state = status.key;

  const title = document.createElement("strong");
  title.textContent = balletCourseName(record);
  const timeText = [balletStartTime(record), balletEndTime(record)].filter(Boolean).join("–")
    || String(record.startTime || "时间待确认");
  const detail = document.createElement("small");
  detail.textContent = [balletTeacher(record) || "老师待确认", timeText].join(" · ");
  const state = document.createElement("span");
  state.className = "ballet-plan-week-state";
  state.textContent = status.label;
  article.append(title, detail);

  if (options.priority) {
    const priority = document.createElement("em");
    priority.textContent = `优先 ${String(options.priority).padStart(2, "0")}`;
    article.appendChild(priority);
  }
  article.appendChild(state);
  article.title = [title.textContent, detail.textContent, record.venue, state.textContent].filter(Boolean).join(" · ");
  return article;
}

function createBalletPlanWeekHeader(date, weekday) {
  const header = document.createElement("header");
  header.className = "ballet-plan-week-day-header";
  header.dataset.dayState = getBalletTimetableDayState(date);
  const name = document.createElement("strong");
  name.textContent = weekday;
  const dateNode = document.createElement("time");
  dateNode.dateTime = date;
  dateNode.textContent = date.slice(5).replace("-", "/");
  header.append(name, dateNode);
  return header;
}

function renderBalletPlanWeekTargets(container, weekDates, weekTargets, allTargets) {
  container.dataset.mode = "targets";
  container.style.removeProperty("--ballet-plan-time-rows");
  container.style.removeProperty("--ballet-plan-room-columns");
  weekDates.forEach(({ date, weekday }) => {
    const day = document.createElement("section");
    day.className = "ballet-plan-week-day";
    day.dataset.dayState = getBalletTimetableDayState(date);
    const header = createBalletPlanWeekHeader(date, weekday);
    const courses = document.createElement("div");
    courses.className = "ballet-plan-week-courses";
    const dayTargets = weekTargets.filter((target) => target.date === date);
    courses.append(
      ...dayTargets.map((target) => createBalletPlanWeekCourse(target, {
        planned: true,
        priority: allTargets.indexOf(target) + 1,
      })),
    );
    if (!courses.childElementCount) {
      const empty = document.createElement("span");
      empty.className = "ballet-plan-week-empty";
      empty.textContent = "暂无安排";
      courses.appendChild(empty);
    }
    day.append(header, courses);
    container.appendChild(day);
  });
}

function buildBalletPlanTimelineRows(days = []) {
  const intervals = days.flatMap((day) =>
    (Array.isArray(day.records) ? day.records : [])
      .map(balletTimetableInterval)
      .filter(Boolean),
  );
  if (!intervals.length) return [];

  const merged = intervals
    .slice()
    .sort((left, right) => left.start - right.start || left.end - right.end)
    .reduce((groups, interval) => {
      const previous = groups[groups.length - 1];
      if (previous && interval.start <= previous.end) {
        previous.end = Math.max(previous.end, interval.end);
      } else {
        groups.push({ start: interval.start, end: interval.end });
      }
      return groups;
    }, []);
  const compressedGaps = merged.slice(0, -1)
    .map((interval, index) => ({ start: interval.end, end: merged[index + 1].start }))
    .filter((gap) => gap.end - gap.start >= 60);
  const firstMinute = merged[0].start;
  const lastMinute = merged[merged.length - 1].end;
  const rows = [];

  for (let minute = firstMinute; minute < lastMinute;) {
    const gap = compressedGaps.find((item) => item.start === minute);
    if (gap) {
      rows.push({
        type: "gap",
        startMinute: gap.start,
        endMinute: gap.end,
        trackCount: 1,
        labelMinute: Math.ceil(gap.start / 60) * 60,
      });
      minute = gap.end;
      continue;
    }

    const nextHour = (Math.floor(minute / 60) + 1) * 60;
    const nextGap = compressedGaps.find((item) => item.start > minute);
    const endMinute = Math.min(lastMinute, nextHour, nextGap?.start ?? lastMinute);
    rows.push({
      type: "time",
      startMinute: minute,
      endMinute,
      trackCount: endMinute - minute,
      labelMinute: minute % 60 === 0 ? minute : null,
    });
    minute = endMinute;
  }
  return rows;
}

function renderBalletPlanWeekTimeline(container, weekDates, actualRecords) {
  const days = weekDates.map(({ date, weekday }) => ({
    date,
    weekday,
    records: actualRecords
      .filter((record) => record.date === date)
      .sort((left, right) =>
        String(balletStartTime(left)).localeCompare(String(balletStartTime(right))),
      ),
  }));
  const rows = buildBalletPlanTimelineRows(days);
  if (!rows.length) {
    renderBalletPlanWeekTargets(container, weekDates, [], []);
    return;
  }

  container.dataset.mode = "timeline";
  const roomColumns = days.flatMap((day) => {
    const hasUnknownRoom = day.records.some((record) => balletTimetableRoomKey(record) === "unknown");
    return BALLET_TIMETABLE_ROOMS.map((room) =>
      hasUnknownRoom || day.records.some((record) => balletTimetableRoomKey(record) === room.key)
        ? "minmax(var(--ballet-plan-active-room-width), 1fr)"
        : "minmax(var(--ballet-plan-empty-room-width), 0.34fr)");
  });
  container.style.setProperty("--ballet-plan-room-columns", roomColumns.join(" "));
  container.style.setProperty(
    "--ballet-plan-time-rows",
    rows
      .map((row) => row.type === "gap"
        ? "24px"
        : `repeat(${row.trackCount}, var(--ballet-plan-minute-height))`)
      .join(" "),
  );

  let nextGridLine = 3;
  const minuteGridLines = new Map();
  const layoutRows = rows.map((row) => {
    const startLine = nextGridLine;
    const endLine = startLine + row.trackCount;
    nextGridLine = endLine;
    if (row.type === "time") {
      for (let minute = 0; minute <= row.trackCount; minute += 1) {
        minuteGridLines.set(row.startMinute + minute, startLine + minute);
      }
    } else {
      minuteGridLines.set(row.startMinute, startLine);
      minuteGridLines.set(row.endMinute, endLine);
    }
    return { ...row, startLine, endLine };
  });

  const corner = document.createElement("div");
  corner.className = "ballet-plan-week-time-corner";
  corner.textContent = "时间";
  corner.style.gridColumn = "1";
  corner.style.gridRow = "1 / 3";
  container.appendChild(corner);

  days.forEach((day, index) => {
    const header = createBalletPlanWeekHeader(day.date, day.weekday);
    header.style.gridColumn = `${index * 2 + 2} / span 2`;
    header.style.gridRow = "1";
    container.appendChild(header);
    BALLET_TIMETABLE_ROOMS.forEach((room, roomIndex) => {
      const roomHeader = createBalletTimetableRoomHeader(
        room,
        getBalletTimetableDayState(day.date),
      );
      roomHeader.classList.add("ballet-plan-week-room");
      roomHeader.style.gridColumn = String(index * 2 + roomIndex + 2);
      roomHeader.style.gridRow = "2";
      container.appendChild(roomHeader);
    });
  });

  layoutRows.forEach((row, rowIndex) => {
    const time = document.createElement("div");
    time.className = "ballet-plan-week-time";
    time.dataset.rowType = row.type;
    time.dataset.rowEdge =
      layoutRows.length === 1 ? "both" : rowIndex === 0 ? "start" : rowIndex === layoutRows.length - 1 ? "end" : "middle";
    const labelText = row.type === "time" && Number.isFinite(row.labelMinute)
      ? formatBalletTimetableHour(Math.floor(row.labelMinute / 60))
      : "";
    if (labelText) {
      const label = document.createElement("span");
      label.textContent = labelText;
      time.appendChild(label);
    }
    time.style.gridColumn = "1";
    time.style.gridRow = `${row.startLine} / ${row.endLine}`;
    container.appendChild(time);
  });

  const finalRow = layoutRows[layoutRows.length - 1];
  if (finalRow) {
    const terminal = document.createElement("div");
    terminal.className = "ballet-plan-week-time ballet-plan-week-end-time";
    terminal.style.gridColumn = "1";
    terminal.style.gridRow = `${nextGridLine} / span 1`;
    const spacer = document.createElement("div");
    spacer.className = "ballet-plan-week-end-spacer";
    spacer.style.gridColumn = "2 / -1";
    spacer.style.gridRow = `${nextGridLine} / span 1`;
    container.append(terminal, spacer);
  }

  days.forEach((day, index) => {
    const dayState = getBalletTimetableDayState(day.date);
    const dayStartColumn = index * 2 + 2;
    BALLET_TIMETABLE_ROOMS.forEach((room, roomIndex) => {
      layoutRows.forEach((row, rowIndex) => {
        const cell = document.createElement("div");
        cell.className = "ballet-plan-week-cell";
        cell.dataset.dayState = dayState;
        cell.dataset.room = room.key;
        cell.dataset.rowType = row.type;
        cell.dataset.rowEdge =
          layoutRows.length === 1 ? "both" : rowIndex === 0 ? "start" : rowIndex === layoutRows.length - 1 ? "end" : "middle";
        cell.style.gridColumn = String(dayStartColumn + roomIndex);
        cell.style.gridRow = `${row.startLine} / ${row.endLine}`;
        container.appendChild(cell);
      });
    });

    [...BALLET_TIMETABLE_ROOMS, { key: "unknown", label: "未标注教室" }].forEach(
      (room, roomIndex) => {
        const roomRecords = day.records.filter(
          (record) => balletTimetableRoomKey(record) === room.key,
        );
        const layout = layoutBalletTimetableRecords(roomRecords);
        layout.items.forEach(({ record, interval, lane, laneCount }) => {
          const startLine = minuteGridLines.get(interval.start);
          const endLine = minuteGridLines.get(interval.end);
          if (!startLine || !endLine || endLine <= startLine) return;
          const course = createBalletPlanWeekCourse(record);
          course.dataset.dayState = dayState;
          course.dataset.room = room.key;
          course.dataset.overlap = laneCount > 1 ? "true" : "false";
          course.style.gridColumn = room.key === "unknown"
            ? `${dayStartColumn} / span 2`
            : String(dayStartColumn + roomIndex);
          course.style.gridRow = `${startLine} / ${endLine}`;
          course.style.setProperty("--ballet-lane-left", `${(lane * 100) / laneCount}%`);
          course.style.setProperty("--ballet-lane-width", `${100 / laneCount}%`);
          container.appendChild(course);
        });
      },
    );
  });

  const todayIndex = days.findIndex((day) => day.date === localDateKey());
  const now = new Date();
  const nowLine = minuteGridLines.get(now.getHours() * 60 + now.getMinutes());
  if (todayIndex >= 0 && nowLine) {
    const marker = document.createElement("div");
    marker.className = "ballet-plan-week-now-line";
    marker.style.gridColumn = "2 / -1";
    marker.style.gridRow = `${nowLine} / span 1`;
    marker.setAttribute("aria-hidden", "true");
    const label = document.createElement("time");
    label.className = "ballet-plan-week-now-label";
    label.dateTime = now.toISOString();
    label.textContent = `${String(now.getHours()).padStart(2, "0")}:${String(now.getMinutes()).padStart(2, "0")}`;
    label.style.gridColumn = "1";
    label.style.gridRow = `${nowLine} / span 1`;
    label.setAttribute("aria-hidden", "true");
    container.append(marker, label);
  }
}

function renderBalletPlanWeek() {
  const container = qs("#ballet-plan-week-days");
  if (!container) return;
  const weekDates = getBalletPlanWeekDates();
  const dateSet = new Set(weekDates.map((item) => item.date));
  const actualRecords = getBalletPlanActualRecords().filter((record) => dateSet.has(record.date));
  const targets = Array.isArray(balletBookingFastData?.targets) ? balletBookingFastData.targets : [];
  const weekTargets = targets.filter((target) => dateSet.has(String(target.date || "")));
  const lastRecords = Array.isArray(balletBookingFastData?.lastRun?.records)
    ? balletBookingFastData.lastRun.records
    : [];
  const hasRunForWeek = lastRecords.some((record) => dateSet.has(balletRecordDate(record)));
  const showTargets = balletPlanWeekOffset === 1 && weekTargets.length && !hasRunForWeek;

  const weekLabel = balletPlanWeekOffset === -1 ? "上周" : balletPlanWeekOffset === 1 ? "下周" : "本周";
  setText("#ballet-plan-week-label", weekLabel);
  setText(
    "#ballet-plan-week-range",
    `${weekDates[0].date.slice(5).replace("-", "/")}–${weekDates[6].date.slice(5).replace("-", "/")}`,
  );
  const previous = qs("#ballet-plan-week-prev");
  const next = qs("#ballet-plan-week-next");
  if (previous) previous.disabled = balletPlanWeekOffset <= -1;
  if (next) next.disabled = balletPlanWeekOffset >= 1;

  container.replaceChildren();
  if (showTargets) renderBalletPlanWeekTargets(container, weekDates, weekTargets, targets);
  else renderBalletPlanWeekTimeline(container, weekDates, actualRecords);

}

function getBalletBookingResultSummary(records = []) {
  const booked = new Set(["booked", "already_booked"]);
  const waitlist = new Set(["waitlisted", "already_waitlisted", "waitlist"]);
  return records.reduce(
    (summary, record) => {
      const status = String(record.status || record.bookingStatus || "").toLowerCase();
      if (booked.has(status)) summary.booked += 1;
      else if (waitlist.has(status)) {
        summary.waitlist += 1;
        const position = Number(record.waitlistPosition);
        if (Number.isInteger(position) && position > 0) summary.positions.push(position);
      } else summary.missed += 1;
      return summary;
    },
    { booked: 0, waitlist: 0, missed: 0, positions: [] },
  );
}

function renderBalletBookingFast() {
  const statusKey = String(balletBookingFastData?.lastStatus || "waiting");
  const statusState =
    BALLET_BOOKING_FAST_STATUS[statusKey] || BALLET_BOOKING_FAST_STATUS.stopped;
  const statusNode = qs("#ballet-booking-fast-status");
  const workspaceStatusNode = qs("#ballet-booking-workspace-status");
  setText("#ballet-booking-fast-status", statusState.label);
  if (statusNode) statusNode.dataset.state = statusState.tone;
  setText("#ballet-booking-workspace-status", statusState.label);
  if (workspaceStatusNode) workspaceStatusNode.dataset.state = statusState.tone;
  setText(
    "#ballet-booking-fast-next",
    formatBalletSessionTimestamp(balletBookingFastData?.nextRunAt),
  );
  setText(
    "#ballet-booking-fast-last",
    formatBalletSessionTimestamp(balletBookingFastData?.lastAttemptAt),
  );
  setText(
    "#ballet-booking-fast-total",
    `${Math.max(0, Math.floor(balletNumber(balletBookingFastData?.totalBooked)))} 约 · ${Math.max(0, Math.floor(balletNumber(balletBookingFastData?.totalWaitlisted)))} 候`,
  );
  setText(
    "#ballet-booking-fast-priority",
    `长期规则：${balletBookingFastData?.prioritySummary || (balletBookingFastData?.priorityOrder || []).join(" > ")}`,
  );

  const targets = Array.isArray(balletBookingFastData?.targets)
    ? balletBookingFastData.targets
    : [];
  const usesWeeklyRules = balletBookingFastData?.planMode === "weekly-rules";
  const lastRecords = Array.isArray(balletBookingFastData?.lastRun?.records)
    ? balletBookingFastData.lastRun.records
    : [];
  const upcomingCount = getBalletUpcomingSummaryRecords().length;
  const grabbedCount = Math.max(
    0,
    Math.floor(balletNumber(balletBookingFastData?.totalBooked)),
  );
  const waitlistedCount = Math.max(
    0,
    Math.floor(balletNumber(balletBookingFastData?.totalWaitlisted)),
  );
  const timing = getBalletBookingTiming(balletBookingFastData?.lastRun);
  const resultSummary = getBalletBookingResultSummary(lastRecords);
  setText("#ballet-booking-result-count", `${lastRecords.length} 节课程`);
  setText(
    "#ballet-booking-result-time",
    balletBookingFastData?.lastAttemptAt
      ? formatBalletSessionTimestamp(balletBookingFastData.lastAttemptAt).replace(/^\d{4}-/, "")
      : "暂无执行",
  );
  setText("#ballet-booking-result-booked", `${resultSummary.booked} 节`);
  setText("#ballet-booking-result-waitlist", `${resultSummary.waitlist} 节`);
  setText("#ballet-booking-result-missed", `${resultSummary.missed} 节`);
  setText(
    "#ballet-booking-result-waitlist-detail",
    resultSummary.positions.length
      ? `当前排位 ${resultSummary.positions.sort((a, b) => a - b).join(" / ")}`
      : resultSummary.waitlist
        ? "候补排位待更新"
        : "本次无候补",
  );
  setText("#ballet-booking-grabbed", `${grabbedCount} 节`);
  setText("#ballet-booking-waitlisted", `${waitlistedCount} 节`);
  setText("#ballet-booking-health", statusState.label);
  setText(
    "#ballet-booking-health-detail",
    balletBookingFastData?.lastAttemptAt
      ? `最近执行 ${formatBalletSessionTimestamp(balletBookingFastData.lastAttemptAt).replace(/^\d{4}-/, "")}`
      : `下次执行 ${formatBalletSessionTimestamp(balletBookingFastData?.nextRunAt).replace(/^\d{4}-/, "")}`,
  );
  setText(
    "#ballet-booking-average",
    formatBalletBookingDuration(timing.totalMilliseconds),
  );
  setText(
    "#ballet-booking-average-detail",
    timing.targetCount && Number.isFinite(timing.averageMilliseconds)
      ? `${timing.targetCount} 个目标 · 平均 ${formatBalletBookingDuration(timing.averageMilliseconds)}/节`
      : "暂无有效执行耗时",
  );
  setText(
    "#ballet-course-plan-count",
    `${upcomingCount} 约 · ${targets.length} ${usesWeeklyRules ? "规则" : "抢"}`,
  );
  renderBalletPlanWeek();
}

function balletRecordDate(item = {}) {
  return String(item.date || item.classDate || item.startDate || item.startAt || item.startTime || "").slice(0, 10);
}

function balletStartTime(item = {}) {
  const direct = String(item.startTime || item.time || "");
  return formatTimeShort(direct || item.startAt || item.datetime || "");
}

function balletEndTime(item = {}) {
  return formatTimeShort(item.endTime || item.endAt || "");
}

function balletCourseName(item = {}) {
  return item.courseName || item.name || item.course || item.title || "未命名课程";
}

function balletTeacher(item = {}) {
  return item.teacherName || item.teacher || item.instructor || "";
}

function getBalletUpcomingRecords() {
  if (Array.isArray(balletData.upcoming)) return balletData.upcoming;
  return Array.isArray(balletData.upcoming?.records) ? balletData.upcoming.records : [];
}

function balletTimetableCourseKey(record = {}) {
  const courseName = balletCourseName(record).replace(/\s+/g, "").toLowerCase();
  return [
    balletRecordDate(record),
    balletStartTime(record),
    balletEndTime(record),
    courseName,
  ].join("|");
}

function getBalletTimetableWaitlistPosition(record = {}) {
  const directPosition = Number(record.waitlistPosition);
  if (Number.isInteger(directPosition) && directPosition > 0) return directPosition;
  const courseKey = balletTimetableCourseKey(record);
  const booking = getBalletUpcomingRecords().find(
    (item) =>
      balletTimetableCourseKey(item) === courseKey
      && String(item.bookingStatus || item.status || "").toLowerCase() === "waitlist",
  );
  const matchedPosition = Number(booking?.waitlistPosition);
  return Number.isInteger(matchedPosition) && matchedPosition > 0 ? matchedPosition : null;
}

function balletClassBoundary(item = {}) {
  const date = balletRecordDate(item);
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) return Number.NaN;
  const time = balletEndTime(item) || balletStartTime(item) || "23:59";
  if (!/^\d{2}:\d{2}$/.test(time)) return Number.NaN;
  return Date.parse(`${date}T${time}:00+08:00`);
}

function getBalletNextClass() {
  const direct = balletData.nextClass || balletData.summary?.nextClass;
  const directBoundary = balletClassBoundary(direct);
  if (direct && (!Number.isFinite(directBoundary) || directBoundary >= Date.now())) {
    return direct;
  }
  return getBalletFutureClasses()[0] || null;
}

function getBalletFutureClasses() {
  return [...getBalletUpcomingRecords()]
    .filter((item) =>
      !["cancelled", "canceled", "已取消"].includes(
        String(item.bookingStatus || item.status || "").toLowerCase(),
      ),
    )
    .filter((item) => {
      const boundary = balletClassBoundary(item);
      return !Number.isFinite(boundary) || boundary >= Date.now();
    })
    .sort((a, b) => {
      const left = `${balletRecordDate(a)}T${balletStartTime(a) || "00:00"}`;
      const right = `${balletRecordDate(b)}T${balletStartTime(b) || "00:00"}`;
      return left.localeCompare(right);
    });
}

function getBalletUpcomingSummaryRecords() {
  const today = localDateKey();
  const records = getBalletBookingSnapshotRecords().filter(
    (record) => balletRecordDate(record) >= today,
  );
  const dates = [...new Set(records.map((record) => balletRecordDate(record)).filter(Boolean))]
    .sort()
    .slice(0, 3);
  const dateSet = new Set(dates);
  return records.filter((record) => dateSet.has(balletRecordDate(record)));
}

function getBalletStatusLabel(value) {
  const status = String(value || "").trim().toLowerCase();
  if (["confirmed", "booked", "reserved", "success", "已预约", "预约成功"].includes(status)) return "已预约";
  if (["waitlist", "waiting", "candidate", "排队中", "候补", "候补中"].includes(status)) return "排队中";
  if (["completed", "attended", "已上课", "已完成"].includes(status)) return "已上课";
  if (["cancelled", "canceled", "已取消"].includes(status)) return "已取消";
  return value ? String(value) : "待确认";
}

function getBalletBookingStatusLabel(record = {}) {
  const label = getBalletStatusLabel(record.bookingStatus || record.status);
  const position = Math.max(0, Math.floor(balletNumber(record.waitlistPosition)));
  return label === "排队中" && position > 0 ? `排队第 ${position} 位` : label;
}

function formatBalletDateTime(value) {
  const parsed = parseLocalDateTime(value);
  if (!parsed) return "";
  return new Intl.DateTimeFormat("zh-CN", {
    month: "numeric",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).format(parsed);
}

function formatBalletCancellation(record = {}) {
  const deadline = formatBalletDateTime(record.cancelDeadlineAt);
  const hours = balletNumber(record.cancelHoursBefore, NaN);
  if (deadline) {
    return `最晚 ${deadline} 取消${Number.isFinite(hours) && hours > 0 ? `（课前 ${hours} 小时）` : ""}`;
  }
  const raw = String(record.cancelRuleText || "").trim();
  return raw ? `取消规则：${raw}` : "";
}

function getBalletCancellationDisplay(record = {}) {
  const knownCancellation = formatBalletCancellation(record);
  if (knownCancellation) return knownCancellation;
  if (record._planSource === "timetable" && balletRecordDate(record) === localDateKey()) {
    const classBoundary = balletClassBoundary(record);
    return Number.isFinite(classBoundary) && classBoundary < Date.now()
      ? "课程已结束"
      : "已过可取消时段";
  }
  return "取消时间未提供";
}

function getBalletUiState() {
  const sync = balletData.sync || {};
  const cacheState = String(sync.cacheState || "").toLowerCase();
  const attempt = String(sync.lastAttemptStatus || "").toLowerCase();
  const authStatus = String(balletData.authHealth?.status || balletData.authHealth || "").toLowerCase();
  const errorCode = String(sync.errorCode || balletData.authHealth?.errorCode || "")
    .toLowerCase()
    .replace(/[^a-z0-9_-]/g, "")
    .slice(0, 48);
  const browserHealth = browserDataHealth.get("ballet");
  const hasCachedData = DATA_SOURCE_OPTIONS.ballet.hasData(balletData);
  const authError = [attempt, authStatus, errorCode].some(
    (value) =>
      value.includes("auth") ||
      value.includes("session") ||
      value.includes("oauth") ||
      value.includes("forbidden") ||
      value.includes("wechat") ||
      value === "401" ||
      value === "403",
  );

  if (authError) {
    return {
      key: "auth",
      label: "需重新登录",
      title: "闻道登录态已失效",
      message: hasCachedData
        ? "仍显示最后一次成功缓存。请在电脑微信重新进入约课页面，并安全刷新服务器凭据后恢复同步。"
        : "请在电脑微信重新进入约课页面，并安全刷新服务器凭据后恢复同步。",
      hasCachedData,
    };
  }

  if (attempt && !["success", "ok", "waiting", "pending", "idle"].includes(attempt)) {
    const sourceChanged = attempt.includes("source") || attempt.includes("parse") || errorCode.includes("source") || errorCode.includes("parse");
    const networkError = attempt.includes("network") || errorCode.includes("network") || errorCode.includes("timeout");
    return {
      key: "error",
      label: "同步失败",
      title: sourceChanged ? "闻道数据结构发生变化" : networkError ? "服务器连接闻道失败" : "课程数据更新失败",
      message: hasCachedData
        ? "已停止覆盖并保留最后一次成功缓存，凭据和原始响应不会显示在页面中。"
        : "当前没有可用缓存，凭据和原始响应不会显示在页面中。",
      hasCachedData,
    };
  }

  if (browserHealth?.status === "failed") {
    return {
      key: "error",
      label: "读取失败",
      title: "暂时无法读取最新芭蕾数据",
      message: hasCachedData ? "仍显示浏览器中的最后一次成功缓存。" : "当前没有可用缓存，请稍后重新刷新 MaxNow。",
      hasCachedData,
    };
  }

  if (cacheState === "stale") {
    return {
      key: "stale",
      label: "数据过期",
      title: "课程缓存已经过期",
      message: "页面仍保留最后一次成功内容，请以闻道当前页面为准。",
      hasCachedData,
    };
  }

  if (sync.lastSuccessAt || balletData.dataAsOf || cacheState === "fresh") {
    return { key: "success", label: "已同步", title: "", message: "", hasCachedData };
  }

  return {
    key: "waiting",
    label: "等待同步",
    title: "等待首次同步",
    message: "同步成功后会显示上课记录、预约和学习趋势。",
    hasCachedData,
  };
}

function formatBalletUpdatedAt() {
  const value = balletData.dataAsOf || balletData.sync?.lastSuccessAt || "";
  return value ? formatSourceUpdatedAt(value) : "尚未同步";
}

function formatBalletUpdatedAtCompact() {
  const value = balletData.dataAsOf || balletData.sync?.lastSuccessAt || "";
  return formatTopbarUpdatedAtCompact(value);
}

function formatTopbarUpdatedAtCompact(value) {
  const text = normalizeSourceUpdatedAt(value);
  const match = text.match(/^\d{4}-(\d{2})-(\d{2})(?:\s+(\d{2}:\d{2}))?$/);
  return match
    ? `${Number(match[1])}/${Number(match[2])}${match[3] ? ` ${match[3]}` : ""}`
    : text || "尚未同步";
}

function renderTopbarDataStatus(key, data, updatedAt, updatedSelector, statusSelector) {
  const options = DATA_SOURCE_OPTIONS[key];
  const health = browserDataHealth.get(key) || dataHealthStatus(options, data);
  const updatedNode = qs(updatedSelector);
  setText(
    updatedSelector,
    updatedAt ? `更新 ${formatTopbarUpdatedAtCompact(updatedAt)}` : "数据尚未更新",
  );
  if (updatedNode) {
    updatedNode.title = updatedAt ? `完整更新时间：${formatSourceUpdatedAt(updatedAt)}` : "数据尚未更新";
    if (updatedAt) updatedNode.setAttribute("datetime", updatedAt);
    else updatedNode.removeAttribute("datetime");
  }

  setText(statusSelector, health.statusLabel);
  const statusNode = qs(statusSelector);
  if (statusNode) statusNode.dataset.state = health.status;
}

function getBalletSummary() {
  const summary = balletData.summary || {};
  const anchor = String(balletData.dataAsOf || balletData.sync?.lastSuccessAt || new Date().toISOString());
  const monthKey = anchor.slice(0, 7);
  const currentMonth =
    (balletData.aggregates?.monthly || []).find((item) => String(item.period || item.month || "") === monthKey) ||
    summary.currentMonth ||
    summary.month ||
    {};
  const now = new Date();
  const startOfWeek = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  startOfWeek.setDate(startOfWeek.getDate() - ((startOfWeek.getDay() + 6) % 7));
  const endOfWeek = new Date(startOfWeek);
  endOfWeek.setDate(endOfWeek.getDate() + 7);
  const weekClasses = (balletData.records || []).filter((record) => {
    const value = parseLocalDateTime(balletRecordDate(record));
    return value && value >= startOfWeek && value < endOfWeek;
  }).length;
  return {
    totalClasses: balletNumber(summary.classes ?? summary.totalClasses ?? summary.classCount),
    totalMinutes: Number.isFinite(Number(summary.minutes ?? summary.totalMinutes))
      ? Number(summary.minutes ?? summary.totalMinutes)
      : null,
    unknownDurationClasses: balletNumber(summary.missingDurationClasses ?? summary.unknownDurationClasses),
    monthClasses: balletNumber(currentMonth.classes ?? currentMonth.totalClasses ?? summary.currentMonthClasses),
    monthMinutes: Number.isFinite(Number(currentMonth.minutes ?? currentMonth.totalMinutes ?? summary.currentMonthMinutes))
      ? Number(currentMonth.minutes ?? currentMonth.totalMinutes ?? summary.currentMonthMinutes)
      : null,
    weekClasses: balletNumber(summary.currentWeek?.classes ?? summary.weekClasses ?? weekClasses),
  };
}

function normalizeBalletDistribution(source, kind) {
  const items = Array.isArray(source)
    ? source
    : source && typeof source === "object"
      ? Object.entries(source).map(([key, value]) =>
          value && typeof value === "object" ? { key, ...value } : { key, classes: value },
        )
      : [];
  const labels =
    kind === "level"
      ? BALLET_LEVEL_LABELS
      : kind === "courseType"
        ? BALLET_COURSE_TYPE_LABELS
        : {};
  const normalized = items
    .map((item) => {
      const key = String(item.key || item.id || item.courseType || item.level || item.label || "").toLowerCase();
      return {
        key,
        label: item.label || labels[key] || item.name || item.courseType || item.level || key || "其他",
        classes: balletNumber(item.classes ?? item.totalClasses ?? item.count ?? item.value),
        minutes: balletMinutes(item),
      };
    })
    .filter((item) => item.classes > 0 || Number(item.minutes) > 0);

  if (kind !== "level" && kind !== "levelDisplay") {
    return normalized.sort((a, b) => b.classes - a.classes || a.label.localeCompare(b.label, "zh-CN"));
  }
  const order = new Map(
    ["L1", "L1.5", "L2", "L3", "L4", "L5", "芭蕾", "软开", "肌肉素质", "技术技巧", "其他"]
      .map((label, index) => [label, index]),
  );
  return normalized.sort(
    (a, b) => (order.get(a.label) ?? 99) - (order.get(b.label) ?? 99) || b.classes - a.classes,
  );
}

function balletTrainingLevelLabel(record = {}) {
  const levelKey = String(record.level || "").trim().toLowerCase();
  if (!BALLET_NO_LEVEL_KEYS.has(levelKey)) {
    return BALLET_LEVEL_LABELS[levelKey] || String(record.level || "").trim();
  }
  const courseTypeKey = String(record.courseType || "").trim().toLowerCase();
  return BALLET_COURSE_TYPE_LABELS[courseTypeKey] || balletCourseName(record) || "其他";
}

function getBalletBreakdownRecords(aggregate = {}) {
  const period = String(aggregate.period || "");
  return (Array.isArray(balletData.records) ? balletData.records : []).filter((record) => {
    if (!isBalletCompletedRecord(record)) return false;
    const date = balletRecordDate(record);
    if (activeBalletPeriod === "all") return true;
    return Boolean(period && date.startsWith(period));
  });
}

function aggregateBalletBreakdown(records, kind) {
  const buckets = new Map();
  records.forEach((record) => {
    const label =
      kind === "teacher"
        ? balletTeacher(record) || "老师待确认"
        : balletTrainingLevelLabel(record);
    const item = buckets.get(label) || {
      key: `${kind}:${label}`,
      label,
      classes: 0,
      minutes: 0,
    };
    item.classes += 1;
    item.minutes += balletMinutes(record) || 0;
    buckets.set(label, item);
  });
  return [...buckets.values()];
}

function getBalletTrainingBreakdowns(aggregate = {}) {
  const records = getBalletBreakdownRecords(aggregate);
  return {
    levels: Array.isArray(aggregate.byLevelDisplay)
      ? aggregate.byLevelDisplay
      : aggregateBalletBreakdown(records, "levelDisplay"),
    teachers: Array.isArray(aggregate.byTeacher)
      ? aggregate.byTeacher
      : aggregateBalletBreakdown(records, "teacher"),
  };
}

function createBalletBarItem(item, maxValue) {
  const article = document.createElement("article");
  article.className = "ballet-bar-item";
  const isClasses = activeBalletMetric === "classes";
  const itemValue = isClasses ? item.classes : (item.minutes || 0) / 60;
  const head = document.createElement("div");
  const label = document.createElement("strong");
  const value = document.createElement("span");
  label.textContent = item.label;
  value.textContent = isClasses ? `${item.classes} 节` : `${formatBalletHours(item.minutes)} 小时`;
  head.append(label, value);
  const track = document.createElement("div");
  track.className = "ballet-bar-track";
  const fill = document.createElement("span");
  fill.style.width = `${Math.max(4, (itemValue / Math.max(1, maxValue)) * 100)}%`;
  track.append(fill);
  article.append(head, track);
  return article;
}

function renderBalletDistribution(selector, source, kind) {
  const container = qs(selector);
  if (!container) return [];
  const items = normalizeBalletDistribution(source, kind);
  container.replaceChildren();
  if (!items.length) {
    container.appendChild(emptyTemplate.content.cloneNode(true));
    return items;
  }
  const maxValue = Math.max(
    ...items.map((item) => activeBalletMetric === "classes" ? item.classes : (item.minutes || 0) / 60),
    1,
  );
  container.append(...items.map((item) => createBalletBarItem(item, maxValue)));
  return items;
}

function getBalletSelectedAggregate() {
  const aggregates = balletData.aggregates || {};
  const now = new Date();
  const year = String(now.getFullYear());
  const month = `${year}-${String(now.getMonth() + 1).padStart(2, "0")}`;
  if (activeBalletPeriod === "month") {
    return (aggregates.monthly || []).find((item) => String(item.period || "") === month) || {
      period: month,
      classes: 0,
      minutes: 0,
      byCourseType: [],
      byLevel: [],
      byLevelDisplay: [],
      byTeacher: [],
    };
  }
  if (activeBalletPeriod === "year") {
    return (aggregates.yearly || []).find((item) => String(item.period || "") === year) || {
      period: year,
      classes: 0,
      minutes: 0,
      byCourseType: [],
      byLevel: [],
      byLevelDisplay: [],
      byTeacher: [],
    };
  }
  return balletData.summary || {
    period: "all",
    classes: 0,
    minutes: 0,
    byCourseType: [],
    byLevel: [],
    byLevelDisplay: [],
    byTeacher: [],
  };
}

function normalizeBalletTrendEntries(source, granularity) {
  if (!Array.isArray(source)) return [];
  return source
    .map((item) => {
      const date = String(
        item.date || item.day || item.month || item.year || item.period || item.label || "",
      ).slice(0, granularity === "year" ? 4 : granularity === "month" ? 7 : 10);
      return {
        date,
        classes: balletNumber(item.classes ?? item.totalClasses ?? item.count),
        minutes: balletNumber(item.minutes ?? item.totalMinutes),
      };
    })
    .filter((item) => item.date);
}

function aggregateBalletRecords(granularity) {
  const buckets = new Map();
  (balletData.records || []).forEach((record) => {
    const date = balletRecordDate(record);
    if (!date) return;
    const key = granularity === "year" ? date.slice(0, 4) : granularity === "month" ? date.slice(0, 7) : date;
    const bucket = buckets.get(key) || { date: key, classes: 0, minutes: 0 };
    bucket.classes += 1;
    bucket.minutes += balletMinutes(record) || 0;
    buckets.set(key, bucket);
  });
  return [...buckets.values()].sort((a, b) => a.date.localeCompare(b.date));
}

function fillBalletMonths(entries, year, monthCount = 12) {
  const byDate = new Map(entries.map((entry) => [entry.date, entry]));
  const visibleMonthCount = Math.max(1, Math.min(12, Math.floor(Number(monthCount)) || 12));
  return Array.from({ length: visibleMonthCount }, (_, index) => {
    const date = `${year}-${String(index + 1).padStart(2, "0")}`;
    return byDate.get(date) || { date, classes: 0, minutes: 0 };
  });
}

function fillBalletDays(entries, month) {
  const [year, monthNumber] = month.split("-").map(Number);
  if (!year || !monthNumber) return entries;
  const days = new Date(year, monthNumber, 0).getDate();
  const byDate = new Map(entries.map((entry) => [entry.date, entry]));
  return Array.from({ length: days }, (_, index) => {
    const date = `${month}-${String(index + 1).padStart(2, "0")}`;
    return byDate.get(date) || { date, classes: 0, minutes: 0 };
  });
}

function getBalletTrend() {
  const aggregates = balletData.aggregates || {};
  const today = localDateKey();
  const year = today.slice(0, 4);
  const month = today.slice(0, 7);
  const coverageDate = String(balletData.dataAsOf || balletData.sync?.lastSuccessAt || today).slice(0, 10);
  let entries = [];
  let title = "";
  let xFormatter = (record) => record.date;
  let chartType = "line";

  if (activeBalletPeriod === "month") {
    const daily = normalizeBalletTrendEntries(aggregates.daily, "day");
    entries = daily.length ? daily.filter((entry) => entry.date.startsWith(month)) : aggregateBalletRecords("day").filter((entry) => entry.date.startsWith(month));
    entries = fillBalletDays(entries, month);
    title = `${Number(month.slice(5, 7))} 月`;
    xFormatter = (record) => record.date.slice(8);
    chartType = "heatmap";
  } else if (activeBalletPeriod === "year") {
    const monthly = normalizeBalletTrendEntries(aggregates.monthly, "month");
    entries = monthly.length ? monthly.filter((entry) => entry.date.startsWith(year)) : aggregateBalletRecords("month").filter((entry) => entry.date.startsWith(year));
    entries = fillBalletMonths(entries, year, Number(month.slice(5, 7)));
    title = `${year} 年`;
    xFormatter = (record) => `${Number(record.date.slice(5, 7))}月`;
  } else {
    const yearly = normalizeBalletTrendEntries(aggregates.yearly, "year");
    entries = (yearly.length ? yearly : aggregateBalletRecords("year"))
      .filter((entry) => entry.classes > 0 || entry.minutes > 0);
    xFormatter = (record) => record.date;
    title = "历年";
  }

  return { entries, title, xFormatter, chartType, coverageDate, month };
}

function balletHeatmapLevel(value, maxValue) {
  if (!value || value <= 0 || maxValue <= 0) return 0;
  return Math.max(1, Math.min(5, Math.ceil((value / maxValue) * 5)));
}

function createBalletMonthHeatmap(records, options = {}) {
  const weekdays = ["一", "二", "三", "四", "五", "六", "日"];
  const firstDate = records[0]?.date || `${options.month}-01`;
  const firstDay = new Date(`${firstDate}T12:00:00`).getDay();
  const leadingBlanks = (firstDay + 6) % 7;
  const maxValue = Math.max(...records.map((record) => Number(record.value) || 0), 0);
  const isClasses = options.metric === "classes";
  const cellValue = (record) => isClasses
    ? `${Math.round(record.value)} 节`
    : `${record.value.toFixed(record.value >= 10 ? 1 : 2).replace(/\.?0+$/, "")} h`;
  const cells = [
    ...Array.from({ length: leadingBlanks }, () => '<span class="ballet-heatmap-cell is-blank" aria-hidden="true"></span>'),
    ...records.map((record) => {
      const uncovered = /^\d{4}-\d{2}-\d{2}$/.test(options.coverageDate)
        && record.date > options.coverageDate
        && record.classes <= 0;
      const level = uncovered ? 0 : balletHeatmapLevel(record.value, maxValue);
      const day = Number(record.date.slice(8, 10));
      const title = uncovered
        ? `${record.date} 尚未纳入同步`
        : `${record.date} ${cellValue(record)}`;
      return `
        <span class="ballet-heatmap-cell" data-level="${level}"${uncovered ? ' data-uncovered="true"' : ""} title="${escapeHtml(title)}" aria-label="${escapeHtml(title)}">
          <span class="ballet-heatmap-day">${day}</span>
          <strong>${uncovered ? "—" : escapeHtml(cellValue(record))}</strong>
        </span>
      `;
    }),
  ];

  return `
    <div class="ballet-month-heatmap" role="img" aria-label="${escapeHtml(options.title)}">
      <div class="ballet-heatmap-weekdays" aria-hidden="true">
        ${weekdays.map((weekday) => `<span>周${weekday}</span>`).join("")}
      </div>
      <div class="ballet-heatmap-grid">${cells.join("")}</div>
      <div class="ballet-heatmap-legend" aria-hidden="true">
        <span>少</span>
        ${Array.from({ length: 5 }, (_, index) => `<i data-level="${index + 1}"></i>`).join("")}
        <span>多</span>
        <em><i data-uncovered="true"></i>尚未纳入同步</em>
      </div>
    </div>
  `;
}

function renderBalletTrend() {
  qsa("[data-ballet-period]").forEach((button) => {
    const active = button.dataset.balletPeriod === activeBalletPeriod;
    button.classList.toggle("is-active", active);
    button.setAttribute("aria-pressed", String(active));
  });
  qsa("[data-ballet-metric]").forEach((button) => {
    const active = button.dataset.balletMetric === activeBalletMetric;
    button.classList.toggle("is-active", active);
    button.setAttribute("aria-pressed", String(active));
  });

  const { entries, title, xFormatter, chartType, coverageDate, month } = getBalletTrend();
  const isClasses = activeBalletMetric === "classes";
  const records = entries.map((entry) => ({
    ...entry,
    value: isClasses ? entry.classes : entry.minutes / 60,
  }));
  const sampleCount = records.reduce((total, entry) => total + balletNumber(entry.classes), 0);
  const hasTrainingRecords = balletNumber(balletData.summary?.classes) > 0
    || aggregateBalletRecords("day").length > 0;
  const trend = qs("#ballet-training-trend");
  const placeholder = qs("#ballet-trend-placeholder");
  const showTrend = chartType === "heatmap" ? hasTrainingRecords : sampleCount > 0;
  if (trend) trend.hidden = !showTrend;
  if (placeholder) {
    placeholder.hidden = showTrend;
    placeholder.textContent = chartType === "heatmap"
      ? "当前还没有可用于月度热力图的上课记录。"
      : "当前时间范围还没有可用于曲线图的上课记录。";
  }
  const label = isClasses ? "上课节数" : "训练小时";
  const chartTitle = `${title}${label}${chartType === "heatmap" ? "热力图" : ""}`;
  setText("#ballet-trend-title", chartTitle);
  const chart = qs("#ballet-trend-chart");
  const detailGrid = qs(".ballet-training-detail-grid");
  const compactChartWidth = chartType === "heatmap"
    ? 840
    : Math.min(840, Math.max(420, records.length * 84 + 104));
  detailGrid?.style.setProperty("--ballet-training-chart-column-width", `${compactChartWidth}px`);
  if (!chart || !showTrend) return;
  chart.classList.toggle("is-heatmap", chartType === "heatmap");
  chart.classList.toggle("is-compact-line", chartType !== "heatmap");
  if (!records.length) {
    chart.innerHTML = `<p class="empty-state">当前时间范围还没有可用统计。</p>`;
    return;
  }
  if (chartType === "heatmap") {
    chart.style.removeProperty("--ballet-trend-chart-width");
    chart.innerHTML = createBalletMonthHeatmap(records, {
      title: chartTitle,
      month,
      coverageDate,
      metric: activeBalletMetric,
    });
    return;
  }
  chart.style.setProperty("--ballet-trend-chart-width", `${compactChartWidth}px`);
  const labelInterval = activeBalletPeriod === "month" ? 5 : entries.length > 24 ? 6 : 1;
  chart.innerHTML = createLineChart(records, {
    key: "value",
    title: chartTitle,
    unit: isClasses ? "节" : "h",
    formatter: (value) => (isClasses ? `${Math.round(value)}` : value.toFixed(value >= 10 ? 1 : 2).replace(/\.?0+$/, "")),
    yFormatter: (value) => (isClasses ? `${Math.round(value)}` : value.toFixed(1).replace(/\.0$/, "")),
    integerYScale: isClasses,
    stroke: "#c44778",
    width: compactChartWidth,
    xFormatter,
    labelInterval,
  });
}

function renderBalletTraining() {
  const aggregate = getBalletSelectedAggregate();
  const breakdowns = getBalletTrainingBreakdowns(aggregate);
  const periodLabel = {
    month: "本月",
    year: "今年",
    all: "全部",
  }[activeBalletPeriod] || "全部";
  const classes = balletNumber(aggregate.classes);
  const minutes = balletNumber(aggregate.minutes);
  const isClasses = activeBalletMetric === "classes";
  setText("#ballet-training-period", `${periodLabel}上课`);
  setText("#ballet-training-value", isClasses ? classes : formatBalletHours(minutes));
  setText("#ballet-training-unit", isClasses ? "节" : "小时");
  setText("#ballet-training-secondary", `共 ${classes} 节 · ${formatBalletHours(minutes)} 小时`);
  const courseTypes = renderBalletDistribution(
    "#ballet-course-types",
    aggregate.byCourseType,
    "courseType",
  );
  const levels = renderBalletDistribution(
    "#ballet-levels",
    breakdowns.levels,
    "levelDisplay",
  );
  const teachers = renderBalletDistribution(
    "#ballet-teachers",
    breakdowns.teachers,
    "teacher",
  );
  setText("#ballet-course-type-count", `${courseTypes.length} 类`);
  setText("#ballet-level-count", `${levels.length} 项`);
  setText("#ballet-teacher-count", `${teachers.length} 位`);
  renderBalletTrend();
}

function createBalletCalendarIcon(className = "") {
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("viewBox", "0 0 24 24");
  svg.setAttribute("aria-hidden", "true");
  svg.classList.add("ballet-membership-calendar-icon");
  if (className) svg.classList.add(className);
  [
    ["rect", { x: "3.5", y: "5.5", width: "17", height: "15", rx: "3" }],
    ["path", { d: "M7.5 3.5v4M16.5 3.5v4M3.5 10h17" }],
    ["path", { d: "M8 14h2M14 14h2M8 17h2M14 17h2" }],
  ].forEach(([tag, attributes]) => {
    const node = document.createElementNS("http://www.w3.org/2000/svg", tag);
    Object.entries(attributes).forEach(([key, value]) => node.setAttribute(key, value));
    svg.appendChild(node);
  });
  return svg;
}

function balletMembershipDisplayName(card = {}) {
  const rawName = String(card.name || "课程卡").trim();
  const formatted = rawName.replace(/\s*-\s*(?=\d+\s*次$)/, " · ");
  return /^芭蕾/.test(formatted) ? formatted : `芭蕾${formatted}`;
}

function createBalletMembershipItem(card = {}, activeCardCount = 1) {
  const article = document.createElement("article");
  article.className = "ballet-membership-item";

  const ticketHead = document.createElement("div");
  ticketHead.className = "ballet-membership-ticket-head";
  const ticketTitle = document.createElement("div");
  const ticketEyebrow = document.createElement("p");
  ticketEyebrow.className = "eyebrow";
  ticketEyebrow.textContent = "Course Card";
  const ticketHeading = document.createElement("h2");
  ticketHeading.textContent = "课程卡";
  ticketTitle.append(ticketEyebrow, ticketHeading);
  const ticketStatus = document.createElement("span");
  ticketStatus.className = "status-pill";
  ticketStatus.textContent = `${activeCardCount} 张有效卡`;
  ticketHead.append(ticketTitle, ticketStatus);

  const artwork = document.createElement("div");
  artwork.className = "ballet-membership-artwork";
  artwork.setAttribute("aria-hidden", "true");
  const artworkImage = document.createElement("img");
  artworkImage.src = "./assets/ballet/membership-ballerina.webp";
  artworkImage.alt = "";
  artwork.appendChild(artworkImage);
  const header = document.createElement("header");
  const title = document.createElement("div");
  const eyebrow = document.createElement("p");
  const name = document.createElement("h3");
  const period = document.createElement("small");
  eyebrow.className = "eyebrow";
  eyebrow.textContent = "Active Card";
  name.textContent = balletMembershipDisplayName(card);
  period.className = "ballet-membership-period";
  period.textContent = card.validFrom ? `${formatDateOnly(card.validFrom)} 开卡` : "开卡日期待同步";
  title.append(eyebrow, name, period);
  const validity = document.createElement("span");
  validity.className = "ballet-membership-validity";
  validity.append(
    createBalletCalendarIcon(),
    document.createTextNode(
      card.validThrough ? `有效至 ${String(card.validThrough).slice(0, 10)}` : "有效期待同步",
    ),
  );
  header.append(title, validity);

  const pace = card.pace || {};
  const usedClasses = Math.max(0, Math.floor(balletNumber(card.usedClasses)));
  const totalClasses = Math.max(0, Math.floor(balletNumber(card.totalClasses)));
  const remainingClasses = Math.max(0, Math.floor(balletNumber(card.remainingClasses)));
  const openDayNumber = Math.max(0, Math.floor(balletNumber(pace.openDayNumber)));
  const validityDays = Math.max(0, Math.floor(balletNumber(pace.validityDays)));
  const usageProgress = totalClasses > 0 ? Math.min(100, (usedClasses / totalClasses) * 100) : 0;
  const validityProgress = validityDays > 0 ? Math.min(100, (openDayNumber / validityDays) * 100) : 0;
  const metrics = document.createElement("div");
  metrics.className = "ballet-membership-metrics";

  const usage = document.createElement("section");
  usage.className = "ballet-membership-usage";
  usage.dataset.tone = "rose";
  const usageLabel = document.createElement("span");
  usageLabel.textContent = "课程使用";
  const usageValue = document.createElement("div");
  usageValue.className = "ballet-membership-usage-value";
  usageValue.setAttribute("aria-label", `已用 ${usedClasses} / ${totalClasses} 节`);
  const usagePrefix = document.createElement("b");
  usagePrefix.textContent = "已用";
  const usageCurrent = document.createElement("strong");
  usageCurrent.textContent = String(usedClasses);
  const usageTotal = document.createElement("b");
  usageTotal.textContent = `/ ${totalClasses} 节`;
  usageValue.append(usagePrefix, usageCurrent, usageTotal);
  const usageTrack = document.createElement("div");
  usageTrack.className = "ballet-membership-usage-track";
  usageTrack.setAttribute("role", "progressbar");
  usageTrack.setAttribute("aria-label", "课程卡已使用课次");
  usageTrack.setAttribute("aria-valuemin", "0");
  usageTrack.setAttribute("aria-valuemax", String(totalClasses));
  usageTrack.setAttribute("aria-valuenow", String(usedClasses));
  const usageFill = document.createElement("span");
  usageFill.style.width = `${usageProgress}%`;
  usageFill.style.minWidth = usageProgress > 0 ? "8px" : "0";
  usageTrack.appendChild(usageFill);
  const usageDetail = document.createElement("small");
  usageDetail.textContent = `剩余 ${remainingClasses} 节`;
  usage.append(usageLabel, usageValue, usageTrack, usageDetail);

  const validityMetric = document.createElement("section");
  validityMetric.className = "ballet-membership-validity-metric";
  validityMetric.dataset.tone = "rose";
  const validityCopy = document.createElement("div");
  validityCopy.className = "ballet-membership-validity-copy";
  const validityLabel = document.createElement("span");
  validityLabel.textContent = "有效进度";
  const validityValue = document.createElement("div");
  validityValue.className = "ballet-membership-day-value";
  if (openDayNumber > 0) {
    const dayPrefix = document.createElement("b");
    dayPrefix.textContent = "第";
    const dayCurrent = document.createElement("strong");
    dayCurrent.className = "ballet-membership-day-current";
    dayCurrent.textContent = String(openDayNumber);
    const dayTotal = document.createElement("b");
    dayTotal.className = "ballet-membership-day-total";
    dayTotal.textContent = `/ ${validityDays} 天`;
    validityValue.append(dayPrefix, dayCurrent, dayTotal);
  } else {
    const unopened = document.createElement("b");
    unopened.textContent = "尚未开卡";
    validityValue.appendChild(unopened);
  }
  const validityDetail = document.createElement("small");
  validityDetail.textContent = `到期前需 ${balletNumber(pace.requiredClassesPerWeek).toFixed(1)} 节/周`;
  validityCopy.append(validityLabel, validityValue, validityDetail);
  const validityRing = document.createElement("div");
  validityRing.className = "ballet-membership-day-ring";
  validityRing.style.setProperty("--membership-day-progress", `${validityProgress}%`);
  validityRing.setAttribute("role", "img");
  validityRing.setAttribute("aria-label", `课程卡有效期第 ${openDayNumber} / ${validityDays} 天`);
  const ringCurrent = document.createElement("strong");
  ringCurrent.textContent = String(openDayNumber);
  const ringTotal = document.createElement("small");
  ringTotal.textContent = `/${validityDays}`;
  validityRing.append(ringCurrent, ringTotal);
  validityMetric.append(validityCopy, validityRing);
  metrics.append(usage, validityMetric);

  const verdict = document.createElement("div");
  verdict.className = "ballet-membership-verdict";
  const verdictIcon = document.createElement("span");
  verdictIcon.className = "ballet-membership-verdict-icon";
  verdictIcon.appendChild(createBalletCalendarIcon());
  const verdictBody = document.createElement("div");
  verdictBody.className = "ballet-membership-verdict-body";
  const verdictTitle = document.createElement("strong");
  const verdictCopy = document.createElement("p");
  const plannedRate = Math.max(0, Math.floor(balletNumber(pace.recommendedWholeClassesPerWeek)));
  if (!remainingClasses) {
    verdict.dataset.state = "success";
    verdictTitle.textContent = "课程卡课次已用完";
    verdictCopy.textContent = "当前没有剩余课次需要安排。";
  } else if (balletNumber(pace.remainingDays) <= 0) {
    verdict.dataset.state = "attention";
    verdictTitle.textContent = "课程卡已到期";
    verdictCopy.textContent = `到期时仍剩 ${remainingClasses} 节。`;
  } else {
    verdict.dataset.state = "plan";
    verdictTitle.textContent = `按每周 ${plannedRate} 节，预计 ${formatDateOnly(pace.plannedFinishDate)} 用完`;
    verdictCopy.textContent = `预计比到期早 ${Math.floor(balletNumber(pace.plannedBufferDays))} 天`;
    if (pace.sampleSufficient && Number.isFinite(Number(pace.observedClassesPerWeek))) {
      const observed = document.createElement("p");
      const observedRate = balletNumber(pace.observedClassesPerWeek).toFixed(1);
      observed.textContent = pace.observedCanFinish
        ? `开卡后实际 ${observedRate} 节/周，按此预计 ${formatDateOnly(pace.observedFinishDate)} 用完。`
        : `开卡后实际 ${observedRate} 节/周，到期预计约剩 ${Math.floor(balletNumber(pace.observedProjectedRemainingAtExpiry))} 节。`;
      verdictBody.append(verdictTitle, verdictCopy, observed);
      verdict.append(verdictIcon, verdictBody);
      article.append(artwork, ticketHead, header, metrics, verdict);
      return article;
    }
  }
  verdictBody.append(verdictTitle, verdictCopy);
  verdict.append(verdictIcon, verdictBody);
  article.append(artwork, ticketHead, header, metrics, verdict);
  return article;
}

function renderBalletMembership() {
  const cards = Array.isArray(balletData.membership?.cards) ? balletData.membership.cards : [];
  const container = qs("#ballet-membership-list");
  if (!container) return;
  container.replaceChildren();
  if (!cards.length) {
    container.appendChild(emptyTemplate.content.cloneNode(true));
    return;
  }
  container.append(...cards.map((card) => createBalletMembershipItem(card, cards.length)));
}

function balletTrainingCompletedAt(record = {}) {
  const date = balletRecordDate(record);
  const endTime = String(record.endTime || "").trim();
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date) || !/^\d{2}:\d{2}$/.test(endTime)) {
    return Number.NaN;
  }
  return Date.parse(`${date}T${endTime}:00+08:00`);
}

function getBalletCompletedTrainingRecords(requestedCutoff = Number.POSITIVE_INFINITY) {
  const sourceCutoff = Date.parse(String(balletData.dataAsOf || balletData.sync?.lastSuccessAt || ""));
  if (!Number.isFinite(sourceCutoff)) return [];
  const cutoff = Math.min(sourceCutoff, Number(requestedCutoff));
  return (Array.isArray(balletData.records) ? balletData.records : []).filter((record) => {
    const status = String(record.attendanceStatus || record.status || "").trim().toLowerCase();
    const completedAt = balletTrainingCompletedAt(record);
    return (
      ["attended", "completed", "已上完", "已完成"].includes(status)
      && Number.isFinite(completedAt)
      && completedAt <= cutoff
    );
  });
}

function getBalletFavoriteCourse(records = []) {
  const courses = new Map();
  records.forEach((record) => {
    const label = balletCourseName(record);
    if (!label) return;
    const key = label.replace(/\s+/g, " ").trim().toLocaleLowerCase("zh-CN");
    const completedAt = balletTrainingCompletedAt(record);
    const current = courses.get(key) || { label, classes: 0, latestCompletedAt: 0 };
    current.classes += 1;
    if (completedAt >= current.latestCompletedAt) {
      current.label = label;
      current.latestCompletedAt = completedAt;
    }
    courses.set(key, current);
  });
  return [...courses.values()].sort(
    (left, right) =>
      right.classes - left.classes
      || right.latestCompletedAt - left.latestCompletedAt
      || left.label.localeCompare(right.label, "zh-CN"),
  )[0] || null;
}

function summarizeBalletTraining(records = []) {
  return {
    classes: records.length,
    minutes: records.reduce((total, record) => total + (balletMinutes(record) || 0), 0),
    favorite: getBalletFavoriteCourse(records),
  };
}

function getBalletWeeklyBriefSummary(config = BALLET_WEEK_FALLBACK_CONFIG, date = new Date()) {
  const info = getBalletWeeklyBriefInfo(config, date);
  const sourceAsOf = String(balletData.dataAsOf || balletData.sync?.lastSuccessAt || "");
  const sourceCutoff = Date.parse(sourceAsOf);
  const completedRecords = getBalletCompletedTrainingRecords(info.cutoff);
  const weekRecords = completedRecords.filter((record) => {
    const recordDate = balletRecordDate(record);
    return recordDate >= info.monday && recordDate <= info.sunday;
  });
  return {
    info,
    sourceAsOf,
    sourceReachedCutoff: Number.isFinite(sourceCutoff) && sourceCutoff >= Date.parse(info.refreshAt),
    completedRecords: completedRecords.length,
    week: summarizeBalletTraining(weekRecords),
    total: summarizeBalletTraining(completedRecords),
  };
}

function setBalletFavoriteCourse(valueSelector, metaSelector, favorite) {
  setText(valueSelector, favorite?.label || "暂无");
  setText(metaSelector, favorite ? `已上 ${favorite.classes} 次` : "暂无已上完课程");
}

function renderBalletWeek() {
  const week = balletData.week || {};
  const start = String(week.weekStart || "");
  const end = String(week.weekEnd || "");
  setText(
    "#ballet-week-range",
    start && end ? `${Number(start.slice(5, 7))}/${Number(start.slice(8, 10))}–${Number(end.slice(5, 7))}/${Number(end.slice(8, 10))}` : "本周",
  );
  const completedRecords = getBalletCompletedTrainingRecords();
  const weekRecords = start && end
    ? completedRecords.filter((record) => {
        const date = balletRecordDate(record);
        return date >= start && date <= end;
      })
    : [];
  const weekSummary = summarizeBalletTraining(weekRecords);
  const totalSummary = summarizeBalletTraining(completedRecords);
  if (balletWeekBriefCache?.sourceAsOf !== String(balletData.dataAsOf || balletData.sync?.lastSuccessAt || "")) {
    balletWeekBriefCache = null;
  }
  setText("#ballet-week-classes", `${weekSummary.classes} 次`);
  setText("#ballet-week-hours", `${formatBalletHours(weekSummary.minutes)} 小时`);
  setBalletFavoriteCourse(
    "#ballet-week-favorite",
    "#ballet-week-favorite-meta",
    weekSummary.favorite,
  );
  setText("#ballet-total-classes", `${totalSummary.classes} 次`);
  setText("#ballet-total-hours", `${formatBalletHours(totalSummary.minutes)} 小时`);
  setBalletFavoriteCourse(
    "#ballet-total-favorite",
    "#ballet-total-favorite-meta",
    totalSummary.favorite,
  );
}

function normalizeBalletLevel(value) {
  const key = String(value || "").trim().toLowerCase();
  return BALLET_LEVEL_LABELS[key] || "";
}

function isBalletCompletedRecord(record = {}) {
  const status = String(record.attendanceStatus || record.status || "").trim().toLowerCase();
  return !["cancelled", "canceled", "absent", "no_show", "已取消", "未到课"].includes(status);
}

function getBalletGrowthRecords() {
  return (Array.isArray(balletData.records) ? balletData.records : []).filter(isBalletCompletedRecord);
}

function getBalletPromotionLevelState(balletRecords, currentLevel) {
  const levelRecords = balletRecords.filter(
    (record) => normalizeBalletLevel(record.level) === currentLevel,
  );
  const completed = levelRecords.length;
  const rule = BALLET_PROMOTION_RULES[currentLevel] || BALLET_PROMOTION_RULES.L1;
  const anchorValue = String(
    balletData.dataAsOf || balletData.sync?.lastSuccessAt || new Date().toISOString(),
  ).slice(0, 10);
  const anchor = Date.parse(`${anchorValue}T23:59:59+08:00`);
  const datedRecords = levelRecords
    .map((record) => Date.parse(`${balletRecordDate(record)}T12:00:00+08:00`))
    .filter(Number.isFinite)
    .sort((a, b) => a - b);
  const firstAt = datedRecords[0];
  const observationDays = Number.isFinite(firstAt) && Number.isFinite(anchor)
    ? Math.min(28, Math.max(1, Math.floor((anchor - firstAt) / 86400000) + 1))
    : 0;
  const recentStart = Number.isFinite(anchor) ? anchor - 27 * 86400000 : Number.NaN;
  const recentClasses = datedRecords.filter(
    (timestamp) => !Number.isFinite(recentStart) || timestamp >= recentStart,
  ).length;
  const weeklyRate = observationDays > 0 ? (recentClasses / observationDays) * 7 : 0;
  const sampleSufficient = observationDays >= 21;
  const hasMetRegularTarget = datedRecords.some((timestamp, index, allDates) => {
    if (index + 1 < rule.regular) return false;
    const historicalFirstAt = allDates[0];
    const historicalObservationDays = Math.min(
      28,
      Math.max(1, Math.floor((timestamp - historicalFirstAt) / 86400000) + 1),
    );
    if (historicalObservationDays < 21) return false;
    const historicalRecentStart = timestamp - 27 * 86400000;
    const historicalRecentClasses = allDates
      .slice(0, index + 1)
      .filter((historicalTimestamp) => historicalTimestamp >= historicalRecentStart)
      .length;
    return (historicalRecentClasses / historicalObservationDays) * 7 >= 2;
  });
  const isRegular = hasMetRegularTarget || (sampleSufficient && weeklyRate >= 2);
  const target = isRegular ? rule.regular : rule.intermittent;
  return {
    currentLevel,
    nextLevel: rule.next,
    completed,
    target,
    remaining: Math.max(0, target - completed),
    regularTarget: rule.regular,
    intermittentTarget: rule.intermittent,
    sampleSufficient,
    isRegular,
    isFinal: !rule.next,
  };
}

function getBalletPromotionState(records) {
  const balletRecords = records.filter(
    (record) =>
      String(record.courseType || "").toLowerCase() === "ballet" &&
      BALLET_PROMOTION_RULES[normalizeBalletLevel(record.level)],
  );
  const recordedLevel = balletRecords.reduce((highest, record) => {
    const level = normalizeBalletLevel(record.level);
    return BALLET_LEVEL_ORDER.indexOf(level) > BALLET_LEVEL_ORDER.indexOf(highest)
      ? level
      : highest;
  }, "L1");
  let promotion = getBalletPromotionLevelState(balletRecords, recordedLevel);
  const promotedLevels = [];
  while (!promotion.isFinal && promotion.completed >= promotion.target) {
    promotedLevels.push(promotion.currentLevel);
    promotion = getBalletPromotionLevelState(balletRecords, promotion.nextLevel);
  }
  return {
    ...promotion,
    recordedLevel,
    promotedLevels,
    autoPromoted: promotedLevels.length > 0,
  };
}

function getBalletGrowthLevelState(records) {
  const completed = records.length;
  const current =
    [...BALLET_GROWTH_LEVELS].reverse().find((level) => completed >= level.threshold) ||
    BALLET_GROWTH_LEVELS[0];
  const currentIndex = BALLET_GROWTH_LEVELS.indexOf(current);
  const next = BALLET_GROWTH_LEVELS[currentIndex + 1] || null;
  const levelCompleted = next ? Math.max(0, completed - current.threshold) : 1;
  const levelTarget = next ? Math.max(1, next.threshold - current.threshold) : 1;
  return {
    completed,
    current,
    next,
    levelCompleted,
    levelTarget,
    remaining: next ? Math.max(0, next.threshold - completed) : 0,
  };
}

function renderBalletSwanLevel(level) {
  const stage = qs("#ballet-swan-stage");
  if (!stage) return;
  const safeLevel = Math.max(1, Math.min(10, Math.floor(balletNumber(level, 1))));
  const icon = qs("#ballet-swan-icon");
  stage.dataset.level = String(safeLevel);
  stage.setAttribute("aria-label", `小天鹅成长等级 Lv.${safeLevel}`);
  if (icon) icon.src = `./assets/ballet/swan-lv${safeLevel}.png`;
}

function updateBalletGrowthProgress(selector, fillSelector, value, maximum) {
  const progress = qs(selector);
  const safeMaximum = Math.max(1, Math.floor(balletNumber(maximum, 1)));
  const safeValue = Math.max(0, Math.floor(balletNumber(value)));
  if (progress) {
    progress.setAttribute("aria-valuemax", String(safeMaximum));
    progress.setAttribute("aria-valuenow", String(Math.min(safeValue, safeMaximum)));
  }
  const fill = qs(fillSelector);
  if (fill) fill.style.width = `${Math.min(100, (safeValue / safeMaximum) * 100)}%`;
}

function renderBalletGrowth() {
  const records = getBalletGrowthRecords();
  const promotion = getBalletPromotionState(records);
  const growth = getBalletGrowthLevelState(records);

  setText(
    "#ballet-promotion-title",
    promotion.isFinal
      ? `${promotion.currentLevel} · 已满级`
      : `${promotion.currentLevel} → ${promotion.nextLevel}`,
  );
  setText(
    "#ballet-promotion-count",
    promotion.isFinal
      ? `本级已上 ${promotion.completed} 节`
      : `已上 ${promotion.completed} / ${promotion.target} 节`,
  );
  setText(
    "#ballet-promotion-rhythm",
    promotion.isFinal
      ? "课程等级已到最高级"
      : `再上 ${promotion.remaining} 节升级到 ${promotion.nextLevel}`,
  );
  setText(
    "#ballet-promotion-note",
    promotion.isFinal
      ? "后续课次继续累计，页面不会回退课程等级。"
      : promotion.autoPromoted
        ? `已自动进入 ${promotion.currentLevel}，本级课次重新累计。`
        : promotion.isRegular
          ? "当前采用规律课次标准。"
          : promotion.sampleSufficient
            ? `当前采用保守课次标准；恢复规律训练后目标可降至 ${promotion.regularTarget} 节。`
            : `当前采用保守课次标准；连续 3 周每周至少 2 节后改用 ${promotion.regularTarget} 节标准。`,
  );
  updateBalletGrowthProgress(
    "#ballet-promotion-progress",
    "#ballet-promotion-progress-fill",
    promotion.isFinal ? Math.max(1, promotion.completed) : promotion.completed,
    promotion.isFinal ? Math.max(1, promotion.completed) : promotion.target,
  );

  setText("#ballet-level-title", `Lv.${growth.current.level}`);
  setText(
    "#ballet-growth-class-count",
    growth.next
      ? `本级 ${growth.levelCompleted} / ${growth.levelTarget} 节`
      : `已累计 ${growth.completed} 节`,
  );
  setText(
    "#ballet-level-next",
    growth.next ? `还差 ${growth.remaining} 节升级到 Lv.${growth.next.level}` : "已满级",
  );
  updateBalletGrowthProgress(
    "#ballet-level-progress",
    "#ballet-level-progress-fill",
    growth.levelCompleted,
    growth.levelTarget,
  );
  renderBalletSwanLevel(growth.current.level);
}

function createBalletHistoryItem(record) {
  const article = document.createElement("article");
  article.className = "ballet-history-item";
  const date = document.createElement("time");
  date.textContent = balletRecordDate(record) || "--";
  const main = document.createElement("div");
  const title = document.createElement("strong");
  const meta = document.createElement("small");
  title.textContent = balletCourseName(record);
  const timeRange = [balletStartTime(record), balletEndTime(record)].filter(Boolean).join("–");
  meta.textContent = [balletTeacher(record), timeRange].filter(Boolean).join(" · ") || "课程详情待补";
  main.append(title, meta);
  const tags = document.createElement("div");
  tags.className = "ballet-history-meta";
  const courseType = record.courseType ? BALLET_COURSE_TYPE_LABELS[String(record.courseType).toLowerCase()] || record.courseType : "";
  const level = balletTrainingLevelLabel(record);
  const duration = balletMinutes(record);
  [
    courseType,
    level !== courseType ? level : "",
    Number.isFinite(duration) ? `${formatBalletHours(duration)}h` : "时长待补",
    record.recordOrigin === "manual" ? "手动添加" : "",
  ]
    .filter(Boolean)
    .forEach((value) => {
      const span = document.createElement("span");
      span.textContent = value;
      tags.appendChild(span);
    });
  article.append(date, main, tags);
  return article;
}

function getBalletHistoryPeriodLabel() {
  return {
    month: "本月",
    year: "今年",
    all: "全部",
  }[activeBalletPeriod] || "全部";
}

function getBalletHistoryRecords() {
  const today = localDateKey();
  const period = activeBalletPeriod === "month"
    ? today.slice(0, 7)
    : activeBalletPeriod === "year"
      ? today.slice(0, 4)
      : "";
  return [...(balletData.records || [])]
    .filter((record) => {
      if (!isBalletCompletedRecord(record)) return false;
      return !period || balletRecordDate(record).startsWith(period);
    })
    .sort((a, b) => {
      const aKey = `${balletRecordDate(a)}T${balletStartTime(a) || "00:00"}`;
      const bKey = `${balletRecordDate(b)}T${balletStartTime(b) || "00:00"}`;
      return bKey.localeCompare(aKey);
    });
}

function createBalletHistoryPreviewItem(record) {
  const article = document.createElement("article");
  article.className = "ballet-history-preview-item";
  const dateValue = balletRecordDate(record);
  const date = document.createElement("time");
  if (dateValue) date.dateTime = dateValue;
  date.textContent = dateValue ? dateValue.slice(5) : "--";
  const main = document.createElement("div");
  const title = document.createElement("strong");
  const meta = document.createElement("small");
  const timeRange = [balletStartTime(record), balletEndTime(record)].filter(Boolean).join("–");
  title.textContent = balletCourseName(record);
  meta.textContent = [balletTeacher(record), timeRange].filter(Boolean).join(" · ") || "课程详情待补";
  main.append(title, meta);
  article.append(date, main);
  return article;
}

function renderBalletHistory() {
  const records = getBalletHistoryRecords();
  const periodLabel = getBalletHistoryPeriodLabel();
  const previewLimit = window.matchMedia("(max-width: 560px)").matches ? 3 : 8;
  setText("#ballet-history-count", `共 ${records.length} 节`);
  setText("#ballet-history-dialog-summary", `${periodLabel} · 共 ${records.length} 节`);

  const preview = qs("#ballet-history-preview");
  if (preview) {
    preview.replaceChildren();
    if (!records.length) {
      const empty = document.createElement("p");
      empty.className = "ballet-history-preview-empty";
      empty.textContent = `${periodLabel}暂无上课记录`;
      preview.appendChild(empty);
    } else {
      preview.append(...records.slice(0, previewLimit).map(createBalletHistoryPreviewItem));
    }
  }

  const openButton = qs("#ballet-history-open");
  if (openButton) {
    const hasMore = records.length > previewLimit;
    openButton.hidden = !hasMore;
    openButton.disabled = !hasMore;
  }

  const container = qs("#ballet-history");
  if (!container) return;
  container.replaceChildren();
  if (!records.length) {
    container.appendChild(emptyTemplate.content.cloneNode(true));
    return;
  }
  container.append(...records.map(createBalletHistoryItem));
}

function createBalletUpcomingItem(record) {
  const article = document.createElement("article");
  article.className = "ballet-upcoming-item";
  const date = document.createElement("time");
  const dateText = balletRecordDate(record);
  const parsedDate = parseLocalDateTime(dateText);
  date.className = "ballet-upcoming-date";
  if (dateText) date.dateTime = dateText;
  const dateLabel = document.createElement("strong");
  const weekdayLabel = document.createElement("span");
  dateLabel.textContent = dateText
    ? `${Number(dateText.slice(5, 7))}月${Number(dateText.slice(8, 10))}日`
    : "--";
  weekdayLabel.textContent = parsedDate
    ? new Intl.DateTimeFormat("zh-CN", { weekday: "long" }).format(parsedDate)
    : "--";
  date.append(dateLabel, weekdayLabel);
  const main = document.createElement("div");
  const title = document.createElement("strong");
  const meta = document.createElement("small");
  title.textContent = balletCourseName(record);
  const timeRange = [balletStartTime(record), balletEndTime(record)].filter(Boolean).join("–");
  const venue = String(record.venue || "").trim();
  meta.textContent = [
    timeRange,
    balletTeacher(record),
    venue,
  ].filter(Boolean).join(" · ") || "课程详情待补";
  const cancellation = document.createElement("small");
  cancellation.className = "ballet-upcoming-note";
  cancellation.textContent = getBalletCancellationDisplay(record);
  main.append(title, meta);
  const tags = document.createElement("div");
  tags.className = "ballet-history-meta";
  const bookingLabel = getBalletBookingStatusLabel(record);
  [
    {
      label: bookingLabel,
      status: bookingLabel.startsWith("排队第") || bookingLabel === "排队中" ? "waitlist" : bookingLabel === "已预约" ? "booked" : "",
    },
    {
      label: balletTrainingLevelLabel(record),
      status: "",
    },
  ]
    .filter((item) => item.label)
    .forEach((item) => {
      const span = document.createElement("span");
      span.textContent = item.label;
      if (item.status) span.dataset.bookingStatus = item.status;
      tags.appendChild(span);
    });
  article.append(date, main, cancellation, tags);
  return article;
}

function renderBalletUpcoming() {
  const panel = qs("#ballet-upcoming-panel");
  const container = qs("#ballet-upcoming-list");
  if (!panel || !container) return;
  const records = getBalletUpcomingSummaryRecords();
  panel.hidden = false;
  setText("#ballet-upcoming-count", `${records.length} 节`);
  container.replaceChildren();
  if (!records.length) {
    container.appendChild(emptyTemplate.content.cloneNode(true));
    return;
  }
  const items = records.map(createBalletUpcomingItem);
  const nearestIndex = records.findIndex((record) => {
    const boundary = balletClassBoundary(record);
    return !Number.isFinite(boundary) || boundary >= Date.now();
  });
  if (nearestIndex >= 0) {
    const nearest = document.createElement("span");
    nearest.className = "ballet-upcoming-nearest";
    nearest.textContent = "最近一节";
    items[nearestIndex].classList.add("is-nearest");
    items[nearestIndex].querySelector(".ballet-history-meta")?.prepend(nearest);
  }
  container.append(...items);
}

function getBalletTimetableDayState(dateText) {
  const today = localDateKey();
  if (dateText === today) return "today";
  return dateText < today ? "past" : "future";
}

function isBalletTimetableAttended(record = {}) {
  const courseName = balletCourseName(record).replace(/\s+/g, "").toLowerCase();
  return (Array.isArray(balletData.records) ? balletData.records : []).some(
    (item) =>
      balletRecordDate(item) === balletRecordDate(record)
      && balletStartTime(item) === balletStartTime(record)
      && balletEndTime(item) === balletEndTime(record)
      && balletCourseName(item).replace(/\s+/g, "").toLowerCase() === courseName,
  );
}

function getBalletTimetableStatus(record = {}) {
  const labels = {
    available: "可约",
    booked: "已预约",
    attended: "已上完",
    waitlist: "排队中",
    queue_available: "可排队",
    full: "已满",
    cancelled: "已取消",
    past: "已过",
  };
  const key = isBalletTimetableAttended(record)
    ? "attended"
    : String(record.availability || "available").toLowerCase();
  const waitlistPosition = key === "waitlist"
    ? getBalletTimetableWaitlistPosition(record)
    : null;
  return {
    key,
    label: waitlistPosition ? `排队中 ${waitlistPosition}` : labels[key] || "待确认",
  };
}

function getBalletTimetableCounts(record = {}) {
  const bookedCount = Number(record.bookedCount);
  const capacity = Number(record.capacity);
  if (
    !Number.isInteger(bookedCount)
    || bookedCount < 0
    || !Number.isInteger(capacity)
    || capacity <= 0
  ) {
    return null;
  }
  const rawWaitlistCount = record.waitlistCount;
  const waitlistCount = Number(rawWaitlistCount);
  const hasWaitlistCount = rawWaitlistCount !== null
    && rawWaitlistCount !== undefined
    && rawWaitlistCount !== ""
    && Number.isInteger(waitlistCount)
    && waitlistCount >= 0;
  return {
    capacity: `${bookedCount}/${capacity} 人`,
    waitlist: hasWaitlistCount ? `排队 ${waitlistCount}` : "",
    accessible: `报名 ${bookedCount}/${capacity} 人${hasWaitlistCount ? `，排队 ${waitlistCount} 人` : ""}`,
  };
}

function createBalletTimetableCourse(record, mobile = false, options = {}) {
  const article = document.createElement("article");
  article.className = mobile ? "ballet-timetable-course is-mobile" : "ballet-timetable-course";
  article.dataset.courseType = String(record.courseType || "other").toLowerCase();
  article.dataset.level = String(record.level || "none").toLowerCase();
  article.dataset.compact = Number(record.durationMinutes) <= 60 ? "true" : "false";
  const status = getBalletTimetableStatus(record);
  article.dataset.availability = status.key;

  const title = document.createElement("strong");
  title.textContent = balletCourseName(record);
  const meta = document.createElement("small");
  meta.className = "ballet-timetable-meta";
  const detail = document.createElement("small");
  detail.className = "ballet-timetable-meta-detail ballet-timetable-teacher";
  const timeText = [balletStartTime(record), balletEndTime(record)].filter(Boolean).join("–") || "时间待确认";
  const detailText = [balletTeacher(record) || "老师待确认", timeText].join(" · ");
  detail.textContent = detailText;
  const counts = options.includeCounts === false
    ? null
    : getBalletTimetableCounts(record);
  if (counts) {
    const capacity = document.createElement("span");
    capacity.className = "ballet-timetable-capacity";
    capacity.textContent = counts.capacity;
    meta.append(capacity);
    if (counts.waitlist) {
      const waitlist = document.createElement("span");
      waitlist.className = "ballet-timetable-waitlist";
      waitlist.textContent = counts.waitlist;
      meta.append(waitlist);
    }
  }
  const foot = document.createElement("div");
  const state = document.createElement("span");
  state.className = "ballet-timetable-state";
  state.textContent = status.label;
  state.dataset.availability = status.key;
  foot.append(state);
  article.append(title, detail);
  if (counts) {
    article.append(meta);
  }
  article.append(foot);
  article.title = [
    balletCourseName(record),
    timeText,
    balletTeacher(record),
    record.venue,
    counts?.accessible,
    status.label,
  ].filter(Boolean).join(" · ");
  return article;
}

const BALLET_TIMETABLE_ROOMS = [
  { key: "large", label: "大教室" },
  { key: "small", label: "小教室" },
];

function balletTimetableRoomKey(record = {}) {
  const venue = String(record.venue || "").replace(/\s+/g, "");
  if (venue.includes("大教室")) return "large";
  if (venue.includes("小教室")) return "small";
  return "unknown";
}

function createBalletTimetableRoomHeader(room, dayState) {
  const header = document.createElement("div");
  header.className = "ballet-timetable-room";
  header.dataset.room = room.key;
  header.dataset.dayState = dayState;
  header.textContent = room.label;
  return header;
}

function createBalletTimetableDayHeader(day, index) {
  const header = document.createElement("div");
  const dateText = String(day.date || "");
  const parsed = parseLocalDateTime(dateText);
  const state = getBalletTimetableDayState(dateText);
  header.className = "ballet-timetable-day";
  header.dataset.dayState = state;
  header.dataset.tone = String(index % 6);
  const weekday = document.createElement("strong");
  weekday.textContent =
    state === "today"
      ? "今天"
      : parsed
        ? new Intl.DateTimeFormat("zh-CN", { weekday: "short" }).format(parsed)
        : "--";
  const date = document.createElement("span");
  date.textContent = dateText
    ? `${Number(dateText.slice(5, 7))}/${Number(dateText.slice(8, 10))}`
    : "--";
  header.append(weekday, date);
  return header;
}

function balletTimetableStartHour(record = {}) {
  const minutes = balletTimetableMinutesFromTime(balletStartTime(record));
  return minutes === null ? null : Math.floor(minutes / 60);
}

function balletTimetableMinutesFromTime(value) {
  const match = String(value || "").match(/^(\d{2}):(\d{2})$/);
  if (!match) return null;
  const hour = Number(match[1]);
  const minute = Number(match[2]);
  if (
    !Number.isInteger(hour) ||
    !Number.isInteger(minute) ||
    hour < 0 ||
    hour > 23 ||
    minute < 0 ||
    minute > 59
  ) {
    return null;
  }
  return hour * 60 + minute;
}

function balletTimetableInterval(record = {}) {
  const start = balletTimetableMinutesFromTime(balletStartTime(record));
  if (start === null) return null;

  const parsedEnd = balletTimetableMinutesFromTime(balletEndTime(record));
  const fallbackDuration = balletMinutes(record) || 60;
  const end = parsedEnd !== null && parsedEnd > start ? parsedEnd : start + fallbackDuration;
  return {
    start,
    end: Math.min(end, 24 * 60),
  };
}

function layoutBalletTimetableRecords(records = []) {
  const items = records
    .map((record) => ({ record, interval: balletTimetableInterval(record) }))
    .filter((item) => item.interval)
    .sort(
      (left, right) =>
        left.interval.start - right.interval.start ||
        left.interval.end - right.interval.end,
    );

  const groups = [];
  let group = [];
  let groupEnd = -1;
  items.forEach((item) => {
    if (group.length && item.interval.start >= groupEnd) {
      groups.push(group);
      group = [];
      groupEnd = -1;
    }
    group.push(item);
    groupEnd = Math.max(groupEnd, item.interval.end);
  });
  if (group.length) groups.push(group);

  groups.forEach((overlapGroup) => {
    const laneEnds = [];
    overlapGroup.forEach((item) => {
      let lane = laneEnds.findIndex((end) => end <= item.interval.start);
      if (lane === -1) {
        lane = laneEnds.length;
        laneEnds.push(item.interval.end);
      } else {
        laneEnds[lane] = item.interval.end;
      }
      item.lane = lane;
    });
    overlapGroup.forEach((item) => {
      item.laneCount = Math.max(1, laneEnds.length);
    });
  });

  return {
    items,
    laneCount: Math.max(1, ...items.map((item) => item.laneCount || 1)),
  };
}

function formatBalletTimetableHour(hour) {
  return `${String(hour).padStart(2, "0")}:00`;
}

function buildBalletTimetableRows(days = []) {
  const intervals = days.flatMap((day) =>
    (Array.isArray(day.records) ? day.records : [])
      .map(balletTimetableInterval)
      .filter(Boolean),
  );
  if (!intervals.length) return [];

  const firstHour = Math.floor(Math.min(...intervals.map((interval) => interval.start)) / 60);
  const lastHour = Math.ceil(Math.max(...intervals.map((interval) => interval.end)) / 60);
  const occupiedHours = new Set();
  for (let hour = firstHour; hour < lastHour; hour += 1) {
    const hourStart = hour * 60;
    const hourEnd = hourStart + 60;
    if (intervals.some((interval) => interval.start < hourEnd && interval.end > hourStart)) {
      occupiedHours.add(hour);
    }
  }

  const rows = [];
  for (let hour = firstHour; hour < lastHour;) {
    if (occupiedHours.has(hour)) {
      rows.push({
        type: "hour",
        hour,
        trackCount: 60,
        label: formatBalletTimetableHour(hour),
      });
      hour += 1;
      continue;
    }

    const gapStart = hour;
    while (hour < lastHour && !occupiedHours.has(hour)) hour += 1;
    rows.push({
      type: "gap",
      trackCount: 1,
      startHour: gapStart,
      endHour: hour,
      label: `${formatBalletTimetableHour(gapStart)}–${formatBalletTimetableHour(hour)}`,
    });
  }
  return rows;
}

function renderBalletTimetable() {
  const timetable = balletData.timetable || {};
  const days = Array.isArray(timetable.days)
    ? timetable.days
        .filter((day) => /^\d{4}-\d{2}-\d{2}$/.test(String(day?.date || "")))
        .sort((a, b) => String(a.date).localeCompare(String(b.date)))
    : [];
  const grid = qs("#ballet-timetable-grid");
  const mobile = qs("#ballet-timetable-mobile");
  if (!grid || !mobile) return;

  const courseCount = days.reduce(
    (total, day) => total + (Array.isArray(day.records) ? day.records.length : 0),
    0,
  );
  setText("#ballet-timetable-count", days.length ? `${days.length} 天 · ${courseCount} 节` : "等待同步");
  grid.replaceChildren();
  mobile.replaceChildren();

  if (!days.length) {
    grid.appendChild(emptyTemplate.content.cloneNode(true));
    mobile.appendChild(emptyTemplate.content.cloneNode(true));
    setText("#ballet-timetable-note", "同步完成后显示本周课程。");
    return;
  }

  const rows = buildBalletTimetableRows(days);
  grid.style.setProperty("--ballet-day-count", String(days.length));
  const timeRows = rows
    .map((row) =>
      row.type === "gap"
        ? "30px"
        : "repeat(60, var(--ballet-minute-height))",
    )
    .join(" ");
  grid.style.setProperty("--ballet-time-rows", timeRows);
  let nextGridLine = 3;
  const minuteGridLines = new Map();
  const layoutRows = rows.map((row) => {
    const startLine = nextGridLine;
    const endLine = startLine + row.trackCount;
    nextGridLine = endLine;
    if (row.type === "hour") {
      for (let minute = 0; minute <= 60; minute += 1) {
        minuteGridLines.set(row.hour * 60 + minute, startLine + minute);
      }
    } else {
      minuteGridLines.set(row.startHour * 60, startLine);
      minuteGridLines.set(row.endHour * 60, endLine);
    }
    return { ...row, startLine, endLine };
  });

  const corner = document.createElement("div");
  corner.className = "ballet-timetable-corner";
  corner.textContent = "时间";
  corner.style.gridColumn = "1";
  corner.style.gridRow = "1 / 3";
  const dayHeaders = days.map((day, index) => {
    const header = createBalletTimetableDayHeader(day, index);
    header.style.gridColumn = `${index * 2 + 2} / span 2`;
    header.style.gridRow = "1";
    return header;
  });
  const roomHeaders = days.flatMap((day, index) => {
    const dayState = getBalletTimetableDayState(day.date);
    return BALLET_TIMETABLE_ROOMS.map((room, roomIndex) => {
      const header = createBalletTimetableRoomHeader(room, dayState);
      header.style.gridColumn = String(index * 2 + roomIndex + 2);
      header.style.gridRow = "2";
      return header;
    });
  });
  const timeHeaders = layoutRows.map((row, index) => {
    const time = document.createElement("div");
    time.className = "ballet-timetable-time";
    time.dataset.rowType = row.type;
    time.dataset.rowEdge =
      layoutRows.length === 1
        ? "both"
        : index === 0
          ? "start"
          : index === layoutRows.length - 1
            ? "end"
            : "middle";
    const timeLabel = document.createElement("span");
    timeLabel.className = "ballet-timetable-time-label";
    timeLabel.textContent = row.label;
    time.appendChild(timeLabel);
    time.style.gridColumn = "1";
    time.style.gridRow = `${row.startLine} / ${row.endLine}`;
    return time;
  });
  const finalRow = layoutRows[layoutRows.length - 1];
  const terminalItems = [];
  if (finalRow) {
    const finalHour =
      finalRow.type === "gap" ? finalRow.endHour : Number(finalRow.hour) + 1;
    const endTime = document.createElement("div");
    endTime.className = "ballet-timetable-time ballet-timetable-end-time";
    endTime.dataset.rowType = "end";
    endTime.style.gridColumn = "1";
    endTime.style.gridRow = `${nextGridLine} / span 1`;
    const endTimeLabel = document.createElement("span");
    endTimeLabel.className = "ballet-timetable-time-label";
    endTimeLabel.textContent = formatBalletTimetableHour(finalHour);
    endTime.appendChild(endTimeLabel);
    const endSpacer = document.createElement("div");
    endSpacer.className = "ballet-timetable-end-spacer";
    endSpacer.style.gridColumn = "2 / -1";
    endSpacer.style.gridRow = `${nextGridLine} / span 1`;
    terminalItems.push(endTime, endSpacer);
  }
  grid.append(
    corner,
    ...dayHeaders,
    ...roomHeaders,
    ...timeHeaders,
    ...terminalItems,
  );

  days.forEach((day, index) => {
    const records = Array.isArray(day.records) ? day.records : [];
    const dayState = getBalletTimetableDayState(day.date);
    const dayStartColumn = index * 2 + 2;
    BALLET_TIMETABLE_ROOMS.forEach((room, roomIndex) => {
      layoutRows.forEach((row, rowIndex) => {
        const cell = document.createElement("div");
        cell.className = "ballet-timetable-cell";
        cell.dataset.dayState = dayState;
        cell.dataset.room = room.key;
        cell.dataset.rowType = row.type;
        cell.dataset.rowEdge =
          layoutRows.length === 1
            ? "both"
            : rowIndex === 0
              ? "start"
              : rowIndex === layoutRows.length - 1
                ? "end"
                : "middle";
        cell.style.gridColumn = String(dayStartColumn + roomIndex);
        cell.style.gridRow = `${row.startLine} / ${row.endLine}`;
        grid.appendChild(cell);
      });
    });

    [...BALLET_TIMETABLE_ROOMS, { key: "unknown", label: "未标注教室" }].forEach(
      (room, roomIndex) => {
        const roomRecords = records.filter(
          (record) => balletTimetableRoomKey(record) === room.key,
        );
        const recordLayout = layoutBalletTimetableRecords(roomRecords);
        recordLayout.items.forEach(({ record, interval, lane, laneCount }) => {
          const startLine = minuteGridLines.get(interval.start);
          const endLine = minuteGridLines.get(interval.end);
          if (!startLine || !endLine || endLine <= startLine) return;
          const course = createBalletTimetableCourse(record);
          course.dataset.dayState = dayState;
          course.dataset.room = room.key;
          course.dataset.overlap = laneCount > 1 ? "true" : "false";
          course.style.gridColumn =
            room.key === "unknown"
              ? `${dayStartColumn} / span 2`
              : String(dayStartColumn + roomIndex);
          course.style.gridRow = `${startLine} / ${endLine}`;
          course.style.setProperty("--ballet-lane-left", `${(lane * 100) / laneCount}%`);
          course.style.setProperty("--ballet-lane-width", `${100 / laneCount}%`);
          grid.appendChild(course);
        });
      },
    );
  });

  const todayIndex = days.findIndex((day) => String(day.date) === localDateKey());
  const now = new Date();
  const nowLine = minuteGridLines.get(now.getHours() * 60 + now.getMinutes());
  if (todayIndex >= 0 && nowLine) {
    const marker = document.createElement("div");
    marker.className = "ballet-timetable-now-line";
    marker.style.gridColumn = "2 / -1";
    marker.style.gridRow = `${nowLine} / span 1`;
    marker.setAttribute("aria-hidden", "true");
    const label = document.createElement("time");
    label.className = "ballet-timetable-now-label";
    label.dateTime = now.toISOString();
    label.textContent = `${String(now.getHours()).padStart(2, "0")}:${String(now.getMinutes()).padStart(2, "0")}`;
    label.style.gridColumn = "1";
    label.style.gridRow = `${nowLine} / span 1`;
    label.setAttribute("aria-hidden", "true");
    grid.append(marker, label);
  }

  days.forEach((day, index) => {
    const group = document.createElement("section");
    group.className = "ballet-timetable-mobile-day";
    group.dataset.dayState = getBalletTimetableDayState(day.date);
    const header = createBalletTimetableDayHeader(day, index);
    const records = Array.isArray(day.records) ? day.records : [];
    const count = document.createElement("span");
    count.className = "status-pill";
    count.textContent = `${records.length} 节`;
    header.appendChild(count);
    group.appendChild(header);
    if (records.length) {
      [...BALLET_TIMETABLE_ROOMS, { key: "unknown", label: "未标注教室" }].forEach(
        (room) => {
          const roomRecords = records
            .filter((record) => balletTimetableRoomKey(record) === room.key)
            .sort(
              (left, right) =>
                String(balletStartTime(left)).localeCompare(String(balletStartTime(right))),
            );
          if (!roomRecords.length) return;
          const roomGroup = document.createElement("div");
          roomGroup.className = "ballet-timetable-mobile-room";
          roomGroup.dataset.room = room.key;
          const roomHeader = document.createElement("div");
          roomHeader.className = "ballet-timetable-mobile-room-head";
          const roomName = document.createElement("strong");
          roomName.textContent = room.label;
          const roomCount = document.createElement("span");
          roomCount.textContent = `${roomRecords.length} 节`;
          roomHeader.append(roomName, roomCount);
          roomGroup.append(
            roomHeader,
            ...roomRecords.map((record) => createBalletTimetableCourse(record, true)),
          );
          group.appendChild(roomGroup);
        },
      );
    } else {
      const empty = document.createElement("p");
      empty.className = "ballet-timetable-empty";
      empty.textContent = "当天暂无课程";
      group.appendChild(empty);
    }
    mobile.appendChild(group);
  });

  const through = String(timetable.availableThrough || "");
  const throughLabel = through
    ? `${Number(through.slice(5, 7))}月${Number(through.slice(8, 10))}日`
    : "本周";
  setText(
    "#ballet-timetable-note",
    timetable.displayMode === "sunday_plus_next_week"
      ? `已切换为今天（周日）与下周课表 · 课程发布至 ${throughLabel}`
      : `课程发布至 ${throughLabel} · 每天 09 / 12 / 15 / 18 / 22 点更新，周日 14:30 检查下周课表`,
  );
}

function renderBalletHome() {
  const state = getBalletUiState();
  const summary = getBalletSummary();
  const nextClass = getBalletNextClass();
  setText("#home-ballet-status", state.label);
  const statusNode = qs("#home-ballet-status");
  if (statusNode) statusNode.dataset.state = state.key;
  qs("#home-ballet-card")?.setAttribute("data-health", state.key);
  setText("#home-ballet-progress", `累计 ${summary.totalClasses || "--"} 节 · ${formatBalletHours(summary.totalMinutes)} 小时`);
  setText("#home-ballet-updated", formatBalletUpdatedAt());

  if (!nextClass) {
    setText("#home-ballet-next-time", "下一节 · --");
    setText("#home-ballet-next-course", state.key === "success" ? "暂无后续预约" : "等待课程数据");
    setText("#home-ballet-next-meta", state.key === "success" ? `本周已上 ${summary.weekClasses} 节` : state.message);
    return;
  }
  const dateText = balletRecordDate(nextClass);
  const time = balletStartTime(nextClass);
  setText("#home-ballet-next-time", `下一节 · ${dateText ? `${Number(dateText.slice(5, 7))}/${Number(dateText.slice(8, 10))}` : "--"} ${time || ""}`.trim());
  setText("#home-ballet-next-course", balletCourseName(nextClass));
  setText(
    "#home-ballet-next-meta",
    [getBalletBookingStatusLabel(nextClass), balletTeacher(nextClass)].filter(Boolean).join(" · "),
  );
}

function renderBallet() {
  const state = getBalletUiState();
  const updatedValue = balletData.dataAsOf || balletData.sync?.lastSuccessAt || "";
  setText(
    "#ballet-updated",
    updatedValue
      ? `更新 ${formatBalletUpdatedAtCompact()}`
      : "数据尚未更新",
  );
  const updatedNode = qs("#ballet-updated");
  if (updatedNode) {
    updatedNode.title = updatedValue ? `完整更新时间：${formatBalletUpdatedAt()}` : "数据尚未更新";
    if (updatedValue) updatedNode.setAttribute("datetime", updatedValue);
    else updatedNode.removeAttribute("datetime");
  }
  setText("#ballet-connection-status", state.label);
  const connectionStatus = qs("#ballet-connection-status");
  if (connectionStatus) connectionStatus.dataset.state = state.key;

  const alert = qs("#ballet-sync-alert");
  const shouldShowAlert = ["auth", "error", "stale"].includes(state.key);
  if (alert) alert.hidden = !shouldShowAlert;
  if (shouldShowAlert) {
    setText("#ballet-sync-alert-title", state.title);
    setText("#ballet-sync-alert-message", state.message);
    if (alert) alert.dataset.state = state.key;
  }

  renderBalletBookingFast();
  renderBalletMembership();
  renderBalletWeek();
  renderBalletGrowth();
  renderBalletUpcoming();
  renderBalletTimetable();
  renderBalletTraining();
  renderBalletHistory();
  renderBalletHome();
  scheduleBalletWeeklyBriefGeneration();
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
  setText("#last30-source", last30Data.updatedAt ? `${copy.updatedAtShort} ${last30Data.updatedAt}` : copy.syncWaiting);
  renderWeather();

  const syncStatus = getDataSyncStatus();
  setText("#metric-today-execution", `${todayTodos.length} \u4e2a`);
  setText("#metric-today-execution-note", todayTodos[0]?.title || copy.noTodayExecution);
  setText("#metric-sync", syncStatus.label);
  setText("#metric-sync-note", syncStatus.note);
  qs(".metric-sync")?.setAttribute("data-health", syncStatus.health);
  const syncMetric = qs(".metric-sync");
  if (syncMetric) {
    syncMetric.title = syncStatus.items
      .map((item) => `${item.label}: ${item.statusLabel}${item.updatedAt ? ` (${formatSourceUpdatedAt(item.updatedAt)})` : ""}`)
      .join("\n");
  }
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
  renderBalletHome();
  renderBalletBookingFast();
  renderBalletSessionExperiment();
  renderWikiTodos(openTodos);
  renderLast30Column("today", "#last30-today-list");
  renderLast30Column("week", "#last30-week-list");
  renderLast30Column("mainlines", "#last30-mainline-list");
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

  renderTopbarDataStatus(
    "token",
    tokenUsageData,
    usage.updatedAt,
    "#token-updated",
    "#token-connection-status",
  );
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

async function readJson(url, fallback, sourceKey) {
  try {
    const response = await fetch(url, { cache: "no-cache" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    if (sourceKey) {
      saveLastGood(sourceKey, data);
      updateBrowserDataHealth(sourceKey, data);
    }
    return data;
  } catch (error) {
    const cached = sourceKey ? readLastGood(sourceKey) : null;
    const data = cached || fallback;
    if (sourceKey) updateBrowserDataHealth(sourceKey, data, error.message || String(error));
    return data;
  }
}

async function readWikiTodo() {
  const data = await readJson(WIKI_TODO_URL, fallbackWikiTodo, "wiki");
  const health = browserDataHealth.get("wiki");
  wikiTodoError = health?.status === "failed"
    ? health.updatedAt
      ? "请求失败，正在展示最后一次成功数据"
      : "请求失败，当前没有可用数据"
    : "";
  return data;
}

function getActiveView() {
  return document.body.dataset.view || "home";
}

function renderActiveView() {
  const view = getActiveView();
  if (view === "home" || view === "cloud") renderHome();
  if (view === "dounai") renderDounai();
  if (view === "tokens") renderTokens();
  if (view === "ballet") renderBallet();
  if (view === "ricky") renderRicky();
  if (view === "life") renderLife();
}

async function loadHomeData({ force = false } = {}) {
  if (!force && homeDataPromise) return homeDataPromise;

  homeDataPromise = Promise.all([
    readJson(DATA_URL, window.MAXNOW_DASHBOARD_DATA || fallbackData, "weather"),
    readJson(LAST30_URL, window.MAXNOW_LAST30_DATA || fallbackLast30, "last30"),
    readWikiTodo(),
    readJson(CHECKIN_URL, fallbackCheckin, "dounai"),
    readJson(MARKET_INDICES_URL, window.MAXNOW_MARKET_INDICES_DATA || fallbackMarketIndices, "market"),
    readJson(PROJECT_META_URL, window.MAXNOW_PROJECT_META_DATA || fallbackProjectMeta, "version"),
    readJson(PROJECT_STATUS_URL, window.MAXNOW_PROJECT_STATUS_DATA || fallbackProjectStatus, "roadmap"),
    readJson(BALLET_URL, window.MAXNOW_BALLET_DATA || fallbackBallet, "ballet"),
    readJson(
      BALLET_SESSION_URL,
      window.MAXNOW_BALLET_SESSION_DATA || fallbackBalletSession,
      "ballet-session",
    ),
    readJson(
      BALLET_BOOKING_FAST_URL,
      window.MAXNOW_BALLET_BOOKING_FAST_DATA || fallbackBalletBookingFast,
      "ballet-booking-fast",
    ),
  ]).then(([dashboard, last30, wikiTodo, checkin, marketIndices, projectMeta, projectStatus, ballet, balletSession, balletBookingFast]) => {
    dashboardData = dashboard;
    last30Data = last30;
    wikiTodoData = wikiTodo;
    checkinData = checkin;
    marketIndicesData = marketIndices;
    projectMetaData = projectMeta;
    balletData = ballet;
    balletSessionData = balletSession;
    balletBookingFastData = balletBookingFast;
    projectStatusData = projectStatus;
    updateClock();
    renderHome();
    if (getActiveView() === "dounai") renderDounai();
    if (getActiveView() === "ballet") renderBallet();
  });

  return homeDataPromise;
}

async function loadTokenData({ force = false } = {}) {
  if (!force && tokenDataPromise) return tokenDataPromise;

  tokenDataPromise = readJson(TOKEN_USAGE_URL, window.MAXNOW_TOKEN_USAGE_DATA || fallbackTokenUsage, "token")
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

  rickyDataPromise = readJson(RICKY_URL, window.MAXNOW_RICKY_DATA || fallbackRicky, "ricky")
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

  lifeDataPromise = readJson(LIFE_FOODS_URL, window.MAXNOW_LIFE_FOODS_DATA || fallbackLifeFoods, "life")
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
  const nextView = ["home", "ricky", "life", "tokens", "ballet", "cloud", "dounai"].includes(view) ? view : "home";
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
        : nextView === "ballet"
          ? copy.balletTitle
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
  if (nextView === "ballet") {
    requestAnimationFrame(renderBallet);
    scheduleBalletWeekCoverWarmup();
  }
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
      if (item.repeat === "monthly") return Number(item.day) === day;
      return Number(item.month) === month && Number(item.day) === day;
    })
    .map((item) => {
      return formatSpecialDateTitle(item, year);
    })
    .filter(Boolean);
}

function formatSpecialDateTitle(item, year) {
  const title = item.title || item.label || item.name || "";
  if (!title) return "";
  const startYear = Number(item.startYear || item.year);
  if (Number.isFinite(startYear) && startYear > 0 && year > startYear) {
    return `${title} ${year - startYear}\u5468\u5e74`;
  }
  return title;
}

function createLocalDate(year, month, day) {
  const candidate = new Date(year, month - 1, day);
  if (
    candidate.getFullYear() !== year ||
    candidate.getMonth() !== month - 1 ||
    candidate.getDate() !== day
  ) {
    return null;
  }
  return candidate;
}

function getNextSpecialDate(date) {
  const specialDates = Array.isArray(dashboardData.specialDates) ? dashboardData.specialDates : [];
  const today = new Date(date.getFullYear(), date.getMonth(), date.getDate());
  const occurrences = [];

  for (let offset = 1; offset <= 370; offset += 1) {
    const candidate = addDays(today, offset);
    const holidayLabels = getHolidayLabels(candidate);
    if (holidayLabels.length) {
      holidayLabels.forEach((title) => occurrences.push({ date: candidate, title }));
      break;
    }
  }

  specialDates.forEach((item) => {
    let candidate = null;
    if (item.date) {
      const match = String(item.date).match(/^(\d{4})-(\d{2})-(\d{2})/);
      if (match) candidate = createLocalDate(Number(match[1]), Number(match[2]), Number(match[3]));
    } else if (item.repeat === "monthly") {
      const day = Number(item.day);
      for (let offset = 0; offset < 24 && !candidate; offset += 1) {
        const monthStart = new Date(today.getFullYear(), today.getMonth() + offset, 1);
        const occurrence = createLocalDate(monthStart.getFullYear(), monthStart.getMonth() + 1, day);
        if (occurrence && occurrence > today) candidate = occurrence;
      }
    } else {
      const month = Number(item.month);
      const day = Number(item.day);
      for (let offset = 0; offset < 8 && !candidate; offset += 1) {
        const occurrence = createLocalDate(today.getFullYear() + offset, month, day);
        if (occurrence && occurrence > today) candidate = occurrence;
      }
    }

    const title = candidate ? formatSpecialDateTitle(item, candidate.getFullYear()) : "";
    if (candidate && candidate > today && title) occurrences.push({ date: candidate, title });
  });

  if (!occurrences.length) return null;
  occurrences.sort((first, second) => first.date - second.date);
  const nextDate = occurrences[0].date;
  const titles = occurrences
    .filter((item) => isSameDay(item.date, nextDate))
    .map((item) => item.title);
  const daysUntil = Math.round(
    (Date.UTC(nextDate.getFullYear(), nextDate.getMonth(), nextDate.getDate()) -
      Date.UTC(today.getFullYear(), today.getMonth(), today.getDate())) /
      86400000,
  );
  return { date: nextDate, daysUntil, titles: [...new Set(titles)] };
}

function formatNextSpecialDate(date) {
  const next = getNextSpecialDate(date);
  if (!next) return copy.noUpcomingSpecialDate;
  const dateLabel = `${next.date.getMonth() + 1}\u6708${next.date.getDate()}\u65e5`;
  return `${next.daysUntil}\u5929\u540e\u662f${next.titles.join("\u3001")}\uff08${dateLabel}\uff09`;
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
  setText("#next-special-label", formatNextSpecialDate(now));
  updateBalletWeekTrigger();
  updateTodayPhase();
  if (qs("#cloud-view")?.classList.contains("is-active")) {
    renderBalletSessionExperiment(now);
  }
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

qs("#home-ballet-card")?.addEventListener("click", () => setView("ballet"));
qs("#home-ballet-card")?.addEventListener("keydown", (event) => {
  if (event.key === "Enter" || event.key === " ") {
    event.preventDefault();
    setView("ballet");
  }
});

qs("#ballet-plan-week-prev")?.addEventListener("click", () => {
  balletPlanWeekOffset = Math.max(-1, balletPlanWeekOffset - 1);
  renderBalletPlanWeek();
});

qs("#ballet-plan-week-next")?.addEventListener("click", () => {
  balletPlanWeekOffset = Math.min(1, balletPlanWeekOffset + 1);
  renderBalletPlanWeek();
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

qsa("[data-ballet-period]").forEach((button) => {
  button.addEventListener("click", () => {
    activeBalletPeriod = button.dataset.balletPeriod || "all";
    renderBalletTraining();
    renderBalletHistory();
  });
});

qsa("[data-ballet-metric]").forEach((button) => {
  button.addEventListener("click", () => {
    activeBalletMetric = button.dataset.balletMetric || "classes";
    renderBalletTraining();
  });
});

const balletHistoryDialog = qs("#ballet-history-dialog");

qs("#ballet-history-open")?.addEventListener("click", () => {
  if (!balletHistoryDialog) return;
  if (typeof balletHistoryDialog.showModal === "function") {
    balletHistoryDialog.showModal();
  } else {
    balletHistoryDialog.setAttribute("open", "");
  }
});

qs("#ballet-history-close")?.addEventListener("click", () => {
  if (!balletHistoryDialog) return;
  if (typeof balletHistoryDialog.close === "function") balletHistoryDialog.close();
  else balletHistoryDialog.removeAttribute("open");
});

balletHistoryDialog?.addEventListener("click", (event) => {
  if (event.target !== balletHistoryDialog) return;
  if (typeof balletHistoryDialog.close === "function") balletHistoryDialog.close();
  else balletHistoryDialog.removeAttribute("open");
});

const balletWeekDialog = qs("#ballet-week-dialog");
const balletWeekCarousel = qs("#ballet-week-carousel");

function selectBalletWeekSlide(type, { scroll = true } = {}) {
  const nextType = type === "brief" ? "brief" : "cover";
  balletWeekActiveSlide = nextType;
  const coverTab = qs("#ballet-week-cover-tab");
  const briefTab = qs("#ballet-week-brief-tab");
  [
    [coverTab, nextType === "cover"],
    [briefTab, nextType === "brief"],
  ].forEach(([tab, active]) => {
    if (!tab) return;
    tab.classList.toggle("is-active", active);
    tab.setAttribute("aria-selected", String(active));
  });
  if (scroll && balletWeekCarousel) {
    const left = nextType === "brief" ? balletWeekCarousel.clientWidth : 0;
    balletWeekCarousel.scrollTo({
      left,
      behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth",
    });
  }
  loadBalletWeekConfig()
    .then((config) => updateBalletWeekDialogRange(config))
    .catch(() => updateBalletWeekDialogRange());
  renderBalletWeekAsset(nextType);
}

qs("#ballet-week-trigger")?.addEventListener("click", () => {
  if (!balletWeekDialog) return;
  if (typeof balletWeekDialog.showModal === "function") balletWeekDialog.showModal();
  else balletWeekDialog.setAttribute("open", "");
  selectBalletWeekSlide(balletWeekActiveSlide, { scroll: false });
});

qs("#ballet-week-trigger")?.addEventListener("pointerenter", scheduleBalletWeekCoverWarmup);
qs("#ballet-week-trigger")?.addEventListener("focus", scheduleBalletWeekCoverWarmup);

qs("#ballet-week-close")?.addEventListener("click", () => {
  if (!balletWeekDialog) return;
  if (typeof balletWeekDialog.close === "function") balletWeekDialog.close();
  else balletWeekDialog.removeAttribute("open");
});

balletWeekDialog?.addEventListener("click", (event) => {
  if (event.target !== balletWeekDialog) return;
  if (typeof balletWeekDialog.close === "function") balletWeekDialog.close();
  else balletWeekDialog.removeAttribute("open");
});

qs("#ballet-week-cover-tab")?.addEventListener("click", () => selectBalletWeekSlide("cover"));
qs("#ballet-week-brief-tab")?.addEventListener("click", () => selectBalletWeekSlide("brief"));

balletWeekCarousel?.addEventListener("scroll", () => {
  if (balletWeekCarouselFrame) cancelAnimationFrame(balletWeekCarouselFrame);
  balletWeekCarouselFrame = requestAnimationFrame(() => {
    balletWeekCarouselFrame = 0;
    const index = balletWeekCarousel.clientWidth
      ? Math.round(balletWeekCarousel.scrollLeft / balletWeekCarousel.clientWidth)
      : 0;
    const nextType = index > 0 ? "brief" : "cover";
    if (nextType !== balletWeekActiveSlide) selectBalletWeekSlide(nextType, { scroll: false });
  });
});

balletWeekCarousel?.addEventListener("keydown", (event) => {
  if (event.key === "ArrowLeft") {
    event.preventDefault();
    selectBalletWeekSlide("cover");
  } else if (event.key === "ArrowRight") {
    event.preventDefault();
    selectBalletWeekSlide("brief");
  }
});

qs("#ballet-week-copy")?.addEventListener("click", async () => {
  const cover = await renderBalletWeekAsset();
  const status = qs("#ballet-week-status");
  if (!cover) return;
  if (!("ClipboardItem" in window) || !navigator.clipboard?.write) {
    if (status) status.textContent = "当前浏览器不支持直接复制图片，请使用下载 PNG";
    return;
  }
  try {
    await navigator.clipboard.write([new ClipboardItem({ "image/png": cover.blob })]);
    if (status) status.textContent = "已复制图片，可以直接粘贴转发";
  } catch (error) {
    if (status) status.textContent = "复制失败，请使用下载 PNG";
  }
});

qs("#ballet-week-download")?.addEventListener("click", async () => {
  const cover = await renderBalletWeekAsset();
  if (!cover) return;
  const url = URL.createObjectURL(cover.blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = cover.filename;
  anchor.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
  const status = qs("#ballet-week-status");
  if (status) status.textContent = `已下载 ${cover.filename}`;
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

window.addEventListener("focus", () => updateBalletWeekTrigger());
document.addEventListener("visibilitychange", () => {
  if (!document.hidden) updateBalletWeekTrigger();
});

let resizeTimer = 0;
window.addEventListener("resize", () => {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => {
    scheduleWeatherMetaFit();
    if (qs("#dounai-view")?.classList.contains("is-active")) renderDounai();
    if (qs("#tokens-view")?.classList.contains("is-active")) renderTokens();
    if (qs("#ballet-view")?.classList.contains("is-active")) {
      renderBalletTrend();
      renderBalletHistory();
    }
  }, 120);
});

updateClock();
setInterval(updateClock, 30000);
loadHomeData().then(() => setView(location.hash.replace("#", "")));
setInterval(() => loadData({ force: true }), DATA_AUTO_REFRESH_INTERVAL_MS);
