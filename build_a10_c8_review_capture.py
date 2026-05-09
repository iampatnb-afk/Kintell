r"""
build_a10_c8_review_capture.py — generate a self-contained loadable HTML
showing the centre page for the 4 verification SA2s with the new
Demographic Mix sub-panel rendered.

Output: docs/a10_c8_review.html

The capture inlines the centre payloads as JSON inside the HTML and stubs
out the /api/centre/<id> fetch path so centre.html can render purely from
local data (no review_server required). Patrick can open the file
directly in a browser.

Run: PYTHONIOENCODING=utf-8 python build_a10_c8_review_capture.py
"""

import json
import sqlite3
import sys
from pathlib import Path

# Pre-amble for finding centre_page.py via venv etc.
sys.path.insert(0, str(Path(__file__).parent))
import centre_page  # noqa: E402

REPO = Path(__file__).parent
SOURCE_HTML = REPO / "docs" / "centre.html"
OUTPUT_HTML = REPO / "docs" / "a10_c8_review.html"
DB_PATH = REPO / "data" / "kintell.db"

VERIFY_SA2 = [
    ("211011251", "Bayswater Vic"),
    ("118011341", "Bondi Junction-Waverly NSW"),
    ("506031124", "Bentley-Wilson-St James WA"),
    ("702041063", "Outback NT (high-ATSI)"),
]


def pick_service_id(con, sa2_code):
    """Pick a representative service for the SA2 — the one with a non-null
    business name, fewest tenure surprises, or just the first."""
    row = con.execute(
        "SELECT service_id FROM services "
        "WHERE sa2_code = ? AND service_name IS NOT NULL "
        "ORDER BY service_id LIMIT 1",
        (sa2_code,),
    ).fetchone()
    return row[0] if row else None


def build():
    if not SOURCE_HTML.exists():
        print(f"ERROR: {SOURCE_HTML} missing.")
        sys.exit(1)
    if not DB_PATH.exists():
        print(f"ERROR: {DB_PATH} missing.")
        sys.exit(1)

    con = sqlite3.connect(DB_PATH)
    captures = []
    for sa2, label in VERIFY_SA2:
        sid = pick_service_id(con, sa2)
        if sid is None:
            print(f"  {sa2} ({label}): no service found, skipping")
            continue
        payload = centre_page.get_centre_payload(sid)
        if not payload:
            print(f"  {sa2} ({label}, sid={sid}): payload None, skipping")
            continue
        captures.append({
            "sa2_code": sa2,
            "sa2_label": label,
            "service_id": sid,
            "service_name": payload.get("header", {}).get("service_name", "(no name)"),
            "payload": payload,
        })
        print(f"  {sa2} ({label}, sid={sid}): payload captured")
    con.close()

    if not captures:
        print("ERROR: no captures built; aborting.")
        sys.exit(2)

    src = SOURCE_HTML.read_text(encoding="utf-8")

    # Build the embedded payloads JSON. Keys are service_id (string).
    payloads_by_id = {str(c["service_id"]): c["payload"] for c in captures}
    payloads_json = json.dumps(payloads_by_id, default=str)

    # Build the chooser bar HTML
    chooser_items = "".join(
        f'<button data-sid="{c["service_id"]}" '
        f'style="padding:8px 14px;background:var(--panel-2);border:1px solid var(--border);'
        f'color:var(--text);border-radius:6px;cursor:pointer;font-size:12.5px;">'
        f'{c["sa2_label"]} <span style="color:var(--text-mute);font-size:11px;">'
        f'sid {c["service_id"]} &middot; {c["sa2_code"]}</span></button>'
        for c in captures
    )
    first_sid = captures[0]["service_id"]

    chooser_html = f"""
  <div id="a10_c8_review_bar" style="
       position:sticky;top:0;z-index:100;
       background:var(--panel);border-bottom:1px solid var(--border);
       padding:14px 22px;display:flex;flex-wrap:wrap;gap:10px;
       align-items:center;">
    <div style="font-weight:600;color:var(--text);margin-right:12px;">
      A10 + C8 review capture
      <span style="font-weight:400;color:var(--text-mute);font-size:12px;margin-left:6px;">
        Demographic Mix bundle &middot; static snapshot ({len(captures)} verification SA2s)
      </span>
    </div>
    {chooser_items}
  </div>
"""

    # Inline payloads + override window.fetch for /api/centre/<id> calls
    review_script = f"""
<script>
window.__A10_C8_PAYLOADS__ = {payloads_json};
const _origFetch = window.fetch ? window.fetch.bind(window) : null;
window.fetch = function(url, opts) {{
  try {{
    const m = String(url).match(/\\/api\\/centre\\/(\\d+)/);
    if (m) {{
      const sid = m[1];
      const data = window.__A10_C8_PAYLOADS__[sid];
      if (data) {{
        // centre.html's api() helper returns r.json() and the page
        // expects shape {{ok: true, centre: <payload>}}.
        const wrapped = {{ ok: true, centre: data }};
        return Promise.resolve({{
          ok: true, status: 200,
          json: () => Promise.resolve(wrapped),
          text: () => Promise.resolve(JSON.stringify(wrapped)),
        }});
      }}
    }}
  }} catch (e) {{ /* fall through */ }}
  if (_origFetch) return _origFetch(url, opts);
  return Promise.reject(new Error("offline review capture: no fallback fetch"));
}};

// Attach service-switcher behaviour after DOM ready
document.addEventListener("DOMContentLoaded", () => {{
  const bar = document.getElementById("a10_c8_review_bar");
  if (!bar) return;
  bar.querySelectorAll("button[data-sid]").forEach(btn => {{
    btn.addEventListener("click", () => {{
      const sid = btn.getAttribute("data-sid");
      const u = new URL(window.location.href);
      u.searchParams.set("id", sid);
      window.location.href = u.toString();
    }});
  }});
  // Highlight active service
  const params = new URLSearchParams(window.location.search);
  const cur = params.get("id");
  bar.querySelectorAll("button[data-sid]").forEach(btn => {{
    if (btn.getAttribute("data-sid") === cur) {{
      btn.style.background = "var(--panel-3)";
      btn.style.borderColor = "var(--accent)";
    }}
  }});
}});
</script>
"""

    # Inject the review script at the start of <body>, then the chooser bar
    # right after <body>.
    body_open_idx = src.lower().find("<body")
    body_open_end = src.find(">", body_open_idx) + 1
    if body_open_idx == -1:
        print("ERROR: <body> not found in centre.html.")
        sys.exit(3)

    new_html = (
        src[:body_open_end]
        + "\n"
        + review_script
        + chooser_html
        + src[body_open_end:]
    )

    # Default the URL to the first captured service if none is set
    # (centre.html's render() reads ?id=<service_id> from the URL).
    # Add a tiny inline <script> at the very top of <head> that sets
    # the URL param if missing — runs before centre.html's own scripts
    # so that location.search.id is populated by the time render() reads it.
    default_id_script = f"""
<script>
(function(){{
  const u = new URL(window.location.href);
  if (!u.searchParams.has("id")) {{
    u.searchParams.set("id", "{first_sid}");
    window.history.replaceState(null, "", u.toString());
  }}
}})();
</script>
"""
    head_idx = new_html.lower().find("<head>")
    if head_idx != -1:
        head_end = head_idx + len("<head>")
        new_html = new_html[:head_end] + "\n" + default_id_script + new_html[head_end:]

    OUTPUT_HTML.write_text(new_html, encoding="utf-8")
    size_kb = OUTPUT_HTML.stat().st_size / 1024
    print(f"\nWrote {OUTPUT_HTML} ({size_kb:.1f} KB).")
    print(f"Open in a browser to review (no review_server needed).")
    print(f"Default service: sid={first_sid} ({captures[0]['sa2_label']}).")


if __name__ == "__main__":
    build()
