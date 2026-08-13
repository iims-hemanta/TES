"""Tests for the radar chart module."""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from src.radar_chart import generate_diamond_radar


class TestGenerateDiamondRadar:
    """Test suite for generate_diamond_radar."""

    def test_generates_png_file(self, tmp_path):
        """Should create a PNG file at the specified path."""
        stakeholder_scores = {
            "Self": 62.0,
            "Superior": 60.0,
            "Peers": 58.0,
            "Students": 65.0,
        }
        output_name = "test_radar.png"

        with patch("src.radar_chart.TEMP_DIR", tmp_path):
            result_path = generate_diamond_radar(stakeholder_scores, output_name)

        assert os.path.exists(result_path)
        assert result_path.endswith(output_name)

    def test_default_output_name(self, tmp_path):
        """Should use 'temp_radar.png' as the default output name."""
        stakeholder_scores = {
            "Self": 60.0,
            "Superior": 60.0,
            "Peers": 60.0,
            "Students": 60.0,
        }

        with patch("src.radar_chart.TEMP_DIR", tmp_path):
            result_path = generate_diamond_radar(stakeholder_scores)

        assert os.path.exists(result_path)
        assert result_path.endswith("temp_radar.png")

    def test_custom_output_name(self, tmp_path):
        """Should use the provided custom output name."""
        stakeholder_scores = {
            "Self": 55.0,
            "Superior": 60.0,
            "Peers": 58.0,
            "Students": 62.0,
        }
        output_name = "custom_radar_0.png"

        with patch("src.radar_chart.TEMP_DIR", tmp_path):
            result_path = generate_diamond_radar(stakeholder_scores, output_name)

        assert os.path.exists(result_path)
        assert result_path.endswith(output_name)

    def test_png_file_is_valid(self, tmp_path):
        """Generated file should be a valid PNG (check magic bytes)."""
        stakeholder_scores = {
            "Self": 62.0,
            "Superior": 60.0,
            "Peers": 58.0,
            "Students": 65.0,
        }

        with patch("src.radar_chart.TEMP_DIR", tmp_path):
            result_path = generate_diamond_radar(stakeholder_scores, "valid_test.png")

        with open(result_path, "rb") as f:
            header = f.read(8)
        # PNG magic bytes
        assert header == b"\x89PNG\r\n\x1a\n"
