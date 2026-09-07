#!/usr/bin/env python3
"""One restrained figure: E3 paired cooperation and fixed-field payoff changes."""
import argparse
import csv
from pathlib import Path
from statistics import mean

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results', type=Path, default=ROOT / 'results/forgiveness_e3')
    parser.add_argument('--output', type=Path, default=ROOT / 'figures')
    args = parser.parse_args()
    with (args.results / 'paired_differences.csv').open() as handle:
        rows = sorted(csv.DictReader(handle), key=lambda r: int(r['seed']))
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'svg.hashsalt': 'eoc-e3-paired', 'pdf.fonttype': 42})
    fig, axes = plt.subplots(1, 2, figsize=(9, 4))
    for ax, key, scale, title, label in zip(axes,
            ['delta_population_cooperation', 'delta_champion_field_payoff'], [100, 1],
            ['A  Cooperation between population members', 'B  Champion fixed-field payoff'],
            ['Cooperation difference (percentage points)', 'Payoff/turn difference']):
        values = [float(r[key]) * scale for r in rows]
        seeds = [int(r['seed']) for r in rows]
        ax.axhline(0, color='#777777', linewidth=.8)
        ax.axhline(mean(values), color='#1f6972', linewidth=1.2, linestyle='--', label='Paired mean')
        ax.scatter(seeds, values, color='#1f6972', s=42, zorder=3)
        ax.set_xticks(seeds)
        ax.set_xlabel('Evolution seed')
        ax.set_ylabel(label)
        ax.set_title(title, loc='left', fontsize=10, fontweight='bold')
        ax.grid(axis='y', alpha=.15)
        ax.set_axisbelow(True)
        ax.legend(frameon=False, fontsize=9)
    fig.suptitle('E3: mixed selection minus fixed-field selection', x=.085, ha='left', fontsize=13)
    fig.text(.085, .025, 'Five paired evolution seeds · 5% action errors · ALLC absent · Mixed training costs 2.5× the matches', fontsize=8.5)
    fig.subplots_adjust(left=.085, right=.98, bottom=.20, top=.79, wspace=.38)
    args.output.mkdir(parents=True, exist_ok=True)
    for extension in ('svg', 'pdf', 'png'):
        metadata = {'Date': None} if extension == 'svg' else ({'CreationDate': None, 'ModDate': None} if extension == 'pdf' else {})
        fig.savefig(args.output / f'e3_paired_effects.{extension}', dpi=180, metadata=metadata)
    plt.close(fig)
    print(f'Wrote E3 SVG, PDF, PNG to {args.output}')


if __name__ == '__main__':
    main()
