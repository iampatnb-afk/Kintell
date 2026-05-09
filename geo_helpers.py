r"""
geo_helpers.py — reusable geographic helpers for SA2 spatial-join work.

Built 2026-05-10 as part of A4 (Schools at SA2). Generalises the
point-in-polygon pattern from `layer2_step1b_apply.py` so future
point-feature ingests can reuse it without re-implementing the
geopandas + sjoin + CRS-reprojection plumbing each time.

Currently used by:
  - layer4_4_step_a4_schools_apply.py (ACARA School Location → SA2)

V2 banked callers:
  - OI-NEW-19 (OSHC-school adjacency derived flag — uses
    `nearest_point_within(threshold_m, ...)` extension once needed)
  - PropCo property location → SA2 (Stream D)
  - Hospital catchment / GP clinic → SA2
  - Transport station → SA2

Module-level cache of the SA2 GeoDataFrame avoids re-reading the GPKG
(30-60s parse) within a single Python process. Multiple ingest scripts
in one session share the cache.

Standards:
  - Lazy import of geopandas / shapely / pandas — only paid when
    a geographic helper is actually called.
  - EPSG:4326 (lat/lon WGS84) for input points, reprojected to the
    GPKG's native CRS (EPSG:7844 for GDA2020 ASGS Ed.3) before sjoin.
  - sjoin predicate "within"; drop_duplicates(subset=key, keep="first")
    in case a point sits on a polygon boundary.
  - Returns hit/miss diagnostics so callers can log coverage and
    halt on low hit-rate (per layer2_step1b precedent: ≥0.99 threshold).

Usage
-----
    # Bulk: pandas DataFrame in, augmented DataFrame out
    from geo_helpers import points_to_sa2

    df = pd.DataFrame({"id": [...], "lat": [...], "lng": [...]})
    joined, hit_rate = points_to_sa2(
        df, lat_col="lat", lng_col="lng", id_col="id",
    )
    # joined now has SA2_CODE_2021, SA2_NAME_2021, STATE_NAME_2021 columns
    # (None where no match — typically offshore points)

    # Single-point convenience (for one-off lookups, e.g. OSHC-school adjacency probes)
    from geo_helpers import point_to_sa2
    sa2 = point_to_sa2(-37.85, 144.99)
    # → "211011251" or None
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

# Default SA2 polygon source — ABS ASGS 2021 Edition 3 GDA2020 GPKG, on disk.
DEFAULT_SA2_GPKG = Path("abs_data") / "ASGS_2021_Main_Structure_GDA2020.gpkg"
DEFAULT_SA2_LAYER = "SA2_2021_AUST_GDA2020"

# Attribute names in the GPKG layer (locked by ABS ASGS 2021 schema).
SA2_CODE_ATTR = "SA2_CODE_2021"
SA2_NAME_ATTR = "SA2_NAME_2021"
SA2_STATE_ATTR = "STATE_NAME_2021"

# Module-level cache. Multiple ingest scripts in the same Python process
# share one parse of the GPKG (30-60s saved on each subsequent call).
_SA2_GDF_CACHE: dict = {}


def _import_geo():
    """Lazy import of geopandas / pandas / shapely. Returns (gpd, pd, Point).

    Lifted directly from `layer2_step1b_apply.py:import_geo`. Mirrors the
    same install hint so the failure mode is identical across callers.
    """
    try:
        import geopandas as gpd
        import pandas as pd
        from shapely.geometry import Point
        return gpd, pd, Point
    except ImportError as e:
        raise ImportError(
            f"geo_helpers requires geopandas/shapely/pyogrio: {e}. "
            f"Install: pip install --break-system-packages "
            f"geopandas shapely pyogrio rtree"
        ) from e


def load_sa2_polygons(
    gpkg_path: Path = DEFAULT_SA2_GPKG,
    layer: str = DEFAULT_SA2_LAYER,
    use_cache: bool = True,
):
    """Load SA2 polygon GeoDataFrame from the ASGS GPKG.

    Returns a 4-column GeoDataFrame: SA2_CODE_2021, SA2_NAME_2021,
    STATE_NAME_2021, geometry.

    Module-level cache keyed on (gpkg_path, layer) avoids re-parsing the
    file for repeat callers within one process.
    """
    gpkg_path = Path(gpkg_path)
    cache_key = (str(gpkg_path), layer)
    if use_cache and cache_key in _SA2_GDF_CACHE:
        return _SA2_GDF_CACHE[cache_key]

    if not gpkg_path.exists():
        raise FileNotFoundError(f"SA2 GPKG not found: {gpkg_path}")

    gpd, _pd, _Point = _import_geo()
    sa2_full = gpd.read_file(gpkg_path, layer=layer, engine="pyogrio")
    needed = [SA2_CODE_ATTR, SA2_NAME_ATTR, SA2_STATE_ATTR, "geometry"]
    missing = [c for c in needed if c not in sa2_full.columns]
    if missing:
        raise KeyError(
            f"GPKG layer '{layer}' missing expected attrs: {missing}. "
            f"Available: {list(sa2_full.columns)}"
        )
    sa2_gdf = sa2_full[needed].copy()
    if use_cache:
        _SA2_GDF_CACHE[cache_key] = sa2_gdf
    return sa2_gdf


def points_to_sa2(
    df,
    lat_col: str = "lat",
    lng_col: str = "lng",
    id_col: Optional[str] = None,
    gpkg_path: Path = DEFAULT_SA2_GPKG,
    layer: str = DEFAULT_SA2_LAYER,
    point_crs: str = "EPSG:4326",
):
    """Spatial-join a DataFrame of (lat, lng) points to SA2 polygons.

    Parameters
    ----------
    df : pandas.DataFrame
        Must contain `lat_col` and `lng_col`.
    lat_col, lng_col : str
        Column names for latitude and longitude (decimal degrees).
    id_col : str, optional
        If provided, used as the dedupe key when a point sits on a
        polygon boundary (first match wins). If None, the DataFrame's
        existing index is used.
    gpkg_path, layer : Path, str
        Override the SA2 source. Defaults to ASGS 2021 Edition 3 GDA2020.
    point_crs : str
        CRS of the input lat/lng. Defaults to EPSG:4326 (WGS84 — what
        ACARA, NQAITS, etc. all publish). Reprojected to the GPKG's
        native CRS before sjoin.

    Returns
    -------
    (joined_df, hit_rate)
        joined_df : pandas.DataFrame with original columns plus
                    SA2_CODE_2021, SA2_NAME_2021, STATE_NAME_2021.
                    Unmatched rows have None in the SA2 columns.
        hit_rate  : float in [0.0, 1.0] — share of input rows with a
                    matched SA2.

    Notes
    -----
    - Drops rows where lat or lng is null BEFORE the join, with a
      printed warning. Returned df is filtered to non-null inputs.
    - Boundary-case duplicates handled via drop_duplicates (first match
      wins on `id_col` if provided, else DataFrame index).
    """
    gpd, pd, Point = _import_geo()

    if lat_col not in df.columns or lng_col not in df.columns:
        raise KeyError(
            f"DataFrame missing lat/lng columns. "
            f"Have: {list(df.columns)}; need: {lat_col}, {lng_col}"
        )

    n_in = len(df)
    df_clean = df.dropna(subset=[lat_col, lng_col]).copy()
    n_clean = len(df_clean)
    if n_clean < n_in:
        print(f"  [geo] dropped {n_in - n_clean:,} rows with null lat/lng "
              f"(geo-unrecoverable; ingest will silently absent them per P-2)")

    if n_clean == 0:
        return df_clean.copy(), 0.0

    # Coerce to float in case CSV reader gave strings
    df_clean[lat_col] = pd.to_numeric(df_clean[lat_col], errors="coerce")
    df_clean[lng_col] = pd.to_numeric(df_clean[lng_col], errors="coerce")
    df_clean = df_clean.dropna(subset=[lat_col, lng_col])

    sa2_gdf = load_sa2_polygons(gpkg_path, layer)
    points_gdf = gpd.GeoDataFrame(
        df_clean,
        geometry=[Point(lon, lat)
                  for lon, lat in zip(df_clean[lng_col], df_clean[lat_col])],
        crs=point_crs,
    )
    points_proj = points_gdf.to_crs(sa2_gdf.crs)

    joined = gpd.sjoin(points_proj, sa2_gdf, how="left", predicate="within")

    # Boundary-case dedupe — a point on a polygon edge can match >1 polygon.
    # First match wins, matching layer2_step1b's convention.
    dedupe_subset = id_col if (id_col and id_col in joined.columns) else None
    if dedupe_subset:
        joined = joined.drop_duplicates(subset=dedupe_subset, keep="first")
    else:
        # Use the source DataFrame index as fallback
        joined = joined[~joined.index.duplicated(keep="first")]

    has_match = joined[SA2_CODE_ATTR].notna()
    hit_rate = float(has_match.sum()) / float(len(joined)) if len(joined) else 0.0

    # Drop the geopandas index_right artifact for clean caller experience
    if "index_right" in joined.columns:
        joined = joined.drop(columns=["index_right"])
    # Drop geometry to keep the return a plain pandas DataFrame
    if hasattr(joined, "drop") and "geometry" in joined.columns:
        joined = joined.drop(columns=["geometry"])

    print(f"  [geo] sjoin: {int(has_match.sum()):,}/{len(joined):,} matched "
          f"({hit_rate:.2%}); {int((~has_match).sum()):,} offshore/no-match")

    # Return a plain DataFrame (not GeoDataFrame) — callers don't need geometry
    if hasattr(joined, "to_frame"):
        joined = pd.DataFrame(joined)
    return joined, hit_rate


def point_to_sa2(
    lat: float,
    lng: float,
    gpkg_path: Path = DEFAULT_SA2_GPKG,
    layer: str = DEFAULT_SA2_LAYER,
) -> Optional[Tuple[str, str, str]]:
    """Return (sa2_code, sa2_name, state_name) for a single point, or None.

    Convenience wrapper for one-off lookups (e.g. interactive probes,
    OI-NEW-19 OSHC-school adjacency derivation that may run per-service).

    For bulk joins use `points_to_sa2()` — that vectorises and is
    orders of magnitude faster.
    """
    if lat is None or lng is None:
        return None
    _gpd, pd, _Point = _import_geo()
    df = pd.DataFrame({"_lat": [lat], "_lng": [lng]})
    joined, _hit = points_to_sa2(df, lat_col="_lat", lng_col="_lng")
    if joined.empty:
        return None
    row = joined.iloc[0]
    code = row.get(SA2_CODE_ATTR)
    if code is None or (hasattr(code, "__class__") and str(code) == "nan"):
        return None
    return (str(code), str(row.get(SA2_NAME_ATTR, "")),
            str(row.get(SA2_STATE_ATTR, "")))


def clear_cache():
    """Drop the module-level SA2 GeoDataFrame cache. Useful for tests
    or long-running processes wanting to force a re-read."""
    _SA2_GDF_CACHE.clear()


# ============================================================================
# Self-check / smoke test
# ============================================================================
if __name__ == "__main__":
    """Quick smoke test against four known SA2s."""
    import pandas as pd

    print(f"GPKG: {DEFAULT_SA2_GPKG}")
    print(f"Layer: {DEFAULT_SA2_LAYER}")
    print()

    # Known reference points (centre lat/lng of the SA2 — approximate).
    # These match the four verifying SA2s used across the V1.5 build.
    test_points = pd.DataFrame([
        {"label": "Bayswater Vic",          "lat": -37.846, "lng": 145.265, "expected_sa2": "211011251"},
        {"label": "Bondi Junction NSW",     "lat": -33.892, "lng": 151.255, "expected_sa2": "118011341"},
        {"label": "Bentley-Wilson WA",      "lat": -32.005, "lng": 115.917, "expected_sa2": "506031124"},
        {"label": "Outback NT",             "lat": -19.10,  "lng": 134.20,  "expected_sa2": "702041063"},
    ])

    print("Bulk join test:")
    joined, hit = points_to_sa2(test_points, lat_col="lat", lng_col="lng",
                                id_col="label")
    print(f"  hit_rate: {hit:.2%}")
    for _, row in joined.iterrows():
        actual = row.get(SA2_CODE_ATTR) or "NO MATCH"
        expected = row["expected_sa2"]
        marker = "OK  " if str(actual) == expected else "MISS"
        print(f"  {marker}  {row['label']:24s}  expected={expected}  actual={actual}")

    print()
    print("Single-point test (Bayswater Vic):")
    single = point_to_sa2(-37.846, 145.265)
    print(f"  result: {single}")
