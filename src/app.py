"""Main Streamlit application for the TES 360° Evaluation System."""

from __future__ import annotations

import io
import os
import sys
import zipfile
from pathlib import Path
from typing import Dict

# Ensure the repo root is on sys.path so `src` package is importable
# (needed when running on Streamlit Cloud where only src/ is on the path)
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import numpy as np
import pandas as pd
import streamlit as st

from src.config import (
    DEFAULT_EXPERIENCE,
    DEFAULT_PERIOD_CODE,
    DEFAULT_PEER_SCORE,
    DEFAULT_QUALIFICATION,
    DEFAULT_SCHOOL_NAME,
    DEFAULT_SELF_SCORE,
    DEFAULT_STAFF_ID,
    DEFAULT_SUPERIOR_SCORE,
    DIMENSIONS,
    SCALE_MAP,
    STAKEHOLDER_LABELS,
    TEMP_DIR,
)
from src.pdf_parser import extract_score_from_pdf
from src.radar_chart import generate_diamond_radar
from src.scorecard import build_pdf_scorecard


def _compute_dimension_scores(means: pd.Series) -> Dict[str, float]:
    """Compute D1–D7 dimension scores from the column means of the rating data."""
    d_scores: Dict[str, float] = {}
    for dim_name, (idx_a, idx_b) in DIMENSIONS.items():
        vals = []
        for idx in (idx_a, idx_b):
            if idx < len(means):
                vals.append(means.iloc[idx])
        d_scores[dim_name] = float(np.mean(vals)) if vals else 0.0
    return d_scores


def _compute_student_score(d_scores: Dict[str, float]) -> float:
    """Convert dimension scores (out of 5) to a 70-point student score."""
    student_avg_5 = float(np.mean(list(d_scores.values())))
    return round((student_avg_5 / 5.0) * 70.0, 1)


def _get_faculty_column(df: pd.DataFrame) -> str:
    """Identify the faculty/lecturer column in the student survey DataFrame."""
    for c in df.columns:
        if "Course / Faculty" in c or "Lecturer" in c or "Faculty" in c:
            return c
    return df.columns[1]


def _clean_faculty_name(raw: str) -> str:
    """Extract the clean faculty name from a raw string like 'ST-1042 - John Doe'."""
    return raw.split("-")[-1].strip() if "-" in raw else raw


def main() -> None:
    """Entry point for the Streamlit app."""
    # Set Streamlit Page Config
    st.set_page_config(
        page_title="IIMS TES System",
        page_icon="📊",
        layout="wide",
    )

    st.title("IIMS TES System")
    st.markdown(
        "Upload **Student Excel responses** and **Self / Peer / Superior PDF forms** "
        "to generate standardized **1-page scorecards**."
    )

    st.sidebar.header("Step 1: Upload Files")

    # File Uploaders
    student_file = st.sidebar.file_uploader("1. Student Survey (.xlsx)", type=["xlsx", "xls"])
    self_pdf = st.sidebar.file_uploader("2. Self-Assessment (.pdf)", type=["pdf"])
    peer_pdf = st.sidebar.file_uploader("3. Peer Assessment (.pdf)", type=["pdf"])
    superior_pdf = st.sidebar.file_uploader("4. Superior Assessment (.pdf)", type=["pdf"])

    if student_file is not None:
        df = pd.read_excel(student_file)

        faculty_col = _get_faculty_column(df)
        unique_faculty = df[faculty_col].dropna().unique().tolist()

        st.sidebar.header("Step 2: Select Mode")
        app_mode = st.sidebar.radio(
            "Mode:", ["Single Faculty Scorecard", "Batch Generation (ZIP All)"]
        )

        if app_mode == "Single Faculty Scorecard":
            _render_single_mode(
                df, faculty_col, unique_faculty, self_pdf, peer_pdf, superior_pdf
            )
        else:
            _render_batch_mode(df, faculty_col, unique_faculty)
    else:
        st.info("Please upload the student evaluation Excel file in the sidebar to begin.")


def _render_single_mode(
    df: pd.DataFrame,
    faculty_col: str,
    unique_faculty: list,
    self_pdf,
    peer_pdf,
    superior_pdf,
) -> None:
    """Render the single-faculty scorecard generation UI."""
    selected_faculty_raw = st.sidebar.selectbox("Choose Faculty Member:", unique_faculty)
    faculty_name_clean = _clean_faculty_name(selected_faculty_raw)

    st.subheader("Step 3: Staff & Metadata")
    col1, col2, col3 = st.columns(3)
    with col1:
        staff_id = st.text_input("Staff ID:", DEFAULT_STAFF_ID)
        school_name = st.text_input("School / College Name:", DEFAULT_SCHOOL_NAME)
    with col2:
        experience = st.text_input("Experience:", DEFAULT_EXPERIENCE)
        qualification = st.text_input("Qualification:", DEFAULT_QUALIFICATION)
    with col3:
        period_code = st.text_input("Appraisal Period Code:", DEFAULT_PERIOD_CODE)

    # Extract Scores from PDFs
    extracted_self = extract_score_from_pdf(self_pdf) if self_pdf else DEFAULT_SELF_SCORE
    extracted_peer = extract_score_from_pdf(peer_pdf) if peer_pdf else DEFAULT_PEER_SCORE
    extracted_superior = (
        extract_score_from_pdf(superior_pdf) if superior_pdf else DEFAULT_SUPERIOR_SCORE
    )

    st.subheader("Step 4: Stakeholder Ratings (Out of 70)")

    # Calculate Student Score from Excel
    fac_df = df[df[faculty_col] == selected_faculty_raw].copy()
    rating_cols = [c for c in fac_df.columns if c.startswith("B.")]

    for c in rating_cols:
        fac_df[c] = fac_df[c].map(SCALE_MAP)

    means = fac_df[rating_cols].mean()
    d_scores = _compute_dimension_scores(means)
    student_score_70 = _compute_student_score(d_scores)

    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        st.metric("Students (Excel)", f"{student_score_70} / 70")
    with col_s2:
        self_score = st.number_input(
            "Self Score (PDF / Manual):", 0.0, 70.0, value=float(extracted_self or 60.0), step=0.5
        )
    with col_s3:
        peer_score = st.number_input(
            "Peer Score (PDF / Manual):", 0.0, 70.0, value=float(extracted_peer or 60.0), step=0.5
        )
    with col_s4:
        superior_score = st.number_input(
            "Superior Score (PDF / Manual):", 0.0, 70.0, value=float(extracted_superior or 60.0), step=0.5
        )

    st.markdown("---")

    if st.button("Generate 360° PDF Scorecard", type="primary"):
        stakeholder_scores = {
            "Self": self_score,
            "Superior": superior_score,
            "Peers": peer_score,
            "Students": student_score_70,
        }

        radar_png = generate_diamond_radar(stakeholder_scores)
        pdf_filename = f"{faculty_name_clean.replace(' ', '_')}_TES_Scorecard.pdf"
        pdf_path = str(TEMP_DIR / pdf_filename)

        pdf_path, weighted_avg, final_score, result_text = build_pdf_scorecard(
            pdf_path,
            faculty_name_clean,
            staff_id,
            school_name,
            experience,
            qualification,
            period_code,
            d_scores,
            stakeholder_scores,
            radar_png,
        )

        st.success(f"Scorecard successfully generated for **{faculty_name_clean}**!")
        st.metric("Final Classification Score", f"{final_score:.1f}%", result_text)

        with open(pdf_path, "rb") as file:
            st.download_button(
                label="Download 1-Page PDF Scorecard",
                data=file,
                file_name=pdf_filename,
                mime="application/pdf",
            )

        # Clean up the generated PDF after download
        if os.path.exists(pdf_path):
            os.remove(pdf_path)


def _render_batch_mode(df: pd.DataFrame, faculty_col: str, unique_faculty: list) -> None:
    """Render the batch ZIP generation UI."""
    st.subheader("Batch Generate Scorecards for ALL Faculty")
    st.write(f"Found **{len(unique_faculty)}** faculty member(s) in the uploaded spreadsheet.")

    if st.button("Batch Process & Download All (.ZIP)", type="primary"):
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for idx, fac_raw in enumerate(unique_faculty):
                fac_clean = _clean_faculty_name(fac_raw)

                fac_df = df[df[faculty_col] == fac_raw].copy()
                rating_cols = [c for c in fac_df.columns if c.startswith("B.")]

                for c in rating_cols:
                    fac_df[c] = fac_df[c].map(SCALE_MAP)

                means = fac_df[rating_cols].mean()
                d_scores = _compute_dimension_scores(means)
                student_score_70 = _compute_student_score(d_scores)

                stakeholder_scores = {
                    "Self": DEFAULT_SELF_SCORE,
                    "Superior": DEFAULT_SUPERIOR_SCORE,
                    "Peers": DEFAULT_PEER_SCORE,
                    "Students": student_score_70,
                }

                radar_png = generate_diamond_radar(stakeholder_scores, f"temp_radar_{idx}.png")
                pdf_filename = f"{fac_clean.replace(' ', '_')}_TES_Scorecard.pdf"
                pdf_path = str(TEMP_DIR / pdf_filename)

                pdf_path, _, _, _ = build_pdf_scorecard(
                    pdf_path,
                    fac_clean,
                    f"ST-10{idx + 1}",
                    DEFAULT_SCHOOL_NAME,
                    "5.0 years",
                    DEFAULT_QUALIFICATION,
                    DEFAULT_PERIOD_CODE,
                    d_scores,
                    stakeholder_scores,
                    radar_png,
                )

                zip_file.write(pdf_path, arcname=pdf_filename)
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)

        zip_buffer.seek(0)
        st.success("All scorecards generated successfully!")
        st.download_button(
            label="Download ZIP Archive of All Scorecards",
            data=zip_buffer,
            file_name="360_Faculty_Scorecards_Batch.zip",
            mime="application/zip",
        )


if __name__ == "__main__":
    main()
