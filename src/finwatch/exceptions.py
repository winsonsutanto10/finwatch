"""Custom exceptions for finwatch."""

from __future__ import annotations


class RetrievalError(Exception):
    """Raised when a price retriever cannot fetch data for a symbol."""
