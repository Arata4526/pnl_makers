# Trading Bot Optimization - Situation Summary

## Project Overview
This is a **Phase 1 hackathon trading bot** that makes portfolio allocation decisions between "Asset A" and "Cash" based on technical indicators. The bot trades over 2,520 epochs (approximately 10 years of daily data).

## What Was Improved

### 1. Enhanced Trading Strategy (`bot_trade.py`)
**Before:**
- Simple buy-and-hold with minimal adjustments
- Only 2-3 allocation levels (0.3, 0.8, 0.95, 1.0)
- Conservative thresholds that never triggered
- No position tracking

**After:**
- Score-based multi-indicator system combining:
  - EMA crossovers (8/21/50/100 periods)
  - RSI momentum (14 period)
  - Price momentum (10 period)
  - Support/resistance levels
  - Volatility filtering
- Granular allocation levels (0.2, 0.4, 0.6, 0.8, 1.0)
- Cooldown period (5 epochs) to prevent overtrading
- Smooth transitions (max 0.2 change per epoch)
- Complete position change tracking with context

### 2. Analytics & Reporting (`main.py`)
**New Features:**
- Comprehensive performance metrics:
  - Total & annualized returns
  - Sharpe ratio
  - Maximum drawdown
  - Win rate
  - Volatility
  - **Alpha** (excess return vs buy-and-hold)
- Transaction tracking with full context (price, RSI, momentum, score)
- Structured exports:
  - `summary_metrics_[timestamp].json` - All metrics
  - `position_changes_[timestamp].csv` - Transaction log
  - `positions_full_[timestamp].csv` - Complete history
  - `trading_analysis_[timestamp].png` - 3-panel visualization

### 3. Visualization
**Three-panel chart showing:**
1. **Portfolio Value Comparison**: Strategy vs Buy & Hold
2. **Asset Allocation Over Time**: Visual of position changes
3. **Drawdown Over Time**: Risk exposure tracking

## Current Performance Results

### Test Data: `asset_a_test.csv` (2,520 epochs)

```
📊 Returns:
  Total Return:         -26.25%
  Annualized Return:     -3.00%
  Buy & Hold Return:      8.32%
  Alpha (Excess):       -34.57%

📈 Risk Metrics:
  Volatility (Ann.):     10.82%
  Sharpe Ratio:          -0.28
  Max Drawdown:         -35.64%
  Win Rate:              50.34%

💰 Portfolio Value:
  Final Value:          0.7375
  Buy & Hold Final:     1.0832

🔄 Trading Activity:
  Position Changes:        480
  Total Epochs:           2520
  Allocation Changes:      440
```

## The Problem

### Strategy Underperforms Buy-and-Hold by 34.57%

**Root Cause Analysis:**

1. **Mean-Reverting Strategy in Trending Market**
   - The asset shows a clear upward trend (+8.32% over the period)
   - Strategy is designed to:
     - Reduce exposure when prices rise (overbought signals)
     - Increase exposure when prices fall (oversold signals)
   - This is the **opposite** of what works in trending markets

2. **Excessive Trading (440 position changes)**
   - Despite cooldown period (down from 1,191 trades originally)
   - Still too reactive to short-term signals
   - Transaction costs would make this even worse in reality

3. **Risk Management Too Aggressive**
   - Trailing stop (10% drawdown) triggers too often
   - Volatility filters reduce exposure during normal volatility
   - Score thresholds cause frequent allocation changes

### Visual Evidence
From the charts:
- **Portfolio Value**: Blue line (strategy) consistently underperforms gray line (buy-and-hold) after epoch 500
- **Allocation**: Constant oscillation between 20%-100% allocation
- **Drawdown**: Reaches -35.64%, never recovers

## What We Need

### Goal
Create a strategy that **beats or matches buy-and-hold** while managing downside risk.

### Proposed Solutions

**Option 1: Trend-Following Strategy**
- Stay fully invested during confirmed uptrends
- Only reduce exposure on trend reversals
- Use longer-term moving averages (50/200 EMA)
- Simpler logic, fewer trades

**Option 2: Market Regime Detection**
- Detect if market is trending or ranging
- Use trend-following in uptrends
- Use mean-reversion in ranges
- Adaptive approach

**Option 3: Momentum-Based with Trend Filter**
- Strong bullish bias (start at 0.8-1.0 allocation)
- Only reduce on multiple strong bearish signals
- Require confluence of indicators before selling
- Much higher thresholds for position changes

**Option 4: Risk-Parity Approach**
- Target constant volatility rather than constant allocation
- Increase exposure in low volatility periods
- Reduce in high volatility periods
- Stay mostly invested but manage risk

## Technical Details

### File Structure
```
ressources/phase1/
├── main.py                    # Main execution + analytics
├── bot_trade.py              # Trading strategy logic
├── data/
│   ├── asset_a_test.csv      # Price data (2,520 epochs)
│   └── [generated files]     # Metrics, logs, charts
└── scoring/
    └── scoring.py            # Scoring functions (unchanged)
```

### Key Functions

**bot_trade.py:**
- `make_decision(epoch, price)` → Returns allocation dict
- `calculate_ema()`, `calculate_rsi()`, `calculate_momentum()`
- `detect_support_resistance()`
- `get_positions_history()` → Returns trade log

**main.py:**
- `calculate_performance_metrics()` → Comprehensive stats
- `export_analytics()` → Generate JSON/CSV exports
- `create_enhanced_visualizations()` → 3-panel chart
- `print_summary_report()` → Console output

### Current Strategy Logic (Simplified)
```python
score = 2.0  # Bullish bias

# Add points for bullish signals
if short_ema > medium_ema > long_ema: score += 3
if rsi < 30: score += 1
if momentum > 0.01: score += 1

# Subtract points for bearish signals
if short_ema < medium_ema: score -= 2
if rsi > 70: score -= 1
if volatility > 0.05: score -= 2

# Convert score to allocation
if score >= 5: allocation = 1.0
elif score >= 2: allocation = 0.8
elif score >= -1: allocation = 0.6
elif score >= -4: allocation = 0.4
else: allocation = 0.2
```

## Questions to Address

1. **Should we prioritize return or risk-adjusted return?**
   - Current focus: Beat buy-and-hold total return
   - Alternative: Achieve similar return with lower drawdown

2. **What's acceptable for trading frequency?**
   - Current: 440 changes over 2,520 epochs (17.5% of days)
   - Target: Fewer trades while maintaining performance?

3. **Is this a one-time optimization or should it generalize?**
   - Optimize specifically for `asset_a_test.csv`?
   - Or create robust strategy for unknown future data?

4. **Are there constraints we don't know about?**
   - Transaction costs?
   - Minimum holding periods?
   - Maximum drawdown limits?

## Files Generated (Latest Run)

```
data/summary_metrics_20251205_195725.json
data/position_changes_20251205_195725.csv
data/positions_full_20251205_195725.csv
data/trading_analysis_20251205_195726.png
```

All analytics infrastructure is working perfectly. We just need to fix the strategy logic to perform better in trending markets.
