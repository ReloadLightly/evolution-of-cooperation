#!/usr/bin/env python3
"""Load a saved evolved strategy and print its decisions round by round."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from eoc.game import Match
from eoc.genomes import MemoryOne

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--results', type=Path, default=ROOT / 'results/forgiveness_e1/champions.json')
parser.add_argument('--run', type=int, default=0)
parser.add_argument('--noise', type=float, default=.05)
parser.add_argument('--turns', type=int, default=20)
args = parser.parse_args()
runs = json.loads(args.results.read_text())
if not 0 <= args.run < len(runs):
    parser.error(f'--run must be between 0 and {len(runs)-1}')
record = runs[args.run]
strategy = MemoryOne(*record['champion'])
print(f"Training: seed={record['seed']}, noise={record['train_noise']}, ALLC={record['include_allc']}")
if 'field_reps' in record:
    print(f"Training matches per opponent: {record['field_reps']}")
print('Evolved probabilities:')
for state, value in zip(('first move', 'after CC', 'after CD', 'after DC', 'after DD'), strategy.vector):
    print(f'  {state:12s}: cooperate with probability {value:.4f}')
match = Match(strategy, MemoryOne.tit_for_tat(), turns=args.turns, noise=args.noise, seed=1_000_000_000_000)
score, other_score = match.play()
print(f'\nAgainst TFT, evaluation noise={args.noise}; C=cooperate, D=defect')
previous = 'start'
for turn, (mine, theirs) in enumerate(match.history, 1):
    index = {'start': 0, 'CC': 1, 'CD': 2, 'DC': 3, 'DD': 4}[previous]
    print(f'round {turn:2d} | previous={previous:5s} | P(C)={strategy.vector[index]:.4f} | realized: me={mine} TFT={theirs}')
    previous = str(mine) + str(theirs)
print(f'Payoffs: evolved={score:.1f}, TFT={other_score:.1f}')
print('P(C) is the intended cooperation probability; action errors may flip the sampled move.')
