#!/usr/bin/env python3
"""Verify saved full E3 data, compare E2, and exactly replay seed 0 mixed."""
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import platform
import time

from run_forgiveness_e3 import (ROOT, evaluate_champion, evaluate_field,
                               evaluate_population, heldout_seeds, paired_differences, references,
                               run_metrics, train_run, write_json)
from eoc.genomes import MemoryOne


def read_csv(path):
    with path.open() as handle:
        return list(csv.DictReader(handle))


def csv_form(rows):
    return [{k: str(v) for k, v in r.items()} for r in rows]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results', type=Path, default=ROOT / 'results/forgiveness_e3')
    args = parser.parse_args()
    output = args.results.resolve()
    manifest = json.loads((output / 'manifest.json').read_text())
    assert platform.python_version() == manifest['python'], 'Run with the manifest Python version for exact replay.'
    assert manifest['seeds'] == list(range(5))
    assert (manifest['population'], manifest['generations'], manifest['turns'], manifest['eval_reps']) == (20, 35, 80, 20)
    for path, digest in manifest['source_sha256'].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path
    runs = json.loads((output / 'champions.json').read_text())
    populations = json.loads((output / 'populations.json').read_text())
    champ_rows = read_csv(output / 'evaluation.csv')
    pop_rows = read_csv(output / 'population_evaluation.csv')
    baselines = read_csv(output / 'baselines.csv')
    metrics = read_csv(output / 'run_metrics.csv')
    pairs = read_csv(output / 'paired_differences.csv')
    assert len(runs) == len(populations) == len(metrics) == 10
    assert len(champ_rows) == 1800 and len(pop_rows) == 38000 and len(baselines) == 2800
    keys = {(s, regime) for s in range(5) for regime in ('fixed', 'mixed')}
    assert {(r['seed'], r['regime']) for r in runs} == keys
    assert {(r['seed'], r['regime']) for r in populations} == keys
    e2 = json.loads((ROOT / 'results/forgiveness_e2/champions.json').read_text())
    e2 = {r['seed']: r for r in e2 if r['field_reps'] == 5 and r['train_noise'] == .05 and not r['include_allc']}
    recomputed = []
    for run, population, metric in zip(runs, populations, metrics):
        seed, regime = run['seed'], run['regime']
        assert (population['seed'], population['regime']) == (seed, regime)
        assert (int(metric['seed']), metric['regime']) == (seed, regime)
        assert len(run['history']) == 35 and len(population['genomes']) == 20
        assert run['champion'] == population['genomes'][0]
        assert all(len(v) == 5 and all(0 <= p <= 1 for p in v) for v in population['genomes'])
        assert run['field_matches'] == 24500
        assert run['peer_matches'] == (36750 if regime == 'mixed' else 0)
        assert run['training_matches'] == (61250 if regime == 'mixed' else 24500)
        if regime == 'fixed':
            assert run['champion'] == e2[seed]['champion']
            assert run['history'] == e2[seed]['history']
        pop = [r for r in pop_rows if (int(r['seed']), r['regime']) == (seed, regime)]
        champ = [r for r in champ_rows if (int(r['seed']), r['regime']) == (seed, regime)]
        expected_pairs = {(str(i), str(j)): 20 for i in range(20) for j in range(i+1, 20)}
        assert Counter((r['i'], r['j']) for r in pop) == expected_pairs
        for row in pop:
            i, j = int(row['i']), int(row['j'])
            assert int(row['match_seed']) in heldout_seeds(seed, 0, j*(j-1)//2+i, 20)
            assert float(row['mean_cooperation']) == (float(row['cooperation']) + float(row['opponent_cooperation'])) / 2
            assert float(row['mean_payoff']) == (float(row['score_per_turn']) + float(row['opponent_score_per_turn'])) / 2
        assert len({r['match_seed'] for r in pop}) == 3800
        assert Counter(r['evaluation_set'] for r in champ) == {'common_field': 140, 'self': 20, 'ALLC': 20}
        numeric_pop = [{k: float(r[k]) for k in ('mean_cooperation', 'mutual_cooperation', 'mean_payoff')} for r in pop]
        numeric_champ = [{**r, 'score_per_turn': float(r['score_per_turn']), 'cooperation': float(r['cooperation'])} for r in champ]
        measured = run_metrics(run, numeric_pop, numeric_champ, float(metric['evaluation_seconds']))
        assert csv_form([measured])[0] == metric
        recomputed.append(measured)
    assert csv_form(paired_differences(recomputed)) == pairs
    print('PASS: source hashes, counts, all metrics/pairs, and five E2 champions + histories.', flush=True)

    start = time.perf_counter()
    with (output / 'replay.log').open('w') as handle:
        def log(message):
            print(message, flush=True)
            handle.write(message + '\n')
        replay, vectors = train_run(0, 'mixed', log=log)
        expected = next(r for r in runs if r['seed'] == 0 and r['regime'] == 'mixed')
        assert json.loads(json.dumps(replay['history'])) == expected['history']
        assert list(replay['champion']) == expected['champion']
        expected_pop = next(r for r in populations if r['seed'] == 0 and r['regime'] == 'mixed')
        assert [list(v) for v in vectors] == expected_pop['genomes']
        tag = {'seed': 0, 'regime': 'mixed'}
        actual_pop = [{**tag, **r} for r in evaluate_population(vectors, 0, 80, 20)]
        actual_champ = [{**tag, **r} for r in evaluate_champion(MemoryOne(*replay['champion']), 0, 80, 20)]
        assert csv_form(actual_pop) == [r for r in pop_rows if r['seed'] == '0' and r['regime'] == 'mixed']
        assert csv_form(actual_champ) == [r for r in champ_rows if r['seed'] == '0' and r['regime'] == 'mixed']
        actual_baselines = [{'seed': 0, 'strategy': name, **r} for name, strategy in references().items()
                            for r in evaluate_field(strategy, 0, 80, 20)]
        assert csv_form(actual_baselines) == [r for r in baselines if r['seed'] == '0']
        log('PASS: seed 0 mixed champion, 35 history records, 20 genomes, 3,800 population matches, '
            '180 champion matches, and 560 baseline matches replay exactly.')
    evidence_files = ['manifest.json', 'champions.json', 'populations.json', 'evaluation.csv',
                      'population_evaluation.csv', 'baselines.csv', 'run_metrics.csv', 'paired_differences.csv']
    write_json(output / 'verification.json', {
        'status': 'passed', 'fixed_runs_identical_to_e2': 5, 'source_hashes_match': True,
        'python': platform.python_version(),
        'training_matches': sum(r['training_matches'] for r in runs),
        'heldout_records': {'population': len(pop_rows), 'champion': len(champ_rows), 'baseline': len(baselines)},
        'all_metrics_and_paired_differences_recomputed': True,
        'exact_replay': {'seed': 0, 'regime': 'mixed', 'history_records': 35, 'population_genomes': 20,
                         'population_matches': 3800, 'champion_matches': 180, 'baseline_matches': 560,
                         'training_matches': replay['training_matches'], 'seconds': time.perf_counter() - start},
        'verifier_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'evidence_sha256': {f: hashlib.sha256((output / f).read_bytes()).hexdigest() for f in evidence_files},
        'note': 'Replay excludes wall-clock equality; all listed scientific records compare exactly.'})


if __name__ == '__main__':
    main()
