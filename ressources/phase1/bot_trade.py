
import numpy as np
import json
import os

# ============================================================================
# Global State Variables
# ============================================================================
history = []  
current_pos = 0.0  
entry_price = 0.0  

# Default Configuration for "Fixed Leverage" (Optimized: 221% PnL, -42% DD)
CONFIG = {
    'bb_window': 15,
    'bb_std': 2.0,
    'rsi_period': 14,
    'rsi_lower': 30,
    'rsi_upper': 70,
    'stop_loss': 0.08,    
    'fixed_leverage': 3.0   # Safe Fixed Leverage
}

if os.path.exists('params.json'):
    try:
        with open('params.json', 'r') as f:
            CONFIG.update(json.load(f))
    except:
        pass

# ============================================================================
# Helper Functions
# ============================================================================

def calculate_bollinger_bands(prices: list, window: int = 20, num_std: float = 2.0) -> dict:
    if len(prices) < window: return None
    prices_array = np.array(prices[-window:])
    sma = np.mean(prices_array)
    std = np.std(prices_array, ddof=1)
    return {
        'sma': sma,
        'upper': sma + (num_std * std),
        'lower': sma - (num_std * std),
        'std': std
    }

def calculate_rsi(prices: list, period: int = 14) -> float:
    if len(prices) < period + 1: return 50.0
    prices_array = np.array(prices[-(period + 1):])
    deltas = np.diff(prices_array)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    avg_loss = np.mean(losses)
    if avg_loss == 0: return 100.0
    rs = np.mean(gains) / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))

# ============================================================================
# Main Decision Function
# ============================================================================

def make_decision(epoch: int, price: float) -> dict:
    global history, current_pos, entry_price

    history.append(price)
    current_price = price

    if len(history) < 30: return {'Asset A': 0.0, 'Cash': 1.0}

    # Indicators
    bb = calculate_bollinger_bands(history, window=int(CONFIG['bb_window']), num_std=CONFIG['bb_std'])
    rsi = calculate_rsi(history, period=int(CONFIG['rsi_period']))
    
    if bb is None: return {'Asset A': 0.0, 'Cash': 1.0}

    # Signals
    buy_signal = False
    sell_signal = False

    # Buy: Price < Lower BB OR RSI < Lower Threshold
    if current_price < bb['lower']: buy_signal = True
    if rsi < CONFIG['rsi_lower']: buy_signal = True

    # Sell: Price > Upper BB OR RSI > Upper Threshold
    if current_price > bb['upper']: sell_signal = True
    if rsi > CONFIG['rsi_upper']: sell_signal = True

    # EXECUTE STATE CHANGE
    if buy_signal:
        if current_pos == 0.0:
            entry_price = current_price
            # FIXED LEVERAGE LOGIC
            # No volatility scaling, no confidence score.
            # Pure conviction in the Mean Reversion Stats.
            current_pos = CONFIG['fixed_leverage']
        else:
            # Hold current position
            pass

    if sell_signal:
        current_pos = 0.0
        entry_price = 0.0

    # STOP LOSS
    if current_pos > 0.0 and entry_price > 0:
        # Stop Loss Logic
        # Now that leverage is fixed, we can have a clearer relationship.
        # But let's stick to the 'Stop Loss % of Price' logic for now 
        # as it proved robust (8% price drop usually signals trend change).
        
        loss_pct = (entry_price - current_price) / entry_price
        if loss_pct > CONFIG['stop_loss']:
            current_pos = 0.0
            entry_price = 0.0
            return {'Asset A': 0.0, 'Cash': 1.0}

    allocation = current_pos
    return {'Asset A': allocation, 'Cash': 1.0 - allocation}
