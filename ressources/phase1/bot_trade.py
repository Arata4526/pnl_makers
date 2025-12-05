"""
Adaptive Trend Follower with RSI & Volatility Filter
Simplified: Maximum investment with minimal interference
"""

import numpy as np

# ============================================================================
# Global State Variables
# ============================================================================
history = []  # List of historical prices
max_price_seen = 0.0  # Maximum price seen (for trailing stop)


# ============================================================================
# Helper Functions
# ============================================================================

def calculate_rsi(prices: list, period: int = 14) -> float:
    """Calculate RSI (Relative Strength Index) from scratch."""
    if len(prices) < period + 1:
        return 50.0

    prices_array = np.array(prices[-(period + 1):])
    deltas = np.diff(prices_array)

    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)

    avg_gain = np.mean(gains)
    avg_loss = np.mean(losses)

    if avg_loss == 0:
        return 100.0 if avg_gain > 0 else 50.0

    rs = avg_gain / avg_loss
    rsi = 100.0 - (100.0 / (1.0 + rs))

    return rsi


def calculate_sma(prices: list, window: int) -> float:
    """Calculate Simple Moving Average."""
    if len(prices) < window:
        return None
    return np.mean(prices[-window:])


def calculate_volatility_pct(prices: list, window: int = 30) -> float:
    """Calculate volatility as percentage of current price."""
    if len(prices) < window:
        return 0.0

    prices_array = np.array(prices[-window:])
    std_dev = np.std(prices_array, ddof=1)
    current_price = prices[-1]

    return std_dev / current_price if current_price > 0 else 0.0


# ============================================================================
# Main Decision Function
# ============================================================================

def make_decision(epoch: int, price: float) -> dict:
    """
    Make portfolio allocation decision.

    Strategy: Stay fully invested, only modulate slightly based on risk indicators.
    """
    global history, max_price_seen

    # Add current price to history
    history.append(price)

    # Update maximum price seen
    if price > max_price_seen:
        max_price_seen = price

    # ========================================================================
    # Warm-up: Stay fully invested
    # ========================================================================
    if len(history) < 30:
        return {'Asset A': 1.0, 'Cash': 0.0}

    # ========================================================================
    # Calculate Indicators
    # ========================================================================
    short_sma = calculate_sma(history, window=10)
    long_sma = calculate_sma(history, window=30)
    rsi = calculate_rsi(history, period=14)
    vol_pct = calculate_volatility_pct(history, window=30)

    # ========================================================================
    # Risk Management
    # ========================================================================

    # Start fully invested
    allocation = 1.0

    # ONLY exit if trailing stop is hit (15% drawdown)
    if price < 0.85 * max_price_seen:
        # Severe drawdown - exit but start re-entering gradually
        max_price_seen = price  # Reset
        return {'Asset A': 0.3, 'Cash': 0.7}

    # Otherwise, minor adjustments based on confluence of signals
    # Only reduce if we have VERY strong warnings across multiple indicators

    warnings = 0

    # Check for bearish trend
    if short_sma and long_sma and short_sma < long_sma * 0.98:
        warnings += 1

    # Check for extreme overbought
    if rsi > 80:
        warnings += 1

    # Check for very high volatility
    if vol_pct > 0.06:
        warnings += 1

    # Only reduce allocation if we have 3 warnings (all indicators agree)
    if warnings >= 3:
        allocation = 0.8
    elif warnings == 2:
        allocation = 0.95

    # RSI oversold boost (buying opportunity)
    if rsi < 30:
        allocation = 1.0

    # ========================================================================
    # Return Decision
    # ========================================================================
    return {
        'Asset A': allocation,
        'Cash': 1.0 - allocation
    }
