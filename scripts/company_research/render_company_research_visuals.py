from __future__ import annotations

import argparse
import json
import logging
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = ROOT / "docs"
DATA_DIR = ROOT / "data" / "company_research"

TYPE_COLORS = {
    "company": "#1d4ed8",
    "brand": "#7c3aed",
    "function": "#059669",
    "department": "#ea580c",
    "team": "#dc2626",
}


def configure_logging(log_path: Path) -> logging.Logger:
    logger = logging.getLogger("company_research_visuals")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger


def load_research(group: str) -> dict:
    path = DATA_DIR / group / "company_people_research.json"
    return json.loads(path.read_text(encoding="utf-8"))


def org_layout(data: dict) -> dict:
    nodes = [dict(node) for node in data["org_structure_inferred"]["nodes"]]
    relationships = [dict(rel) for rel in data["org_structure_inferred"]["relationships"]]
    nodes_by_id = {node["id"]: node for node in nodes}
    children: dict[str | None, list[str]] = {}
    for node in nodes:
        children.setdefault(node["parent_id"], []).append(node["id"])
    for key in children:
        children[key].sort(key=lambda item: nodes_by_id[item]["name"])

    levels: dict[str, int] = {}

    def assign(node_id: str, depth: int) -> None:
        levels[node_id] = depth
        for child_id in children.get(node_id, []):
            assign(child_id, depth + 1)

    roots = children.get(None, [])
    for root_id in roots:
        assign(root_id, 0)

    grouped: dict[int, list[dict]] = {}
    for node in nodes:
        grouped.setdefault(levels.get(node["id"], 0), []).append(node)
    for level in grouped.values():
        level.sort(key=lambda item: item["name"])

    max_columns = max((len(level_nodes) for level_nodes in grouped.values()), default=1)
    node_w = 260
    node_h = 100
    top = 140
    left = 120
    x_gap = 80
    y_gap = 180
    width = max(1800, left * 2 + max_columns * node_w + max(0, max_columns - 1) * x_gap)
    depth_count = max(grouped.keys(), default=0) + 1
    height = max(980, top + depth_count * y_gap + node_h + 120)

    laid_out = []
    for level_index in sorted(grouped):
        level_nodes = grouped[level_index]
        total_width = len(level_nodes) * node_w + max(0, len(level_nodes) - 1) * x_gap
        start_x = max(left, (width - total_width) / 2)
        for index, node in enumerate(level_nodes):
            x = round(start_x + index * (node_w + x_gap), 2)
            y = round(top + level_index * y_gap, 2)
            node["x"] = x
            node["y"] = y
            node["width"] = node_w
            node["height"] = node_h
            node["color"] = TYPE_COLORS.get(node["type"], "#475569")
            laid_out.append(node)

    relationships_out = []
    for rel in relationships:
        source = nodes_by_id[rel["from_id"]]
        target = nodes_by_id[rel["to_id"]]
        sx = source["x"] + node_w / 2
        sy = source["y"] + node_h
        tx = target["x"] + node_w / 2
        ty = target["y"]
        mid_y = round((sy + ty) / 2, 2)
        rel["path"] = f"M {sx} {sy} L {sx} {mid_y} L {tx} {mid_y} L {tx} {ty}"
        rel["label_x"] = round((sx + tx) / 2, 2)
        rel["label_y"] = mid_y - 8
        relationships_out.append(rel)

    return {"width": width, "height": height, "nodes": laid_out, "relationships": relationships_out}


def people_layout(data: dict) -> dict:
    people_nodes = [dict(node) for node in data["people_graph_inferred"]["nodes"]]
    org_nodes_lookup = {node["id"]: dict(node) for node in data["org_structure_inferred"]["nodes"]}
    relationships = [dict(rel) for rel in data["people_graph_inferred"]["relationships"]]

    referenced_entity_ids: set[str] = set()
    for node in people_nodes:
        referenced_entity_ids.update(node["associated_entities"])
    for rel in relationships:
        if "to_entity_id" in rel:
            referenced_entity_ids.add(rel["to_entity_id"])

    entity_nodes = [org_nodes_lookup[entity_id] for entity_id in sorted(referenced_entity_ids) if entity_id in org_nodes_lookup]
    company_like = [node for node in entity_nodes if node["type"] in {"brand", "company"}]
    function_like = [node for node in entity_nodes if node["type"] in {"function", "department", "team"}]

    width = 2260
    people_box_h = 88
    entity_box_h = 96

    def place_vertical(items: list[dict], x: float, top: float, gap: float, box_type: str) -> list[dict]:
        output = []
        for idx, item in enumerate(sorted(items, key=lambda value: value.get("name", value.get("id", "")))):
            node = dict(item)
            node["x"] = x
            node["y"] = top + idx * gap
            node["box_type"] = box_type
            node["color"] = TYPE_COLORS.get(node.get("type", "team"), "#475569")
            output.append(node)
        return output

    people_laid_out = place_vertical(people_nodes, 120, 170, 126, "person")
    company_laid_out = place_vertical(company_like, 940, 170, 138, "entity")
    function_laid_out = place_vertical(function_like, 1680, 170, 126, "entity")

    all_nodes: dict[str, dict] = {}
    for person in people_laid_out:
        person["width"] = 220
        person["height"] = people_box_h
        all_nodes[person["person_id"]] = person
    for entity in company_laid_out + function_laid_out:
        entity["width"] = 280
        entity["height"] = entity_box_h
        all_nodes[entity["id"]] = entity

    people_bottom = max((node["y"] + node["height"] for node in people_laid_out), default=0)
    company_bottom = max((node["y"] + node["height"] for node in company_laid_out), default=0)
    function_bottom = max((node["y"] + node["height"] for node in function_laid_out), default=0)
    height = max(1180, people_bottom, company_bottom, function_bottom) + 140

    rendered_relationships = []
    for rel in relationships:
        source = all_nodes[rel["from_person_id"]]
        target_id = rel.get("to_person_id") or rel.get("to_entity_id")
        target = all_nodes[target_id]
        sx = source["x"] + source["width"]
        sy = source["y"] + source["height"] / 2
        tx = target["x"]
        ty = target["y"] + target["height"] / 2
        c1x = round(sx + (tx - sx) * 0.35, 2)
        c2x = round(sx + (tx - sx) * 0.7, 2)
        rel["path"] = f"M {sx} {sy} C {c1x} {sy}, {c2x} {ty}, {tx} {ty}"
        rel["label_x"] = round((sx + tx) / 2, 2)
        rel["label_y"] = round((sy + ty) / 2 - 10, 2)
        rendered_relationships.append(rel)

    return {
        "width": width,
        "height": height,
        "people_nodes": people_laid_out,
        "entity_nodes": company_laid_out + function_laid_out,
        "column_labels": [
            {"label": "People", "x": 120, "y": 110},
            {"label": "Companies and Brands", "x": 940, "y": 110},
            {"label": "Functions, Departments, and Teams", "x": 1680, "y": 110},
        ],
        "relationships": rendered_relationships,
    }


def page_shell(title: str, subtitle: str, legend_html: str, canvas_html: str, data_json: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
    :root {{
      --bg: #f3f4f6;
      --panel: #ffffff;
      --ink: #0f172a;
      --muted: #475569;
      --line: #cbd5e1;
      --warning: #fff7ed;
      --warning-border: #fb923c;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
      background: linear-gradient(180deg, #e2e8f0 0%, #f8fafc 24%, #f3f4f6 100%);
      color: var(--ink);
    }}
    .page {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) 340px;
      gap: 18px;
      min-height: 100vh;
      padding: 20px;
    }}
    .main-panel, .side-panel {{
      background: rgba(255,255,255,0.92);
      border: 1px solid rgba(148,163,184,0.35);
      border-radius: 18px;
      box-shadow: 0 16px 40px rgba(15,23,42,0.08);
      overflow: hidden;
    }}
    .header {{
      padding: 20px 22px 16px;
      border-bottom: 1px solid var(--line);
    }}
    .header h1 {{ margin: 0 0 8px; font-size: 30px; }}
    .header p {{ margin: 0; color: var(--muted); line-height: 1.45; }}
    .warning {{
      margin-top: 14px;
      padding: 10px 12px;
      border-radius: 12px;
      border: 1px solid var(--warning-border);
      background: var(--warning);
      color: #9a3412;
      font-weight: 600;
    }}
    .legend {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px 14px;
      margin-top: 14px;
      color: var(--muted);
      font-size: 14px;
    }}
    .legend-item {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
    }}
    .swatch {{
      width: 12px;
      height: 12px;
      border-radius: 999px;
      border: 1px solid rgba(15,23,42,0.15);
      display: inline-block;
    }}
    .canvas-wrap {{
      height: calc(100vh - 210px);
      background:
        radial-gradient(circle at 1px 1px, rgba(148,163,184,0.22) 1px, transparent 0) 0 0 / 22px 22px,
        linear-gradient(180deg, #fff, #f8fafc);
      position: relative;
      overflow: hidden;
    }}
    svg {{ width: 100%; height: 100%; display: block; cursor: grab; }}
    svg.dragging {{ cursor: grabbing; }}
    .node-label {{ font-size: 13px; fill: #0f172a; font-weight: 700; }}
    .node-sub {{ font-size: 11px; fill: #334155; }}
    .edge-label {{ font-size: 11px; fill: #475569; font-weight: 700; paint-order: stroke; stroke: #fff; stroke-width: 5px; stroke-linejoin: round; }}
    .side-panel {{
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}
    .side-panel h2 {{ margin: 0; font-size: 18px; }}
    .detail {{
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 14px;
      background: #f8fafc;
      min-height: 220px;
    }}
    .detail h3 {{ margin: 0 0 8px; font-size: 18px; }}
    .detail p {{ margin: 0 0 10px; color: var(--muted); line-height: 1.45; }}
    .detail ul {{
      margin: 10px 0 0;
      padding-left: 18px;
      color: var(--muted);
      line-height: 1.45;
    }}
    .help {{
      border: 1px dashed var(--line);
      border-radius: 14px;
      padding: 14px;
      color: var(--muted);
      background: #fff;
      font-size: 14px;
      line-height: 1.45;
    }}
    @media (max-width: 1180px) {{
      .page {{ grid-template-columns: 1fr; }}
      .canvas-wrap {{ height: 70vh; }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <section class="main-panel">
      <div class="header">
        <h1>{escape(title)}</h1>
        <p>{escape(subtitle)}</p>
        <div class="warning">Inferred from public evidence; not an official org chart.</div>
        <div class="legend">{legend_html}</div>
      </div>
      <div class="canvas-wrap">
        {canvas_html}
      </div>
    </section>
    <aside class="side-panel">
      <h2>Details</h2>
      <div class="detail" id="detail-panel">
        <h3>Hover a node or edge</h3>
        <p>Use the canvas to inspect inferred structure, confidence, and supporting evidence.</p>
      </div>
      <div class="help">
        Drag to pan. Use the mouse wheel to zoom. Hover or click an item for details.
      </div>
    </aside>
  </div>
  <script>
    const graphData = {data_json};
    const detailPanel = document.getElementById('detail-panel');
    function renderDetail(title, body, evidence) {{
      const items = Array.isArray(evidence) ? evidence.map((item) => `<li>${{item}}</li>`).join('') : '';
      detailPanel.innerHTML = `<h3>${{title}}</h3><p>${{body}}</p>${{items ? `<ul>${{items}}</ul>` : ''}}`;
    }}
    const svg = document.querySelector('svg');
    const viewport = document.getElementById('viewport');
    let scale = 1;
    let tx = 0;
    let ty = 0;
    let dragging = false;
    let lastX = 0;
    let lastY = 0;
    function applyTransform() {{
      viewport.setAttribute('transform', `translate(${{tx}} ${{ty}}) scale(${{scale}})`);
    }}
    svg.addEventListener('wheel', (event) => {{
      event.preventDefault();
      const delta = event.deltaY < 0 ? 1.08 : 0.92;
      scale = Math.min(2.4, Math.max(0.45, scale * delta));
      applyTransform();
    }}, {{ passive: false }});
    svg.addEventListener('mousedown', (event) => {{
      dragging = true;
      lastX = event.clientX;
      lastY = event.clientY;
      svg.classList.add('dragging');
    }});
    window.addEventListener('mouseup', () => {{
      dragging = false;
      svg.classList.remove('dragging');
    }});
    window.addEventListener('mousemove', (event) => {{
      if (!dragging) return;
      tx += event.clientX - lastX;
      ty += event.clientY - lastY;
      lastX = event.clientX;
      lastY = event.clientY;
      applyTransform();
    }});
    document.querySelectorAll('[data-detail]').forEach((element) => {{
      const payload = JSON.parse(element.dataset.detail);
      const handler = () => renderDetail(payload.title, payload.body, payload.evidence);
      element.addEventListener('mouseenter', handler);
      element.addEventListener('click', handler);
    }});
    applyTransform();
  </script>
</body>
</html>
"""


def render_org_chart_html(data: dict) -> str:
    layout = org_layout(data)
    legend = "".join(
        f'<span class="legend-item"><span class="swatch" style="background:{color}"></span>{escape(node_type.title())}</span>'
        for node_type, color in TYPE_COLORS.items()
    )
    legend += (
        '<span class="legend-item"><strong>Confidence:</strong> High &gt;= 0.80, Medium 0.60-0.79, Low &lt; 0.60</span>'
    )

    edge_parts = []
    for rel in layout["relationships"]:
        detail = {
            "title": f'{rel["relationship_type"]}: {rel["from_id"]} -> {rel["to_id"]}',
            "body": f'Confidence {rel["confidence"]:.3f}. Inferred operating link, not a legal reporting statement.',
            "evidence": rel["evidence"],
        }
        edge_parts.append(
            f'<path d="{rel["path"]}" fill="none" stroke="#94a3b8" stroke-width="2.4" '
            f'data-detail="{escape(json.dumps(detail, ensure_ascii=True))}"></path>'
        )
        edge_parts.append(
            f'<text x="{rel["label_x"]}" y="{rel["label_y"]}" text-anchor="middle" class="edge-label">{escape(rel["relationship_type"])}</text>'
        )

    node_parts = []
    for node in layout["nodes"]:
        detail = {
            "title": node["name"],
            "body": f'{node["type"].title()} node with confidence {node["confidence"]:.3f}. {node["description"]}',
            "evidence": node["evidence"],
        }
        node_parts.append(
            f'<g transform="translate({node["x"]} {node["y"]})" data-detail="{escape(json.dumps(detail, ensure_ascii=True))}">'
            f'<rect width="{node["width"]}" height="{node["height"]}" rx="18" fill="#ffffff" stroke="{node["color"]}" stroke-width="3"></rect>'
            f'<rect width="{node["width"]}" height="12" rx="18" fill="{node["color"]}"></rect>'
            f'<text x="16" y="34" class="node-label">{escape(node["name"])}</text>'
            f'<text x="16" y="56" class="node-sub">Type: {escape(node["type"])}</text>'
            f'<text x="16" y="74" class="node-sub">Confidence: {node["confidence"]:.3f}</text>'
            '</g>'
        )

    canvas = (
        f'<svg viewBox="0 0 {layout["width"]} {layout["height"]}" aria-label="Venuiti inferred org structure">'
        '<g id="viewport">'
        + "".join(edge_parts)
        + "".join(node_parts)
        + '</g></svg>'
    )
    return page_shell(
        "Venuiti Inferred Org Structure",
        "Evidence-based operating hierarchy view of the Venuiti group, brands, and supported functions. This is an inferred structure view, not an authoritative legal org chart.",
        legend,
        canvas,
        json.dumps(layout, ensure_ascii=True, indent=2),
    )


def render_people_graph_html(data: dict) -> str:
    layout = people_layout(data)
    legend = (
        '<span class="legend-item"><span class="swatch" style="background:#0f766e"></span>Person</span>'
        '<span class="legend-item"><span class="swatch" style="background:#1d4ed8"></span>Company</span>'
        '<span class="legend-item"><span class="swatch" style="background:#7c3aed"></span>Brand</span>'
        '<span class="legend-item"><span class="swatch" style="background:#059669"></span>Function</span>'
        '<span class="legend-item"><span class="swatch" style="background:#ea580c"></span>Department</span>'
        '<span class="legend-item"><span class="swatch" style="background:#dc2626"></span>Team</span>'
        '<span class="legend-item"><strong>Confidence:</strong> High &gt;= 0.80, Medium 0.60-0.79, Low &lt; 0.60</span>'
    )

    label_parts = []
    for item in layout["column_labels"]:
        label_parts.append(
            f'<text x="{item["x"]}" y="{item["y"]}" class="node-label">{escape(item["label"])}</text>'
        )

    edge_parts = []
    for rel in layout["relationships"]:
        target_key = rel.get("to_person_id") or rel.get("to_entity_id")
        detail = {
            "title": rel["relationship_type"],
            "body": f'{rel["from_person_id"]} linked to {target_key} with confidence {rel["confidence"]:.3f}. No reporting line is implied.',
            "evidence": rel["evidence"],
        }
        edge_parts.append(
            f'<path d="{rel["path"]}" fill="none" stroke="#94a3b8" stroke-width="2.2" '
            f'data-detail="{escape(json.dumps(detail, ensure_ascii=True))}"></path>'
        )
        edge_parts.append(
            f'<text x="{rel["label_x"]}" y="{rel["label_y"]}" text-anchor="middle" class="edge-label">{escape(rel["relationship_type"])}</text>'
        )

    node_parts = []
    for person in layout["people_nodes"]:
        detail = {
            "title": person["name"],
            "body": f'Person node with confidence {person["confidence"]:.3f}. Likely functions: {", ".join(person["likely_functions"])}.',
            "evidence": [f'Associated entities: {", ".join(person["associated_entities"])}'],
        }
        node_parts.append(
            f'<g transform="translate({person["x"]} {person["y"]})" data-detail="{escape(json.dumps(detail, ensure_ascii=True))}">'
            f'<rect width="{person["width"]}" height="{person["height"]}" rx="18" fill="#ecfeff" stroke="#0f766e" stroke-width="3"></rect>'
            f'<text x="16" y="32" class="node-label">{escape(person["name"])}</text>'
            f'<text x="16" y="54" class="node-sub">Person</text>'
            f'<text x="16" y="72" class="node-sub">Confidence: {person["confidence"]:.3f}</text>'
            '</g>'
        )

    for entity in layout["entity_nodes"]:
        detail = {
            "title": entity["name"],
            "body": f'{entity["type"].title()} node from the inferred structure graph with confidence {entity["confidence"]:.3f}. {entity["description"]}',
            "evidence": entity["evidence"],
        }
        node_parts.append(
            f'<g transform="translate({entity["x"]} {entity["y"]})" data-detail="{escape(json.dumps(detail, ensure_ascii=True))}">'
            f'<rect width="{entity["width"]}" height="{entity["height"]}" rx="18" fill="#ffffff" stroke="{entity["color"]}" stroke-width="3"></rect>'
            f'<rect width="{entity["width"]}" height="10" rx="18" fill="{entity["color"]}"></rect>'
            f'<text x="16" y="34" class="node-label">{escape(entity["name"])}</text>'
            f'<text x="16" y="56" class="node-sub">Type: {escape(entity["type"])}</text>'
            f'<text x="16" y="74" class="node-sub">Confidence: {entity["confidence"]:.3f}</text>'
            '</g>'
        )

    canvas = (
        f'<svg viewBox="0 0 {layout["width"]} {layout["height"]}" aria-label="Venuiti inferred people graph">'
        '<g id="viewport">'
        + "".join(label_parts)
        + "".join(edge_parts)
        + "".join(node_parts)
        + '</g></svg>'
    )
    return page_shell(
        "Venuiti Inferred People Graph",
        "Static network view of evidence-backed person-to-entity and person-to-person relationships across the Venuiti research set. Relationship labels are intentionally conservative and do not imply reporting lines.",
        legend,
        canvas,
        json.dumps(layout, ensure_ascii=True, indent=2),
    )


def write_visuals(group: str, logger: logging.Logger) -> None:
    data = load_research(group)
    org_html = render_org_chart_html(data)
    people_html = render_people_graph_html(data)
    org_path = DOCS_DIR / f"{group}_org_chart.html"
    people_path = DOCS_DIR / f"{group}_people_graph.html"
    org_path.write_text(org_html, encoding="utf-8")
    people_path.write_text(people_html, encoding="utf-8")
    logger.info("Wrote %s", org_path)
    logger.info("Wrote %s", people_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render standalone company research visual pages.")
    parser.add_argument("--group", default="venuiti", help="Group slug to render.")
    args = parser.parse_args()
    log_dir = DATA_DIR / args.group
    log_dir.mkdir(parents=True, exist_ok=True)
    logger = configure_logging(log_dir / "render_company_research_visuals.log.txt")
    try:
        write_visuals(args.group, logger)
    except Exception as exc:
        logger.exception("Visual render failed: %s", exc)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
