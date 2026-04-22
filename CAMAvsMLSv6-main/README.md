# Streamlit App V6 — MLS vs CAMA Data Comparison Tool

A Streamlit web application for the Stark County Auditor's Office, Property Assessment Division. Automates the weekly comparison of MLS (Multiple Listing Service) sales data against CAMA (Computer Assisted Mass Appraisal) records to identify discrepancies and ensure accurate residential property assessments.

---

## What It Does

Compares residential property sales data (land use codes 510 and 550) across six field comparisons:

| MLS Field | CAMA Field | Type |
|---|---|---|
| Above Grade Finished Area | SFLA | Direct numeric |
| Bedrooms Total | RMBED | Direct numeric |
| Bathrooms Full | FIXBATH | Direct numeric |
| Bathrooms Half | FIXHALF | Direct numeric |
| Below Grade Finished Area | RECROMAREA + FINBSMTAREA + UFEATAREA | Sum comparison |
| Cooling (Central Air?) | HEAT | Categorical |

---

## Features

- **Auto blank-fill** — MLS blank cells are automatically filled with 0 on upload (no manual CTRL+H)
- **Four result categories** — Missing in CAMA, Missing in MLS, Value Mismatches, Perfect Matches
- **MLS Search Batches** — Missing in MLS parcels exported as comma-separated batches of 35, zero-padded to 8 digits, ready to paste directly into MLS parcel search
- **CAMA Mass Update files** — Generates `SALETAB_MassUpdate_MMDDYY.xlsx` and `MassEntranceMMDDYY.csv` for iasWorld bulk import
- **ADDITIONAL_PARCELS expansion** — Multi-parcel sales automatically expanded so each parcel gets its own SALETAB row with the correct SALEKEY
- **Hyperlinked Excel reports** — Parcel_ID links to iasWorld, Address links to Zillow
- **City-level match statistics** — Match rate breakdown by city with bar charts
- **ZIP download** — All reports downloadable in one click
- **Context columns** — Value mismatches and perfect matches include YRBLT, EFFYR, GRADE, CDU (from CAMA) and Public Remarks (from MLS) for staff review

---

## File Structure

```
streamlit-app-v6/
├── streamlit_app.py      # Main application
├── requirements.txt      # Python dependencies
├── runtime.txt           # Python version for Streamlit Cloud
└── README.md             # This file
```

---

## Requirements

- Python 3.12
- See `requirements.txt` for packages

---

## Local Development

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/streamlit-app-v6.git
cd streamlit-app-v6

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_app.py
```

---

## Deployment (Streamlit Cloud)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app**
4. Select this repo, branch `main`, file `streamlit_app.py`
5. Click **Deploy**

Streamlit Cloud will use `runtime.txt` to pin Python 3.12 and install from `requirements.txt` automatically.

---

## Required Input Files

### MLS Data (`.xlsx`)
Export from MLS portal, open CSV in Excel, save as `.xlsx`. No other preparation needed — blank cells are auto-filled on upload.

| Column | Notes |
|---|---|
| `Parcel Number` | Match key |
| `Above Grade Finished Area` | |
| `Bedrooms Total` | |
| `Bathrooms Full` | |
| `Bathrooms Half` | |
| `Below Grade Finished Area` | |
| `Cooling` | Text field, checked for "Central Air" |
| `Address`, `City`, `State or Province`, `Postal Code` | Used for Zillow links |
| `Listing #` | Written to USER11 in SALETAB mass update |
| `Public Remarks` | Included in mismatch/match output for staff review |

### CAMA Data (`.xlsx`)
Export from Oracle SQL Developer using the production query.

| Column | Notes |
|---|---|
| `PARID` | Match key |
| `SALEKEY` | Comma-separated for multi-parcel sales |
| `NOPAR` | Number of parcels in sale |
| `ADDITIONAL_PARCELS` | Comma-separated additional parcel IDs |
| `CITYNAME` | Used for city-level statistics |
| `SFLA`, `RMBED`, `FIXBATH`, `FIXHALF` | Compared directly against MLS |
| `RECROMAREA`, `FINBSMTAREA`, `UFEATAREA` | Summed and compared against Below Grade Finished Area |
| `HEAT` | Compared categorically against MLS Cooling field |
| `YRBLT`, `EFFYR`, `GRADE`, `CDU` | Included in output for staff review |

---

## Output Files

| File | Format | Purpose |
|---|---|---|
| `SALETAB_MassUpdate_MMDDYY.xlsx` | Excel | Mass update SALETAB in iasWorld (PARID, SALEKEY, USER11, SOURCE, SALEVAL, USER1, USER2) |
| `MassEntranceMMDDYY.csv` | CSV | Mass update ENTRANCE tab via SCENTERADDS job |
| `missing_in_CAMA_YYYY-MM-DD.xlsx` | Excel | MLS sales with no matching CAMA parcel |
| `missing_in_MLS_YYYY-MM-DD.xlsx` | Excel | CAMA parcels with no matching MLS listing |
| `value_mismatches_YYYY-MM-DD.xlsx` | Excel | Parcels where at least one field disagrees |
| `perfect_matches_YYYY-MM-DD.xlsx` | Excel | Parcels where all fields agree |
| `city_match_statistics_YYYY-MM-DD.csv` | CSV | Match rate by city |
| `MLS_Search_Batches_MMDDYY.xlsx` | Excel | Missing parcels in comma-separated batches of 35 |

---

## Configuration

Key settings are defined at the top of `streamlit_app.py`:

```python
NUMERIC_TOLERANCE = 0.01      # Tolerance for numeric comparisons
SKIP_ZERO_VALUES = True       # Skip comparisons where both values are 0
```

The WindowId for iasWorld parcel hyperlinks is entered in the app sidebar at runtime — it does not need to be hardcoded.

---

## Version History

| Version | Notes |
|---|---|
| V6 | Added YRBLT, EFFYR, GRADE, CDU, Public Remarks to mismatch/match exports. MLS Search Batches output as comma-separated for direct MLS paste. Tab display bug fixed. |
| V5 | Added MLS Search Batches export (zero-padded, batches of 35). Auto blank-fill on MLS upload (replaces manual CTRL+H). |
| V4 | Session state persistence for comparison results. Mass update file generation with ADDITIONAL_PARCELS expansion. |
| V3 | City-level match rate statistics and charts. ZIP download for all reports. |
| V2 | ADDITIONAL_PARCELS multi-parcel sale support. SKIP_ZERO_VALUES bug fix (zeros are meaningful data). |
| V1 | Initial release. Direct, sum, and categorical field comparisons. Excel reports with iasWorld and Zillow hyperlinks. |

---

*Stark County Auditor's Office — Property Assessment Division*
