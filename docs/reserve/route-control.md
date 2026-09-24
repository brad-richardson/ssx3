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

Four steered runs on Aloha, each 200 s, exit 0, riding observed.

**The controller.** Heading-error steering does not work: one route reached 2 of
6 waypoints and a second, wider one 0 of 3. Replacing it with pure pursuit —
aim at a point a fixed distance ahead *along* the polyline — plus late
engagement is what made it steer usefully.

**The sign cannot be calibrated by holding an input.** The first version held
+0.15 for 1.5 s and read the heading change: −12°, so `sign = -1`. That reading
is dominated by the terrain, which turns the rider far harder than a test
offset, and pinning it produced runs that steered *away* from the target: the
unsteered line passed within 27 units of collider 524 while the steered ones
managed only 598 and 725. The sign is now inferred from the controller's own
behaviour — steer with a tentative sense, and if the mean heading error grows
over the first 1.5 s, flip once. In the run below it started at +1, watched the
error go from 71.6° to 111.1°, and flipped to −1 at t = 131.08.

**It moves the rider toward a chosen target.** Collider rid 529 (donor instance
883) sits 2,637 units off the natural line. Routed at it with a 6,000-unit
engagement radius (`route-004`):

| | unsteered (`ride-003`) | steered (`route-004`) |
| --- | ---: | ---: |
| closest approach to the target | 2,636 units | **868 units** |
| broad-phase tests of that object | — | 794 |
| narrow-phase queries | — | 19 |
| positive contacts | — | 0 |

So steering closed two thirds of the gap and brought the object from never
being tested to being narrow-phase tested nineteen times, and it still did not
touch it — it stopped 68 units outside its own 800-unit tolerance. What is
left is tuning rather than mechanism:

1. **Vertical alignment.** Steering is horizontal by design, so a route can
   arrive beside an object it passes over or under. The target's *mesh* is
   also much smaller than its 6,605-unit bounding box.
2. **Tolerance and gain** are guesses; 868 against 800 is one notch away.
3. **Speed.** Nothing brakes or tucks, so each approach gets one attempt.

A recorded movie whose line already passes through the target remains the
reliable way to prove contact
([example](aloha-conversion.md#93-static-collision-observed-under-movie-playback));
the autopilot is what extends that to objects no recorded line happens to hit,
and it is now close enough to be worth finishing.

## What it is for

- The deliberate-contact test for imported objects: point a route at a bound
  block, pane or collider and the contact stops depending on luck
  ([collision](gamecube-collision.md)).
- Gate, checkpoint and finish claims, which no free ride can support.
- A repeatable line for phone A/B work, where dual-core rides diverge within
  about three seconds.
