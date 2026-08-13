"""Configuration constants for the TES 360° Evaluation System."""

from __future__ import annotations

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Base paths
# ---------------------------------------------------------------------------
BASE_DIR: Path = Path(__file__).resolve().parent.parent
SRC_DIR: Path = BASE_DIR / "src"
TEMP_DIR: Path = BASE_DIR / "temp"
TEMP_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Default metadata
# ---------------------------------------------------------------------------
DEFAULT_SCHOOL_NAME: str = os.getenv("DEFAULT_SCHOOL_NAME", "IIMS College - BCS (Hons)")
DEFAULT_STAFF_ID: str = os.getenv("DEFAULT_STAFF_ID", "ST-1042")
DEFAULT_EXPERIENCE: str = os.getenv("DEFAULT_EXPERIENCE", "5.5 years")
DEFAULT_QUALIFICATION: str = os.getenv("DEFAULT_QUALIFICATION", "M.Sc. Computer Science")
DEFAULT_PERIOD_CODE: str = os.getenv("DEFAULT_PERIOD_CODE", "AP2024/04")

# ---------------------------------------------------------------------------
# Default stakeholder scores (fallbacks when PDF parsing fails)
# ---------------------------------------------------------------------------
DEFAULT_SELF_SCORE: float = float(os.getenv("DEFAULT_SELF_SCORE", "62.0"))
DEFAULT_PEER_SCORE: float = float(os.getenv("DEFAULT_PEER_SCORE", "58.0"))
DEFAULT_SUPERIOR_SCORE: float = float(os.getenv("DEFAULT_SUPERIOR_SCORE", "60.0"))

# ---------------------------------------------------------------------------
# Rating scale mapping (Likert → numeric)
# ---------------------------------------------------------------------------
SCALE_MAP: dict[str, float] = {
    "Extremely Evident": 5.0,
    "Agree": 4.0,
    "Neutral": 3.0,
    "Disagree": 2.0,
    "Not Evident": 1.0,
}

# ---------------------------------------------------------------------------
# Dimension definitions (D1–D7)
# Each entry maps a dimension name to the column indices used for averaging.
# ---------------------------------------------------------------------------
DIMENSIONS: dict[str, tuple[int, int]] = {
    "D1 - Subject knowledge contextualization": (0, 12),
    "D2 - Supportive Learning Environment": (1, 11),
    "D3 - Impact to student achievement/learning outcomes": (4, 5),
    "D4 - Provision of appropriate feedback": (6, 7),
    "D5 - Use of relevant learning technology": (8, 9),
    "D6 - Attention to affective attributes": (2, 3),
    "D7 - Use of research to inform teaching": (10, 13),
}

# ---------------------------------------------------------------------------
# Classification thresholds (percentage)
# ---------------------------------------------------------------------------
CLASSIFICATION_THRESHOLDS: list[tuple[float, str, str]] = [
    (56.0, "POOR TEACHING ENGAGEMENT", "Poor Teaching Engagement"),
    (65.0, "FAIR TEACHING ENGAGEMENT", "Fair Teaching Engagement"),
    (75.0, "AVERAGE TEACHING ENGAGEMENT", "Average Teaching Engagement"),
    (85.0, "ABOVE AVERAGE TEACHING ENGAGEMENT", "Above Average Teaching Engagement"),
    (float("inf"), "EXCELLENT TEACHING ENGAGEMENT", "Excellent Teaching Engagement"),
]

# ---------------------------------------------------------------------------
# Color palette (shared between radar chart and PDF)
# ---------------------------------------------------------------------------
COLOR_PRIMARY: str = "#1E293B"       # Deep Slate
COLOR_MUTED_TEXT: str = "#64748B"    # Secondary Slate
COLOR_BG_HEADER: str = "#334155"     # Banner Header
COLOR_BG_ROW_ALT: str = "#F8FAFC"    # Cool White Row Stripe
COLOR_BORDER: str = "#E2E8F0"       # Soft Divider Line
COLOR_ACCENT_HL: str = "#E2E8F0"     # Highlight Active Tier
COLOR_ACCENT_BLUE: str = "#3B82F6"   # Cool Blue Accent

# ---------------------------------------------------------------------------
# Stakeholder labels (order matters for radar chart)
# ---------------------------------------------------------------------------
STAKEHOLDER_LABELS: list[str] = ["Self", "Superior", "Peers", "Students"]

# ---------------------------------------------------------------------------
# Score ranges
# ---------------------------------------------------------------------------
MAX_STAKEHOLDER_SCORE: float = 70.0
MAX_DIMENSION_SCORE: float = 5.0
