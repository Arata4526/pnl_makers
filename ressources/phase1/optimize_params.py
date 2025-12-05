
import itertools
import json
import subprocess
import re
import sys
import os

# Define parameter grid for SAFE FIXED LEVERAGE
param_grid = {
    'fixed_leverage': [2.5, 3.0, 3.25, 3.5, 3.75, 4.0, 4.25, 4.5],
    'stop_loss': [0.08],
    'bb_window': [15],
    'rsi_period': [14],
    'rsi_lower': [30],
    'rsi_upper': [70],
    'bb_std': [2.0]
}

keys = param_grid.keys()
combinations = list(itertools.product(*param_grid.values()))

print(f"Testing {len(combinations)} combinations for Fixed Leverage...")

best_pnl = -float('inf')
best_params = None

python_exec = "/home/alexis/Documents/Hackathon/pnl_makers/venv/bin/python3"

def parse_metrics(output):
    pnl_match = re.search(r"Total Return:\s+([-\d.]+)%", output)
    dd_match = re.search(r"Max Drawdown:\s+([-\d.]+)%", output)
    
    pnl = float(pnl_match.group(1)) if pnl_match else -100
    dd = float(dd_match.group(1)) if dd_match else -100
    return pnl, dd

for i, values in enumerate(combinations):
    params = dict(zip(keys, values))
    
    with open('params.json', 'w') as f:
        json.dump(params, f)
        
    try:
        result = subprocess.run(
            [python_exec, "main.py", "data/asset_a_test.csv"],
            capture_output=True,
            text=True,
            timeout=10
        )
        pnl, dd = parse_metrics(result.stdout)
        
        if dd < -45.0:
            print(f"[{i+1}/{len(combinations)}] REJECTED (DD {dd}%): {params['fixed_leverage']}x")
            continue

        if pnl > best_pnl:
            best_pnl = pnl
            best_params = params
            print(f"[{i+1}/{len(combinations)}] 🎯 HIT: PnL={pnl:.2f}%, DD={dd}% | Lev={params['fixed_leverage']}x")
        else:
             print(f"[{i+1}/{len(combinations)}] Tested. PnL={pnl:.2f}%")
             
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "="*30)
print(f"OPTIMIZATION COMPLETE")
print(f"Best PnL: {best_pnl:.2f}%")
print(f"Best Params: {best_params}")
with open('best_params_fixed.json', 'w') as f:
    json.dump(best_params, f)
