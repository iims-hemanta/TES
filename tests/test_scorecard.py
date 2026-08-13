"""Tests for the PDF scorecard engine module."""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from src.scorecard import _classify, build_pdf_scorecard


class TestClassify:
    """Test suite for the _classify helper."""

    def test_poor_engagement(self):
        """Score below 56 should classify as Poor."""
        result_text, description = _classify(50.0)
        assert result_text == "POOR TEACHING ENGAGEMENT"
        assert description == "Poor Teaching Engagement"

    def test_fair_engagement(self):
        """Score 56–65 should classify as Fair."""
        result_text, description = _classify(60.0)
        assert result_text == "FAIR TEACHING ENGAGEMENT"
        assert description == "Fair Teaching Engagement"

    def test_average_engagement(self):
        """Score 65–75 should classify as Average."""
        result_text, description = _classify(70.0)
        assert result_text == "AVERAGE TEACHING ENGAGEMENT"
        assert description == "Average Teaching Engagement"

    def test_above_average_engagement(self):
        """Score 75–85 should classify as Above Average."""
        result_text, description = _classify(80.0)
        assert result_text == "ABOVE AVERAGE TEACHING ENGAGEMENT"
        assert description == "Above Average Teaching Engagement"

    def test_excellent_engagement(self):
        """Score >= 85 should classify as Excellent."""
        result_text, description = _classify(90.0)
        assert result_text == "EXCELLENT TEACHING ENGAGEMENT"
        assert description == "Excellent Teaching Engagement"

    def test_boundary_56(self):
        """Score exactly 56 should classify as Fair (boundary)."""
        result_text, _ = _classify(56.0)
        assert result_text == "FAIR TEACHING ENGAGEMENT"

    def test_boundary_65(self):
        """Score exactly 65 should classify as Average (boundary)."""
        result_text, _ = _classify(65.0)
        assert result_text == "AVERAGE TEACHING ENGAGEMENT"

    def test_boundary_75(self):
        """Score exactly 75 should classify as Above Average (boundary)."""
        result_text, _ = _classify(75.0)
        assert result_text == "ABOVE AVERAGE TEACHING ENGAGEMENT"

    def test_boundary_85(self):
        """Score exactly 85 should classify as Excellent (boundary)."""
        result_text, _ = _classify(85.0)
        assert result_text == "EXCELLENT TEACHING ENGAGEMENT"


class TestBuildPdfScorecard:
    """Test suite for build_pdf_scorecard."""

    @pytest.fixture
    def sample_data(self, tmp_path):
        """Provide sample data for scorecard generation."""
        # Create a real radar PNG using matplotlib
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np

        radar_png = str(tmp_path / "test_radar.png")
        fig, ax = plt.subplots(figsize=(3.5, 3.5), subplot_kw=dict(polar=True))
        angles = np.linspace(0, 2 * np.pi, 4, endpoint=False).tolist()
        angles += angles[:1]
        values = [62.0, 60.0, 58.0, 65.0, 62.0]
        ax.plot(angles, values, color="#1E293B", linewidth=2)
        ax.fill(angles, values, color="#3B82F6", alpha=0.15)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(["Self", "Superior", "Peers", "Students"], size=8)
        ax.set_ylim(0, 70.0)
        plt.tight_layout()
        plt.savefig(radar_png, dpi=300, transparent=True)
        plt.close()

        d_scores = {
            "D1 - Subject knowledge contextualization": 4.2,
            "D2 - Supportive Learning Environment": 3.8,
            "D3 - Impact to student achievement/learning outcomes": 4.0,
            "D4 - Provision of appropriate feedback": 3.5,
            "D5 - Use of relevant learning technology": 4.1,
            "D6 - Attention to affective attributes": 3.9,
            "D7 - Use of research to inform teaching": 4.3,
        }

        stakeholder_scores = {
            "Self": 62.0,
            "Superior": 60.0,
            "Peers": 58.0,
            "Students": 65.0,
        }

        pdf_path = str(tmp_path / "test_scorecard.pdf")

        return {
            "pdf_path": pdf_path,
            "faculty_name": "John Doe",
            "staff_id": "ST-1042",
            "school_name": "IIMS College",
            "experience": "5.5 years",
            "qualification": "M.Sc. Computer Science",
            "period_code": "AP2024/04",
            "d_scores": d_scores,
            "stakeholder_scores": stakeholder_scores,
            "radar_png": radar_png,
        }

    def test_generates_pdf_file(self, sample_data):
        """Should create a PDF file at the specified path."""
        result = build_pdf_scorecard(**sample_data)
        pdf_path, weighted_avg, final_score, result_text = result

        assert os.path.exists(pdf_path)
        assert pdf_path == sample_data["pdf_path"]

    def test_returns_correct_weighted_avg(self, sample_data):
        """Should return the correct weighted average of stakeholder scores."""
        _, weighted_avg, _, _ = build_pdf_scorecard(**sample_data)

        expected_avg = (62.0 + 60.0 + 58.0 + 65.0) / 4
        assert weighted_avg == pytest.approx(expected_avg, rel=1e-6)

    def test_returns_correct_final_score(self, sample_data):
        """Should return the correct final classification score (percentage)."""
        _, weighted_avg, final_score, _ = build_pdf_scorecard(**sample_data)

        expected_final = (weighted_avg / 70.0) * 100.0
        assert final_score == pytest.approx(expected_final, rel=1e-6)

    def test_returns_correct_result_text(self, sample_data):
        """Should return the correct classification result text."""
        _, _, final_score, result_text = build_pdf_scorecard(**sample_data)

        expected_text, _ = _classify(final_score)
        assert result_text == expected_text

    def test_cleans_up_radar_png(self, sample_data):
        """Should delete the radar PNG after building the PDF."""
        build_pdf_scorecard(**sample_data)
        assert not os.path.exists(sample_data["radar_png"])

    def test_pdf_is_valid(self, sample_data):
        """Generated file should be a valid PDF (check magic bytes)."""
        build_pdf_scorecard(**sample_data)

        with open(sample_data["pdf_path"], "rb") as f:
            header = f.read(5)
        assert header == b"%PDF-"
