"""Regression tests for the legacy content analyzer."""

import pytest

pytest.importorskip("pypdf")

from pdf_content_analyzer import PDFContentAnalyzer


def test_random_case_filename_trips_case_check():
    _is_gibberish, checks = PDFContentAnalyzer().is_gibberish_filename("aBcDeFgHiJ.pdf")

    assert checks["random_case_mix"] is True


def test_normal_title_case_filename_is_not_random_case():
    _is_gibberish, checks = PDFContentAnalyzer().is_gibberish_filename("Python Cookbook.pdf")

    assert checks["random_case_mix"] is False
