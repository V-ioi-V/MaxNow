(() => {
  const button = document.querySelector("[data-random-articles]");
  const feed = document.querySelector("[data-article-feed]");

  if (!button || !feed) {
    return;
  }

  const sourcePages = [
    "./topic-algorithm.html",
    "./topic-cs.html",
    "./topic-algorithm-gap.html",
    "./topic-engineering.html",
  ];

  let articleCache = null;

  const shuffle = (items) => {
    const copy = [...items];
    for (let index = copy.length - 1; index > 0; index -= 1) {
      const swapIndex = Math.floor(Math.random() * (index + 1));
      [copy[index], copy[swapIndex]] = [copy[swapIndex], copy[index]];
    }
    return copy;
  };

  const normalizeCard = (card, sourceUrl) => {
    const clone = card.cloneNode(true);
    clone.classList.remove("is-featured");

    const link = clone.getAttribute("href");
    if (link) {
      clone.href = `${new URL(link, sourceUrl).pathname.split("/").pop()}?from=articles`;
    }

    return {
      card: clone,
      key: `${clone.querySelector("h2")?.textContent || ""}-${clone.querySelector("time")?.textContent || ""}`,
    };
  };

  const loadArticles = async () => {
    if (articleCache) {
      return articleCache;
    }

    const parser = new DOMParser();
    const seen = new Set();
    const articles = [];

    const pages = await Promise.all(
      sourcePages.map(async (page) => {
        const response = await fetch(page, { cache: "no-cache" });
        if (!response.ok) {
          throw new Error(`Failed to load ${page}`);
        }
        return { page, html: await response.text() };
      }),
    );

    pages.forEach(({ page, html }) => {
      const doc = parser.parseFromString(html, "text/html");
      const sourceUrl = new URL(page, window.location.href);
      doc.querySelectorAll(".topic-feed > .article-preview").forEach((card) => {
        const article = normalizeCard(card, sourceUrl);
        if (!article.key.trim() || seen.has(article.key)) {
          return;
        }
        seen.add(article.key);
        articles.push(article.card);
      });
    });

    articleCache = articles;
    return articleCache;
  };

  const renderRandomArticles = async () => {
    button.disabled = true;
    button.textContent = "换中";
    button.setAttribute("aria-busy", "true");

    try {
      const articles = await loadArticles();
      const selected = shuffle(articles).slice(0, 10).map((card, index) => {
        const clone = card.cloneNode(true);
        clone.classList.toggle("is-featured", index === 0);
        return clone;
      });

      feed.replaceChildren(...selected);
      button.textContent = "再换一批";
    } catch (error) {
      button.textContent = "再试一次";
      console.error(error);
    } finally {
      button.disabled = false;
      button.removeAttribute("aria-busy");
    }
  };

  button.addEventListener("click", renderRandomArticles);
})();
