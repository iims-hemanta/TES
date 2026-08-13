"""Tests for the PDF parser module."""

from __future__ import annotations

import io
from unittest.mock import MagicMock, patch

import pytest

from src.pdf_parser import extract_score_from_pdf


class TestExtractScoreFromPdf:
    """Test suite for extract_score_from_pdf."""

    def test_returns_none_when_pdf_file_is_none(self):
        """Should return None when no file is provided."""
        assert extract_score_from_pdf(None) is None

    @patch("src.pdf_parser.pypdf.PdfReader")
    def test_extracts_explicit_total_score(self, mock_reader_cls):
        """Should extract score from 'Total Score (Out of 70): 62' pattern."""
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Total Score (Out of 70): 62"
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]
        mock_reader_cls.return_value = mock_reader

        pdf_file = MagicMock()
        pdf_file.name = "self_assessment.pdf"

        result = extract_score_from_pdf(pdf_file)
        assert result == 62.0

    @patch("src.pdf_parser.pypdf.PdfReader")
    def test_extracts_score_with_equals_sign(self, mock_reader_cls):
        """Should extract score from 'Score = 55' pattern."""
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Score = 55"
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]
        mock_reader_cls.return_value = mock_reader

        pdf_file = MagicMock()
        pdf_file.name = "peer_assessment.pdf"

        result = extract_score_from_pdf(pdf_file)
        assert result == 55.0

    @patch("src.pdf_parser.pypdf.PdfReader")
    def test_fallback_to_last_number(self, mock_reader_cls):
        """Should fall back to the last number in the text when no explicit pattern matches."""
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Some text 45 more text 68"
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]
        mock_reader_cls.return_value = mock_reader

        pdf_file = MagicMock()
        pdf_file.name = "superior_assessment.pdf"

        result = extract_score_from_pdf(pdf_file)
        assert result == 68.0

    @patch("src.pdf_parser.pypdf.PdfReader")
    def test_returns_none_when_no_numbers_found(self, mock_reader_cls):
        """Should return None when no numbers are found in the text."""
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "No numbers here at all"
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]
        mock_reader_cls.return_value = mock_reader

        pdf_file = MagicMock()
        pdf_file.name = "empty.pdf"

        result = extract_score_from_pdf(pdf_file)
        assert result is None

    @patch("src.pdf_parser.pypdf.PdfReader")
    def test_handles_exception_gracefully(self, mock_reader_cls):
        """Should return None and show a warning when an exception occurs."""
        mock_reader_cls.side_effect = Exception("PDF parsing error")

        pdf_file = MagicMock()
        pdf_file.name = "corrupt.pdf"

        with patch("src.pdf_parser.st.sidebar.warning") as mock_warning:
            result = extract_score_from_pdf(pdf_file)
            assert result is None
            mock_warning.assert_called_once()

    @patch("src.pdf_parser.pypdf.PdfReader")
    def test_handles_multiple_pages(self, mock_reader_cls):
        """Should concatenate text from all pages."""
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Page 1 text"
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "Total Score (Out of 70): 65"
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page1, mock_page2]
        mock_reader_cls.return_value = mock_reader

        pdf_file = MagicMock()
        pdf_file.name = "multi_page.pdf"

        result = extract_score_from_pdf(pdf_file)
        assert result == 65.0
