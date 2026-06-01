"""Technical indicator functions."""

from __future__ import annotations

from finwatch.indicators.ema import ema
from finwatch.indicators.fibonacci import fibonacci_retracements
from finwatch.indicators.macd import MACDResult, macd
from finwatch.indicators.rsi import rsi
from finwatch.indicators.sma import sma
from finwatch.indicators.smma import smma
from finwatch.indicators.stochastic import StochasticResult, stochastic
from finwatch.indicators.vwap import vwap

__all__ = [
    "ema",
    "fibonacci_retracements",
    "MACDResult",
    "macd",
    "rsi",
    "sma",
    "smma",
    "StochasticResult",
    "stochastic",
    "vwap",
]
