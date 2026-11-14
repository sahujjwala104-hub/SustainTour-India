"""
constants.py
============
Constants, file paths, state name bridges, and application metadata
for SustainTour India.
"""

from pathlib import Path

# Base Paths
SRC_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SRC_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXTRACTED_DATA_DIR = DATA_DIR / "extracted_2026_compendium"
GEO_DATA_DIR = DATA_DIR / "geo"
REPORTS_DIR = PROJECT_ROOT / "reports"
RESEARCH_DIR = PROJECT_ROOT / "research"

# Data File Paths
TOURISM_PANEL_PATH = PROCESSED_DATA_DIR / "tourism_timeseries_2011_2025.csv"
NATIONAL_STATISTICS_PATH = EXTRACTED_DATA_DIR / "national_tourism_statistics.csv"
SUSTAINABILITY_SNAPSHOT_PATH = PROCESSED_DATA_DIR / "state_sustainability_snapshot.csv"
FOREST_COVER_PATH = PROCESSED_DATA_DIR / "forest_cover_long.csv"
GROUNDWATER_PATH = PROCESSED_DATA_DIR / "groundwater_long.csv"
SDG_SCORES_PATH = PROCESSED_DATA_DIR / "sdg_scores_long.csv"
GEOJSON_PATH = GEO_DATA_DIR / "india_states.geojson"

# State Name Bridge between Canonical Dataset and GeoJSON features
CANONICAL_TO_GEOJSON_NAME = {
    "Andaman & Nicobar Islands": "Andaman and Nicobar Islands",
    "Dadra & Nagar Haveli and Daman & Diu": "Dadra and Nagar Haveli and Daman and Diu",
}
GEOJSON_TO_CANONICAL_NAME = {v: k for k, v in CANONICAL_TO_GEOJSON_NAME.items()}

# State Name Bridge between 2025 Compendium PDF raw labels and Canonical Names
COMPENDIUM_TO_CANONICAL_NAME = {
    "Dadra Nagar Haveli & Daman & Diu": "Dadra & Nagar Haveli and Daman & Diu",
    "Jammu & Kashmir": "Jammu and Kashmir",
}

# ISO 3166-2:IN Code Mapping
STATE_TO_ISO_CODE = {
    "Andaman & Nicobar Islands": "IN-AN",
    "Andhra Pradesh": "IN-AP",
    "Arunachal Pradesh": "IN-AR",
    "Assam": "IN-AS",
    "Bihar": "IN-BR",
    "Chandigarh": "IN-CH",
    "Chhattisgarh": "IN-CT",
    "Dadra & Nagar Haveli and Daman & Diu": "IN-DH",
    "Delhi": "IN-DL",
    "Goa": "IN-GA",
    "Gujarat": "IN-GJ",
    "Haryana": "IN-HR",
    "Himachal Pradesh": "IN-HP",
    "Jammu and Kashmir": "IN-JK",
    "Jharkhand": "IN-JH",
    "Karnataka": "IN-KA",
    "Kerala": "IN-KL",
    "Ladakh": "IN-LA",
    "Lakshadweep": "IN-LD",
    "Madhya Pradesh": "IN-MP",
    "Maharashtra": "IN-MH",
    "Manipur": "IN-MN",
    "Meghalaya": "IN-ML",
    "Mizoram": "IN-MZ",
    "Nagaland": "IN-NL",
    "Odisha": "IN-OR",
    "Puducherry": "IN-PY",
    "Punjab": "IN-PB",
    "Rajasthan": "IN-RJ",
    "Sikkim": "IN-SK",
    "Tamil Nadu": "IN-TN",
    "Telangana": "IN-TG",
    "Tripura": "IN-TR",
    "Uttar Pradesh": "IN-UP",
    "Uttarakhand": "IN-UT",
    "West Bengal": "IN-WB",
}

# Application Navigation Sections  (6 sections — Task 2 scope)
NAV_SECTIONS = [
    "Tourism Intelligence",
    "Sustainability Intelligence",
    "State Comparison",
    "Machine Learning Intelligence",
    "Sustainable Planning Studio",
    "AI Policy Assistant",
]

# Section Icons / Badges
NAV_ICONS = {
    "Tourism Intelligence": "✈️",
    "Sustainability Intelligence": "🌿",
    "State Comparison": "⚖️",
    "Machine Learning Intelligence": "🤖",
    "Sustainable Planning Studio": "🗺️",
    "AI Policy Assistant": "💡",
}

# Color Palette (Emerald / Teal / Slate / Amber / Coral)
THEME_COLORS = {
    "primary": "#0F766E",       # Deep teal
    "primary_light": "#14B8A6", # Vibrant teal
    "secondary": "#0284C7",     # Azure blue
    "accent": "#F59E0B",        # Warm amber
    "danger": "#EF4444",        # Coral red
    "dark_bg": "#0B1320",       # Dark slate
    "card_bg": "#FFFFFF",
    "border": "#E2E8F0",
    "text": "#1E293B",
    "text_muted": "#64748B",
}
