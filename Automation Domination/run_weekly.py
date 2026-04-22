"""
run_weekly.py — Automation Domination: Monday morning pipeline
Stark County Auditor — MLS vs CAMA Review Portal

Steps (run in order):
  1. CAMA extract     → Oracle → cama_YYYY-MM-DD.csv
  2. MLS export       → MLS Matrix → mls_YYYY-MM-DD.csv + .xlsx
  3. Compare          → 4 Excel files (mismatches, perfects, missing_cama, missing_mls)
  4. Zillow photos    → Photos_New/ + Photos_New_Portal/  (requires manual CAPTCHA)
  5. Build portal     → review_portal.html + archive/YYYY-WNN.json

Manual steps (not automated — done in iasWorld after this script):
  - Sale Tab Mass Update
  - MassEntrance
  - iasWorld photo upload (Document Loader CSV is generated in step 4)
"""

import sys
import subprocess
from datetime import date, timedelta
from pathlib import Path

# Force UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── Paths ──────────────────────────────────────────────────────────────────────
HERE         = Path(__file__).parent                            # Automation Domination/
PORTAL_ROOT  = HERE.parent                                      # Portal Builder/
MLSCAMA_ROOT = PORTAL_ROOT / "MLSvsCAMA"                        # MLSvsCAMA/
ZILLOW_SCRIPT = PORTAL_ROOT / "ZillowPhotos" / "download_zillow_photos.py"
BUILD_SCRIPT  = PORTAL_ROOT / "build_portal.py"

# ── Imports from this project ──────────────────────────────────────────────────
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(PORTAL_ROOT))

from cama_extract import extract_cama, get_week_dates
from mls_export   import export_mls
from compare      import run_comparison
import credentials

# build_portal functions imported directly (skip its interactive main())
import build_portal as bp
import datetime as _dt


# ── Date helpers ───────────────────────────────────────────────────────────────

def folder_name_from_date(d: date) -> str:
    """Format date as M-DD-YY for folder naming (matches existing convention)."""
    return f"{d.month}-{d.day:02d}-{str(d.year)[2:]}"


def date_str_from_date(d: date) -> str:
    """Format date as YYYY-MM-DD for file naming."""
    return d.strftime("%Y-%m-%d")


# ── Main pipeline ──────────────────────────────────────────────────────────────

def run(run_date: date = None, start_date=None, end_date=None):
    run_date = run_date or date.today()
    if start_date is None or end_date is None:
        start_date, end_date = get_week_dates(run_date)
    folder_name = folder_name_from_date(run_date)
    date_str    = date_str_from_date(run_date)

    print("=" * 70)
    print("  AUTOMATION DOMINATION — Weekly Pipeline")
    print("=" * 70)
    print(f"  Run date:        {run_date}  ({run_date.strftime('%A')})")
    print(f"  Sale date range: {start_date} to {end_date} (exclusive)")
    print(f"  Output folder:   MLSvsCAMA/{folder_name}/")
    print("=" * 70)

    # Create output folder
    week_folder = MLSCAMA_ROOT / folder_name
    week_folder.mkdir(parents=True, exist_ok=True)

    # ── Step 1: CAMA extract ───────────────────────────────────────────────────
    print(f"\n[1/5] CAMA Extract")
    cama_csv = week_folder / f"cama_{date_str}.csv"
    df_cama  = extract_cama(cama_csv, start_date=start_date, end_date=end_date)

    # ── Step 2: MLS export ────────────────────────────────────────────────────
    print(f"\n[2/5] MLS Export")
    mls_csv  = week_folder / f"mls_{date_str}.csv"
    mls_xlsx = week_folder / f"mls_{date_str}.xlsx"
    df_mls   = export_mls(mls_csv, mls_xlsx)

    # ── Step 3: Compare ────────────────────────────────────────────────────────
    print(f"\n[3/5] CAMA vs MLS Comparison")
    counts = run_comparison(df_mls, df_cama, week_folder, date_str)
    print(f"\n  Summary:")
    print(f"    Value mismatches:  {counts['mismatches']}")
    print(f"    Perfect matches:   {counts['perfects']}")
    print(f"    Missing in CAMA:   {counts['missing_cama']}")
    print(f"    Missing in MLS:    {counts['missing_mls']}")

    # ── Step 4: Zillow photos ──────────────────────────────────────────────────
    print(f"\n[4/5] Zillow Photos  (requires manual CAPTCHA solving)")
    photos_dir = week_folder / "Photos_New"

    mismatches_xlsx = week_folder / f"value_mismatches_{date_str}.xlsx"
    perfects_xlsx   = week_folder / f"perfect_matches_{date_str}.xlsx"

    # Run value_mismatches first (more photos needed), then perfect_matches
    for xlsx_file, label in [
        (mismatches_xlsx, "value_mismatches"),
        (perfects_xlsx,   "perfect_matches"),
    ]:
        if not xlsx_file.exists():
            print(f"  Skipping {label} — file not found")
            continue
        print(f"\n  Downloading photos for {label}...")
        result = subprocess.run(
            [sys.executable, str(ZILLOW_SCRIPT),
             str(xlsx_file), str(photos_dir)],
            cwd=str(PORTAL_ROOT),
        )
        if result.returncode != 0:
            print(f"  ⚠  Zillow downloader exited with code {result.returncode}")

    # ── Step 5: Build portal ───────────────────────────────────────────────────
    print(f"\n[5/5] Building Portal")

    portal_photos_dir = week_folder / "Photos_New_Portal"
    output_html       = PORTAL_ROOT / "review_portal.html"

    # Read Excel files
    mismatches_rows = bp.xlsx_to_json(mismatches_xlsx) if mismatches_xlsx.exists() else []
    perfects_rows   = bp.xlsx_to_json(perfects_xlsx)   if perfects_xlsx.exists()   else []

    # Load photos
    photo_map = bp.load_photos(portal_photos_dir) if portal_photos_dir.is_dir() else {}

    # Week label
    monday    = run_date - _dt.timedelta(days=run_date.weekday())
    week_label = f"Week of {monday.strftime('%B %d, %Y')}"
    week_key   = bp.get_iso_week_key(run_date)

    print(f"  Week label: {week_label}")

    # Build HTML
    html = bp.build_html(
        mismatches_rows, perfects_rows, photo_map, week_label,
        api_key="",  # Key stored in staff browsers via localStorage — never embedded in HTML
        github_pages_base=bp.GITHUB_PAGES_BASE,
        shared_api_url=bp.SHARED_API_URL,
    )

    output_html.write_text(html, encoding="utf-8")
    size_mb = output_html.stat().st_size / (1024 * 1024)
    print(f"  ✓ review_portal.html  ({size_mb:.1f} MB)")

    # Save archive
    archive_path = bp.save_archive(
        mismatches_rows, perfects_rows,
        week_key, week_label, PORTAL_ROOT,
    )
    print(f"  ✓ {archive_path.relative_to(PORTAL_ROOT)}")

    # ── Done ───────────────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  PIPELINE COMPLETE")
    print("=" * 70)
    print(f"\n  Weekly files:  MLSvsCAMA/{folder_name}/")
    print(f"  Portal:        review_portal.html")
    print(f"  Archive:       archive/{week_key}.json")
    print()
    print("  Upload to GitHub:")
    print("    1. review_portal.html")
    print(f"    2. archive/{week_key}.json")
    print()
    print("  Manual steps remaining in iasWorld:")
    print("    - Sale Tab Mass Update")
    print("    - MassEntrance")
    print(f"    - Photo upload via Document Loader CSV in Photos_New/")
    print()
    try:
        input("Press Enter to close...")
    except EOFError:
        pass


if __name__ == "__main__":
    run()
