#!/usr/bin/env python3
"""I26: build a PS2X_PAD_SCRIPT (vsync clock) from guest-tick press times.

Each entry: (tick, button, hold_ms). ms = ceil(tick * 100000 / 5994), so the
press fires on the first pad read at or after that vsync tick.
Usage: make_route.py v1|v2 ... (prints the string)
"""
import math, sys

def ms(tick):
    return math.ceil(tick * 100000 / 5994)

def route(entries):
    return ",".join(f"{ms(t)}:{b}:{h}" for t, b, h in entries)

M = 66  # >= 1 s (60 ticks) after the screen appears, +6 ticks slack

def v1():
    # Appear ticks = press tick + transition measured in boot i26base
    # (settle.py): title 264; start->main +64; cross->char +39; ->2nd +41;
    # ->peak +28; ->mode +9; ->event +7; ->rules +37; ->rival +203.
    e = []
    t = 264 + M; e.append((t, "start", 250))            # title
    t = t + 64 + M; e.append((t, "cross", 250))         # main menu: Single Event
    t = t + 39 + M; e.append((t, "cross", 250))         # Select Character: Zoe
    t = t + 41 + M; e.append((t, "cross", 250))         # 2nd character screen
    t = t + 28 + M; e.append((t, "cross", 250))         # Select Peak: Peak 1
    t = t + 9 + M; e.append((t, "cross", 250))          # Select Mode: Race
    t = t + 7 + M; e.append((t, "down", 150))           # Select Event: Snow Jam -> Metro-City
    t = t + 30; e.append((t, "down", 150))              # -> Happiness
    t = t + 36; e.append((t, "cross", 250))             # Happiness
    t = t + 37 + M; e.append((t, "cross", 250))         # My Rules: Continue
    t = t + 203 + M                                     # Rival Challenge card
    for k in range(20):                                 # probe: one cross tap per second
        e.append((t + 60 * k, "cross", 200))
    e.append((t, "down", 30000))                        # tuck (as E33's 20 s down)
    return e

def v2():
    # v1 showed the title ignores START until "Press START button" shows
    # (~tick 570; base 560, v1 569) and the screen order is title -> Main
    # Menu -> Select Character -> Setup Character -> Select Peak -> Select
    # Mode -> Select Event -> My Rules -> loading -> Rival Challenge card.
    # Settle times after a press: start->main +64 (base, v1); main->char
    # (rider drawn) +52 (v1); char->setup +43 (v1); setup->peak +40 (panel
    # animates; v1 +22 first frame); peak->mode +20, mode->event +20 (base
    # +9/+7, padded); event->rules +37 (base); rules->rival +203 (base).
    e = []
    t = 570 + M; e.append((t, "start", 250))            # title prompt
    t = t + 64 + M; e.append((t, "cross", 250))         # Main Menu: Single Event
    t = t + 52 + M; e.append((t, "cross", 250))         # Select Character: Zoe
    t = t + 43 + M; e.append((t, "cross", 250))         # Setup Character: Continue
    t = t + 40 + M; e.append((t, "cross", 250))         # Select Peak: Peak 1
    t = t + 20 + M; e.append((t, "cross", 250))         # Select Mode: Race
    t = t + 20 + M; e.append((t, "down", 150))          # Select Event: Snow Jam -> Metro-City
    t = t + 30; e.append((t, "down", 150))              # -> Happiness
    t = t + 36; e.append((t, "cross", 250))             # Happiness
    t = t + 37 + M; e.append((t, "cross", 250))         # My Rules: Continue
    t = t + 203 + M                                     # Rival Challenge card
    for k in range(20):                                 # probe: one cross tap per second
        e.append((t + 60 * k, "cross", 200))
    e.append((t, "down", 30000))                        # tuck (as E33's 20 s down)
    return e

def v3():
    # v2 menus all landed (1.1-1.3 s after each screen settled), but the
    # Rival Challenge card ignored 20 cross taps (1709-2849): it takes X only
    # once the course has loaded (base: accepted at 6793, 2700 ticks after
    # the card). So: tap X once a second for 50 s from card+66 (the first
    # accepted tap starts the race; later taps are jumps in the race), and
    # hold down (tuck) 70 s from the same tick (base held 20 s from its tap).
    e = v2()[:10]
    t = e[-1][0] + 203 + M                              # Rival Challenge card (v2: 1640)
    for k in range(50):
        e.append((t + 60 * k, "cross", 200))
    e.append((t, "down", 70000))
    return e

def v4():
    # v3a: 50 taps (1709-4649) with down held throughout were all ignored.
    # Either the card needs X with no other button held, or it only takes X
    # after a fixed guest tick (base took it at 6793). v4 covers both: every
    # 60 ticks an X tap (12 ticks) with down released, then down (tuck) for
    # 42 ticks; 90 cycles run the taps to ~7050, past base's 6793.
    e = v2()[:10]
    t = e[-1][0] + 203 + M                              # Rival Challenge card (v2: 1640)
    for k in range(90):
        c = t + 60 * k
        e.append((c, "cross", 200))                     # 12 ticks
        e.append((c + 15, "down", 700))                 # ticks +15..+57
    return e

def v5():
    # v4a: the first tap (1709, down released) dismissed the card; race HUD
    # 00:00:00 at 1713. So the card only needs X without down held. Final:
    # same first 10 presses; 10 X taps a second apart (retries for a slower
    # host; after the race starts they are jumps), down released during each
    # tap and held between; then a steady 30 s tuck.
    e = v2()[:10]
    t = e[-1][0] + 203 + M                              # Rival Challenge card (v2: 1640)
    for k in range(10):
        c = t + 60 * k
        e.append((c, "cross", 200))                     # 12 ticks
        e.append((c + 15, "down", 700))                 # ticks +15..+57
    e.append((t + 60 * 10, "down", 30000))              # steady tuck
    return e

ROUTES = {"v1": v1, "v2": v2, "v3": v3, "v4": v4, "v5": v5}

if __name__ == "__main__":
    print(route(ROUTES[sys.argv[1]]()))
