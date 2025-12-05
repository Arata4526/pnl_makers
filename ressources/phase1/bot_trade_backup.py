"""
Adaptive Trend Follower with RSI & Volatility Filter
A sophisticated trading algorithm for single-asset portfolio management
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
    """
    Calculate RSI (Relative Strength Index) from scratch.

    Args:
        prices: List of historical prices
        period: RSI period (default: 14)

    Returns:
        RSI value between 0 and 100
    """
    if len(prices) < period + 1:
        return 50.0  # Neutral RSI during warm-up

    # Calculate price changes
    prices_array = np.array(prices[-(period + 1):])
    deltas = np.diff(prices_array)

    # Separate gains and losses
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)

    # Calculate average gain and loss
    avg_gain = np.mean(gains)
    avg_loss = np.mean(losses)

    # Avoid division by zero
    if avg_loss == 0:
        return 100.0 if avg_gain > 0 else 50.0

    # Calculate RS and RSI
    rs = avg_gain / avg_loss
    rsi = 100.0 - (100.0 / (1.0 + rs))

    return rsi


def calculate_sma(prices: list, window: int) -> float:
    """
    Calculate Simple Moving Average.

    Args:
        prices: List of historical prices
        window: SMA window size

    Returns:
        SMA value or None if insufficient data
    """
    if len(prices) < window:
        return None

    return np.mean(prices[-window:])


def calculate_volatility_pct(prices: list, window: int = 30) -> float:
    """
    Calculate volatility as percentage of current price.

    Args:
        prices: List of historical prices
        window: Window for volatility calculation

    Returns:
        Volatility as percentage of current price
    """
    if len(prices) < window:
        return 0.0

    prices_array = np.array(prices[-window:])
    std_dev = np.std(prices_array, ddof=1)
    current_price = prices[-1]

    return std_dev / current_price if current_price > 0 else 0.0


def calculate_momentum(prices: list, lookback: int = 10) -> float:
    """
    Calculate momentum as percentage change over lookback period.

    Args:
        prices: List of historical prices
        lookback: Number of periods to look back

    Returns:
        Momentum as percentage change
    """
    if len(prices) < lookback + 1:
        return 0.0

    old_price = prices[-(lookback + 1)]
    current_price = prices[-1]

    if old_price == 0:
        return 0.0

    return (current_price - old_price) / old_price


# ============================================================================
# Main Decision Function
# ============================================================================

def make_decision(epoch: int, price: float) -> dict:
    """
    Make portfolio allocation decision based on adaptive trend following strategy.

    Args:
        epoch: Current time step
        price: Current asset price

    Returns:
        Dictionary with 'Asset A' and 'Cash' allocations summing to 1.0
    """
    global history, max_price_seen

    # Add current price to history
    history.append(price)

    # Update maximum price seen
    if price > max_price_seen:
        max_price_seen = price

    # ========================================================================
    # WARM-UP PHASE: Insufficient data for indicators
    # ========================================================================
    if len(history) < 15:
        # Aggressive during warm-up: full allocation to capture early trends
        return {'Asset A': 1.0, 'Cash': 0.0}

    # ========================================================================
    # Calculate Indicators
    # ========================================================================

    # Trend indicators
    short_sma = calculate_sma(history, window=10)
    long_sma = calculate_sma(history, window=30)

    # Momentum
    momentum_10 = calculate_momentum(history, lookback=10)
    momentum_5 = calculate_momentum(history, lookback=5)

    # Volatility
    vol_pct = calculate_volatility_pct(history, window=30)

    # RSI
    rsi = calculate_rsi(history, period=14)

    # Current price vs SMA
    price_vs_sma = (price / long_sma - 1.0) if long_sma else 0.0

    # ========================================================================
    # PRIORITY 1: Hard Stop Loss (Drawdown Protection)
    # ========================================================================
    if price < 0.88 * max_price_seen:
        # 12% drawdown from peak - exit to cash
        max_price_seen = price  # Reset to allow re-entry
        return {'Asset A': 0.0, 'Cash': 1.0}

    # ========================================================================
    # PRIORITY 2: Strong Negative Momentum (Crash Protection)
    # ========================================================================
    if momentum_5 < -0.05:  # 5% drop in 5 periods
        # Rapid decline - reduce to 20% allocation
        return {'Asset A': 0.2, 'Cash': 0.8}

    # ========================================================================
    # PRIORITY 3: Dynamic Allocation Based on Multiple Factors
    # ========================================================================

    # Start with base allocation
    allocation = 0.9  # Default to 90% invested

    # Factor 1: Trend (using SMA crossover as confirmation, not signal)
    if short_sma and long_sma:
        if short_sma > long_sma:
            # Bullish trend confirmed - increase allocation
            allocation = 1.0
        else:
            # Bearish or unclear trend - moderate allocation
            allocation = 0.6

    # Factor 2: RSI-based adjustments
    if rsi > 70:
        # Overbought - reduce allocation slightly
        allocation *= 0.85
    elif rsi < 30:
        # Oversold - increase allocation (buying opportunity)
        allocation = min(1.0, allocation * 1.2)
    elif rsi < 40:
        # Mild oversold - slight increase
        allocation = min(1.0, allocation * 1.1)

    # Factor 3: Momentum boost
    if momentum_10 > 0.03:  # Strong positive momentum
        allocation = min(1.0, allocation * 1.1)
    elif momentum_10 < -0.03:  # Strong negative momentum
        allocation *= 0.8

    # Factor 4: Volatility adjustment
    if vol_pct > 0.04:  # High volatility
        allocation *= 0.9  # Slight reduction
    elif vol_pct < 0.015:  # Low volatility
        allocation = min(1.0, allocation * 1.05)  # Slight increase

    # Factor 5: Price position vs long-term SMA
    if price_vs_sma > 0.05:  # More than 5% above SMA
        allocation *= 0.95  # Slight caution
    elif price_vs_sma < -0.03:  # More than 3% below SMA
        allocation = min(1.0, allocation * 1.1)  # Buying opportunity

    # ========================================================================
    # Safety Checks
    # ========================================================================

    # Clamp allocation to valid range [0.0, 1.0]
    allocation = max(0.0, min(1.0, allocation))

    # Calculate cash allocation
    cash_allocation = 1.0 - allocation

    # Return the decision
    return {
        'Asset A': allocation,
        'Cash': cash_allocation
    }
