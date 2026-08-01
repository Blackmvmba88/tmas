(() => {
  "use strict";

  const STORAGE_KEY = "blackmamba-ui-lab-v1";

  const components = [
    {
      id: "BM-BTN-001",
      name: "Neon Amber Core",
      category: "button",
      tags: ["ámbar", "acción", "neon"],
      tokens: ["amber", "orange", "pill", "strong-glow"],
      demo: "neon-amber",
      label: "Start project",
    },
    {
      id: "BM-BTN-002",
      name: "Liquid Chrome",
      category: "button",
      tags: ["chrome", "líquido", "premium"],
      tokens: ["pink", "violet", "specular", "pill"],
      demo: "liquid-chrome",
      label: "Create visual",
    },
    {
      id: "BM-BTN-003",
      name: "Aurora Border",
      category: "button",
      tags: ["aurora", "gradiente", "dark"],
      tokens: ["cyan", "violet", "gradient-border"],
      demo: "aurora",
      label: "Explore system",
    },
    {
      id: "BM-BTN-004",
      name: "Holographic Solid",
      category: "button",
      tags: ["holográfico", "iridiscente", "claro"],
      tokens: ["holographic", "high-contrast", "solid"],
      demo: "holographic",
      label: "Generate theme",
    },
    {
      id: "BM-BTN-005",
      name: "Glass Ghost",
      category: "button",
      tags: ["vidrio", "minimal", "secondary"],
      tokens: ["glass", "blur", "quiet-action"],
      demo: "glass-ghost",
      label: "Secondary action",
    },
    {
      id: "BM-BTN-006",
      name: "Coquette Ribbon",
      category: "button",
      tags: ["ribbon", "rosa", "editorial"],
      tokens: ["pink", "asymmetric-radius", "soft-glow"],
      demo: "ribbon",
      label: "Save collection",
    },
    {
      id: "BM-ICO-001",
      name: "Cyan Send Orb",
      category: "button",
      tags: ["icono", "enviar", "cian"],
      tokens: ["cyan", "circle", "focus-ring"],
      demo: "icon",
      label: "➤",
    },
    {
      id: "BM-INP-001",
      name: "Neon Search Field",
      category: "input",
      tags: ["buscar", "input", "violeta"],
      tokens: ["glass", "violet", "pill", "input"],
      demo: "input",
      label: "Buscar componentes…",
    },
    {
      id: "BM-TGL-001",
      name: "Orange Listening Toggle",
      category: "toggle",
      tags: ["toggle", "mic", "naranja"],
      tokens: ["orange", "white-thumb", "active-state"],
      demo: "toggle",
      label: "Mic activo",
    },
    {
      id: "BM-CHP-001",
      name: "Pink Filter Chip",
      category: "chip",
      tags: ["chip", "filtro", "rosa"],
      tokens: ["pink", "compact", "selected-state"],
      demo: "chip",
      label: "Liquid chrome ×",
    },
    {
      id: "BM-CRD-001",
      name: "Glass Action Card",
      category: "card",
      tags: ["card", "acción", "vidrio"],
      tokens: ["glass", "cyan-corner", "raised"],
      demo: "card",
      label: "Visual baseline",
    },
    {
      id: "BM-BTN-007",
      name: "Disabled System State",
      category: "button",
      tags: ["disabled", "estado", "accesibilidad"],
      tokens: ["disabled", "low-emphasis", "no-pointer"],
      demo: "disabled",
      label: "Unavailable action",
    },
  ];

  const categoryNames = {
    button: "Botón",
    input: "Input",
    toggle: "Toggle",
    chip: "Chip",
    card: "Card",
  };

  const state = loadState();
  const comparison = new Set();

  const grid = document.querySelector("#componentGrid");
  const template = document.querySelector("#componentCardTemplate");
  const emptyState = document.querySelector("#emptyState");
  const searchInput = document.querySelector("#searchInput");
  const categoryFilter = document.querySelector("#categoryFilter");
  const statusFilter = document.querySelector("#statusFilter");
  const glowRange = document.querySelector("#glowRange");
  const glowValue = document.querySelector("#glowValue");
  const compareDialog = document.querySelector("#compareDialog");
  const compareContent = document.querySelector("#compareContent");

  function createDefaultState() {
    return {
      reviews: {},
      settings: {
        theme: "neon",
        glow: 72,
      },
      updatedAt: null,
    };
  }

  function loadState() {
    try {
      const value = window.localStorage.getItem(STORAGE_KEY);
      if (!value) return createDefaultState();
      const parsed = JSON.parse(value);
      return {
        ...createDefaultState(),
        ...parsed,
        settings: {
          ...createDefaultState().settings,
          ...(parsed.settings || {}),
        },
      };
    } catch (error) {
      console.warn("No se pudo cargar el estado guardado", error);
      return createDefaultState();
    }
  }

  function saveState() {
    state.updatedAt = new Date().toISOString();
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    updateSummary();
  }

  function reviewFor(id) {
    if (!state.reviews[id]) {
      state.reviews[id] = { score: null, verdict: null, notes: "" };
    }
    return state.reviews[id];
  }

  function renderDemo(component) {
    const label = escapeHtml(component.label);
    switch (component.demo) {
      case "neon-amber":
      case "liquid-chrome":
      case "aurora":
      case "holographic":
      case "glass-ghost":
      case "ribbon":
        return `<div class="demo-stack"><button class="demo-button ${component.demo}" type="button">${label}</button></div>`;
      case "icon":
        return `<button class="demo-icon-button" type="button" aria-label="Enviar">${label}</button>`;
      case "input":
        return `<div class="input-shell"><input class="demo-input" type="search" placeholder="${label}" aria-label="${label}"></div>`;
      case "toggle":
        return `<div class="toggle-shell"><span>${label}</span><button class="demo-toggle" type="button" aria-pressed="true" aria-label="Alternar micrófono"></button></div>`;
      case "chip":
        return `<button class="demo-chip" type="button" aria-pressed="true">${label}</button>`;
      case "card":
        return `<button class="demo-card-action" type="button"><strong>${label}</strong><span>Revisar capturas, riesgo y cambios.</span><em>↗</em></button>`;
      case "disabled":
        return `<button class="demo-button glass-ghost is-disabled" type="button" disabled>${label}</button>`;
      default:
        return `<span>${label}</span>`;
    }
  }

  function wireDemoInteractions(stage, component) {
    if (component.demo === "toggle") {
      const toggle = stage.querySelector(".demo-toggle");
      toggle?.addEventListener("click", () => {
        const next = toggle.getAttribute("aria-pressed") !== "true";
        toggle.setAttribute("aria-pressed", String(next));
      });
    }

    if (component.demo === "chip") {
      const chip = stage.querySelector(".demo-chip");
      chip?.addEventListener("click", () => {
        const next = chip.getAttribute("aria-pressed") !== "true";
        chip.setAttribute("aria-pressed", String(next));
        chip.style.opacity = next ? "1" : ".48";
      });
    }
  }

  function renderComponents() {
    const query = searchInput.value.trim().toLocaleLowerCase("es");
    const category = categoryFilter.value;
    const status = statusFilter.value;

    const visible = components.filter((component) => {
      const review = state.reviews[component.id] || {};
      const haystack = [component.id, component.name, component.category, ...component.tags, ...component.tokens]
        .join(" ")
        .toLocaleLowerCase("es");
      const matchesQuery = !query || haystack.includes(query);
      const matchesCategory = category === "all" || component.category === category;
      const matchesStatus =
        status === "all" ||
        (status === "unrated" && !review.verdict && !review.score) ||
        review.verdict === status;
      return matchesQuery && matchesCategory && matchesStatus;
    });

    grid.replaceChildren();
    emptyState.hidden = visible.length !== 0;

    for (const component of visible) {
      const fragment = template.content.cloneNode(true);
      const card = fragment.querySelector(".component-card");
      const review = reviewFor(component.id);
      card.dataset.componentId = component.id;
      if (review.verdict) card.dataset.verdict = review.verdict;

      fragment.querySelector(".component-code").textContent = component.id;
      fragment.querySelector(".component-name").textContent = component.name;
      fragment.querySelector(".category-pill").textContent = categoryNames[component.category];

      const stage = fragment.querySelector(".component-stage");
      stage.innerHTML = renderDemo(component);
      wireDemoInteractions(stage, component);

      const tokenRow = fragment.querySelector(".token-row");
      component.tokens.forEach((token) => {
        const badge = document.createElement("span");
        badge.textContent = token;
        tokenRow.append(badge);
      });

      const scoreOutput = fragment.querySelector(".score-output");
      scoreOutput.textContent = review.score ? `${review.score} / 10` : "Sin calificar";

      const scoreButtons = fragment.querySelector(".score-buttons");
      for (let score = 1; score <= 10; score += 1) {
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = String(score);
        button.setAttribute("aria-label", `Calificar ${component.name} con ${score}`);
        button.classList.toggle("is-active", review.score === score);
        button.addEventListener("click", () => {
          review.score = score;
          saveState();
          renderComponents();
        });
        scoreButtons.append(button);
      }

      fragment.querySelectorAll(".verdict-buttons button").forEach((button) => {
        const verdict = button.dataset.verdict;
        button.classList.toggle("is-active", review.verdict === verdict);
        button.addEventListener("click", () => {
          review.verdict = review.verdict === verdict ? null : verdict;
          saveState();
          renderComponents();
        });
      });

      const notes = fragment.querySelector("textarea");
      notes.value = review.notes || "";
      notes.addEventListener("input", () => {
        review.notes = notes.value;
        saveState();
      });

      const compareButton = fragment.querySelector(".compare-button");
      compareButton.classList.toggle("is-selected", comparison.has(component.id));
      compareButton.textContent = comparison.has(component.id) ? "Seleccionado para comparar" : "Añadir a comparación";
      compareButton.addEventListener("click", () => toggleComparison(component.id));

      grid.append(fragment);
    }
  }

  function toggleComparison(id) {
    if (comparison.has(id)) {
      comparison.delete(id);
      renderComponents();
      return;
    }

    if (comparison.size >= 2) comparison.delete(comparison.values().next().value);
    comparison.add(id);
    renderComponents();

    if (comparison.size === 2) openComparison();
  }

  function openComparison() {
    compareContent.replaceChildren();
    [...comparison].forEach((id) => {
      const component = components.find((item) => item.id === id);
      const review = reviewFor(id);
      const item = document.createElement("article");
      item.className = "compare-item";
      item.innerHTML = `
        <span class="component-code">${escapeHtml(component.id)}</span>
        <h3>${escapeHtml(component.name)}</h3>
        <div class="component-stage">${renderDemo(component)}</div>
        <p><strong>${review.score || "—"}/10</strong> · ${verdictLabel(review.verdict)}</p>
        <p>${escapeHtml(review.notes || "Sin notas todavía.")}</p>
      `;
      wireDemoInteractions(item.querySelector(".component-stage"), component);
      compareContent.append(item);
    });
    compareDialog.showModal();
  }

  function verdictLabel(verdict) {
    return {
      approved: "Aprobado",
      revise: "Revisar",
      rejected: "Rechazado",
    }[verdict] || "Sin veredicto";
  }

  function updateSummary() {
    const reviews = Object.values(state.reviews);
    const counts = {
      approved: reviews.filter((review) => review.verdict === "approved").length,
      revise: reviews.filter((review) => review.verdict === "revise").length,
      rejected: reviews.filter((review) => review.verdict === "rejected").length,
    };
    const scored = reviews.filter((review) => Number.isFinite(review.score));
    const average = scored.length
      ? (scored.reduce((total, review) => total + review.score, 0) / scored.length).toFixed(1)
      : "—";
    const evaluatedIds = components.filter((component) => {
      const review = state.reviews[component.id];
      return review && (review.score || review.verdict || review.notes);
    });

    document.querySelector("#approvedCount").textContent = String(counts.approved);
    document.querySelector("#reviseCount").textContent = String(counts.revise);
    document.querySelector("#rejectedCount").textContent = String(counts.rejected);
    document.querySelector("#averageScore").textContent = average;
    document.querySelector("#reviewProgress").textContent = `${evaluatedIds.length} / ${components.length} evaluados`;
  }

  function setTheme(theme) {
    state.settings.theme = theme;
    document.documentElement.dataset.theme = theme;
    document.querySelectorAll("[data-theme-choice]").forEach((button) => {
      button.setAttribute("aria-pressed", String(button.dataset.themeChoice === theme));
    });
    saveState();
  }

  function setGlow(value) {
    const numeric = Number(value);
    state.settings.glow = numeric;
    document.documentElement.style.setProperty("--glow-level", String(numeric / 100));
    glowRange.value = String(numeric);
    glowValue.textContent = `${numeric}%`;
    saveState();
  }

  function exportReviews() {
    const payload = {
      schemaVersion: 1,
      project: "BlackMamba UI Component Lab",
      exportedAt: new Date().toISOString(),
      settings: state.settings,
      components: components.map((component) => ({
        ...component,
        review: state.reviews[component.id] || { score: null, verdict: null, notes: "" },
      })),
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `blackmamba-ui-review-${new Date().toISOString().slice(0, 10)}.json`;
    link.click();
    URL.revokeObjectURL(url);
  }

  function resetReviews() {
    const accepted = window.confirm("¿Borrar calificaciones, veredictos y notas guardadas en este navegador?");
    if (!accepted) return;
    state.reviews = {};
    comparison.clear();
    saveState();
    renderComponents();
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  searchInput.addEventListener("input", renderComponents);
  categoryFilter.addEventListener("change", renderComponents);
  statusFilter.addEventListener("change", renderComponents);
  glowRange.addEventListener("input", (event) => setGlow(event.target.value));
  document.querySelectorAll("[data-theme-choice]").forEach((button) => {
    button.addEventListener("click", () => setTheme(button.dataset.themeChoice));
  });
  document.querySelector("#exportButton").addEventListener("click", exportReviews);
  document.querySelector("#resetButton").addEventListener("click", resetReviews);

  setTheme(state.settings.theme);
  setGlow(state.settings.glow);
  renderComponents();
  updateSummary();
})();
