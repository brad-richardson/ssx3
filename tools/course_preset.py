#!/usr/bin/env python3
"""Per-course presets: the donor files, the target slot and the placement transform.

A conversion needs four families of constants that were previously typed on the
command line for every stage: which donor course, which SSX 3 location (and its
terrain group, track index, template patch and texture group), the placement
transform, and the slot's race-line shape. Those are per-course facts, not
per-invocation choices, so they live in `tools/course_presets/<name>.json`.

A preset only supplies values for options the caller did not type. Passing the
flags explicitly, as the Garibaldi lineage does, keeps the old behaviour and the
old output bytes exactly; a preset is never consulted for an option that appears
in argv.
"""
import json
from pathlib import Path

PRESET_DIR = Path(__file__).resolve().parent / 'course_presets'
ROOT = Path(__file__).resolve().parents[1]

# Preset key -> argparse destination. Dotted keys index into nested objects.
TERRAIN_KEYS = {
    'donor.nbd': 'nbd',
    'donor.textures': 'textures',
    'donor.lightmaps': 'lightmaps',
    'donor.reset_paths': 'reset_aip',
    'donor.race_paths': 'race_aip',
    'target.location': 'location',
    'target.template_rid': 'template_rid',
    'target.texture_group': 'pin_texture_group',
    'placement.source_anchor': 'source_anchor',
    'placement.target_anchor': 'target_anchor',
    'placement.yaw_degrees': 'yaw',
    'placement.scale': 'scale',
}

PATH_DESTS = {'nbd', 'textures', 'lightmaps', 'reset_aip', 'race_aip', 'gsf'}


def available():
    return sorted(p.stem for p in PRESET_DIR.glob('*.json'))


def load(name):
    """Load a preset by name (tools/course_presets/NAME.json) or by explicit path."""
    path = Path(name)
    if not path.suffix:
        path = PRESET_DIR / f'{name}.json'
    preset = json.loads(path.read_text())
    for required in ('name', 'donor', 'target', 'placement'):
        if required not in preset:
            raise ValueError(f'Preset {path} is missing "{required}"')
    preset['preset_path'] = str(path)
    return preset


def get(preset, dotted, default=None):
    node = preset
    for part in dotted.split('.'):
        if not isinstance(node, dict) or part not in node:
            return default
        node = node[part]
    return node


def resolve(value, dest):
    """Preset paths are recorded relative to the repository root."""
    if dest in PATH_DESTS and isinstance(value, str):
        return Path(value) if Path(value).is_absolute() else ROOT / value
    return value


def given(ap, argv):
    """The argparse destinations whose option strings appear in argv."""
    seen = set()
    words = {word.split('=', 1)[0] for word in argv}
    for action in ap._actions:
        if any(option in words for option in action.option_strings):
            seen.add(action.dest)
    return seen


def apply(ap, args, argv, keys=TERRAIN_KEYS):
    """Fill options the caller omitted from `args.preset`; returns a receipt dict."""
    if not getattr(args, 'preset', None):
        return None
    preset = load(args.preset)
    supplied = given(ap, argv)
    filled = {}
    for dotted, dest in keys.items():
        if dest in supplied:
            continue
        value = get(preset, dotted)
        if value is None:
            continue
        setattr(args, dest, resolve(value, dest))
        filled[dest] = value
    return dict(name=preset['name'], path=preset['preset_path'], filled=filled,
                race=preset.get('race', {}), target=preset['target'], donor=preset['donor'])
