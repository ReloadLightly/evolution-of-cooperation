#!/usr/bin/env python3
"""Export E2's paired results as one reusable manuscript figure."""
import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--results', type=Path, default=ROOT / 'results/forgiveness_e2')
parser.add_argument('--output', type=Path, default=ROOT / 'figures')
args = parser.parse_args()
with (args.results / 'paired_differences.csv').open() as f:
    rows = list(csv.DictReader(f))
conditions = [(0., False), (0., True), (.05, False), (.05, True)]
labels = ['Clean\nALLC absent', 'Clean\nALLC present', '5% errors\nALLC absent', '5% errors\nALLC present']
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.spines.top': False,
                     'axes.spines.right': False, 'axes.edgecolor': '#777777',
                     'svg.hashsalt': 'eoc-e2-paired', 'pdf.fonttype': 42})
fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.3))
for ax, metric, title, ylabel in zip(axes,
        ['delta_heldout_payoff', 'delta_pCD'],
        ['A  Held-out payoff', 'B  Conditional forgiveness'],
        ['Payoff/turn difference (five − one)', 'pCD difference (five − one)']):
    ax.axhline(0, color='#444444', linewidth=.8, zorder=1)
    for index, (noise, include) in enumerate(conditions):
        group = sorted((r for r in rows if float(r['train_noise']) == noise
                        and (r['include_allc'] == 'True') == include), key=lambda r: int(r['seed']))
        values = [float(r[metric]) for r in group]
        positions = [index + (j - (len(group)-1)/2)*.065 for j in range(len(group))]
        ax.scatter(positions, values, color='#1f6972', s=34, alpha=.85, zorder=3)
        ax.plot([index-.24, index+.24], [mean(values)]*2, color='#202020', linewidth=2.3, zorder=4)
    ax.set_xticks(range(4), labels)
    ax.set_ylabel(ylabel)
    ax.set_title(title, loc='left', fontweight='bold', pad=14)
    ax.grid(axis='y', alpha=.15)
    ax.set_axisbelow(True)
    ax.tick_params(axis='x', length=0, pad=8)
fig.suptitle('Does more training sampling change evolved strategies?', x=.07, ha='left', fontsize=14, fontweight='bold')
fig.text(.07, .025, 'Dots: paired evolution seeds (n = 5 per condition). Bars: means. Five-match training uses 5× the match budget.', fontsize=9)
fig.subplots_adjust(left=.075, right=.98, bottom=.24, top=.78, wspace=.31)
args.output.mkdir(parents=True, exist_ok=True)
for extension in ('svg', 'pdf', 'png'):
    metadata = {'Date': None} if extension == 'svg' else ({'CreationDate': None, 'ModDate': None} if extension == 'pdf' else {})
    fig.savefig(args.output / f'e2_paired_effects.{extension}', dpi=180, metadata=metadata)
plt.close(fig)
print(f'Wrote SVG, PDF, and PNG to {args.output}')
