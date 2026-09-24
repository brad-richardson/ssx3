# X4B — dense Qwen RTC path trial (incomplete)

The worker ran for its 25-minute limit, reached about 37.7k context, and
stopped producing output before replacing its placeholder report. It made
no commit. The orchestrator closed the pane, then checked the source
anchors below directly. This is an **orchestrator audit of partial work**,
not a passed worker source map. Fork source pin: `bc1c70f` in W1F; the
newer `aa20d4a` leaves `CD.cpp` unchanged. Guest source: canonical E56
codegen. No build, boot, device use or source edit occurred.

| Observed edge | Exact source anchor | Limit |
| --- | --- | --- |
| `sceCdReadClock` calls host `std::time(nullptr)`, converts with `localtime_r`/`localtime_s`, and writes 8 BCD clock bytes: zero, seconds, minutes, hours, zero, day, month, year | `ps2xRuntime/src/lib/Kernel/Stubs/CD.cpp:696-729` | Host local time is used when the call runs; runtime reach not shown here |
| Guest `0x31ae80` passes `$sp` as `$a0` in the delay slot to `jal 0x402520` | `sub_0031ADB0_0x31adb0.cpp:277-291`; `local/tooling/ee/ee-at 0x31ae80 10 20` | No LSP confirmation |
| Generated `0x402520` shim directly calls `ps2_stubs::sceCdReadClock` | `sub_00402520_0x402520.cpp:9-14` | Source call edge, no runtime tap |
| After the call, guest loads words at `4(sp)` and `0(sp)`, shifts the first by 3, XORs them, and passes the result in `$a0` to `0x3177c8` | `sub_0031ADB0_0x31adb0.cpp:292-310`; guest `0x31ae88-0x31ae98` | This proves a data path from the clock buffer, assuming the HLE call succeeds |
| `0x3177c8` passes that value to `0x317958` with destination address `0x4ff018`; `0x317958` transforms the value and stores six words at offsets `0..0x14` | `sub_003177C8_0x3177c8.cpp:28-45`; `sub_00317958_0x317958.cpp:98-156`; `ee-at 0x3177c8 0 20` | `ee-label` calls both guest functions unknown; PRNG identity and boot reach require separate evidence |

The worker initially pursued syscall case `0x24`, which is actually
`ExitDeleteThread` (`Kernel/Syscalls/Dispatcher.cpp:189-191`). The
orchestrator corrected that lead. The narrow dense trial still failed
its report and time-box gates. Use the audited call path to scope E55's
fixed-RTC mode; verify the site's live reach and deterministic state
there rather than accepting an unverified RNG label.
