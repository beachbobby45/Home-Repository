"""Tests for Gate 0 verification helpers."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.config import Settings, missing_required_keys


def test_missing_required_keys_detects_empty_values():
    settings = Settings(
        anthropic_api_key="sk-test",
        fred_api_key="",
        finnhub_api_key="fh-test",
        massive_api_key=None,
        verify_test_ticker="SPY",
        app_api_key="",
        alpaca_api_key=None,
        alpaca_secret_key=None,
    )
    missing = missing_required_keys(settings)
    assert "FRED_API_KEY" in missing
    assert "ANTHROPIC_API_KEY" not in missing


def test_missing_required_keys_passes_when_all_set():
    settings = Settings(
        anthropic_api_key="sk-test",
        fred_api_key="fred-key",
        finnhub_api_key="fh-test",
        massive_api_key=None,
        verify_test_ticker="SPY",
        app_api_key="x",
        alpaca_api_key=None,
        alpaca_secret_key=None,
    )
    assert missing_required_keys(settings) == []


def test_verify_access_module_imports():
    """Ensure verify_access script is importable."""
    import importlib.util
    import sys

    script = ROOT / "scripts" / "verify_access.py"
    spec = importlib.util.spec_from_file_location("verify_access", script)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["verify_access"] = module
    spec.loader.exec_module(module)
    assert "CHECKS" in dir(module)
    assert set(module.REQUIRED_CHECKS) == {"anthropic", "fred", "finnhub"}
