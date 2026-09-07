#!/usr/bin/env python3
"""E3: fixed-field versus mixed field/peer selection. Standard library only."""
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

PEER_START = 100_000_000_000
EVAL_START = 3_000_000_000_000
REGIMES = {'fixed': 1.0, 'mixed': 0.5}
PROBABILITIES = ('p0', 'pCC', 'pCD', 'pDC', 'pDD')
OUTCOMES = ('population_cooperation', 'population_mutual_cooperation',
            'population_payoff', 'champion_field_payoff', 'champion_self_cooperation',
            'champion_allc_payoff', 'champion_allc_cooperation', *PROBABILITIES)


def heldout_seeds(seed, domain, index, reps):
    """Fixed slots keep short replays nested in the full evaluation schedule."""
    return [EVAL_START + seed * 100_000_000 + domain * 10_000_000
            + 2 * (index * 100 + r) for r in range(reps)]


def evaluate_field(strategy, seed, turns, reps):
    rows = []
    for index, opponent in enumerate(controlled_forgiveness_field(False)):
        rows.extend(evaluate(strategy, [opponent], noise=.05, turns=turns,
                             seeds=heldout_seeds(seed, 1, index, reps)))
    return rows


def evaluate_champion(champion, seed, turns, reps):
    rows = [{'evaluation_set': 'common_field', **r}
            for r in evaluate_field(champion, seed, turns, reps)]
    for domain, label, opponent in [(2, 'self', champion.clone()),
                                     (3, 'ALLC', MemoryOne.always_cooperate())]:
        rows.extend({'evaluation_set': label, **r}
                    for r in evaluate(champion, [opponent], noise=.05, turns=turns,
                                      seeds=heldout_seeds(seed, domain, 0, reps)))
    return rows


def evaluate_population(vectors, seed, turns, reps):
    """Off-diagonal members in final fitness order; retain both player outcomes."""
    rows = []
    for i, vector in enumerate(vectors):
        for j in range(i + 1, len(vectors)):
            pair_index = j * (j - 1) // 2 + i
            measurements = evaluate(MemoryOne(*vector), [MemoryOne(*vectors[j])],
                                    noise=.05, turns=turns,
                                    seeds=heldout_seeds(seed, 0, pair_index, reps))
            rows.extend({'i': i, 'j': j, **r,
                         'mean_cooperation': (r['cooperation'] + r['opponent_cooperation']) / 2,
                         'mean_payoff': (r['score_per_turn'] + r['opponent_score_per_turn']) / 2}
                        for r in measurements)
    return rows


def train_run(seed, regime, *, population=20, generations=35, turns=80, log=print):
    ga = MemoryOneGA(field=controlled_forgiveness_field(False), seed=seed,
                     population_size=population, turns=turns, noise=.05,
                     mutation_sigma=.06, crossover_rate=.7, elite=2, tournament_k=3,
                     field_weight=REGIMES[regime], field_reps=5, peer_reps=5,
                     peer_seed=PEER_START + seed * 1_000_000)
    start = time.perf_counter()
    result = ga.run(generations=generations, seed_tft=False, log=log)
    elapsed = time.perf_counter() - start
    expected_field = population * 7 * 5 * generations
    expected_peer = population * (population + 1) // 2 * 5 * generations if regime == 'mixed' else 0
    assert ga.field_matches == expected_field
    assert ga.peer_matches == expected_peer
    run = {'seed': seed, 'regime': regime, 'train_noise': .05, 'include_allc': False,
           'field_weight': REGIMES[regime], 'field_reps': 5, 'peer_reps': 5,
           'champion': result.champion.vector,
           'history': [asdict(r) for r in result.history],
           'field_matches': ga.field_matches, 'peer_matches': ga.peer_matches,
           'training_matches': ga.field_matches + ga.peer_matches,
           'training_seconds': elapsed}
    return run, [ind.genome.vector for ind in result.population]


def run_metrics(run, population_rows, champion_rows, evaluation_seconds):
    field = [r for r in champion_rows if r['evaluation_set'] == 'common_field']
    self_rows = [r for r in champion_rows if r['evaluation_set'] == 'self']
    allc = [r for r in champion_rows if r['evaluation_set'] == 'ALLC']
    return {**{k: run[k] for k in ('seed', 'regime', 'field_weight', 'field_matches',
                                   'peer_matches', 'training_matches', 'training_seconds')},
            'evaluation_seconds': evaluation_seconds,
            'population_cooperation': mean(r['mean_cooperation'] for r in population_rows),
            'population_mutual_cooperation': mean(r['mutual_cooperation'] for r in population_rows),
            'population_payoff': mean(r['mean_payoff'] for r in population_rows),
            'champion_field_payoff': mean(r['score_per_turn'] for r in field),
            'champion_self_cooperation': mean(r['cooperation'] for r in self_rows),
            'champion_allc_payoff': mean(r['score_per_turn'] for r in allc),
            'champion_allc_cooperation': mean(r['cooperation'] for r in allc),
            **dict(zip(PROBABILITIES, run['champion']))}


def paired_differences(metrics):
    lookup = {(r['seed'], r['regime']): r for r in metrics}
    pairs = []
    for seed in sorted({r['seed'] for r in metrics}):
        if all((seed, regime) in lookup for regime in REGIMES):
            a, b = lookup[seed, 'fixed'], lookup[seed, 'mixed']
            pairs.append({'seed': seed, **{f'delta_{key}': b[key] - a[key] for key in OUTCOMES}})
    return pairs


def summarize(metrics, pairs, baselines, output):
    lines = ['# E3: fixed-field versus mixed field/peer selection', '',
             'Exploratory results at 5% errors without ALLC in training. '
             'Population cooperation averages both players in off-diagonal matches only. '
             'Payoff is per turn; cooperation and probabilities use fractions in [0, 1].', '',
             '| Outcome | Fixed mean | Mixed mean |', '|---|---|---|']
    for key in OUTCOMES:
        values = []
        for regime in REGIMES:
            group = [r[key] for r in metrics if r['regime'] == regime]
            values.append(f'{mean(group):.6f}' if group else '—')
        lines.append(f"| {key} | {' | '.join(values)} |")
    lines += ['', '## Paired mixed-minus-fixed differences', '',
              'One replication per evolution seed. SD is sample SD across pairs, '
              'not across matches. All probabilities and differences retain full precision in CSV.', '']
    if pairs:
        lines += ['| Outcome | ' + ' | '.join(f"Seed {r['seed']}" for r in pairs) + ' | Mean | Sample SD |',
                  '|---|' + '---|' * (len(pairs) + 2)]
        for key in OUTCOMES:
            values = [r[f'delta_{key}'] for r in pairs]
            sd = f'{stdev(values):.6f}' if len(values) > 1 else 'undefined (one pair)'
            lines.append(f"| {key} | " + ' | '.join(f'{v:+.6f}' for v in values)
                         + f' | {mean(values):+.6f} | {sd} |')
    else:
        lines.append('Single-regime replay: no paired comparison.')
    lines += ['', '## Common-field reference payoff', '',
              '| Strategy | Mean payoff/turn |', '|---|---|']
    for name in references():
        lines.append(f"| {name} | {mean(r['score_per_turn'] for r in baselines if r['strategy'] == name):.6f} |")
    manifest = json.loads((output / 'manifest.json').read_text())
    lines += ['', '## Measured cost', '',
              '| Regime | Training matches | Training rounds | Training seconds | Held-out seconds |',
              '|---|---|---|---|---|']
    for regime in REGIMES:
        group = [r for r in metrics if r['regime'] == regime]
        count = sum(r['training_matches'] for r in group)
        lines.append(f"| {regime} | {count:,} | {count * manifest['turns']:,} | "
                     f"{sum(r['training_seconds'] for r in group):.3f} | "
                     f"{sum(r['evaluation_seconds'] for r in group):.3f} |")
    ratio = 1 + (manifest['population'] + 1) / 14
    extra = manifest['population'] * (manifest['population'] + 1) // 2 * 5 * manifest['generations']
    lines += ['', f"Total runner wall time: {manifest['total_seconds']:.3f} seconds; "
              f"baseline evaluation: {manifest['baseline_seconds']:.3f} seconds. "
              'Per-run held-out time includes population and champion evaluation.', '',
              f'Mixed training uses {ratio:g}× the matches (+{100*(ratio-1):g}%) at fixed population/generations. '
              f'This is {extra:,} extra matches per run at these settings. '
              'Raw mixed and fixed training fitness are different objectives.', '',
              'Clone matches are included in mixed training but excluded from the primary outcome. '
              'This estimates the complete peer-selection regime, not a distinct-peer-only effect. '
              f"{len(manifest['seeds'])} evolution seeds, fixed position seeds and one environment limit generalization.", '',
              'See [protocol](../../docs/forgiveness_e3.md) and [manuscript](../../README.md).', '']
    (output / 'summary.md').write_text('\n'.join(lines))


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seeds', type=int, nargs='+', default=list(range(5)))
    parser.add_argument('--regimes', choices=REGIMES, nargs='+', default=list(REGIMES))
    parser.add_argument('--generations', type=int, default=35)
    parser.add_argument('--population', type=int, default=20)
    parser.add_argument('--turns', type=int, default=80)
    parser.add_argument('--eval-reps', type=int, default=20)
    parser.add_argument('--output', type=Path, default=ROOT / 'artifacts/forgiveness_e3_live')
    args = parser.parse_args()
    if args.generations < 1 or not 2 <= args.population <= 100 or args.turns < 1 or not 1 <= args.eval_reps <= 100:
        parser.error('positive generations/turns, population 2..100, eval-reps 1..100')
    if len(set(args.seeds)) != len(args.seeds) or any(not 0 <= s < 1000 for s in args.seeds):
        parser.error('seeds must be unique integers in [0, 1000)')
    if len(set(args.regimes)) != len(args.regimes):
        parser.error('regimes must be unique')
    output = args.output.resolve()
    if output.exists() and any(output.iterdir()):
        parser.error(f'output is not empty: {output}; choose a new directory')
    output.mkdir(parents=True, exist_ok=True)
    files = sorted((ROOT / 'src/eoc').rglob('*.py')) + [Path(__file__).resolve(),
            ROOT / 'experiments/run_forgiveness.py', ROOT / 'docs/forgiveness_e3.md']
    manifest = {'experiment': 'E3', 'python': platform.python_version(), 'platform': platform.platform(),
                'base_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
                **{k: v for k, v in vars(args).items() if k != 'output'},
                'train_noise': .05, 'eval_noise': .05, 'include_allc': False,
                'field': [p.name for p in controlled_forgiveness_field(False)],
                'payoffs': {'T': 5, 'R': 3, 'P': 1, 'S': 0},
                'mutation_sigma': .06, 'elite': 2, 'crossover_rate': .7, 'tournament_k': 3,
                'field_reps': 5, 'peer_reps': 5, 'field_weights': REGIMES, 'seed_tft': False,
                'field_seed': 's + i*1000003 + o*97 + r (unchanged from E1/E2)',
                'peer_seed': '100000000000 + s*1000000 + 2*((j*(j+1)//2+i)*5+r), i<=j',
                'evaluation_seed': '3000000000000 + s*100000000 + d*10000000 + 2*(k*100+r)',
                'evaluation_domains': {'population': 0, 'common_field': 1, 'self': 2, 'ALLC': 3},
                'evaluation_index': 'population: j*(j-1)//2+i, i<j; field: opponent index; else 0',
                'diagonal': 'Only first player credited once per diagonal match; distinct pairs credit both.',
                'population_order': 'Final training fitness descending, duplicates retained.',
                'note': 'Source hashes identify executed working-tree code; base commit may precede edits.'}
    write_json(output / 'manifest.json', manifest)
    runs, populations, scores, population_scores, baselines, metrics = [], [], [], [], [], []
    start_all = time.perf_counter()
    baseline_seconds = 0.0
    with (output / 'run.log').open('w') as log_file:
        def log(message):
            print(message, flush=True)
            log_file.write(message + '\n')
            log_file.flush()
        for seed in args.seeds:
            log(f'\n=== seed={seed}: held-out reference strategies ===')
            start = time.perf_counter()
            for name, strategy in references().items():
                baselines.extend({'seed': seed, 'strategy': name, **r}
                                 for r in evaluate_field(strategy, seed, args.turns, args.eval_reps))
            baseline_seconds += time.perf_counter() - start
            for regime in args.regimes:
                log(f'\n=== seed={seed} regime={regime} field_weight={REGIMES[regime]} ===')
                run, vectors = train_run(seed, regime, population=args.population,
                                         generations=args.generations, turns=args.turns, log=log)
                tag = {'seed': seed, 'regime': regime}
                runs.append(run)
                populations.append({**tag, 'genomes': vectors})
                write_json(output / 'champions.json', runs)
                write_json(output / 'populations.json', populations)
                log('CHAMPION ' + format_vector(MemoryOne(*run['champion'])))
                log(f"Training: {run['training_matches']:,} matches in {run['training_seconds']:.3f}s; evaluating held-out matches...")
                start = time.perf_counter()
                pop_rows = evaluate_population(vectors, seed, args.turns, args.eval_reps)
                champ_rows = evaluate_champion(MemoryOne(*run['champion']), seed, args.turns, args.eval_reps)
                elapsed = time.perf_counter() - start
                population_scores.extend({**tag, **r} for r in pop_rows)
                scores.extend({**tag, **r} for r in champ_rows)
                metric = run_metrics(run, pop_rows, champ_rows, elapsed)
                metrics.append(metric)
                log(f"Held-out: {len(pop_rows):,} population + {len(champ_rows)} champion matches; "
                    f"population cooperation={metric['population_cooperation']:.4%}, "
                    f"field payoff={metric['champion_field_payoff']:.6f}, time={elapsed:.3f}s")
    pairs = paired_differences(metrics)
    for name, rows in [('evaluation.csv', scores), ('population_evaluation.csv', population_scores),
                       ('baselines.csv', baselines), ('run_metrics.csv', metrics),
                       ('paired_differences.csv', pairs)]:
        if rows:
            write_csv(output / name, rows)
    manifest.update(total_seconds=time.perf_counter() - start_all, baseline_seconds=baseline_seconds,
                    records={'runs': len(runs), 'population_matches': len(population_scores),
                             'champion_matches': len(scores), 'baseline_matches': len(baselines)})
    write_json(output / 'manifest.json', manifest)
    summarize(metrics, pairs, baselines, output)
    print((output / 'summary.md').read_text())
    print(f'Saved E3 to {output}', flush=True)


if __name__ == '__main__':
    main()
