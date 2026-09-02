import argparse
import math
import time
import webbrowser
from pathlib import Path

from mnemo import config, store

K_NEIGHBORS = 3


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb) if na and nb else 0.0


def _build_graph_data(records: list[dict], k: int = K_NEIGHBORS) -> dict:
    n = len(records)
    sim = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                sim[i][j] = _cosine(records[i]["vector"], records[j]["vector"])

    edge_set = set()
    for i in range(n):
        neighbors = sorted((j for j in range(n) if j != i), key=lambda j: -sim[i][j])[:k]
        for j in neighbors:
            edge_set.add(tuple(sorted((i, j))))

    nodes = [
        {
            "id": r["id"],
            "project": r["project"],
            "type": r["type"],
            "content": r["content"],
            "slug": r.get("slug"),
        }
        for r in records
    ]
    edges = [
        {"source": records[i]["id"], "target": records[j]["id"], "sim": round(sim[i][j], 3)}
        for i, j in edge_set
    ]
    return {"nodes": nodes, "edges": edges, "k": k}


def _render_html(graph: dict) -> str:
    import json

    data_json = json.dumps(graph, ensure_ascii=False)
    return _TEMPLATE.replace("__DATA_JSON__", data_json)


def main(argv: list[str]) -> None:
    parser = argparse.ArgumentParser(prog="mnemo graph")
    parser.add_argument("--project", default=None)
    parser.add_argument("--out", default=None)
    args = parser.parse_args(argv)

    client = store.get_client()
    records = store.get_all_with_vectors(client, project=args.project)

    if len(records) < 2:
        print("Need at least 2 memories to build a graph.")
        return

    graph = _build_graph_data(records)
    html = _render_html(graph)

    out_path = Path(args.out) if args.out else Path.cwd() / f"mnemo-graph-{int(time.time())}.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"Graph written to {out_path}")
    webbrowser.open(out_path.as_uri())


_TEMPLATE = r"""<title>Mnemo Graph</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Special+Elite&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">

<style>
  :root {
    --bg: #0F0D0A;
    --panel: #1B1712;
    --ink: #E8DFC8;
    --ink-dim: #948A6C;
    --edge: rgba(232, 223, 200, 0.16);
    --edge-hi: rgba(232, 223, 200, 0.68);
    --stamp: #D2604E;
    --border: #332C22;
  }

  * { box-sizing: border-box; }

  html, body {
    margin: 0;
    height: 100%;
    background: var(--bg);
    color: var(--ink);
    font-family: "Source Serif 4", Georgia, serif;
    overflow: hidden;
  }

  .mono { font-family: "JetBrains Mono", ui-monospace, "SF Mono", Menlo, monospace; font-variant-numeric: tabular-nums; }
  .stamp-face { font-family: "Special Elite", "Courier New", monospace; }

  a, button { color: inherit; }
  button:focus-visible, [tabindex]:focus-visible {
    outline: 2px solid var(--stamp);
    outline-offset: 2px;
  }

  #stage { position: fixed; inset: 0; display: block; cursor: grab; }
  #stage.dragging { cursor: grabbing; }

  header.hud {
    position: fixed;
    top: 0; left: 0; right: 0;
    padding: clamp(16px, 3vw, 30px) clamp(16px, 3vw, 34px) 0;
    pointer-events: none;
    z-index: 5;
  }

  .eyebrow {
    font-family: "JetBrains Mono", monospace;
    font-size: 0.7rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--stamp);
    display: flex; align-items: center; gap: 9px;
    margin-bottom: 8px;
  }
  .eyebrow::before {
    content: ""; width: 6px; height: 6px; border-radius: 50%;
    background: var(--stamp);
    box-shadow: 0 0 0 3px rgba(210, 96, 78, 0.22);
  }

  h1.title {
    font-family: "Special Elite", "Courier New", monospace;
    font-weight: 400;
    font-size: clamp(1.5rem, 3.4vw, 2.1rem);
    margin: 0 0 6px;
    text-wrap: balance;
  }

  .sub {
    font-family: "JetBrains Mono", monospace;
    font-size: 0.78rem;
    color: var(--ink-dim);
  }

  .legend {
    position: fixed;
    bottom: clamp(16px, 3vw, 30px);
    left: clamp(16px, 3vw, 34px);
    display: flex;
    flex-direction: column;
    gap: 6px;
    font-family: "JetBrains Mono", monospace;
    font-size: 0.74rem;
    color: var(--ink-dim);
    z-index: 5;
    pointer-events: none;
  }
  .legend-row { display: flex; align-items: center; gap: 8px; }
  .legend-dot { width: 9px; height: 9px; border-radius: 50%; flex: none; }

  .hint {
    position: fixed;
    bottom: clamp(16px, 3vw, 30px);
    right: clamp(16px, 3vw, 34px);
    font-family: "JetBrains Mono", monospace;
    font-size: 0.72rem;
    color: var(--ink-dim);
    z-index: 5;
    text-align: right;
    pointer-events: none;
  }

  .node-label {
    position: fixed;
    pointer-events: none;
    font-family: "JetBrains Mono", monospace;
    font-size: 0.72rem;
    color: var(--ink);
    background: rgba(15, 13, 10, 0.88);
    border: 1px solid var(--border);
    padding: 3px 8px;
    white-space: nowrap;
    transform: translate(-50%, -140%);
    z-index: 8;
    opacity: 0;
    transition: opacity 120ms ease;
  }
  .node-label.show { opacity: 1; }

  .overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.6);
    display: flex;
    align-items: flex-start;
    justify-content: center;
    padding: clamp(16px, 5vh, 64px) 16px;
    overflow-y: auto;
    z-index: 20;
  }
  .overlay[hidden] { display: none; }

  .case-file {
    background: var(--panel);
    border: 1px solid var(--border);
    max-width: 720px;
    width: 100%;
    box-shadow: 0 20px 60px rgba(0,0,0,0.6);
  }
  .case-head {
    padding: 18px 22px 14px;
    border-bottom: 3px double var(--border);
    display: flex; justify-content: space-between; align-items: flex-start; gap: 16px;
  }
  .case-project {
    font-family: "JetBrains Mono", monospace;
    font-size: 0.76rem;
    letter-spacing: 0.07em;
    text-transform: uppercase;
  }
  .close-btn {
    background: transparent;
    border: 1px solid var(--border);
    color: var(--ink-dim);
    font-family: "JetBrains Mono", monospace;
    font-size: 0.74rem;
    padding: 6px 10px;
    cursor: pointer;
    flex: none;
  }
  .close-btn:hover { color: var(--ink); border-color: var(--ink-dim); }

  .case-body {
    padding: 20px 22px 6px;
    max-height: 60vh;
    overflow-y: auto;
    overflow-x: auto;
    line-height: 1.65;
    font-size: 0.98rem;
  }
  .case-body h2, .case-body h3, .case-body h4 { font-family: "Source Serif 4", serif; margin: 1em 0 0.4em; text-wrap: balance; }
  .case-body h2 { font-size: 1.25rem; }
  .case-body h3 { font-size: 1.05rem; color: var(--stamp); }
  .case-body p { margin: 0 0 0.85em; }
  .case-body ul { margin: 0 0 0.85em; padding-left: 1.3em; }
  .case-body li { margin-bottom: 0.3em; }
  .case-body hr { border: none; border-top: 1px solid var(--border); margin: 1.3em 0; }
  .case-body code { font-family: "JetBrains Mono", monospace; font-size: 0.85em; background: rgba(255,255,255,0.06); padding: 0.1em 0.35em; word-break: break-word; }
  .case-body strong { color: var(--stamp); }

  .case-foot {
    padding: 10px 22px 18px;
    font-family: "JetBrains Mono", monospace;
    font-size: 0.7rem;
    color: var(--ink-dim);
    display: flex; flex-wrap: wrap; gap: 4px 16px;
  }

  @media (max-width: 640px) {
    .legend { display: none; }
    .hint { max-width: 46%; }
  }
</style>

<canvas id="stage"></canvas>

<header class="hud">
  <div class="eyebrow">Recalled from Qdrant · linked by meaning, not by hand</div>
  <h1 class="title">Mnemo Graph</h1>
  <div class="sub" id="stat-line"></div>
</header>

<div class="legend" id="legend"></div>
<div class="hint">drag to rearrange · hover to trace · click to read</div>
<div class="node-label" id="node-label"></div>

<div class="overlay" id="overlay" hidden>
  <div class="case-file" role="dialog" aria-modal="true" aria-labelledby="case-title">
    <div class="case-head">
      <div style="display:flex; flex-direction:column; gap:6px;">
        <span class="case-project" id="case-project"></span>
        <h2 id="case-title" class="stamp-face" style="margin:0; font-size:1.1rem; font-weight:400;"></h2>
      </div>
      <button class="close-btn mono" id="close-btn">CLOSE ✕</button>
    </div>
    <div class="case-body" id="case-body"></div>
    <div class="case-foot" id="case-foot"></div>
  </div>
</div>

<script>
  const GRAPH = __DATA_JSON__;

  const PROJECT_COLOR = {};
  const PALETTE = ["#D2604E", "#7FA08D", "#C9A24B", "#6C8FB0", "#A87FB0", "#8FB06C"];
  const projects = [...new Set(GRAPH.nodes.map(n => n.project))].sort();
  projects.forEach((p, i) => PROJECT_COLOR[p] = PALETTE[i % PALETTE.length]);

  const REDUCE_MOTION = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function escapeHtml(s) {
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
  function renderMarkdown(text) {
    const lines = escapeHtml(text).split("\n");
    let html = ""; let inList = false;
    const closeList = () => { if (inList) { html += "</ul>"; inList = false; } };
    const inline = (s) => s.replace(/`([^`]+)`/g, "<code>$1</code>").replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
    for (const line of lines) {
      if (/^### /.test(line)) { closeList(); html += `<h4>${inline(line.slice(4))}</h4>`; continue; }
      if (/^## /.test(line)) { closeList(); html += `<h3>${inline(line.slice(3))}</h3>`; continue; }
      if (/^# /.test(line)) { closeList(); html += `<h2>${inline(line.slice(2))}</h2>`; continue; }
      if (/^-{3,}$/.test(line.trim())) { closeList(); html += "<hr>"; continue; }
      if (/^[-*]\s+/.test(line)) { if (!inList) { html += "<ul>"; inList = true; } html += `<li>${inline(line.replace(/^[-*]\s+/, ""))}</li>`; continue; }
      if (/^\d+\.\s+/.test(line)) { if (!inList) { html += "<ul>"; inList = true; } html += `<li>${inline(line.replace(/^\d+\.\s+/, ""))}</li>`; continue; }
      closeList();
      if (line.trim() === "") continue;
      html += `<p>${inline(line)}</p>`;
    }
    closeList();
    return html;
  }
  function preview(text, len) {
    len = len || 60;
    const s = text.replace(/[#*`_>]/g, "").replace(/\s+/g, " ").trim();
    return s.length > len ? s.slice(0, len) + "…" : s;
  }

  const nodeById = {};
  const nodes = GRAPH.nodes.map((n, i) => {
    const angle = (i / GRAPH.nodes.length) * Math.PI * 2;
    const obj = { ...n, x: Math.cos(angle) * 160, y: Math.sin(angle) * 160, vx: 0, vy: 0, r: 9, degree: 0 };
    nodeById[n.id] = obj;
    return obj;
  });

  const edges = GRAPH.edges.map(e => ({ ...e, s: nodeById[e.source], t: nodeById[e.target] }));
  edges.forEach(e => { e.s.degree++; e.t.degree++; });
  nodes.forEach(n => { n.r = 7 + Math.min(n.degree, 6) * 1.1; });

  function simTick() {
    const REPEL = 2600;
    const SPRING = 0.02;
    const CENTER = 0.0015;
    const DAMP = 0.86;

    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const a = nodes[i], b = nodes[j];
        let dx = a.x - b.x, dy = a.y - b.y;
        let distSq = dx * dx + dy * dy;
        if (distSq < 1) distSq = 1;
        const dist = Math.sqrt(distSq);
        const force = REPEL / distSq;
        const fx = (dx / dist) * force, fy = (dy / dist) * force;
        a.vx += fx; a.vy += fy;
        b.vx -= fx; b.vy -= fy;
      }
    }

    for (const e of edges) {
      const dx = e.t.x - e.s.x, dy = e.t.y - e.s.y;
      const dist = Math.sqrt(dx * dx + dy * dy) || 1;
      const rest = 260 - e.sim * 190;
      const force = (dist - rest) * SPRING;
      const fx = (dx / dist) * force, fy = (dy / dist) * force;
      e.s.vx += fx; e.s.vy += fy;
      e.t.vx -= fx; e.t.vy -= fy;
    }

    for (const n of nodes) {
      if (n.pinned) continue;
      n.vx -= n.x * CENTER;
      n.vy -= n.y * CENTER;
      n.vx *= DAMP; n.vy *= DAMP;
      n.x += n.vx; n.y += n.vy;
    }
  }

  if (REDUCE_MOTION) {
    for (let i = 0; i < 400; i++) simTick();
  }

  const canvas = document.getElementById("stage");
  const ctx = canvas.getContext("2d");
  let W, H, DPR;
  function resize() {
    DPR = Math.min(window.devicePixelRatio || 1, 2);
    W = window.innerWidth; H = window.innerHeight;
    canvas.width = W * DPR; canvas.height = H * DPR;
    canvas.style.width = W + "px"; canvas.style.height = H + "px";
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
  }
  window.addEventListener("resize", resize);
  resize();

  let hoverNode = null;
  let dragNode = null;
  let dragOffset = { x: 0, y: 0 };

  function toScreen(n) { return { x: W / 2 + n.x, y: H / 2 + n.y }; }
  function fromScreen(x, y) { return { x: x - W / 2, y: y - H / 2 }; }

  function connectedIds(n) {
    const set = new Set([n.id]);
    edges.forEach(e => { if (e.s === n) set.add(e.t.id); if (e.t === n) set.add(e.s.id); });
    return set;
  }

  function draw() {
    ctx.clearRect(0, 0, W, H);
    const highlight = hoverNode ? connectedIds(hoverNode) : null;

    for (const e of edges) {
      const p1 = toScreen(e.s), p2 = toScreen(e.t);
      const dim = highlight && !(highlight.has(e.s.id) && highlight.has(e.t.id));
      ctx.strokeStyle = dim ? "rgba(232,223,200,0.05)" : (highlight ? "rgba(232,223,200,0.55)" : `rgba(232,223,200,${0.08 + e.sim * 0.22})`);
      ctx.lineWidth = highlight && !dim ? 1.4 : 1;
      ctx.beginPath();
      ctx.moveTo(p1.x, p1.y);
      ctx.lineTo(p2.x, p2.y);
      ctx.stroke();
    }

    for (const n of nodes) {
      const p = toScreen(n);
      const dim = highlight && !highlight.has(n.id);
      const color = PROJECT_COLOR[n.project];
      ctx.save();
      ctx.globalAlpha = dim ? 0.28 : 1;
      ctx.shadowColor = color;
      ctx.shadowBlur = n === hoverNode ? 22 : 10;
      ctx.beginPath();
      ctx.arc(p.x, p.y, n.r, 0, Math.PI * 2);
      ctx.fillStyle = color;
      ctx.fill();
      ctx.restore();
    }
  }

  function loop() {
    if (!REDUCE_MOTION) simTick();
    draw();
    requestAnimationFrame(loop);
  }
  loop();

  function nodeAt(x, y) {
    const p = fromScreen(x, y);
    for (let i = nodes.length - 1; i >= 0; i--) {
      const n = nodes[i];
      const dx = n.x - p.x, dy = n.y - p.y;
      if (dx * dx + dy * dy <= (n.r + 4) * (n.r + 4)) return n;
    }
    return null;
  }

  const labelEl = document.getElementById("node-label");

  canvas.addEventListener("mousemove", (e) => {
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left, y = e.clientY - rect.top;
    if (dragNode) {
      const p = fromScreen(x, y);
      dragNode.x = p.x + dragOffset.x;
      dragNode.y = p.y + dragOffset.y;
      dragNode.vx = 0; dragNode.vy = 0;
      return;
    }
    const hit = nodeAt(x, y);
    hoverNode = hit;
    if (hit) {
      const p = toScreen(hit);
      labelEl.textContent = `${hit.project} · ${hit.type} · ${preview(hit.content, 46)}`;
      labelEl.style.left = p.x + "px";
      labelEl.style.top = p.y + "px";
      labelEl.classList.add("show");
      canvas.style.cursor = "pointer";
    } else {
      labelEl.classList.remove("show");
      canvas.style.cursor = "grab";
    }
  });

  canvas.addEventListener("mousedown", (e) => {
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left, y = e.clientY - rect.top;
    const hit = nodeAt(x, y);
    if (hit) {
      dragNode = hit;
      dragNode.pinned = true;
      const p = fromScreen(x, y);
      dragOffset = { x: hit.x - p.x, y: hit.y - p.y };
      canvas.classList.add("dragging");
    }
  });

  let dragStartMoved = false;
  window.addEventListener("mouseup", () => {
    if (dragNode) {
      canvas.classList.remove("dragging");
      if (!dragStartMoved) openCase(dragNode.id);
      dragNode.pinned = false;
      dragNode = null;
    }
    dragStartMoved = false;
  });
  canvas.addEventListener("mousemove", () => { if (dragNode) dragStartMoved = true; });

  canvas.addEventListener("touchstart", (e) => {
    const t = e.touches[0];
    const rect = canvas.getBoundingClientRect();
    const hit = nodeAt(t.clientX - rect.left, t.clientY - rect.top);
    if (hit) openCase(hit.id);
  }, { passive: true });

  function openCase(id) {
    const n = nodeById[id];
    if (!n) return;
    document.getElementById("case-project").textContent = n.project + (n.slug ? " · " + n.slug : "");
    document.getElementById("case-title").textContent = n.type.toUpperCase();
    document.getElementById("case-body").innerHTML = renderMarkdown(n.content);
    const foot = [`id: ${n.id}`, `${n.degree} linked ${n.degree === 1 ? "memory" : "memories"}`];
    document.getElementById("case-foot").innerHTML = foot.map(f => `<span>${escapeHtml(f)}</span>`).join("");
    document.getElementById("overlay").hidden = false;
    document.getElementById("close-btn").focus();
  }
  function closeCase() { document.getElementById("overlay").hidden = true; }
  document.getElementById("close-btn").addEventListener("click", closeCase);
  document.getElementById("overlay").addEventListener("click", (e) => { if (e.target.id === "overlay") closeCase(); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape" && !document.getElementById("overlay").hidden) closeCase(); });

  document.getElementById("stat-line").textContent =
    `${nodes.length} memories · ${edges.length} connections · linked to their ${GRAPH.k} nearest neighbors by meaning`;

  document.getElementById("legend").innerHTML = projects.map(p =>
    `<div class="legend-row"><span class="legend-dot" style="background:${PROJECT_COLOR[p]}"></span>${escapeHtml(p)}</div>`
  ).join("");
</script>
"""
