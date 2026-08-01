"""Tests for package-level metadata."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from unittest.mock import patch

import finwatch


def test_version_is_non_empty_string() -> None:
    assert isinstance(finwatch.__version__, str)
    assert len(finwatch.__version__) > 0


def test_version_fallback_when_not_installed() -> None:
    with patch("finwatch.version", side_effect=PackageNotFoundError):
        assert finwatch._resolve_version() == "0.0.0"


def test_version_in_all_exports() -> None:
    assert "__version__" in finwatch.__all__
