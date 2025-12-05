#! /usr/bin/env python3

import csv
import json
import os
import sys

# Empêcher la création de __pycache__
sys.dont_write_bytecode = True


from scoring.scoring import get_local_score, show_result
import pandas as pd
from bot_trade import make_decision as decision_generator
import matplotlib.pyplot as plt
from datetime import datetime


def find_csv_file(path_csv: str) -> pd.DataFrame:
    if not os.path.exists(path_csv):
        raise FileNotFoundError(f"Le fichier CSV {path_csv} n'existe pas")
    prices_list = [
        pd.read_csv(path_csv, index_col=0)
    ]
    prices = pd.concat(prices_list, axis=1)
    prices["Cash"] = 1
    return prices

def validate_decision(decision: dict) -> bool:
    expected_keys = {'Asset A', 'Cash'}
    if set(decision.keys()) != expected_keys:
        print(f"ERREUR: Les clés attendues sont {expected_keys}, mais reçu {set(decision.keys())}")
        return False

    for key, value in decision.items():
        if not isinstance(value, (int, float)):
            print(f"ERREUR: La valeur pour '{key}' n'est pas numérique: {value}")
            return False

    # Allow leverage: Asset A can be > 1.0, Cash can be negative
    # The sum must still equal 1.0 (Asset A = 1.5, Cash = -0.5 means 1.5x leverage)
    total = sum(decision.values())
    if abs(total - 1.0) > 0.00001:
        print(f"ERREUR: La somme des allocations doit être égale à 1, mais vaut {total}")
        return False

    # Check leverage limits (max 100x leverage = Asset A <= 100.0)
    if decision['Asset A'] < 0 or decision['Asset A'] > 100.0:
        print(f"ERREUR: Asset A doit être entre 0 et 100.0 (max 100x leverage), reçu: {decision['Asset A']}")
        return False

    return True


def calculate_performance_metrics(positions: pd.DataFrame, prices: pd.DataFrame, local_score: dict) -> dict:
    """Calculate comprehensive performance metrics."""

    # Get PNL from local_score
    pnl_dict = local_score.get('pnl', {})

    if len(pnl_dict) == 0:
        print("Warning: No PNL data available")
        return {}

    # Convert to Series
    pv = pd.Series(pnl_dict)

    # Calculate returns
    returns = pv.pct_change().dropna()

    # Calculate metrics
    total_return = (pv.iloc[-1] - pv.iloc[0]) / pv.iloc[0] if pv.iloc[0] != 0 else 0

    # Annualized metrics (assuming ~252 trading days per year)
    periods_per_year = 252
    n_periods = len(pv)
    years = n_periods / periods_per_year

    annualized_return = ((1 + total_return) ** (1 / years) - 1) if years > 0 else 0

    # Volatility
    volatility = returns.std()
    annualized_volatility = volatility * (periods_per_year ** 0.5)

    # Sharpe Ratio (assuming 0 risk-free rate)
    sharpe_ratio = (annualized_return / annualized_volatility) if annualized_volatility > 0 else 0

    # Maximum Drawdown
    cummax = pv.cummax()
    drawdown = (pv - cummax) / cummax
    max_drawdown = drawdown.min()

    # Win rate (percentage of positive returns)
    win_rate = (returns > 0).sum() / len(returns) if len(returns) > 0 else 0

    # Count position changes
    position_changes = (positions['Asset A'].diff().abs() > 0.01).sum()

    # Buy and hold comparison
    buy_hold_return = (prices['Asset A'].iloc[-1] - prices['Asset A'].iloc[0]) / prices['Asset A'].iloc[0]
    buy_hold_value = [prices['Asset A'].iloc[i] for i in range(len(prices))]

    metrics = {
        'total_return': total_return,
        'annualized_return': annualized_return,
        'volatility': annualized_volatility,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_drawdown,
        'win_rate': win_rate,
        'position_changes': position_changes,
        'final_value': pv.iloc[-1],
        'buy_hold_return': buy_hold_return,
        'buy_hold_final': buy_hold_value[-1] if buy_hold_value else 0,
        'alpha': total_return - buy_hold_return,  # Excess return vs buy-and-hold
        'total_epochs': n_periods
    }

    return metrics


def export_analytics(positions: pd.DataFrame, metrics: dict, positions_history: list, output_dir: str = '.'):
    """Export comprehensive analytics to files."""

    import numpy as np

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # 1. Export summary metrics to JSON
    summary_file = os.path.join(output_dir, f'summary_metrics_{timestamp}.json')
    with open(summary_file, 'w') as f:
        # Convert numpy types to Python types for JSON serialization
        metrics_clean = {}
        for k, v in metrics.items():
            if isinstance(v, (np.integer, np.int64, np.int32)):
                metrics_clean[k] = int(v)
            elif isinstance(v, (np.floating, np.float64, np.float32)):
                metrics_clean[k] = float(v)
            elif isinstance(v, (int, float)):
                metrics_clean[k] = v
            else:
                metrics_clean[k] = str(v)
        json.dump(metrics_clean, f, indent=2)
    print(f"\n✓ Summary metrics saved to: {summary_file}")

    # 2. Export position changes to CSV
    if positions_history:
        changes_file = os.path.join(output_dir, f'position_changes_{timestamp}.csv')
        changes_df = pd.DataFrame(positions_history)
        changes_df.to_csv(changes_file, index=False)
        print(f"✓ Position changes saved to: {changes_file}")

    # 3. Export full positions to CSV (compressed)
    positions_file = os.path.join(output_dir, f'positions_full_{timestamp}.csv')
    positions.to_csv(positions_file)
    print(f"✓ Full positions saved to: {positions_file}")

    return summary_file


def print_summary_report(metrics: dict, positions_history: list):
    """Print a formatted summary report to console."""

    if not metrics:
        print("\n⚠ Warning: Could not calculate performance metrics")
        return

    print("\n" + "="*60)
    print("TRADING PERFORMANCE SUMMARY")
    print("="*60)

    print(f"\n📊 Returns:")
    print(f"  Total Return:       {metrics['total_return']*100:>8.2f}%")
    print(f"  Annualized Return:  {metrics['annualized_return']*100:>8.2f}%")
    print(f"  Buy & Hold Return:  {metrics['buy_hold_return']*100:>8.2f}%")
    print(f"  Alpha (Excess):     {metrics['alpha']*100:>8.2f}%")

    print(f"\n📈 Risk Metrics:")
    print(f"  Volatility (Ann.):  {metrics['volatility']*100:>8.2f}%")
    print(f"  Sharpe Ratio:       {metrics['sharpe_ratio']:>8.2f}")
    print(f"  Max Drawdown:       {metrics['max_drawdown']*100:>8.2f}%")
    print(f"  Win Rate:           {metrics['win_rate']*100:>8.2f}%")

    print(f"\n💰 Portfolio Value:")
    print(f"  Final Value:        {metrics['final_value']:>8.4f}")
    print(f"  Buy & Hold Final:   {metrics['buy_hold_final']:>8.4f}")

    print(f"\n🔄 Trading Activity:")
    print(f"  Position Changes:   {metrics['position_changes']:>8d}")
    print(f"  Total Epochs:       {metrics['total_epochs']:>8d}")
    print(f"  Allocation Changes: {len(positions_history):>8d}")

    if positions_history:
        print(f"\n📝 Recent Position Changes (last 5):")
        for change in positions_history[-5:]:
            print(f"  Epoch {change['epoch']:4d}: {change['allocation']:.2f} @ {change['price']:.4f}")

    print("\n" + "="*60)

def main():
    output = []

    if (len(sys.argv) > 1):
        path_csv = sys.argv[1]
        prices = find_csv_file(path_csv=path_csv)
    else:
        raise ValueError("No path to the csv file provided, ./main.py <path_to_csv>")

    print(f"Running trading simulation with {len(prices)} epochs...")

    # Run trading simulation and track position changes
    positions_history = []
    last_allocation = None

    for index, row in prices.iterrows():
        decision = decision_generator(int(index), float(row['Asset A']))
        if not validate_decision(decision):
            raise ValueError(f"Décision invalide: {decision}")
        decision['epoch'] = int(index)
        output.append(decision)

        # Track position changes
        current_allocation = decision['Asset A']
        if last_allocation is not None and current_allocation != last_allocation:
            positions_history.append({
                'epoch': int(index),
                'price': float(row['Asset A']),
                'allocation': current_allocation,
                'change': current_allocation - last_allocation
            })
        last_allocation = current_allocation

    positions = pd.DataFrame(output).set_index("epoch")
    local_score = get_local_score(prices=prices, positions=positions)

    # Calculate performance metrics
    metrics = calculate_performance_metrics(positions, prices, local_score)

    # Print summary report
    print_summary_report(metrics, positions_history)

    # Export analytics
    output_dir = os.path.dirname(path_csv) or '.'
    export_analytics(positions, metrics, positions_history, output_dir)

    # Show graph if requested
    if len(sys.argv) > 2 and sys.argv[2] == "--show-graph":
        show_result(local_score, is_show_graph=True)
        create_enhanced_visualizations(positions, prices, local_score, metrics, positions_history, output_dir)
    else:
        show_result(local_score, is_show_graph=False)
        print("\033[91m\nPour afficher les graphiques, utilisez: ./main.py <path_to_csv> --show-graph\033[0m")


def create_enhanced_visualizations(positions: pd.DataFrame, prices: pd.DataFrame,
                                   local_score: dict, metrics: dict,
                                   positions_history: list, output_dir: str):
    """Create enhanced visualization charts."""

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Create a figure with multiple subplots
    fig, axes = plt.subplots(3, 1, figsize=(14, 12))

    # 1. Portfolio Value vs Buy & Hold
    pnl_dict = local_score.get('pnl', {})
    portfolio_value = list(pd.Series(pnl_dict).values)
    epochs = list(range(len(portfolio_value)))

    axes[0].plot(epochs, portfolio_value, label='Strategy Portfolio', linewidth=2, color='blue')

    # Buy and hold comparison
    buy_hold_values = [prices['Asset A'].iloc[i] for i in range(len(prices))]
    axes[0].plot(epochs, buy_hold_values, label='Buy & Hold', linewidth=2, color='gray', linestyle='--')

    axes[0].set_title('Portfolio Value Comparison', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Portfolio Value')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # 2. Asset Allocation Over Time
    axes[1].plot(positions.index, positions['Asset A'], label='Asset A Allocation', linewidth=2, color='green')
    axes[1].fill_between(positions.index, 0, positions['Asset A'], alpha=0.3, color='green')
    axes[1].set_title('Asset Allocation Over Time', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Allocation')
    axes[1].set_ylim(0, 1.1)
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    # Mark position changes
    if positions_history:
        change_epochs = [change['epoch'] for change in positions_history]
        change_allocations = [change['allocation'] for change in positions_history]
        axes[1].scatter(change_epochs, change_allocations, color='red', s=30, zorder=5,
                       label='Position Changes', alpha=0.6)

    # 3. Drawdown Chart
    portfolio_series = pd.Series(portfolio_value)
    cummax = portfolio_series.cummax()
    drawdown = (portfolio_series - cummax) / cummax * 100

    axes[2].fill_between(epochs, drawdown, 0, alpha=0.5, color='red', label='Drawdown')
    axes[2].plot(epochs, drawdown, color='darkred', linewidth=1)
    axes[2].set_title('Drawdown Over Time', fontsize=14, fontweight='bold')
    axes[2].set_xlabel('Epoch')
    axes[2].set_ylabel('Drawdown (%)')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()

    # Save the figure
    chart_file = os.path.join(output_dir, f'trading_analysis_{timestamp}.png')
    plt.savefig(chart_file, dpi=150, bbox_inches='tight')
    print(f"✓ Trading analysis chart saved to: {chart_file}")

    plt.show()


if __name__ == "__main__":
    main()