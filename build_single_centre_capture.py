r"""
build_single_centre_capture.py — build a clean single-centre static HTML capture.

Loads centre.html, inlines a single centre's payload as JSON, stubs the
/api/centre/<id> fetch, and writes a self-contained HTML file with no
chooser bar. Open directly in a browser; no review_server needed.

Default LDC: sid 2358 (Sparrow Early Learning Bayswater). Override via:
    python build_single_centre_capture.py --sid <service_id> [--out <filename>]
"""

import argparse
import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import centre_page  # noqa: E402

REPO = Path(__file__).parent
SOURCE_HTML = REPO / "docs" / "centre.html"
DB_PATH = REPO / "data" / "kintell.db"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sid", type=int, default=2358,
                    help="service_id to render (default 2358 = Sparrow Early Learning Bayswater)")
    ap.add_argument("--out", default=None,
                    help="output filename (default docs/centre_single_<sid>.html)")
    args = ap.parse_args()

    if not SOURCE_HTML.exists():
        print(f"ERROR: {SOURCE_HTML} missing.")
        sys.exit(1)
    if not DB_PATH.exists():
        print(f"ERROR: {DB_PATH} missing.")
        sys.exit(1)

    con = sqlite3.connect(DB_PATH)
    row = con.execute(
        "SELECT service_id, service_name, sa2_code, sa2_name, service_sub_type "
        "FROM services WHERE service_id = ?",
        (args.sid,),
    ).fetchone()
    if not row:
        print(f"ERROR: service_id {args.sid} not found.")
        sys.exit(2)
    sid, name, sa2, sa2_name, subtype = row
    print(f"sid {sid}: {name}  ({subtype} @ {sa2_name} {sa2})")

    payload = centre_page.get_centre_payload(sid)
    if not payload:
        print(f"ERROR: payload empty for sid {sid}.")
        sys.exit(3)
    con.close()

    out_path = REPO / "docs" / (args.out or f"centre_single_{sid}.html")
    src = SOURCE_HTML.read_text(encoding="utf-8")

    payload_json = json.dumps({str(sid): payload}, default=str)

    review_script = f"""
<script>
window.__SINGLE_CENTRE_PAYLOAD__ = {payload_json};
const _origFetch = window.fetch ? window.fetch.bind(window) : null;
window.fetch = function(url, opts) {{
  try {{
    const m = String(url).match(/\\/api\\/centre\\/(\\d+)/);
    if (m) {{
      const data = window.__SINGLE_CENTRE_PAYLOAD__[m[1]];
      if (data) {{
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
  return Promise.reject(new Error("offline single-centre capture: no fallback fetch"));
}};
</script>
"""

    default_id_script = f"""
<script>
(function(){{
  const u = new URL(window.location.href);
  if (!u.searchParams.has("id")) {{
    u.searchParams.set("id", "{sid}");
    window.history.replaceState(null, "", u.toString());
  }}
}})();
</script>
"""

    body_open_idx = src.lower().find("<body")
    body_open_end = src.find(">", body_open_idx) + 1
    head_open_end = src.find(">", src.lower().find("<head")) + 1

    new_html = (
        src[:head_open_end]
        + "\n"
        + default_id_script
        + src[head_open_end:body_open_end]
        + "\n"
        + review_script
        + src[body_open_end:]
    )

    out_path.write_text(new_html, encoding="utf-8")
    size_kb = out_path.stat().st_size / 1024
    print(f"Wrote {out_path} ({size_kb:.1f} KB).")


if __name__ == "__main__":
    main()
