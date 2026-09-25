# FR1 routes (PS2X_PAD_SCRIPT with PS2X_PAD_SCRIPT_CLOCK=vsync)

Times are guest ms (`vsyncTick x 100000/5994`); entries are `at_ms:button:hold_ms`.
Derived from I26-FAST (`local/research/I26/ROUTES.md`); that file is untouched
(the orchestrator renames the "tuck" leg). Needs `PS2X_SKIP_MOVIE=1`
(dev-only movie bypass) and an empty memory card, as in SJ1.

SJ1 found d-pad down brakes the rider (0–2 MPH held, 44 MPH released), so the
30 s down-hold at the end of I26-FAST is dropped wherever race progress
matters. The 0.7 s down holds interleaved with the Rival-card taps are kept:
each tap still gets a down-free window (X is ignored while down is held).

## FR1-R1 — Happiness full race, no race inputs (30 entries)

I26-FAST minus the final `38522:down:30000`. Menus → Happiness → 10 card taps
(the first starts the race, the rest are jumps) → rider rides untouched.

```
10611:start:250,12780:cross:250,14749:cross:250,16567:cross:250,18336:cross:250,19770:cross:250,21205:down:150,21706:down:150,22306:cross:250,24025:cross:250,28512:cross:200,28763:down:700,29513:cross:200,29764:down:700,30514:cross:200,30765:down:700,31515:cross:200,31766:down:700,32516:cross:200,32767:down:700,33517:cross:200,33768:down:700,34518:cross:200,34769:down:700,35519:cross:200,35770:down:700,36520:cross:200,36771:down:700,37521:cross:200,37772:down:700
```

## FR1-R2 — Snow Jam (92 entries, SJ1 R2 verbatim)

As SJ1 R2 (`local/research/SJ1/REPORT.md` appendix): FR1-R1 shape minus the
two Select-Event downs (Snow Jam is the default), plus an X tap every 10 s
guest with down held between taps out to ~358 s guest. Replicates the SJ1 R2
"loads and races" verdict on the same tip.

```
10611:start:250,12780:cross:250,14749:cross:250,16567:cross:250,18336:cross:250,19770:cross:250,22306:cross:250,24025:cross:250,28512:cross:200,28763:down:700,29513:cross:200,29764:down:700,30514:cross:200,30765:down:700,31515:cross:200,31766:down:700,32516:cross:200,32767:down:700,33517:cross:200,33768:down:700,34518:cross:200,34769:down:700,35519:cross:200,35770:down:700,36520:cross:200,36771:down:700,37521:cross:200,37772:down:700,38522:cross:200,38772:down:9750,48522:cross:200,48772:down:9750,58522:cross:200,58772:down:9750,68522:cross:200,68772:down:9750,78522:cross:200,78772:down:9750,88522:cross:200,88772:down:9750,98522:cross:200,98772:down:9750,108522:cross:200,108772:down:9750,118522:cross:200,118772:down:9750,128522:cross:200,128772:down:9750,138522:cross:200,138772:down:9750,148522:cross:200,148772:down:9750,158522:cross:200,158772:down:9750,168522:cross:200,168772:down:9750,178522:cross:200,178772:down:9750,188522:cross:200,188772:down:9750,198522:cross:200,198772:down:9750,208522:cross:200,208772:down:9750,218522:cross:200,218772:down:9750,228522:cross:200,228772:down:9750,238522:cross:200,238772:down:9750,248522:cross:200,248772:down:9750,258522:cross:200,258772:down:9750,268522:cross:200,268772:down:9750,278522:cross:200,278772:down:9750,288522:cross:200,288772:down:9750,298522:cross:200,298772:down:9750,308522:cross:200,308772:down:9750,318522:cross:200,318772:down:9750,328522:cross:200,328772:down:9750,338522:cross:200,338772:down:9750,348522:cross:200,348772:down:9750
```

## FR1-R3 — Metro-City, no race inputs (29 entries)

FR1-R1 shape with one Select-Event down (Snow Jam → Metro-City) instead of
two, no tail: the rider rides untouched so the run shows whether the event
genuinely races. Metro-City needs no save (adjacent menu entry).

```
10611:start:250,12780:cross:250,14749:cross:250,16567:cross:250,18336:cross:250,19770:cross:250,21205:down:150,22306:cross:250,24025:cross:250,28512:cross:200,28763:down:700,29513:cross:200,29764:down:700,30514:cross:200,30765:down:700,31515:cross:200,31766:down:700,32516:cross:200,32767:down:700,33517:cross:200,33768:down:700,34518:cross:200,34769:down:700,35519:cross:200,35770:down:700,36520:cross:200,36771:down:700,37521:cross:200,37772:down:700
```
