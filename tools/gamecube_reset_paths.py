"""Compile grounded recovery paths independently of airborne racer AI paths.

The native reset lookup can choose XY on an airborne AI segment and land on a
hazard underneath. Retain indexed racer geometry, disable its reset eligibility,
and append separate, terrain-checked portions of the donor race routes.
"""
from collections import Counter
import math
import struct

from course_route import race_paths, ssx3_paths
from import_terrain import apply
from probe_worlds import patch_point
from race_course import path_geometry
from terrain_contact import hit

PROFILE = 'grounded-race-route-reset-v1'


def sample_line(points, spacing):
    for a, b in zip(points, points[1:]):
        n = max(1, math.ceil(math.dist(a, b) / spacing))
        for j in range(n):
            yield tuple(a[k] + (b[k] - a[k]) * j / n for k in range(3))
    yield tuple(points[-1])


def safe_runs(samples, classify, *, margin=300, minimum=1000):
    """Split at every rejected sample; trim endpoints by travelled distance.

    Returning one list with unsafe points removed would reconnect across the
    very jump/hazard being excluded. Each resulting run is an independent path.
    """
    runs, current, reasons = [], [], Counter()

    def finish():
        if len(current) < 2:
            return
        distance = [0.]
        for a, b in zip(current, current[1:]):
            distance.append(distance[-1] + math.dist(a, b))
        kept = [p for p, d in zip(current, distance) if margin <= d <= distance[-1] - margin]
        if len(kept) >= 2 and sum(math.dist(a, b) for a, b in zip(kept, kept[1:])) >= minimum:
            runs.append(kept)

    for point in samples:
        grounded, reason = classify(point)
        reasons[reason] += 1
        if grounded is None:
            finish()
            current = []
        else:
            current.append(grounded)
    finish()
    return runs, dict(reasons)


def compile_reset_paths(aip, donor, records, matrix, translation, scale):
    if not math.isfinite(scale) or scale <= 0:
        raise ValueError('Reset path scale must be positive and finite')
    ai, tracks, tail, starts = ssx3_paths(aip)
    if len(ai) > 200:
        raise ValueError('AI path count exceeds runtime capacity')
    eligible = [p for p in ai if struct.unpack_from('<I', p, 24)[0]]
    if not eligible:
        raise ValueError('No imported reset path header is available')
    fields = struct.unpack_from('<7I', eligible[0])
    surfaces, flags, coefficients = [], {}, {}
    for e, p in records:
        if e['kind'] != 1:
            continue
        if len(p) != 430 or e['rid'] in flags:
            raise ValueError('Expected unique GC terrain patches')
        c = [struct.unpack_from('>4f', p, 64 + 16*j)[:3] for j in range(16)]
        lo, hi = struct.unpack_from('>3f', p, 384), struct.unpack_from('>3f', p, 396)
        grid = [(u/4, v/4, patch_point(c, u/4, v/4)) for u in range(5) for v in range(5)]
        surfaces.append((e['rid'], c, lo, hi, grid))
        flags[e['rid']] = struct.unpack_from('>H', p, 10)[0]
        coefficients[e['rid']] = c
    if not surfaces:
        raise ValueError('Reset compilation requires terrain')

    def classify(point):
        contact = hit(surfaces, *point)
        if contact is None:
            return None, 'no-ground'
        if flags[contact['rid']] & 2:
            return None, 'reset-terrain'
        # Donor AI/race lines have small authored height offsets; large offsets
        # indicate a jump, bridge not represented by terrain, or wrong layer.
        if abs(contact['residual']) > 400 * scale:
            return None, 'airborne-or-buried'
        c, u, v = coefficients[contact['rid']], contact['u'], contact['v']
        p = patch_point(c, u, v)
        du = [x-y for x, y in zip(patch_point(c, u+1e-4, v), p)]
        dv = [x-y for x, y in zip(patch_point(c, u, v+1e-4), p)]
        normal = (du[1]*dv[2]-du[2]*dv[1], du[2]*dv[0]-du[0]*dv[2], du[0]*dv[1]-du[1]*dv[0])
        if abs(normal[2]) < math.hypot(*normal[:2]):
            return None, 'steep-ground'
        return (point[0], point[1], contact['z'] + 10*scale), 'safe'

    routes, report = [], []
    for route in race_paths(donor):
        points = [apply(matrix, translation, p) for p in route['points']]
        runs, reasons = safe_runs(sample_line(points, 180*scale), classify,
                                  margin=600*scale, minimum=1800*scale)
        routes.extend(runs)
        report.append(dict(donor_route=route['index'], runs=len(runs), samples=reasons))
    if not routes or len(ai) + len(routes) > 200:
        raise ValueError(f'Reset network needs {len(routes)} paths; {200-len(ai)} slots available')
    out = bytearray(struct.pack('<2I', 0x69696969, len(ai)+len(routes)))
    for p in ai:
        out.extend(p[:24] + struct.pack('<I', 0) + p[28:])
    for points in routes:
        out.extend(struct.pack('<9I', *fields, len(points)-1, 0) + path_geometry(points))
    out.extend(struct.pack('<I', len(tracks)) + b''.join(tracks) + tail)
    new_ai, new_tracks, new_tail, new_starts = ssx3_paths(out)
    if new_tracks != tracks or new_tail != tail or new_starts != starts:
        raise RuntimeError('Reset compiler changed indexed race/start data')
    for old, new in zip(ai, new_ai):
        if old[:24]+old[28:] != new[:24]+new[28:]:
            raise RuntimeError('Reset compiler changed indexed AI geometry/events')
    return bytes(out), dict(profile=PROFILE, original_ai_paths=len(ai),
        reset_paths=len(routes), ai_path_count=len(new_ai), routes=report,
        sample_spacing=180*scale, maximum_height_error=400*scale,
        endpoint_margin=600*scale, minimum_run_length=1800*scale,
        maximum_slope_degrees=45, native_verified=False)
