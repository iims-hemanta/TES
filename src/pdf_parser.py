"""PDF score extraction utilities for stakeholder assessment forms."""

from __future__ import annotations

import re
from typing import Optional

import pypdf
import streamlit as st


def extract_score_from_pdf(pdf_file) -> Optional[float]:
    """
    Parse an uploaded PDF evaluation form (Self, Peer, or Superior)
    and extract the 'Total Score (Out of 70)' rating using regex.

    Parameters
    ----------
    pdf_file : file-like or None
        A file-like object uploaded via Streamlit's file_uploader.

    Returns
    -------
    float or None
        The extracted score, or ``None`` if parsing fails.
    """
    if pdf_file is None:
        return None

    try:
        reader = pypdf.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""

        # Match explicit text patterns like "Total Score (Out of 70): 62"
        match = re.search(
            r"(?:Total Score|Score)\s*(?:\(Out of 70\))?\s*[:=]\s*(\d+(?:\.\d+)?)",
            text,
            re.IGNORECASE,
        )
        if match:
            return float(match.group(1))

        # Fallback: search for isolated numbers near 70
        numbers = re.findall(r"\b([1-6]?\d(?:\.\d)?|70)\b", text)
        if numbers:
            return float(numbers[-1])

    except Exception as e:
        st.sidebar.warning(f"Could not parse score from {pdf_file.name}: {e}")

    return None
