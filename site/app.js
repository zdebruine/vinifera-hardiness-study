"use strict";

// ---- helpers ---------------------------------------------------------------
const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
const el = (tag, attrs = {}, ...kids) => {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") n.className = v;
    else if (k === "html") n.innerHTML = v;
    else n.setAttribute(k, v);
  }
  for (const kid of kids) n.append(kid && kid.nodeType ? kid : document.createTextNode(kid ?? ""));
  return n;
};
const pct = (x) => (x == null ? "—" : (100 * x).toFixed(0) + "%");
const erf = (x) => {
  // Abramowitz & Stegun 7.1.26
  const s = x < 0 ? -1 : 1;
  x = Math.abs(x);
  const t = 1 / (1 + 0.3275911 * x);
  const y = 1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-x * x);
  return s * y;
};
const normCdf = (z) => 0.5 * (1 + erf(z / Math.SQRT2));

const DATA = {};
const FILES = ["varieties", "sites", "freeze_events", "site_minima", "lt50", "ripening", "colocation", "survival", "suitability", "meta"];

async function loadAll() {
  await Promise.all(FILES.map(async (f) => {
    const res = await fetch(`./data/${f}.json`);
    DATA[f] = await res.json();
  }));
}

// ---- tabs ------------------------------------------------------------------
function initTabs() {
  $$(".tab").forEach((btn) => {
    btn.addEventListener("click", () => {
      $$(".tab").forEach((b) => b.setAttribute("aria-selected", String(b === btn)));
      $$(".panel").forEach((p) => (p.hidden = p.id !== btn.dataset.tab));
    });
  });
}

// ---- 1. suitability --------------------------------------------------------
function initSuitability() {
  const vSel = $("#suit-variety"), sSel = $("#suit-site");
  const scored = [...new Set(DATA.suitability.map((r) => r.variety_id))];
  DATA.varieties.filter((v) => scored.includes(v.variety_id))
    .forEach((v) => vSel.append(el("option", { value: v.variety_id }, v.prime_name)));
  DATA.sites.forEach((s) => sSel.append(el("option", { value: s.site_id }, s.name)));

  const render = () => {
    const row = DATA.suitability.find((r) => r.variety_id === vSel.value && r.site_id === sSel.value);
    const card = $("#suit-result");
    card.innerHTML = "";
    if (!row) { card.append(el("p", {}, "No screening freeze event recorded for this site.")); return; }
    const axis = (cls, label, val, sd) => el("div", { class: `axis ${cls}` },
      el("div", { class: "label" }, label),
      el("div", { class: "val" }, pct(val)),
      el("div", { class: "sd" }, `±${pct(sd)}`),
      el("div", { class: "bar" }, el("span", { style: `width:${Math.max(0, Math.min(1, val)) * 100}%` })));
    card.append(el("div", { class: "axes" },
      axis("survive", "Survival", row.p_survive, row.p_survive_sd),
      axis("ripen", "Ripening", row.p_ripen, row.p_ripen_sd),
      axis("suit", "Suitability", row.suitability, row.suitability_sd)));
    const note = `Screened against ${row.event_label} (min ${row.event_tmin_c}°C). `
      + (row.burial_flag ? "⚠ This site buries vines over winter — survival here is uninformative about genetic hardiness." : "");
    card.append(el("div", { class: "note-line" }, note));
  };
  vSel.addEventListener("change", render);
  sSel.addEventListener("change", render);
  render();

  // matrix
  const cols = [
    ["variety_name", "Variety", false], ["site_name", "Site", false],
    ["p_survive", "Survival", true], ["p_ripen", "Ripening", true], ["suitability", "Suitability", true],
  ];
  let sortKey = "suitability", sortDir = -1;
  const table = $("#suit-table");
  const draw = () => {
    const rows = [...DATA.suitability].sort((a, b) => {
      const x = a[sortKey], y = b[sortKey];
      return (x < y ? -1 : x > y ? 1 : 0) * sortDir;
    });
    table.innerHTML = "";
    const thead = el("tr");
    cols.forEach(([key, label, num]) => {
      const th = el("th", { class: `sortable ${num ? "num" : ""}` }, label);
      th.addEventListener("click", () => { sortDir = sortKey === key ? -sortDir : -1; sortKey = key; draw(); });
      thead.append(th);
    });
    table.append(el("thead", {}, thead));
    const tb = el("tbody");
    rows.forEach((r) => {
      tb.append(el("tr", {},
        el("td", {}, r.variety_name),
        el("td", {}, r.site_name + (r.burial_flag ? " ❄" : "")),
        el("td", { class: "num" }, pct(r.p_survive)),
        el("td", { class: "num" }, pct(r.p_ripen)),
        el("td", { class: "num" }, pct(r.suitability))));
    });
    table.append(tb);
  };
  draw();
}

// ---- 2. ripening calculator ------------------------------------------------
function initRipening() {
  const gdd = $("#rip-gdd"), req = $("#rip-req"), sigma = $("#rip-sigma"), vSel = $("#rip-variety");
  DATA.varieties.filter((v) => v.gdd_req_f != null)
    .forEach((v) => vSel.append(el("option", { value: v.variety_id }, v.prime_name)));

  const draw = () => {
    const g = +gdd.value, r = +req.value, s = +sigma.value;
    $("#rip-gdd-out").textContent = g;
    $("#rip-req-out").textContent = r;
    $("#rip-sigma-out").textContent = s;
    const p = normCdf((g - r) / s);
    $("#rip-result").innerHTML = "";
    $("#rip-result").append(el("div", { class: "axes" },
      el("div", { class: "axis ripen" },
        el("div", { class: "label" }, "P(ripen)"),
        el("div", { class: "val" }, pct(p)),
        el("div", { class: "bar" }, el("span", { style: `width:${p * 100}%` })))));
    drawCurve(r, s, g);
  };
  const drawCurve = (r, s, g) => {
    const svg = $("#rip-curve");
    const W = 600, H = 240, padL = 36, padB = 26, padT = 10, padR = 10;
    const x0 = 1200, x1 = 4000;
    const X = (v) => padL + (v - x0) / (x1 - x0) * (W - padL - padR);
    const Y = (p) => padT + (1 - p) * (H - padT - padB);
    let d = "";
    for (let v = x0; v <= x1; v += 20) {
      const p = normCdf((v - r) / s);
      d += (v === x0 ? "M" : "L") + X(v).toFixed(1) + " " + Y(p).toFixed(1) + " ";
    }
    const ticks = [0, 0.5, 1].map((p) => `<line x1="${padL}" y1="${Y(p)}" x2="${W - padR}" y2="${Y(p)}" stroke="var(--line)"/>`
      + `<text x="4" y="${Y(p) + 4}" fill="var(--muted)" font-size="11">${p * 100}%</text>`).join("");
    svg.innerHTML = ticks
      + `<path d="${d}" fill="none" stroke="var(--leaf)" stroke-width="2.5"/>`
      + `<line x1="${X(g)}" y1="${padT}" x2="${X(g)}" y2="${H - padB}" stroke="var(--wine)" stroke-width="1.5" stroke-dasharray="4 3"/>`
      + `<text x="${Math.min(W - 70, X(g) + 4)}" y="${padT + 12}" fill="var(--wine)" font-size="11">site GDD</text>`
      + `<text x="${W / 2}" y="${H - 4}" text-anchor="middle" fill="var(--muted)" font-size="11">GDD (base 50°F)</text>`;
  };
  vSel.addEventListener("change", () => {
    const v = DATA.varieties.find((x) => x.variety_id === vSel.value);
    if (v && v.gdd_req_f != null) { req.value = v.gdd_req_f; sigma.value = v.ripening_sigma_f; }
    draw();
  });
  [gdd, req, sigma].forEach((i) => i.addEventListener("input", draw));
  draw();
}

// ---- 3. climate ------------------------------------------------------------
function initClimate() {
  const cards = $("#climate-cards");
  DATA.sites.forEach((s) => {
    const minima = DATA.site_minima.filter((m) => m.site_id === s.site_id)
      .map((m) => `${m.event_label}: ${m.tmin_c}°C`).join(" · ") || "no recorded event";
    cards.append(el("div", { class: "card" },
      el("h4", {}, s.name, s.burial_flag ? el("span", { class: "flag", style: "margin-left:6px" }, "buried") : ""),
      el("div", { class: "meta" }, `${s.region}, ${s.country}`),
      el("div", { class: "meta" }, `GDD ${Math.round(s.gdd_winkler_f)} · ${s.latitude.toFixed(2)}, ${s.longitude.toFixed(2)}`),
      el("div", { class: "meta", style: "margin-top:6px" }, minima)));
  });
  buildTable($("#freeze-table"),
    [["event_label", "Event", false], ["date", "Date", false], ["description", "Description", false]],
    DATA.freeze_events);
}

// ---- 4. lt50 ---------------------------------------------------------------
function initLt50() {
  const nameById = Object.fromEntries(DATA.varieties.map((v) => [v.variety_id, v.prime_name]));
  const rows = DATA.lt50.map((r) => ({ ...r, variety: nameById[r.variety_id] || r.variety_id, lt50_c: +r.lt50_c }));
  const cols = [["variety", "Variety", false], ["lt50_c", "LT50 °C", true],
    ["method", "Method", false], ["tissue", "Tissue", false], ["source", "Source", false]];
  const table = $("#lt50-table");
  const render = (filter = "") => {
    const f = filter.toLowerCase();
    buildTable(table, cols, rows.filter((r) =>
      r.variety.toLowerCase().includes(f) || r.method.toLowerCase().includes(f)), "lt50_c", 1);
  };
  $("#lt50-filter").addEventListener("input", (e) => render(e.target.value));
  render();
}

// ---- 5. varieties ----------------------------------------------------------
function initVarieties() {
  const cards = $("#variety-cards");
  const render = (filter = "") => {
    const f = filter.toLowerCase();
    cards.innerHTML = "";
    DATA.varieties.filter((v) =>
      v.prime_name.toLowerCase().includes(f) || v.synonyms.some((s) => s.toLowerCase().includes(f))
    ).forEach((v) => {
      const c = el("div", { class: "card" },
        el("h4", {}, v.prime_name),
        el("div", { class: "meta" }, `${v.color} · ${v.species}`));
      if (v.lt50_c != null) c.append(el("div", { class: "meta" }, `LT50 ${v.lt50_c}°C · GDD req ${v.gdd_req_f ?? "—"}`));
      if (v.parents.length) c.append(el("div", { class: "meta", style: "margin-top:4px" },
        "parents: " + v.parents.map((p) => p.name).join(" × ")));
      if (v.synonyms.length) {
        const chips = el("div", { style: "margin-top:6px" });
        v.synonyms.forEach((s) => chips.append(el("span", { class: "chip" }, s)));
        c.append(chips);
      }
      cards.append(c);
    });
  };
  $("#var-filter").addEventListener("input", (e) => render(e.target.value));
  render();
}

// ---- 6. colocation ---------------------------------------------------------
function initColocation() {
  const nameById = Object.fromEntries(DATA.varieties.map((v) => [v.variety_id, v.prime_name]));
  const byRegion = {};
  DATA.colocation.forEach((r) => {
    (byRegion[r.region] ||= []).push({ name: nameById[r.variety_id] || r.variety_id, ha: +r.bearing_ha });
  });
  const cards = $("#coloc-regions");
  Object.entries(byRegion).forEach(([region, vars]) => {
    vars.sort((a, b) => b.ha - a.ha);
    const c = el("div", { class: "card" }, el("h4", {}, region));
    vars.forEach((v) => c.append(el("div", { class: "meta" }, `${v.name} — ${v.ha.toLocaleString()} ha`)));
    cards.append(c);
  });
}

// ---- generic table ---------------------------------------------------------
function buildTable(table, cols, rows, sortKey = null, sortDir = 1) {
  const draw = () => {
    const data = sortKey ? [...rows].sort((a, b) => {
      const x = a[sortKey], y = b[sortKey];
      return (x < y ? -1 : x > y ? 1 : 0) * sortDir;
    }) : rows;
    table.innerHTML = "";
    const tr = el("tr");
    cols.forEach(([key, label, num]) => {
      const th = el("th", { class: `sortable ${num ? "num" : ""}` }, label);
      th.addEventListener("click", () => { sortDir = sortKey === key ? -sortDir : 1; sortKey = key; draw(); });
      tr.append(th);
    });
    table.append(el("thead", {}, tr));
    const tb = el("tbody");
    data.forEach((r) => {
      const row = el("tr");
      cols.forEach(([key, , num]) => row.append(el("td", { class: num ? "num" : "" }, String(r[key]))));
      tb.append(row);
    });
    table.append(tb);
  };
  draw();
}

// ---- boot ------------------------------------------------------------------
(async function () {
  initTabs();
  try {
    await loadAll();
  } catch (e) {
    $("main").prepend(el("div", { class: "banner" }, "Could not load data bundles. If viewing locally, serve over HTTP (e.g. python3 -m http.server)."));
    return;
  }
  initSuitability();
  initRipening();
  initClimate();
  initLt50();
  initVarieties();
  initColocation();
  if (DATA.meta && DATA.meta.built_at) $("#build-time").textContent = DATA.meta.built_at.replace("T", " ");
})();
