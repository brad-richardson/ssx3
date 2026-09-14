#!/usr/bin/env python3
"""Summarize an owned static-obstacle trace without mistaking a clean ride for contact.

Positive returns establish engine contact with the selected object. The current
probe can observe opponents too, so nearby player reactions are separate spatial
observations, not a proven query-to-player association or a unique impact count.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path


def assess(recipe, receipt, observations, events, riders, source_instance):
    matches = [e for e in recipe['collisions']['enabled_instances']
               if e['source_instance'] == source_instance]
    if len(matches) != 1:
        raise ValueError('Expected one enabled source obstacle in the candidate')
    selected = (recipe['track'] << 24) | matches[0]['instance']
    if receipt.get('world_archive_sha256') != recipe['output_sha256']:
        raise ValueError('Runtime world does not match the candidate recipe')
    evidence = receipt.get('evidence') or {}
    counters = evidence.get('shutdown_counters') or {}
    faults = ('invalid_memory_accesses', 'gpu_command_errors',
              'unknown_guest_instructions', 'fallback_jit_runs')
    if (receipt.get('exit_code') != 0 or receipt.get('stopped_on_fault') or
            not evidence.get('module_loaded') or counters.get('native', 0) <= 0 or
            counters.get('smc_failed') != 0 or any(evidence.get(k) != 0 for k in faults)):
        raise ValueError('Missing or failed native runtime evidence')
    if not observations.get('riding_observed_after_start') or observations.get('reset_loops'):
        raise ValueError('Missing riding or a detected reset loop')
    if any(e.get('stage') == 'overflow' for e in events):
        raise ValueError('Collision trace overflowed')
    if not events or any(e.get('instance_id') != selected for e in events):
        raise ValueError('Collision trace does not belong to the selected obstacle')
    stages = Counter(e['stage'] for e in events)
    if not stages['bound']:
        raise ValueError('Missing selected-obstacle registration')
    returns = [e for e in events if e['stage'] == 'narrow_exit']
    if any(type(e.get('contacts')) is not int or e['contacts'] < 0 for e in returns):
        raise ValueError('Invalid narrow-phase return count')
    positive = [e for e in returns if e['contacts'] > 0]
    bounds = next(e['bounds'] for e in events if e['stage'] == 'bound')
    nearby = [r for r in riders if r['state'] == 8 and all(
        bounds[k] - 150 <= r[axis] <= bounds[k + 3] + 150
        for k, axis in enumerate(('x', 'y', 'z')))]
    first = nearby[0] if nearby else None
    recovery = next((r for r in riders if first and first['t'] < r['t'] <= first['t'] + 15
                     and r['state'] == 0 and not (r.get('terrain_flags', 0) & 2)), None)
    return dict(schema=1, source_instance=source_instance,
        target_instance=matches[0]['instance'], packed_instance=selected,
        world_sha256=recipe['output_sha256'], module_sha256=receipt.get('module_sha256'),
        stages=dict(stages), contact_return_histogram=dict(Counter(e['contacts'] for e in returns)),
        positive_returns=len(positive), summed_contact_counts=sum(e['contacts'] for e in positive),
        narrow_phase_observed=bool(stages['narrow_enter'] and stages['narrow_exit']),
        selected_obstacle_contact_verified=bool(positive),
        player_query_identity_verified=False,
        first_spatially_near_player_reaction=first, subsequent_normal_player_state=recovery,
        final_rider=riders[-1] if riders else None,
        complete_hazard_resets=observations.get('complete_hazard_resets', 0),
        reset_loops=observations.get('reset_loops', []),
        limitations=['Contact returns can include opponents and repeat across frames.',
                     'Player reaction is joined by position, not query identity or a shared timestamp.',
                     'This fixture does not certify every obstacle, uninterrupted progress, or finish.'])


def summarize(run, build, source_instance):
    recipe = json.loads((build / 'experiment.json').read_text())
    archive_hash = hashlib.sha256((build / 'BAM.BIG').read_bytes()).hexdigest()
    if archive_hash != recipe['output_sha256']:
        raise ValueError('Candidate archive does not match its recipe')
    logs = [Path(line[5:]) for line in (run / 'runtime.log').read_text().splitlines()
            if line.startswith('Log: ')]
    if len(logs) != 1:
        raise ValueError('Expected one native run log')
    log = logs[0]
    receipt = json.loads(log.with_suffix('.json').read_text())
    events = [json.loads(line.removeprefix('[ssx-collision] '))
              for line in log.read_text().splitlines() if line.startswith('[ssx-collision] ')]
    riders = [json.loads(line) for line in (run / 'rider.jsonl').read_text().splitlines()]
    observations = json.loads((run / 'observations.json').read_text())
    report = assess(recipe, receipt, observations, events, riders, source_instance)
    report.update(run=str(run), build=str(build), runtime_receipt=str(log.with_suffix('.json')),
                  collision_log_sha256=hashlib.sha256(log.read_bytes()).hexdigest(),
                  rider_trace_sha256=hashlib.sha256((run / 'rider.jsonl').read_bytes()).hexdigest())
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--source-instance', type=int, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = summarize(args.run, args.build, args.source_instance)
    with args.output.open('x') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')
    print(json.dumps(report, indent=2))
    if not report['selected_obstacle_contact_verified']:
        raise SystemExit('No positive selected-obstacle contact; clean runtime alone is insufficient')


if __name__ == '__main__':
    main()
