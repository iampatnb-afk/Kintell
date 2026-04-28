"""
layer3_diag.py

Read-only diagnostic for Layer 3 banding apply work.

Probes the live DB and supporting files to surface:
  1. SA2 cohort lookup source (state + remoteness assignment per SA2)
  2. Source-metric inventory across abs_sa2_* tables
  3. Banding cutoff conventions in shipped UI (low/mid/high)
  4. Initial Layer 3 metric set proposal with formulas
  5. Expected row counts for layer3_sa2_metric_banding

Output: recon/layer3_diag.md
No DB writes. No file mutations outside recon/.

Usage:
  cd <repo root>
  python layer3_diag.py
"""
import os
import re
import sqlite3
from collections import defaultdict
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
DB_PATH = REPO_ROOT / "data" / "kintell.db"
OUTPUT_PATH = REPO_ROOT / "recon" / "layer3_diag.md"
GPKG_PATH = REPO_ROOT / "abs_data" / "ASGS_2021_Main_Structure_GDA2020.gpkg"

# Files that may contain banding cutoff conventions
UI_FILES_TO_GREP = [
    "docs/_op_chunks/part2.txt",
    "docs/_op_chunks/part3.txt",
    "docs/_op_chunks/part4.txt",
    "docs/operator.html",
    "docs/centre.html",
    "docs/index.html",
    "catchment_html.py",
    "centre_page.py",
    "operator_page.py",
    "module2b_catchment.py",
    "generate_dashboard.py",
]

# State-from-SA2-prefix mapping (ABS convention)
STATE_PREFIX_MAP = {
    "1": "NSW", "2": "VIC", "3": "QLD", "4": "SA",
    "5": "WA",  "6": "TAS", "7": "NT",  "8": "ACT",
    "9": "OT",
}


# --------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------

def fmt_int(n):
    if n is None:
        return "n/a"
    return f"{n:,}"


def md_pipe_safe(s):
    if s is None:
        return ""
    return str(s).replace("|", "\\|").replace("\n", " ")


def clip(s, n=140):
    s = str(s).replace("\t", " ").rstrip()
    if len(s) > n:
        return s[: n - 3] + "..."
    return s


def read_text_safe(path):
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="latin-1")
        except Exception:
            return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


# --------------------------------------------------------------------
# Section 1 — SA2 cohort source
# --------------------------------------------------------------------

def probe_sa2_cohort_source(cur):
    print("[1/5] Probing SA2 cohort source...", flush=True)
    findings = {}

    # 1a. State-from-prefix distribution across services.sa2_code
    try:
        cur.execute("""
            SELECT SUBSTR(sa2_code, 1, 1) AS state_digit, COUNT(*) AS n
              FROM services
             WHERE sa2_code IS NOT NULL
          GROUP BY state_digit
          ORDER BY state_digit
        """)
        rows = cur.fetchall()
        findings["state_prefix_dist"] = rows
    except sqlite3.Error as e:
        findings["state_prefix_dist_err"] = str(e)

    # 1b. SA2 distinct count from each source we might draw cohorts from
    try:
        cur.execute("SELECT COUNT(DISTINCT sa2_code) FROM services "
                    "WHERE sa2_code IS NOT NULL")
        findings["distinct_sa2_services"] = cur.fetchone()[0]
    except sqlite3.Error:
        findings["distinct_sa2_services"] = None

    try:
        cur.execute("SELECT COUNT(DISTINCT sa2_code) FROM abs_sa2_erp_annual")
        findings["distinct_sa2_erp"] = cur.fetchone()[0]
    except sqlite3.Error:
        findings["distinct_sa2_erp"] = None

    try:
        cur.execute("SELECT COUNT(DISTINCT sa2_code) FROM abs_sa2_births_annual")
        findings["distinct_sa2_births"] = cur.fetchone()[0]
    except sqlite3.Error:
        findings["distinct_sa2_births"] = None

    # 1c. services-derived remoteness: most-common aria_plus per SA2
    try:
        cur.execute("""
            WITH ranked AS (
                SELECT sa2_code, aria_plus, COUNT(*) AS n,
                       ROW_NUMBER() OVER (
                         PARTITION BY sa2_code
                         ORDER BY COUNT(*) DESC, aria_plus
                       ) AS rk
                  FROM services
                 WHERE sa2_code IS NOT NULL
                   AND aria_plus IS NOT NULL
              GROUP BY sa2_code, aria_plus
            )
            SELECT aria_plus, COUNT(*) AS sa2_n
              FROM ranked
             WHERE rk = 1
          GROUP BY aria_plus
          ORDER BY sa2_n DESC
        """)
        findings["services_derived_remoteness_dist"] = cur.fetchall()
    except sqlite3.Error as e:
        findings["services_derived_remoteness_err"] = str(e)

    # 1d. SA2s WITHOUT any service coverage (would be missed by services-derived)
    try:
        cur.execute("""
            SELECT COUNT(DISTINCT e.sa2_code)
              FROM abs_sa2_erp_annual e
             WHERE e.sa2_code NOT IN (
                   SELECT DISTINCT sa2_code FROM services
                    WHERE sa2_code IS NOT NULL
             )
        """)
        findings["sa2s_no_services"] = cur.fetchone()[0]
    except sqlite3.Error:
        findings["sa2s_no_services"] = None

    # 1e. GeoPackage probe — try fiona for layer schema (read-only)
    findings["gpkg_path"] = str(GPKG_PATH.relative_to(REPO_ROOT)).replace("\\", "/")
    findings["gpkg_exists"] = GPKG_PATH.exists()
    if GPKG_PATH.exists():
        try:
            import fiona
            layers = fiona.listlayers(str(GPKG_PATH))
            findings["gpkg_layers"] = layers
            sa2_layer = next(
                (lyr for lyr in layers if "SA2" in lyr.upper()),
                None
            )
            findings["gpkg_sa2_layer"] = sa2_layer
            if sa2_layer:
                with fiona.open(str(GPKG_PATH), layer=sa2_layer) as src:
                    findings["gpkg_sa2_schema"] = dict(src.schema["properties"])
                    findings["gpkg_sa2_feature_count"] = len(src)
                    sample = next(iter(src), None)
                    if sample:
                        findings["gpkg_sa2_sample_props"] = dict(
                            sample["properties"])
        except ImportError:
            findings["gpkg_err"] = "fiona not installed (pip install fiona)"
        except Exception as e:
            findings["gpkg_err"] = f"{type(e).__name__}: {e}"

    return findings


# --------------------------------------------------------------------
# Section 2 — Source-metric inventory
# --------------------------------------------------------------------

def probe_source_metrics(cur):
    print("[2/5] Probing source-metric inventory...", flush=True)
    findings = {}

    # 2a. abs_sa2_erp_annual — list age_groups + per-year SA2 counts
    try:
        cur.execute("""
            SELECT age_group, COUNT(*) AS n_rows,
                   COUNT(DISTINCT sa2_code) AS n_sa2,
                   MIN(year) AS y_min, MAX(year) AS y_max,
                   SUM(CASE WHEN persons IS NULL THEN 1 ELSE 0 END) AS n_nulls
              FROM abs_sa2_erp_annual
          GROUP BY age_group
          ORDER BY age_group
        """)
        findings["erp_age_groups"] = cur.fetchall()
    except sqlite3.Error as e:
        findings["erp_age_groups_err"] = str(e)

    # 2b. abs_sa2_socioeconomic_annual — distinct metric_name
    try:
        cur.execute("""
            SELECT metric_name, COUNT(*) AS n_rows,
                   COUNT(DISTINCT sa2_code) AS n_sa2,
                   MIN(year) AS y_min, MAX(year) AS y_max,
                   SUM(CASE WHEN value IS NULL THEN 1 ELSE 0 END) AS n_nulls,
                   AVG(value) AS avg_val
              FROM abs_sa2_socioeconomic_annual
          GROUP BY metric_name
          ORDER BY metric_name
        """)
        findings["socioeconomic_metrics"] = cur.fetchall()
    except sqlite3.Error as e:
        findings["socioeconomic_metrics_err"] = str(e)

    # 2c. abs_sa2_education_employment_annual — distinct metric_name
    try:
        cur.execute("""
            SELECT metric_name, COUNT(*) AS n_rows,
                   COUNT(DISTINCT sa2_code) AS n_sa2,
                   MIN(year) AS y_min, MAX(year) AS y_max,
                   SUM(CASE WHEN value IS NULL THEN 1 ELSE 0 END) AS n_nulls,
                   AVG(value) AS avg_val
              FROM abs_sa2_education_employment_annual
          GROUP BY metric_name
          ORDER BY metric_name
        """)
        findings["ee_metrics"] = cur.fetchall()
    except sqlite3.Error as e:
        findings["ee_metrics_err"] = str(e)

    # 2d. abs_sa2_births_annual — yearly summary
    try:
        cur.execute("""
            SELECT year, COUNT(*) AS n_rows,
                   COUNT(DISTINCT sa2_code) AS n_sa2,
                   SUM(CASE WHEN births_count IS NULL THEN 1 ELSE 0 END) AS n_nulls,
                   SUM(births_count) AS national_total
              FROM abs_sa2_births_annual
          GROUP BY year
          ORDER BY year
        """)
        findings["births_yearly"] = cur.fetchall()
    except sqlite3.Error as e:
        findings["births_yearly_err"] = str(e)

    # 2e. abs_sa2_unemployment_quarterly — latest 4 quarters
    try:
        cur.execute("""
            SELECT year_qtr, COUNT(*) AS n_rows,
                   COUNT(DISTINCT sa2_code) AS n_sa2,
                   SUM(CASE WHEN rate IS NULL THEN 1 ELSE 0 END) AS n_null_rate,
                   AVG(rate) AS avg_rate
              FROM abs_sa2_unemployment_quarterly
          GROUP BY year_qtr
          ORDER BY year_qtr DESC
             LIMIT 8
        """)
        findings["salm_recent"] = cur.fetchall()
    except sqlite3.Error as e:
        findings["salm_recent_err"] = str(e)

    # 2f. JSA IVI state — latest months
    try:
        cur.execute("""
            SELECT year_month, COUNT(*) AS n_rows
              FROM jsa_ivi_state_monthly
          GROUP BY year_month
          ORDER BY year_month DESC
             LIMIT 6
        """)
        findings["jsa_state_recent"] = cur.fetchall()
    except sqlite3.Error as e:
        findings["jsa_state_recent_err"] = str(e)

    return findings


# --------------------------------------------------------------------
# Section 3 — Banding cutoff conventions in shipped UI
# --------------------------------------------------------------------

def probe_banding_cutoffs():
    print("[3/5] Probing shipped UI banding cutoffs...", flush=True)

    # Patterns that often surround actual numerical cutoffs
    patterns = [
        re.compile(r"(?:^|[^\w])decile\s*[<>=!]{1,2}\s*\d+", re.IGNORECASE),
        re.compile(r"\d+\s*[<>=!]{1,2}\s*decile", re.IGNORECASE),
        re.compile(r"['\"]?(?:low|mid|medium|high)['\"]?[^,;:\n]{0,40}"
                   r"[<>=!]{1,2}\s*\d+", re.IGNORECASE),
        re.compile(r"\bif\s+\w*decile\w*\s*[<>=!]{1,2}\s*\d+", re.IGNORECASE),
        re.compile(r"weighted_decile\s*[<>=!]{1,2}\s*\d+", re.IGNORECASE),
        re.compile(r"\bwd\s*[<>=!]{1,2}\s*\d+", re.IGNORECASE),
        re.compile(r"['\"]low['\"]\s*:.*?\d+|['\"]high['\"]\s*:.*?\d+",
                   re.IGNORECASE),
    ]
    keyword_re = re.compile(r"low|mid|medium|high|decile", re.IGNORECASE)

    hits_per_file = []
    for relpath in UI_FILES_TO_GREP:
        path = REPO_ROOT / relpath
        if not path.exists():
            continue
        text = read_text_safe(path)
        if not text:
            continue
        for line_no, line in enumerate(text.splitlines(), 1):
            for pat in patterns:
                if pat.search(line):
                    hits_per_file.append({
                        "file": relpath.replace("\\", "/"),
                        "line": line_no,
                        "snippet": clip(line, 200),
                    })
                    break

        # Also: capture lines containing both 'decile' and a comparator,
        # for context that the regex above might miss
        for line_no, line in enumerate(text.splitlines(), 1):
            if "decile" in line.lower() and any(
                k in line for k in ["<=", ">=", "<", ">", "==", "!="]
            ):
                hits_per_file.append({
                    "file": relpath.replace("\\", "/"),
                    "line": line_no,
                    "snippet": clip(line, 200),
                })

    # De-dup by (file, line)
    seen = set()
    unique = []
    for h in hits_per_file:
        key = (h["file"], h["line"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(h)
    unique.sort(key=lambda x: (x["file"], x["line"]))
    return unique


# --------------------------------------------------------------------
# Section 4 — Proposed initial metric set
# --------------------------------------------------------------------

PROPOSED_METRICS = [
    # (canonical_metric_name, source_table, source_column_or_metric_name,
    #  filter, description, default_cohort)
    ("sa2_under5_count",
     "abs_sa2_erp_annual",
     "persons",
     "age_group = '0-4'",
     "Under-5 population, by year",
     "state"),
    ("sa2_total_population",
     "abs_sa2_erp_annual",
     "persons",
     "age_group = 'All ages'",
     "Total SA2 population (verify exact age_group label in diag)",
     "state_x_remoteness"),
    ("sa2_under5_growth_5y",
     "abs_sa2_erp_annual (derived)",
     "persons",
     "age_group = '0-4'; (year_t - year_t-5) / year_t-5",
     "5-year CAGR of under-5 population",
     "remoteness"),
    ("sa2_births_count",
     "abs_sa2_births_annual",
     "births_count",
     "(none)",
     "SA2 births, by year",
     "state_x_remoteness"),
    ("sa2_unemployment_rate",
     "abs_sa2_unemployment_quarterly",
     "rate",
     "latest year_qtr",
     "Unemployment rate, latest quarter",
     "state"),
    ("sa2_median_employee_income",
     "abs_sa2_socioeconomic_annual",
     "value where metric_name = 'median_employee_income' (verify)",
     "(verify metric_name)",
     "Median annual employee income",
     "remoteness"),
    ("sa2_median_total_income_excl_govt",
     "abs_sa2_socioeconomic_annual",
     "value where metric_name = 'median_total_income_excl_govt' (verify)",
     "(verify metric_name)",
     "Median total income excl. govt pensions",
     "remoteness"),
    ("sa2_lfp_persons",
     "abs_sa2_education_employment_annual",
     "value where metric_name = 'ee_lfp_persons_pct' (verify)",
     "(verify metric_name; canonical per Decision 61)",
     "Labour force participation, persons",
     "state_x_remoteness"),
    ("sa2_lfp_females",
     "abs_sa2_education_employment_annual or census-derived",
     "value where metric_name = 'census_lfp_females_pct' (verify)",
     "(verify metric_name; T33-derived per Decision 61)",
     "LFP, females (sex-disaggregated, Census-derived)",
     "state_x_remoteness"),
    ("sa2_lfp_males",
     "abs_sa2_education_employment_annual or census-derived",
     "value where metric_name = 'census_lfp_males_pct' (verify)",
     "(verify metric_name; T33-derived per Decision 61)",
     "LFP, males (sex-disaggregated, Census-derived)",
     "state_x_remoteness"),
    ("seifa_decile_sa2",
     "(SA2-level lookup; derived or external)",
     "seifa_decile aggregated to SA2 mode",
     "(decision needed: derive from services or import ABS SEIFA)",
     "SEIFA IRSD decile at SA2 level (national cohort, raw passthrough)",
     "national"),
]


# --------------------------------------------------------------------
# Section 5 — Expected row counts
# --------------------------------------------------------------------

def estimate_row_counts(metric_findings):
    """
    Rough cardinality envelope for layer3_sa2_metric_banding.
    """
    n_sa2 = 2450  # approximate, per status doc
    metrics_count = len(PROPOSED_METRICS)
    yrs_min = 1   # static metrics like SEIFA: 1 year
    yrs_avg = 5   # midpoint of "latest only" vs full 14-year history
    yrs_max = 14  # full history for births / ERP

    return {
        "n_sa2_estimate": n_sa2,
        "metrics_count": metrics_count,
        "low_estimate": n_sa2 * metrics_count * yrs_min,
        "mid_estimate": n_sa2 * metrics_count * yrs_avg,
        "high_estimate": n_sa2 * metrics_count * yrs_max,
    }


# --------------------------------------------------------------------
# Markdown emit
# --------------------------------------------------------------------

def emit_markdown(coh, metrics, cutoffs, row_est):
    print(f"[4/5] Writing {OUTPUT_PATH}...", flush=True)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out = []
    w = out.append

    w("# Layer 3 Diagnostic")
    w("")
    w(f"_Generated: {datetime.now().isoformat(timespec='seconds')}_")
    w("")
    w("Read-only design probe ahead of `layer3_apply.py`. References:")
    w("- `recon/layer3_decisions.md` (D1-D4 closed)")
    w("- `recon/layer3_precedent_survey.md` (raw evidence)")
    w("- `recon/db_inventory.md` (Standard 28 snapshot)")
    w("")
    w("**Goal of this artefact:** answer the open design questions so the apply")
    w("script can be written cleanly, with no ambiguity about data sources,")
    w("metric definitions, cohort logic, or banding cutoffs.")
    w("")
    w("---")
    w("")

    # --- Section 1 ---
    w("## 1. SA2 cohort lookup source")
    w("")
    w("Layer 3 banding requires a per-SA2 cohort assignment: `(state, "
      "remoteness)`. State is trivially derivable from the first digit of "
      "`sa2_code` (ABS convention). Remoteness is the open question.")
    w("")

    w("### 1.1 State-from-SA2-prefix validation")
    w("")
    w("First digit of `services.sa2_code` (ABS convention: "
      "1=NSW 2=VIC 3=QLD 4=SA 5=WA 6=TAS 7=NT 8=ACT 9=OT):")
    w("")
    rows = coh.get("state_prefix_dist") or []
    if rows:
        w("| Prefix | Implied state | Service rows |")
        w("|:-:|---|---:|")
        for prefix, n in rows:
            state = STATE_PREFIX_MAP.get(prefix, "?")
            w(f"| {prefix} | {state} | {fmt_int(n)} |")
    else:
        err = coh.get("state_prefix_dist_err", "_no rows_")
        w(f"_Query failed or empty: {err}_")
    w("")

    w("### 1.2 Distinct SA2 counts across candidate cohort sources")
    w("")
    w("| Source | Distinct SA2s |")
    w("|---|---:|")
    w(f"| `services` (centres with assigned SA2) "
      f"| {fmt_int(coh.get('distinct_sa2_services'))} |")
    w(f"| `abs_sa2_erp_annual` "
      f"| {fmt_int(coh.get('distinct_sa2_erp'))} |")
    w(f"| `abs_sa2_births_annual` "
      f"| {fmt_int(coh.get('distinct_sa2_births'))} |")
    w("")
    no_svc = coh.get("sa2s_no_services")
    if no_svc is not None:
        w(f"_SA2s present in `abs_sa2_erp_annual` but with NO matching "
          f"services row: **{fmt_int(no_svc)}**_  ")
        w("These SA2s would NOT receive remoteness assignment if we use a "
          "services-derived approach — important constraint to consider.")
    w("")

    w("### 1.3 Services-derived remoteness distribution")
    w("")
    w("If we derive SA2 remoteness as the most-common `services.aria_plus` "
      "within each SA2:")
    w("")
    rows = coh.get("services_derived_remoteness_dist") or []
    if rows:
        w("| ARIA+ category | SA2 count |")
        w("|---|---:|")
        for arpia, n in rows:
            w(f"| {md_pipe_safe(arpia)} | {fmt_int(n)} |")
    else:
        err = coh.get("services_derived_remoteness_err", "_no rows_")
        w(f"_Query failed or empty: {err}_")
    w("")

    w("### 1.4 ABS GeoPackage probe")
    w("")
    w(f"GeoPackage: `{coh.get('gpkg_path')}` "
      f"(exists={coh.get('gpkg_exists')})")
    w("")
    if coh.get("gpkg_layers"):
        w("**Layers in GeoPackage:**")
        w("")
        for lyr in coh["gpkg_layers"]:
            marker = " <-- SA2 layer" if lyr == coh.get("gpkg_sa2_layer") else ""
            w(f"- `{lyr}`{marker}")
        w("")
    if coh.get("gpkg_sa2_schema"):
        w(f"**SA2 layer fields** ({coh.get('gpkg_sa2_feature_count')} "
          f"features):")
        w("")
        w("| Field | Type |")
        w("|---|---|")
        for k, v in coh["gpkg_sa2_schema"].items():
            w(f"| `{k}` | {v} |")
        w("")
        # Highlight: any remoteness-related fields?
        rem_keys = [k for k in coh["gpkg_sa2_schema"]
                    if "REMOTE" in k.upper() or "ARIA" in k.upper()
                    or k.upper().startswith("RA_")]
        if rem_keys:
            w(f"_Remoteness-related fields present: {rem_keys}_")
        else:
            w("_NO remoteness-related fields in this GeoPackage's SA2 layer. "
              "Remoteness Areas are typically a separate ABS GeoPackage "
              "(not currently in `abs_data/`)._")
        w("")
    if coh.get("gpkg_err"):
        w(f"**GeoPackage probe error:** {coh['gpkg_err']}")
        w("")
    if coh.get("gpkg_sa2_sample_props"):
        w("**Sample SA2 feature properties:**")
        w("")
        w("```")
        for k, v in coh["gpkg_sa2_sample_props"].items():
            w(f"  {k}: {v}")
        w("```")
        w("")

    w("### 1.5 RECOMMENDATION (for Patrick to confirm)")
    w("")
    w("**State:** derive from `SUBSTR(sa2_code, 1, 1)` per the ABS "
      "convention. No table needed.")
    w("")
    w("**Remoteness:** see Section 1.4 above. If the GeoPackage contains "
      "remoteness fields, use those (cleanest). If NOT, two paths:")
    w("")
    w("  - **Path A (preferred if data available):** download the ABS "
      "Remoteness Areas GeoPackage (separate file, ~free from ABS) and "
      "build a one-off `sa2_cohort` lookup table via SA1 -> RA join. "
      "Cleanest but adds a small data-sourcing step.")
    w("")
    w("  - **Path B (pragmatic fallback):** derive SA2 remoteness as the "
      "most-common `services.aria_plus` within each SA2 (Section 1.3 "
      "shows this works for SA2s with services). For SA2s with NO "
      "services (Section 1.2 count above), backfill by nearest-SA2 in "
      "the same state, OR mark as `null` cohort and exclude from banding.")
    w("")
    w("Either way, write a `sa2_cohort` table with columns: "
      "`(sa2_code, state_code, state_name, remoteness, "
      "remoteness_band INTEGER 1..5)` and store as a Layer-3-prep step.")
    w("")
    w("---")
    w("")

    # --- Section 2 ---
    w("## 2. Source-metric inventory")
    w("")

    w("### 2.1 `abs_sa2_erp_annual` — age groups present")
    w("")
    rows = metrics.get("erp_age_groups") or []
    if rows:
        w("| age_group | Rows | Distinct SA2 | Year range | NULL persons |")
        w("|---|---:|---:|---|---:|")
        for ag, n, n_sa2, ymin, ymax, nn in rows:
            w(f"| `{md_pipe_safe(ag)}` | {fmt_int(n)} | {fmt_int(n_sa2)} | "
              f"{ymin}-{ymax} | {fmt_int(nn)} |")
    else:
        w(f"_Query failed: {metrics.get('erp_age_groups_err','')}_")
    w("")

    w("### 2.2 `abs_sa2_socioeconomic_annual` — distinct metrics")
    w("")
    rows = metrics.get("socioeconomic_metrics") or []
    if rows:
        w("| metric_name | Rows | Distinct SA2 | Years | NULLs | Avg value |")
        w("|---|---:|---:|---|---:|---:|")
        for m, n, n_sa2, ymin, ymax, nn, avgv in rows:
            avg_str = f"{avgv:,.2f}" if avgv is not None else "n/a"
            w(f"| `{md_pipe_safe(m)}` | {fmt_int(n)} | {fmt_int(n_sa2)} | "
              f"{ymin}-{ymax} | {fmt_int(nn)} | {avg_str} |")
    else:
        w(f"_Query failed: {metrics.get('socioeconomic_metrics_err','')}_")
    w("")

    w("### 2.3 `abs_sa2_education_employment_annual` — distinct metrics")
    w("")
    rows = metrics.get("ee_metrics") or []
    if rows:
        w("| metric_name | Rows | Distinct SA2 | Years | NULLs | Avg value |")
        w("|---|---:|---:|---|---:|---:|")
        for m, n, n_sa2, ymin, ymax, nn, avgv in rows:
            avg_str = f"{avgv:,.2f}" if avgv is not None else "n/a"
            w(f"| `{md_pipe_safe(m)}` | {fmt_int(n)} | {fmt_int(n_sa2)} | "
              f"{ymin}-{ymax} | {fmt_int(nn)} | {avg_str} |")
    else:
        w(f"_Query failed: {metrics.get('ee_metrics_err','')}_")
    w("")

    w("### 2.4 `abs_sa2_births_annual` — yearly profile")
    w("")
    rows = metrics.get("births_yearly") or []
    if rows:
        w("| year | Rows | Distinct SA2 | NULLs | National total |")
        w("|---:|---:|---:|---:|---:|")
        for yr, n, n_sa2, nn, total in rows:
            w(f"| {yr} | {fmt_int(n)} | {fmt_int(n_sa2)} | {fmt_int(nn)} | "
              f"{fmt_int(total)} |")
    else:
        w(f"_Query failed: {metrics.get('births_yearly_err','')}_")
    w("")

    w("### 2.5 `abs_sa2_unemployment_quarterly` — recent quarters")
    w("")
    rows = metrics.get("salm_recent") or []
    if rows:
        w("| year_qtr | Rows | Distinct SA2 | NULL rate | Avg rate (%) |")
        w("|---|---:|---:|---:|---:|")
        for yq, n, n_sa2, nr, avgr in rows:
            avg_str = f"{avgr:.2f}" if avgr is not None else "n/a"
            w(f"| `{md_pipe_safe(yq)}` | {fmt_int(n)} | {fmt_int(n_sa2)} | "
              f"{fmt_int(nr)} | {avg_str} |")
    else:
        w(f"_Query failed: {metrics.get('salm_recent_err','')}_")
    w("")

    w("### 2.6 `jsa_ivi_state_monthly` — recent months")
    w("")
    rows = metrics.get("jsa_state_recent") or []
    if rows:
        w("| year_month | Rows |")
        w("|---|---:|")
        for ym, n in rows:
            w(f"| `{md_pipe_safe(ym)}` | {fmt_int(n)} |")
    else:
        w(f"_Query failed: {metrics.get('jsa_state_recent_err','')}_")
    w("")

    w("---")
    w("")

    # --- Section 3 ---
    w("## 3. Banding cutoff conventions in shipped UI")
    w("")
    w("Searching shipped UI files for `low/mid/high decile` cutoffs to "
      "ensure Layer 3 band thresholds match the existing convention "
      "(Decision 65 / Visual Consistency Principle).")
    w("")
    if cutoffs:
        w(f"_{len(cutoffs)} candidate hit(s) found across UI files:_")
        w("")
        w("| File | Line | Snippet |")
        w("|---|---:|---|")
        for h in cutoffs:
            w(f"| `{h['file']}` | {h['line']} | "
              f"`{md_pipe_safe(h['snippet'])}` |")
    else:
        w("_No literal numerical cutoffs detected via regex. The shipped "
          "low/mid/high split may use computed thresholds (e.g. weighted "
          "mean) rather than fixed decile boundaries. Manual code review "
          "of `docs/_op_chunks/part3.txt` around the `weighted_decile` "
          "computation is recommended to confirm the convention before "
          "Layer 3 codifies bands._")
    w("")

    w("**RECOMMENDATION (subject to confirmation by code review):**  ")
    w("Use the conventional decile-based split:  ")
    w("  - `low`  = decile 1-3  ")
    w("  - `mid`  = decile 4-7  ")
    w("  - `high` = decile 8-10  ")
    w("")
    w("This matches typical ABS / Remara-style 30/40/30 partitioning. If "
      "the shipped UI uses different cutoffs, Layer 3 should match those "
      "exactly per Decision 65. Decision needed before apply.")
    w("")
    w("---")
    w("")

    # --- Section 4 ---
    w("## 4. Initial metric set proposal")
    w("")
    w("Based on the Layer 4 design block in the project status doc and "
      "the cohort overrides documented in `recon/layer3_decisions.md` D3:")
    w("")
    w("| Metric (canonical name) | Source | Column / formula | Filter "
      "/ note | Default cohort |")
    w("|---|---|---|---|---|")
    for m in PROPOSED_METRICS:
        w(f"| `{m[0]}` | `{md_pipe_safe(m[1])}` | "
          f"{md_pipe_safe(m[2])} | {md_pipe_safe(m[3])} | "
          f"{md_pipe_safe(m[5])} |")
    w("")
    w("_Several `metric_name` strings above are placeholders — the "
      "diagnostic Section 2.2 / 2.3 above lists the actual values "
      "present in `abs_sa2_socioeconomic_annual` and "
      "`abs_sa2_education_employment_annual`. Apply script must use the "
      "exact strings from those tables; this proposal must be "
      "reconciled against Section 2 before code is written._")
    w("")
    w("---")
    w("")

    # --- Section 5 ---
    w("## 5. Expected row counts for `layer3_sa2_metric_banding`")
    w("")
    w(f"- Distinct SA2s (estimate): **{fmt_int(row_est['n_sa2_estimate'])}**")
    w(f"- Proposed metric count: **{fmt_int(row_est['metrics_count'])}**")
    w(f"- Year coverage: 1 year (latest-only metrics) to ~14 years (births / "
      "ERP)")
    w("")
    w("Cardinality envelope:")
    w(f"- Lower bound (latest-year only across all metrics): "
      f"~{fmt_int(row_est['low_estimate'])}")
    w(f"- Mid estimate (5-year average history): "
      f"~{fmt_int(row_est['mid_estimate'])}")
    w(f"- Upper bound (full 14-year history all metrics): "
      f"~{fmt_int(row_est['high_estimate'])}")
    w("")
    w("Per-cohort dimension multiplies these by 1-3 (default cohort + any "
      "per-metric overrides).")
    w("")
    w("---")
    w("")

    # --- Open decisions ---
    w("## 6. Open decisions before apply")
    w("")
    w("**O1.** Remoteness assignment path: **A** (download ABS Remoteness "
      "Areas GeoPackage, separate one-off ingest) or **B** "
      "(services-derived most-common ARIA+ per SA2, with backfill rule "
      "for SA2s lacking services)?")
    w("")
    w("**O2.** Banding cutoffs: confirm low/mid/high split. Default "
      "proposal `1-3 / 4-7 / 8-10` — confirm matches shipped UI.")
    w("")
    w("**O3.** Metric set: review Section 4 against Section 2 actuals; "
      "reconcile placeholder `metric_name` strings.")
    w("")
    w("**O4.** Year coverage scope per metric: latest-year-only, "
      "full-history, or per-metric configurable?")
    w("")
    w("**O5.** SEIFA: include in `layer3_sa2_metric_banding` as a "
      "national-cohort passthrough, OR leave as raw `services.seifa_decile` "
      "and not duplicate?")
    w("")
    w("---")
    w("")
    w("_End of diag._")

    OUTPUT_PATH.write_text("\n".join(out), encoding="utf-8")
    size = OUTPUT_PATH.stat().st_size
    print(f"  wrote {OUTPUT_PATH} ({size:,} bytes)", flush=True)


# --------------------------------------------------------------------
# Main
# --------------------------------------------------------------------

def main():
    print("Layer 3 Diagnostic - read-only")
    print(f"Repo: {REPO_ROOT}")
    print(f"DB:   {DB_PATH}")
    print(f"Out:  {OUTPUT_PATH}")
    print()

    if not DB_PATH.exists():
        print(f"ERROR: DB not found at {DB_PATH}")
        return 1

    uri = f"file:{DB_PATH.as_posix()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    cur = conn.cursor()

    coh = probe_sa2_cohort_source(cur)
    metrics = probe_source_metrics(cur)
    cutoffs = probe_banding_cutoffs()
    row_est = estimate_row_counts(metrics)

    conn.close()

    emit_markdown(coh, metrics, cutoffs, row_est)

    print("[5/5] Done.")
    print(f"Review: {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
