#!/usr/bin/env python3
"""E2: one vs five training matches, with fresh held-out evaluation."""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import platform
from statistics import mean, stdev
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'experiments'))
from eoc.evolve_m1 import MemoryOneGA, format_vector
from eoc.fields import controlled_forgiveness_field
from eoc.genomes import MemoryOne
from run_forgiveness import evaluate, references, write_csv


def evaluate_sets(strategy, seeds, turns):
    rows = []
    for noise in (0., .05):
        sets = {'common_field': controlled_forgiveness_field(False),
                'ALLC': [MemoryOne.always_cooperate()], 'self': [strategy.clone()]}
        for label, opponents in sets.items():
            rows.extend({'eval_noise': noise, 'evaluation_set': label, **row}
                        for row in evaluate(strategy, opponents, noise=noise, turns=turns, seeds=seeds))
    return rows


def run_metrics(run, evaluation, turns):
    matched = [r for r in evaluation if r['eval_noise'] == run['train_noise']]
    common = [r for r in matched if r['evaluation_set'] == 'common_field']
    field = common + [r for r in matched if run['include_allc'] and r['evaluation_set'] == 'ALLC']
    self_rows = [r for r in matched if r['evaluation_set'] == 'self']
    return {**{k: run[k] for k in ('seed', 'field_reps', 'train_noise', 'include_allc')},
            **dict(zip(('p0', 'pCC', 'pCD', 'pDC', 'pDD'), run['champion'])),
            'heldout_payoff': mean(r['score_per_turn'] for r in field),
            'common_payoff': mean(r['score_per_turn'] for r in common),
            'self_cooperation': mean(r['cooperation'] for r in self_rows),
            'training_payoff': run['history'][-1]['best_fitness'] / turns,
            'training_matches': run['training_matches'],
            'training_seconds': run['training_seconds']}


def paired_differences(metrics):
    pairs = []
    lookup = {(r['seed'], r['train_noise'], r['include_allc'], r['field_reps']): r for r in metrics}
    for seed, noise, include, reps in lookup:
        if reps != 1:
            continue
        a, b = lookup[seed, noise, include, 1], lookup[seed, noise, include, 5]
        pairs.append({'seed': seed, 'train_noise': noise, 'include_allc': include,
                      **{f'delta_{key}': b[key] - a[key]
                         for key in ('heldout_payoff', 'common_payoff', 'pCD', 'pCC', 'self_cooperation')}})
    return pairs


def summarize(metrics, pairs, baselines, output):
    lines = ['# E2: one versus five training matches', '',
             'All payoff/cooperation columns use evaluation noise matching training noise. '
             'Held-out payoff uses the corresponding training field (seven or eight opponents).', '',
             '| Noise | ALLC | Matches/opponent | pCD | Held-out payoff/turn | Self cooperation |',
             '|---|---|---|---|---|---|']
    for noise in (0., .05):
        for include in (False, True):
            for reps in (1, 5):
                group = [r for r in metrics if r['train_noise'] == noise and r['include_allc'] == include and r['field_reps'] == reps]
                lines.append(f"| {noise:.0%} | {'present' if include else 'absent'} | {reps} | "
                             f"{mean(r['pCD'] for r in group):.3f} | {mean(r['heldout_payoff'] for r in group):.3f} | "
                             f"{mean(r['self_cooperation'] for r in group):.1%} |")
    lines += ['', '## Paired five-minus-one differences', '',
              'Means and sample SD across evolution seeds. All individual differences are in paired_differences.csv.', '',
              '| Noise | ALLC | Payoff difference (SD) | Positive payoff pairs | pCD difference | Self-cooperation difference |',
              '|---|---|---|---|---|---|']
    for noise in (0., .05):
        for include in (False, True):
            group = [r for r in pairs if r['train_noise'] == noise and r['include_allc'] == include]
            d = [r['delta_heldout_payoff'] for r in group]
            sd = stdev(d) if len(d) > 1 else 0.
            lines.append(f"| {noise:.0%} | {'present' if include else 'absent'} | {mean(d):+.3f} ({sd:.3f}) | "
                         f"{sum(v > 0 for v in d)}/{len(d)} | {mean(r['delta_pCD'] for r in group):+.3f} | "
                         f"{100*mean(r['delta_self_cooperation'] for r in group):+.1f} pp |")
    lines += ['', '## Noise effect on pCD', '',
              'Within-seed pCD(noise=5%) minus pCD(noise=0%).', '',
              '| Matches/opponent | ALLC | Mean noise effect | Individual seed differences |',
              '|---|---|---|---|']
    lookup = {(r['seed'], r['train_noise'], r['include_allc'], r['field_reps']): r for r in metrics}
    seeds = sorted({r['seed'] for r in metrics})
    for reps in (1, 5):
        for include in (False, True):
            deltas = [lookup[s, .05, include, reps]['pCD'] - lookup[s, 0., include, reps]['pCD'] for s in seeds]
            lines.append(f"| {reps} | {'present' if include else 'absent'} | {mean(deltas):+.3f} | "
                         f"{', '.join(f'{v:+.3f}' for v in deltas)} |")
    lines += ['', '## Baselines on the common seven opponents', '',
              '| Strategy | Clean payoff/turn | Noisy payoff/turn |', '|---|---|---|']
    for name in references():
        values = [mean(r['score_per_turn'] for r in baselines if r['strategy'] == name
                       and r['eval_noise'] == noise and r['evaluation_set'] == 'common_field') for noise in (0., .05)]
        lines.append(f'| {name} | {values[0]:.3f} | {values[1]:.3f} |')
    lines += ['', '## Training cost', '', '| Matches/opponent | Training matches | Training rounds | Measured training seconds |',
              '|---|---|---|---|']
    for reps in (1, 5):
        group = [r for r in metrics if r['field_reps'] == reps]
        matches = sum(r['training_matches'] for r in group)
        manifest = json.loads((output / 'manifest.json').read_text())
        lines.append(f"| {reps} | {matches:,} | {matches * manifest['turns']:,} | {sum(r['training_seconds'] for r in group):.2f} |")
    lines += ['', 'Five-match training uses five times the match budget at fixed population/generations. '
              'This does not estimate superiority at equal compute. Five seeds support exploratory descriptions; '
              'matches within a seed are repeated measurements.', '',
              'See [design](../../docs/forgiveness_e2.md) and [README interpretation](../../README.md).', '']
    (output / 'summary.md').write_text('\n'.join(lines))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seeds', type=int, nargs='+', default=list(range(5)))
    parser.add_argument('--generations', type=int, default=35)
    parser.add_argument('--population', type=int, default=20)
    parser.add_argument('--turns', type=int, default=80)
    parser.add_argument('--eval-reps', type=int, default=20)
    parser.add_argument('--output', type=Path, default=ROOT / 'artifacts/forgiveness_e2_live')
    args = parser.parse_args()
    if args.generations < 1 or args.population < 2 or args.turns < 1 or args.eval_reps < 1:
        parser.error('positive generations, turns and eval-reps; population >= 2')
    if len(set(args.seeds)) != len(args.seeds) or any(s < 0 or s >= 1_000_000 for s in args.seeds):
        parser.error('seeds must be unique integers in [0, 1000000)')
    output = args.output.resolve()
    if output.exists() and any(output.iterdir()):
        parser.error(f'output is not empty: {output}; choose a new directory')
    output.mkdir(parents=True, exist_ok=True)
    files = sorted((ROOT / 'src/eoc').rglob('*.py')) + [Path(__file__).resolve(), ROOT / 'experiments/run_forgiveness.py', ROOT / 'docs/forgiveness_e2.md']
    manifest = {'experiment': 'E2', 'python': platform.python_version(),
                'base_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
                'seeds': args.seeds, 'generations': args.generations, 'population': args.population,
                'turns': args.turns, 'eval_reps': args.eval_reps, 'field_reps': [1, 5],
                'train_noise': [0., .05], 'include_allc': [False, True],
                'mutation_sigma': .06, 'elite': 2, 'crossover_rate': .7, 'tournament_k': 3,
                'field_weight': 1., 'seed_tft': False, 'evaluation_seed_start': 2_000_000_000_000,
                'note': 'Source hashes identify executed working-tree code; base_commit may precede these edits.'}
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    runs, scores, baselines, metrics = [], [], [], []
    with (output / 'run.log').open('w') as log_file:
        def log(message):
            print(message, flush=True)
            log_file.write(message + '\n')
            log_file.flush()
        for seed in args.seeds:
            eval_seeds = [2_000_000_000_000 + seed * args.eval_reps + r for r in range(args.eval_reps)]
            for name, strategy in references().items():
                baselines.extend({'seed': seed, 'strategy': name, **r} for r in evaluate_sets(strategy, eval_seeds, args.turns))
            for reps in (1, 5):
                for noise in (0., .05):
                    for include in (False, True):
                        tag = {'seed': seed, 'field_reps': reps, 'train_noise': noise, 'include_allc': include}
                        log(f'\n=== seed={seed} field_reps={reps} noise={noise:.0%} ALLC={include} ===')
                        field = controlled_forgiveness_field(include)
                        ga = MemoryOneGA(field=field, seed=seed, population_size=args.population,
                                         turns=args.turns, noise=noise, mutation_sigma=.06,
                                         elite=2, field_weight=1., field_reps=reps)
                        start = time.perf_counter()
                        result = ga.run(generations=args.generations, seed_tft=False, log=log)
                        elapsed = time.perf_counter() - start
                        run = {**tag, 'champion': result.champion.vector,
                               'history': [asdict(r) for r in result.history],
                               'training_matches': args.population * args.generations * len(field) * reps,
                               'training_seconds': elapsed}
                        runs.append(run)
                        (output / 'champions.json').write_text(json.dumps(runs, indent=2) + '\n')
                        log('CHAMPION ' + format_vector(result.champion))
                        evaluation = evaluate_sets(result.champion, eval_seeds, args.turns)
                        scores.extend({**tag, **r} for r in evaluation)
                        metrics.append(run_metrics(run, evaluation, args.turns))
                        log('Fresh held-out evaluation complete.')
    pairs = paired_differences(metrics)
    for name, rows in [('evaluation.csv', scores), ('baselines.csv', baselines),
                       ('run_metrics.csv', metrics), ('paired_differences.csv', pairs)]:
        write_csv(output / name, rows)
    summarize(metrics, pairs, baselines, output)
    print((output / 'summary.md').read_text())
    print(f'Saved {len(runs)} runs, {len(scores)} champion matches and {len(baselines)} baseline matches to {output}')


if __name__ == '__main__':
    main()
