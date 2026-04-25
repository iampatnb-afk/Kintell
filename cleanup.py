"""
cleanup.py — housekeeping script for remara-agent folder.
Deletes one-time patch/install scripts that are no longer needed.
Run once: python cleanup.py
"""
from pathlib import Path

TO_DELETE = [
    "patch_module5.py",
    "patch_module5b.py", 
    "patch_module5_footer.py",
    "install_module2b.py",
    "fix_module2b.py",
    "check_review.py",
]

for fname in TO_DELETE:
    p = Path(fname)
    if p.exists():
        p.unlink()
        print(f"Deleted: {fname}")
    else:
        print(f"Not found (already gone): {fname}")

# Fix duplicate prospecting banners in module5
src = Path("module5_digest.py").read_text(encoding="utf-8")
banner = (
    "<div style='margin-top:20px;padding:12px 16px;"
    "background:#2c3e50;border-radius:6px;text-align:center'>"
    "<a href='data/operators_prospecting.html' "
    "style='color:#3498db;font-size:13px;font-weight:bold;text-decoration:none'>"
    "View Full Prospecting List &#8594;</a>"
    "<span style='color:#aaa;font-size:12px;margin-left:16px'>"
    "Hot &amp; warm targets, filterable by state / score / centre count"
    "</span></div><br>"
)
count = src.count(banner)
if count > 1:
    # Keep only first occurrence
    first = src.find(banner)
    rest = src[first + len(banner):]
    rest_cleaned = rest.replace(banner, "")
    src = src[:first + len(banner)] + rest_cleaned
    Path("module5_digest.py").write_text(src, encoding="utf-8")
    print(f"Fixed: removed {count-1} duplicate prospecting banner(s) from module5_digest.py")
elif count == 1:
    print("module5_digest.py: prospecting banner OK (1 instance)")
else:
    print("module5_digest.py: no prospecting banner found")

# Clear test data from leads_catchment.json
import json
Path("leads_catchment.json").write_text("[]", encoding="utf-8")
print("Cleared: leads_catchment.json reset to empty")

print("\nCleanup complete.")
