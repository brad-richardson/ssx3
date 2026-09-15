# Route control for the native runtime

Steering the rider along chosen waypoints, so a run can reach a particular
object, gate or finish instead of whatever the fall line happens to hit.

## Why

A free-running ride is not reproducible: two runs of the same archive, single
core, with identical scripted input, separate within 0.21 guest seconds of the
race start and end a median 449 / maximum 69,184 world units apart
([measurement](aloha-conversion.md#92-a-free-running-ride-cannot-ab-anything)).
Movie playback fixes that — two replays agree on all 879 sampled control-flow
rows — but a movie only replays *the line it recorded*. Aiming at something new
needs steering.

## Using it

```sh
python3 tools/gamecube_course_check.py --game ... --profile ... --output ... \
  --course-manifest ... --route local/research/aloha/route-collider-524.json --seconds 200
```

A route is JSON — either a bare list of waypoints or an object with options:

```json
{"waypoints": [[-119899.1, 74127.7, -230494.1], [-118570.0, 68742.0, -266856.0]],
 "tolerance": 600, "gain": 1.5}
```

Waypoints are world coordinates, `[x, y, z]` or `{"x":…, "y":…, "z":…}`.
`tolerance` (default 500) is how close counts as reached, `gain` (default 1.5)
how hard it steers, and `sign` pins the steering sense instead of calibrating
it. The harness records the route and its outcome — waypoints reached, the sign
it settled on, and a timestamped event per waypoint — in the run's
`observations.json` under `route_result`.

The easiest way to author a route is to read one off a ride that already went
somewhere near: take the rider trace, sample a point every few guest seconds,
and append the place you actually want to reach.

## How it works, and what it does not assume

The harness already observes the rider several times a second and the pad is a
named pipe, so the loop is: infer the heading from how the rider actually moved,
compare it with the bearing to the next waypoint, and push the stick to close
the difference. `SET MAIN x y` goes straight to the pipe rather than through
`gamecube_input.py`, because a route needs an update per sample.

Two things are measured rather than assumed:

- **Which way left turns.** The sign between stick x and the heading's rotation
  is a property of the game and its camera, and the PS2 tools' note about it
  does not transfer. So a route holds one steady offset for the first 1.5 guest
  seconds of riding, watches which way the heading goes, and adopts that sense.
  It keeps holding rather than guessing if the turn is under two degrees.
- **Which axis is up.** Steering works in the x/z plane because y is the
  vertical in this game's world coordinates (a climbing rider gains y), so a
  waypoint's height never enters the bearing.

It also declines to steer rather than steering on noise: nothing is sent while
the rider has moved less than three units between samples, or while the
observed state is not one of the riding states — a reset or a wipeout moves the
position for reasons a route cannot answer.

## Measured, September 15

The first steered run on Aloha (`local/research/aloha/route-001`, 200 s, exit 0,
riding observed) calibrated and followed:

```
{'t': 125.75, 'calibration': 'started'}
{'t': 127.26, 'calibration': 'done', 'turned_degrees': -11.98, 'sign': -1}
{'t': 128.35, 'reached': 0, 'waypoint': [-119899.1, -230494.1]}
{'t': 131.71, 'reached': 1, 'waypoint': [-118654.3, -231618.5]}
```

So on this game and camera **a positive stick x turns the heading clockwise in
the x/z plane** — the calibration measured −12° over 1.5 s and adopted
`sign = -1`. No writes were lost (`unavailable_writes: 0`) once the pipe is
opened per write; holding one open across the menu-to-gameplay transition gets
`EPIPE`, because the runtime closes and reopens its read end.

That route reached 2 of its 6 waypoints. A second attempt at the same object
with three wider waypoints, a 1,500-unit tolerance and the sign pinned
(`route-002`, with the collision-trace module aimed at instance 524) rode
cleanly for 999 samples and reached **none** of them, and
`gamecube_collision_check` reported no contact.

So the honest state is: **the steering mechanism works and route *following*
does not yet.** Calibration measures the sense, the stick reaches the runtime,
waypoints are consumed when the rider passes near one — but a proportional
controller on heading error alone does not hold a line down a mountain. The
rider accelerates, the terrain turns under it, and the first waypoint 14,000
units downhill is never approached within tolerance.

What it needs next, in order:

1. **Pure pursuit instead of raw heading error** — aim at a point a fixed
   distance ahead *along* the route rather than at the next waypoint, which is
   what keeps a fast vehicle on a curved path.
2. **Engage late.** A short route that starts near its target is far more
   likely to work than one that tries to drive the whole descent, and it is all
   a deliberate-contact test needs.
3. **Speed.** Nothing currently brakes or tucks; a controller that cannot slow
   down has one attempt per approach.

Until then, the tool that reliably reaches a *chosen* object is a recorded
movie whose line already passes through it
([contact](aloha-conversion.md#93-static-collision-observed-under-movie-playback)),
with the autopilot for objects no recorded line happens to hit.

## What it is for

- The deliberate-contact test for imported objects: point a route at a bound
  block, pane or collider and the contact stops depending on luck
  ([collision](gamecube-collision.md)).
- Gate, checkpoint and finish claims, which no free ride can support.
- A repeatable line for phone A/B work, where dual-core rides diverge within
  about three seconds.
