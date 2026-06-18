(() => {
  const feed = document.querySelector(".topic-feed");
  const pageHead = document.querySelector(".topic-page-head");

  if (!feed || !pageHead || feed.dataset.subtopicReady === "true") {
    return;
  }

  const cards = Array.from(feed.querySelectorAll(":scope > .article-preview"));
  if (cards.length < 2) {
    return;
  }

  const parseTags = (rawText) => {
    const normalized = rawText
      .replace(/^[\[【]/, "")
      .replace(/[\]】]$/, "")
      .replace(/\s+/g, " ")
      .trim();

    return normalized
      .split(/[，,、/]+/)
      .map((tag) => tag.trim())
      .filter(Boolean);
  };

  const groups = new Map();

  cards.forEach((card) => {
    const tagNode = card.querySelector(".tag");
    const tagText = tagNode ? tagNode.textContent : "";
    const [primaryTag] = parseTags(tagText);
    const key = primaryTag || "未分类";

    if (!groups.has(key)) {
      groups.set(key, {
        tag: key,
        className: tagNode ? tagNode.className : "tag",
        cards: [],
      });
    }

    groups.get(key).cards.push(card);
  });

  if (groups.size < 2) {
    return;
  }

  const orderedGroups = Array.from(groups.values()).sort((left, right) => {
    return right.cards.length - left.cards.length || left.tag.localeCompare(right.tag, "zh-Hans-CN");
  });

  const sectionId = (index) => `subtopic-${index + 1}`;
  const text = (value) => document.createTextNode(value);

  const indexSection = document.createElement("section");
  indexSection.className = "subtopic-index";
  indexSection.setAttribute("aria-label", "细分标签索引");

  const indexHeader = document.createElement("div");
  indexHeader.className = "subtopic-index-head";
  indexHeader.innerHTML = `
    <div>
      <p class="eyebrow">Subtopics</p>
      <h2>细分标签索引</h2>
    </div>
    <span>${orderedGroups.length} 个标签</span>
  `;

  const indexGrid = document.createElement("div");
  indexGrid.className = "subtopic-grid";

  orderedGroups.forEach((group, index) => {
    const link = document.createElement("a");
    link.className = "subtopic-card";
    link.href = `#${sectionId(index)}`;

    const badge = document.createElement("span");
    badge.className = group.className;
    badge.textContent = group.tag;

    const count = document.createElement("strong");
    count.textContent = `${group.cards.length} 篇`;

    const sample = document.createElement("p");
    sample.textContent = group.cards
      .slice(0, 3)
      .map((card) => card.querySelector("h2")?.textContent.trim())
      .filter(Boolean)
      .join(" / ");

    link.append(badge, count, sample);
    indexGrid.appendChild(link);
  });

  indexSection.append(indexHeader, indexGrid);

  const fragment = document.createDocumentFragment();
  orderedGroups.forEach((group, index) => {
    const groupSection = document.createElement("section");
    groupSection.className = "subtopic-group";
    groupSection.id = sectionId(index);

    const groupHead = document.createElement("div");
    groupHead.className = "subtopic-group-head";

    const titleWrap = document.createElement("div");
    const eyebrow = document.createElement("p");
    eyebrow.className = "eyebrow";
    eyebrow.textContent = "Subtopic";
    const title = document.createElement("h2");
    title.appendChild(text(group.tag));
    titleWrap.append(eyebrow, title);

    const count = document.createElement("span");
    count.textContent = `${group.cards.length} 篇`;
    groupHead.append(titleWrap, count);

    const list = document.createElement("div");
    list.className = "subtopic-articles";
    group.cards.forEach((card) => list.appendChild(card));

    groupSection.append(groupHead, list);
    fragment.appendChild(groupSection);
  });

  feed.dataset.subtopicReady = "true";
  feed.classList.add("is-grouped");
  feed.replaceChildren(fragment);
  pageHead.insertAdjacentElement("afterend", indexSection);
})();
