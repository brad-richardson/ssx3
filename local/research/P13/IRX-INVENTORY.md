# T3 — IRX inventory (static, lease-free)

Standalone evidence for the §13 IOP-model decision row. Tables, no verdicts.
Peer-owned `REPORT.md` untouched. Methods at the end; machine-readable mirror:
`irx-table.csv` (same dir, one row per IRX).

## 1. Extraction receipt

- ISO: `/Volumes/Extreme SSD/ps2recomp-spike/SSX 3 (USA).iso`, read-only.
- ISO bytes: 3,005,415,424 (matches brief).
- Extract: `bsdtar -xf "<iso>" 'DATA/MODULES/*.IRX'` into `/tmp/t3-irx/` (scratch, not repo).
- Count: **22** `DATA/MODULES/*.IRX` (matches brief).
- Sample re-measure: SNDDRV 96,016 ✓, MSIFRPC 7,377 ✓, PADMAN 43,813 ✓, SDRDRV 8,065 ✓.
- `file(1)`: all 22 = `ELF 32-bit LSB PlayStation 2 IOP module, MIPS, MIPS-I version 1 (SYSV)`.
- All retain ELF section headers; reloc types in every module are
  `{R_MIPS_32, R_MIPS_26, R_MIPS_HI16, R_MIPS_LO16}` (2,4,5,6 — not 32-only).
- `.mdebug`+`.symtab`+`.strtab` retained by the 3 EA modules only (all
  Sony/Logitech modules stripped to 1 null sym): SNDDRV 364 syms, DRTYSCKF 468
  syms, VOIPF 120 syms (SNDDRV symtab used as cross-check, §5).
- Rerun: re-extracted to `/tmp/t3-irx/t3-rerun/` (first extraction at
  `/tmp/t3-irx/DATA/` left untouched); all sizes/MD5s/entries identical.

| File | Bytes | MD5 | Module (`.iopmod`) | Mod ver | Entry |
| --- | ---: | --- | --- | --- | --- |
| DEV9.IRX | 13,197 | f19372fc914d7e6be7a6808be08c2993 | dev9 | 2.4 | 0x2e8 |
| DRTYSCKF.IRX | 102,751 | 2eca06c18e0604a324b257c7f223dc8d | Dirtysock | 1.1 | 0xa4 |
| INET.IRX | 141,181 | d70d29e05694d2d1f90b4c61568c5f1c | INET_service | 1.92 | 0x11ebc |
| INETCTL.IRX | 24,781 | 537821cab9969a21c41ff4f35a0d4ca0 | INET_control | 1.92 | 0x3aac |
| LGAUD.IRX | 45,109 | dbaee103500b9fc7ee81c186ba18629a | lgAud | 1.8 | 0x120c |
| LIBNET.IRX | 6,661 | 953045c6551bd77fccdcb3a58fcf49cd | Libnet | 1.23 | 0xafc |
| LIBSD.IRX | 28,557 | 696cebe67c2ee3a1d3e8b67137b1ce95 | Sound_Device_Library | 3.3 | 0xb0 |
| MCMAN.IRX | 95,877 | 4b9daf423479eded7d7cd812528cbbfb | mcman | 2.34 | 0x178 |
| MCSERV.IRX | 7,417 | 4b7bf828b3a13cee39bcd618899bf1a8 | mcserv | 2.16 | 0x58 |
| MSIFRPC.IRX | 7,377 | a5ccf7db41f9239f81502564b8fed272 | IOP_MSIF_rpc_interface | 2.5 | 0x0 |
| NETCNF.IRX | 65,805 | c516c4314e1aef82641ad6d02e93564a | NET_configuration | 1.20 | 0x334 |
| PADMAN.IRX | 43,813 | 1cd17027460197a5903f89bce1c5c10b | padman | 4.5 | 0x3178 |
| PPP.IRX | 102,285 | c1b40994bdcb296cbb6cd32bc3962189 | INET_PPP | 1.92 | 0xea0c |
| PPPOE.IRX | 17,121 | 89575a55cbefc35c9ec3e9bbfc7ffcdb | INET_PPPoE_driver | 1.92 | 0x2388 |
| SDRDRV.IRX | 8,065 | 50d7187c61f0c1a1cd754ef9399602c4 | sdr_driver | 4.1 | 0x0 |
| SIO2MAN.IRX | 6,641 | 07d3682a85c246cff2537f5b037a5283 | sio2man | 3.0 | 0x634 |
| SMAP.IRX | 16,977 | 2aab2a455b034d42fc9ef863d8c178b1 | INET_SMAP_driver | 1.92 | 0x272c |
| SNDDRV.IRX | 96,016 | a874dc35d6c5423aa47ab3cc05f87acb | SND_Library_EE_Driver | 8.3 | 0x9244 |
| SPDUART.IRX | 18,537 | cb34571bac9b04df6fd4c2762df003da | INET_SPEED_UART_driver | 2.1 | 0x1a80 |
| USBD.IRX | 34,969 | 6d8e4ec5acba0ef3abe6b8cff7edfe1e | USB_driver | 2.4 | 0x4cc4 |
| USBKB.IRX | 12,853 | 1d597b55517582696deb93b19f47d405 | USB_Keyboard_Driver | 2.2 | 0x0 |
| VOIPF.IRX | 16,105 | 37d1fc1a7629ba6350a85093901512ac | Tiburon VoIP | 1.2 | 0x1484 |

## 2. Origin + stamps (EA-built vs Sony-built)

| File | Call | Evidence |
| --- | --- | --- |
| SNDDRV.IRX | EA | `Snd::System::Init`, EA SND src paths (`ps2/sndiop.c`, `mix/…`, `cmn/…`), `gcc2_compiled`, `__gnu_compiled_c` |
| DRTYSCKF.IRX | EA | module `Dirtysock` (EA DirtySDK net lib), `RPC IOP Ver 1.0`, `gcc2_compiled` |
| VOIPF.IRX | EA | module `Tiburon VoIP` (EA Tiburon studio), `Aug  8 2003`, `gcc2_compiled` |
| LGAUD.IRX | Logitech | module `lgAud`, `built on May 21 2003 at 15:18:36`, `lgaud: USBD Version insufficient` |
| LIBSD.IRX | Sony | `PsIIlibsd   2700`, module `Sound_Device_Library` v3.3 |
| MCMAN.IRX | Sony | `PsIImcman   2700`, `Sony PS2 Memory Card Format` |
| MCSERV.IRX | Sony | `PsIImcserv  2700` |
| MSIFRPC.IRX | Sony | `PsIImsifrpc 2700`, `Multi-thread available sifrpc module...` |
| PADMAN.IRX | Sony | `PsIIpadman  2700` |
| SDRDRV.IRX | Sony | `PsIIsdrdrv  2700`, `SDR driver version 4.0.1 (C) SCEI` |
| SIO2MAN.IRX | Sony | `PsIIsio2man 2700` |
| USBD.IRX | Sony | `PsIIusbd    2700`, `Version 1.1.0`, `USB Driver (%s)` |
| USBKB.IRX | Sony | `PsIIusbkb   2700`, `USB Keyboard Driver 1.03` |
| LIBNET.IRX | Sony | `PsIIlibnet  2710`, `Libnet: type %d: id %d` |
| INET.IRX | Sony | `Version 1.92.0`, stack src names (`tcp.c`, `udp.c`, `ip.c`, …) |
| INETCTL.IRX | Sony | `Version 1.92.0`, `inetctl: sce…` diagnostics |
| PPP.IRX | Sony | `Version 1.92.0`, stack src names (`lcp.c`, `pap.c`, `pppmain.c`, …) |
| SMAP.IRX | Sony | `Version 1.92.0`, `smap: dev9 module version must be 2.4 or later` |
| PPPOE.IRX | Sony | module v1.92 (TCP/IP family), `pppoe.c` |
| SPDUART.IRX | Sony | `Version 2.1.0`, module `INET_SPEED_UART_driver` |
| NETCNF.IRX | Sony | `# <Sony Computer Entertainment Inc.>`, `sceNetCnf…` diagnostics |
| DEV9.IRX | Sony | `PsIIDEV9    2710` + `dev9: CXD9566/CXD9611…driver start` (Sony HW ids) |

Tally: Sony 18, EA 3, Logitech 1.

## 3. Decision table (ranked: SND path → input → rest)

`imports` = `lib(count)`; full funcno→name lists in §4 (SND) and §6 (rest).
`funcno→name` via PCSX2 `IopModuleNames.cpp`; `?N` = no table entry (see gaps).
`RPC-S` = `sceSifRegisterRpc` sid @ call-pc → handler; `RPC-C` = BindRpc sid /
CallRpc fno; `CMD` = `sceSifAddCmdHandler` cid → handler. All immediates verified
by disassembly incl. jal delay slots. `exports` = `lib vV: slots(live)`.

| Rank | IRX | N imp | Imports (lib n) | Exports | RPC-S (serve) | RPC-C / CMD |
| --- | --- | ---: | --- | --- | --- | --- |
| S1 | SNDDRV | 41 | libsd 12, sysmem 3, intrman 2, loadcore 1, sifcmd 9, sifman 1, sysclib 4, thbase 9 | — none — | 0x534E44 `SND` @0x9310 → 0x8bf0 | CMD cid 0 @0x8ff8 → 0x8ba0; SEND cid 1 @0x911c,@0x9188 |
| S2 | SDRDRV | 47 | libsd 26, intrman 2, loadcore 1, sifcmd 6, stdio 1, sysclib 3, thbase 8 | sdrdrv v1.1: 6 slots, live 1–5 | 0x80000701 @0x3cc → 0x410 | bind 0x80000704 @0xe34; call fno 0 @0xce0 (client 0x19f0, 64 B) |
| S3 | MSIFRPC | 25 | sysmem 3, loadcore 1, intrman 2, stdio 1, sifcmd 4, sifman 1, thbase 10, thmsgbx 3 | msifrpc v1.1: 22 slots, live {4,17} | — | CMD 0x80000019 @0x100 → 0x298; 0x8000001a @0x118 → 0x510; 0x8000001d @0x130 → 0x3c4; SEND 0x80000001 @0x164; 0x80000018 @0xa14,@0xc80,@0xf9c |
| S4 | LIBSD | 19 | intrman 7, loadcore 2, sifman 2, sysclib 1, thevent 7 | libsd v1.5: 34 slots (0–33), all live | — | — |
| I1 | PADMAN | 38 | sysmem 1, loadcore 1, intrman 2, stdio 1, sio2man 7, thbase 7, thevent 6, sifman 4, sifcmd 4, vblank 2, sysclib 3 | padman v2.3: 18 slots, all live | 0x80000100 @0x7604 → 0x7414; 0x80000101 @0x76c8 → 0x7624 | — |
| R01 | DEV9 | 16 | stdio 1, loadcore 2, thbase 1, thsemap 3, ioman 2, dmacman 2, intrman 5 | dev9 v1.7: 14 slots (0–13), all live | — | — |
| R02 | DRTYSCKF | 59 | inet 13, netcnf 3, inetctl 5, sysmem 2, intrman 2, sifcmd 3, sifman 2, stdio 1, sysclib 13, thbase 10, thsemap 5 | — none — | — | CMD cid 1 @0x1998 → 0x17b8 (param s0+0x1840; SetCmdBuffer buf s0+0x17c0 @0x18e0) |
| R03 | INET | 40 | sysmem 2, intrman 2, loadcore 2, stdio 1, sysclib 9, thbase 13, thevent 5, thsemap 4, cdvdman 1, modload 1 | inet v1.1: 47 slots, live 30; netdev v1.1: 24 slots, live 16 | — | — |
| R04 | INETCTL | 49 | inet 12, netcnf 3, loadcore 2, stdio 1, sysclib 8, thbase 9, thevent 5, thsemap 4, sysmem 2, intrman 2, modload 1 | inetctl v1.1: 20 slots, live 11 (0,4–13; dummy 0x3c08 ×9) | — | — |
| R05 | LGAUD | 34 | usbd 9, sysmem 2, intrman 2, loadcore 2, modload 2, sifcmd 4, stdio 1, sysclib 4, thbase 4, thsemap 4 | lgaud v1.8: 23 slots (0–22), all live | 0x50494C42 `BLIP` @0x171c → 0x173c | — |
| R06 | LIBNET | 45 | msifrpc 2, inet 20, inetctl 7, intrman 2, loadcore 2, sifcmd 1, stdio 1, sysclib 1, thbase 5, thsemap 4 | Libnet v1.1: 4 slots (0–3 only, no fns ≥4) | — | — (MSIF client: MInitRpc+MEntryLoop) |
| R07 | MCMAN | 33 | loadcore 2, intrman 2, sio2man 5, sysclib 8, stdio 1, thbase 3, thsemap 5, modload 1, ioman 2, secrman 3, cdvdman 1 | mcman v2.7: 62 slots, live 48 | — | — |
| R08 | MCSERV | 53 | loadcore 2, intrman 2, sysclib 4, stdio 1, sifman 4, sifcmd 7, thbase 8, thsemap 2, mcman 23 | mcserv v2.1: 8 slots, all live | 0x80000400 @0x31c → 0x33c | — |
| R09 | NETCNF | 43 | sysmem 2, loadcore 2, intrman 2, thbase 1, thsemap 4, sysclib 14, ioman 16, stdio 1, cdvdman 1 | netcnf v1.32: 24 slots (0–23), all live | — | — |
| R10 | PPP | 43 | netdev 10, intrman 2, loadcore 2, sysclib 9, thbase 10, thevent 5, thsemap 4, modload 1 | modem v1.1: 24 slots, live 0–5 | — | — |
| R11 | PPPOE | 39 | modem 2, netdev 10, sysclib 7, thbase 8, thevent 5, thsemap 4, intrman 2, modload 1 | — none — | — | — |
| R12 | SIO2MAN | 28 | loadcore 1, intrman 6, stdio 1, dmacman 5, thbase 3, thevent 5, thsemap 4, sysclib 3 | sio2man v2.4: 64 slots, live 62 (4,27 NULL; slot 0 = 0x634 entry, live) | — | — |
| R13 | SMAP | 42 | netdev 7, dev9 7, intrman 2, stdio 1, sysclib 6, thbase 9, thevent 5, modload 3, loadcore 2 | smap v1.1: 4 slots (0–3 only) | — | — |
| R14 | SPDUART | 40 | modem 2, netdev 1, dev9 4, intrman 2, loadcore 2, stdio 1, sysclib 9, thbase 10, thevent 5, ioman 3, modload 1 | spduart v1.1: 4 slots (0–3 only) | — | — |
| R15 | USBD | 28 | sysmem 2, loadcore 2, intrman 6, stdio 1, thbase 6, thevent 5, thsemap 4, sysclib 2 | usbd v1.1: 19 slots (0–18), all live | — | — |
| R16 | USBKB | 27 | usbd 9, sysmem 2, intrman 2, sifcmd 6, stdio 1, sysclib 2, thbase 5 | — none — | 0x80000211 @0x74c → 0x76c | — |
| R17 | VOIPF | 39 | lgaud 14, inet 9, intrman 2, sifcmd 4, sifman 1, stdio 1, sysclib 3, thbase 3, vblank 2 | — none — | 0x237 @0xdec → 0x890 | — |

Disc-internal linkage (importer → provider lib): libsd ← SNDDRV, SDRDRV;
sio2man ← MCMAN, PADMAN; mcman ← MCSERV; usbd ← LGAUD, USBKB; lgaud ← VOIPF;
inet ← DRTYSCKF, INETCTL, LIBNET, VOIPF; netdev ← PPP, PPPOE, SMAP, SPDUART;
modem ← PPPOE, SPDUART; inetctl ← DRTYSCKF, LIBNET; netcnf ← DRTYSCKF, INETCTL;
dev9 ← SMAP, SPDUART; msifrpc ← LIBNET.
No on-disc importers: sdrdrv, mcserv, padman, Libnet(≥4), smap(≥4), spduart(≥4).
All other imported libs are ROM-resident (intrman, loadcore, stdio, sysclib,
sysmem, thbase, thevent, thsemap, thmsgbx, sifcmd, sifman, ioman, dmacman,
cdvdman, secrman, modload, vblank) — import closure complete, nothing dangling.

## 4. SND deep section (SND audio-path modules only)

### 4a. SNDDRV.IRX — EA `SND_Library_EE_Driver` v8.3

Full imports (funcno = name; stub vaddr in parens; symtab-confirmed, §5):

- libsd (req v1.5): 4 sceSdInit (0x9d74), 5 sceSdSetParam (0x9d7c),
  6 sceSdGetParam (0x9d84), 7 sceSdSetSwitch (0x9d8c), 9 sceSdSetAddr (0x9d94),
  10 sceSdGetAddr (0x9d9c), 11 sceSdSetCoreAttr (0x9da4),
  17 sceSdVoiceTrans (0x9dac), 18 sceSdBlockTrans (0x9db4),
  20 sceSdBlockTransStatus (0x9dbc), 23 sceSdSetEffectAttr (0x9dc4),
  26 sceSdSetTransIntrHandler (0x9dcc)
- sysmem (v1.1): 4 AllocSysMemory, 5 FreeSysMemory, 14 Kprintf
- intrman (v1.2): 17 CpuSuspendIntr, 18 CpuResumeIntr
- loadcore (v1.3): 5 FlushDcache (no RegisterLibraryEntries → exports nothing)
- sifcmd (v1.1): 4 sceSifInitCmd, 8 sceSifSetCmdBuffer, 10 sceSifAddCmdHandler,
  12 sceSifSendCmd, 13 isceSifSendCmd, 17 sceSifRegisterRpc,
  19 sceSifSetRpcQueue, 20 sceSifGetNextRequest, 21 sceSifExecRequest
  (no BindRpc/CallRpc → pure server side)
- sifman (v1.1): 8 sceSifDmaStat
- sysclib (v1.3): 8 look_ctype_table, 14 memset, 19 sprintf, 27 strlen
- thbase (v1.2): 4 CreateThread, 6 StartThread, 20 GetThreadId, 24 SleepThread,
  25 WakeupThread, 26 iWakeupThread, 33 DelayThread, 34 GetSystemTime,
  40 SysClock2USec

RPC sids registered: one — **0x534E44** (`SND`) @0x9310 → handler 0x8bf0
(`SNDIOP_dispatchrpc` per symtab), queue a3 = s1+0x5bf8. SifRpcData* a0 =
s1+0x6410 (s1-relative incoming pointer, not stack; not statically
meaningful). Direction served: EE→IOP.
RPC sids called: none (no BindRpc/CallRpc imports; no client call sites).
SIF cmd handlers served: one — **cid 0** @0x8ff8 → handler 0x8ba0
(`SNDIOP_cmdhandler` per symtab), param 0xad70. NOTE: cid comes from the jal
delay slot (`move a0,zero` at 0x8ffc); the pre-slot `lui/addiu a0` builds
0xad78 (SetCmdBuffer's buffer, §13's "cid 1" is the *send* side, next line).
SIF cmds sent (IOP→EE): **cid 1** at two `SendCmd` sites — @0x911c
(a2 size 0x20) and @0x9188 (a1 0xad30, a2 size 0x20); both set
`addiu a0,zero,1` immediately before (0x90d0, 0x913c).

Strings (RPC/commands/versions/EA internals): no numeric sid/cid strings; RPC
surface is immediate-built (`lui a1,0x53; ori a1,0x4e44`). Version handshake is
a runtime EE↔IOP check:
`* Snd::System::Init - APPLICATION LINKED WITH SND VERSION %i.%02i.%02i, BUT
LOADED SNDDRV.IRX VER %i.%02i.%02i. …`; `*** SND LIBRARY ABORTED *** %s`;
`SNDfxinitbus - … FILTER NOT SUPPORTED ON IOP …` (×4: LOW PASS FIR8, HIGH PASS,
BAND PASS, RESONANCE); `Failed to start main IOP thread.`; `Failed to start SPU
thread.`; EA src paths `ps2/sndiop.c`, `ps2/sdxa16ciop.c`, `ps2/supxaf*.c`,
`mix/…` (24 unique paths, 28 `.mdebug` lines), `cmn/…` (4 files).

Surface line: **41 imports / 0 exports / 1 sid served (EE→IOP) + cmd cid 0
served + cmd cid 1 sent ×2 sites (IOP→EE), 0 RPC client**.

### 4b. SDRDRV.IRX — Sony `sdr_driver` v4.1

Full imports:

- libsd (req v1.5): 4 sceSdInit, 5 sceSdSetParam, 6 sceSdGetParam,
  7 sceSdSetSwitch, 8 sceSdGetSwitch, 9 sceSdSetAddr, 10 sceSdGetAddr,
  11 sceSdSetCoreAttr, 12 sceSdGetCoreAttr, 13 sceSdNote2Pitch,
  14 sceSdPitch2Note, 15 sceSdProcBatch, 16 sceSdProcBatchEx,
  17 sceSdVoiceTrans, 18 sceSdBlockTrans, 19 sceSdVoiceTransStatus,
  20 sceSdBlockTransStatus, 23 sceSdSetEffectAttr, 24 sceSdGetEffectAttr,
  25 sceSdClearEffectWorkArea, 26 sceSdSetTransIntrHandler,
  27 sceSdSetSpu2IntrHandler, 30 sceSdStopTrans, 31 sceSdCleanEffectWorkArea,
  32 sceSdSetEffectMode, 33 sceSdSetEffectModeParams
  (26 of 34 libsd slots; NOT used: 2 Quit, 21 SetTransCallback, 22 SetIRQCallback,
  28/29 Get*IntrHandlerArgument)
- intrman (v1.2): 17 CpuSuspendIntr, 18 CpuResumeIntr
- loadcore (v1.3): 6 RegisterLibraryEntries (exports `sdrdrv` v1.1, 6 slots)
- sifcmd (v1.1): 14 sceSifInitRpc, 15 sceSifBindRpc, 16 sceSifCallRpc,
  17 sceSifRegisterRpc, 19 sceSifSetRpcQueue, 22 sceSifRpcLoop
- stdio (v1.3): 4 printf
- sysclib (v1.3): 8 look_ctype_table, 29 strncmp, 36 strtol
- thbase (v1.2): 4 CreateThread, 6 StartThread, 14 ChangeThreadPriority,
  20 GetThreadId, 22 ReferThreadStatus, 24 SleepThread, 26 iWakeupThread,
  28 iCancelWakeupThread

RPC sids registered: one — **0x80000701** @0x3cc → handler 0x410.
RPC sids called: one — **0x80000704** bound @0xe34 (client struct 0x19f0, mode 0),
called @0xce0 with fno **0**, mode 0, 64-byte send (`li v0,64`), no recv.
No server of 0x80000704 exists on disc (EE-side peer, direction IOP→EE).
SIF cmd handlers: none.

Strings: `SDR driver version 4.0.1 (C) SCEI`; `PsIIsdrdrv  2700`;
`SDR driver ERROR: unknown command %x `; ` SDR driver error: invalid priority %d`;
`thpri=`; `SDR driver: thread priority: main=%d, callback=%d`;
` Exit rsd_main `; `SDR callback thread created`.

Surface line: **47 imports / 6 export slots (5 live: sdrdrv 1–5) /
1 sid served (EE→IOP: 0x80000701) + 1 sid called (IOP→EE: 0x80000704, fno 0)**.

### 4c. MSIFRPC.IRX — Sony `IOP_MSIF_rpc_interface` v2.5

Full imports:

- sysmem (v1.1): 4 AllocSysMemory, 5 FreeSysMemory, 14 Kprintf
- loadcore (v1.3): 6 RegisterLibraryEntries (exports `msifrpc` v1.1)
- intrman (v1.2): 17 CpuSuspendIntr, 18 CpuResumeIntr
- stdio (v1.3): 4 printf
- sifcmd (v1.1): 6 sceSifGetSreg, 10 sceSifAddCmdHandler, 12 sceSifSendCmd,
  13 isceSifSendCmd (no InitRpc/Bind/Call/RegisterRpc — NOT an RPC endpoint;
  it is the multi-thread SIF-RPC *transport* used by LIBNET)
- sifman (v1.1): 7 sceSifSetDma
- thbase (v1.2): 4 CreateThread, 5 DeleteThread, 6 StartThread,
  10 TerminateThread, 14 ChangeThreadPriority, 20 GetThreadId,
  22 ReferThreadStatus, 24 SleepThread, 26 iWakeupThread, 33 DelayThread
- thmsgbx (v1.1): 4 CreateMbx, 7 iSendMbx, 8 ReceiveMbx

RPC sids registered/called: none. SIF cmd handlers served: three —
**cid 0x80000019** @0x100 → 0x298; **cid 0x8000001a** @0x118 → 0x510;
**cid 0x8000001d** @0x130 → 0x3c4 (queue/param 0x2380 all three).
SIF cmds sent (IOP→EE): **0x80000001** @0x164 (a2 size 0x18);
**0x80000018** @0xa14, @0xc80, @0xf9c (a2 size 0x40 each).
Exports `msifrpc` v1.1: 22 slots, live only idx 4 (sceSifMInitRpc) and
idx 17 (sceSifMEntryLoop); rest dummy 0x1060; idx 16 (MTermRpc slot) is dummy.

Strings: `Multi-thread available sifrpc module...`; `%s(): sceSifSendCmd
failed.`; `AllocSysMemory/CreateMbx/ReceiveMbx/StartThread… failed.`;
`sceSifMEntryLoop`; `PsIImsifrpc 2700`.

Surface line: **25 imports / 22 export slots (2 live: msifrpc 4,17) /
0 sids + 3 cmd cids served + 2 cmd cids sent (0x80000001 ×1, 0x80000018 ×3)**.

### 4d. LIBSD.IRX — Sony `Sound_Device_Library` v3.3

Full imports (no sifcmd at all — no RPC surface; lowest-level SPU2 driver):

- intrman (v1.2): 4 RegisterIntrHandler, 5 ReleaseIntrHandler, 6 EnableIntr,
  7 DisableIntr, 17 CpuSuspendIntr, 18 CpuResumeIntr, 23 QueryIntrContext
- loadcore (v1.3): 5 FlushDcache, 6 RegisterLibraryEntries
  (export table at module offset 0; `lui a0,0; addiu a0,a0,0` + base reloc)
- sifman (v1.1): 7 sceSifSetDma, 8 sceSifDmaStat
- sysclib (v1.3): 17 bzero
- thevent (v1.1): 4 CreateEventFlag, 5 DeleteEventFlag, 6 SetEventFlag,
  7 iSetEventFlag, 8 ClearEventFlag, 9 iClearEventFlag, 10 WaitEventFlag

RPC sids registered/called: none. SIF cmd handlers: none.
Exports `libsd` v1.5: 34 slots (idx 0–33), all live — the full `sceSd*` surface
consumed by SNDDRV (12) and SDRDRV (26); union = 26 distinct (SNDDRV ⊆ SDRDRV).

Strings: module name + `PsIIlibsd   2700` only (no diagnostics, no version text).

Surface line: **19 imports / 34 live exports (libsd 0–33) / 0 sids**.

## 5. Method (provenance, not verdicts)

- Import groups: `.text` scan for LE magic `0x41e00000` → header
  `{magic, 0, ver2B, 0, name8}` + 8-byte stubs `{jr ra; addiu zero,zero,funcno}`.
  funcno→name via PCSX2 `IopModuleNames.cpp` (`pcsx2-ref`, read-only).
- Export tables: `.text` scan for LE magic `0x41c00000` →
  `{magic, 0, ver2B, 0, name8, u32 func[idx]…}`; slot count ends at first
  out-of-range/un-aligned word; dummy-fill tables (INET, MSIFRPC, PPP, MCMAN,
  INETCTL) classified by modal value; every on-disc import max-funcno fits its
  provider's live set (§3 linkage cross-checked both directions).
- RPC/cmd immediates: `jal`→stub map + 48-insn linear lui/ori/addiu/move
  resolution over a0–a2 **including the jal delay slot**; every site in §3/§4
  re-verified by hand disassembly.
- SNDDRV `.symtab` (364 entries) independently confirms all 41 stub names
  (e.g. `sceSdBlockTrans@0x9db4` = libsd:18, `sceSifRegisterRpc@0x9e9c` =
  sifcmd:17), both RPC handlers (`SNDIOP_dispatchrpc@0x8bf0`,
  `SNDIOP_cmdhandler@0x8ba0`), and `start@0x9244`.
- sid mnemonics: 0x534E44 = `SND`, 0x50494C42 = `BLIP` (LE byte order).
- Rerun (independent, same brief): fresh extract to `/tmp/t3-irx/t3-rerun/`;
  per-word capstone MIPS disassembly (robust to export tables at vaddr 0,
  which truncate linear disassembly — that hid MCSERV's sites in rerun v1);
  64-insn lui/ori/addiu/move resolution incl. jal delay slot; s-reg/gp
  sources kept symbolic (`s1+0x6410`); every site hand-verified against the
  printed window. funcno→name mappings (§4/§6) carried from the PCSX2 table
  cited above; all funcnos + counts re-verified, names spot-checked on the
  SND path only.
- No boots, no harness, no fork changes, no adb, no leases; ISO read-only;
  scratch in `/tmp/t3-irx/` only.

## 6. Full import lists — non-SND modules (funcno = name)

- DEV9 (16): stdio 4 printf; loadcore 6 RegisterLibraryEntries,
  12 QueryBootMode; thbase 33 DelayThread; thsemap 4 CreateSema, 6 SignalSema,
  8 WaitSema; ioman 20 AddDrv, 21 DelDrv; dmacman 16 SetDPCR2, 17 GetDPCR2;
  intrman 4 RegisterIntrHandler, 6 EnableIntr, 7 DisableIntr,
  17 CpuSuspendIntr, 18 CpuResumeIntr.
- DRTYSCKF (59): inet 4 Name2Address, 6 Create, 7 Open, 8 Close, 9 Recv,
  10 Send, 11 Abort, 12 RecvFrom, 13 SendTo, 15 Control, 24 GetInterfaceList,
  25 InterfaceControl, 30 GetNameServers (all `sceInet*`); netcnf 4 GetCount,
  5 GetList, 6 LoadEntry (`sceNetCnf*`); inetctl 4 SetConfiguration,
  6 DownInterface, 7 SetAutoMode, 8 RegisterEventHandler, 10 GetState
  (`sceInetCtl*`); sysmem 4 Alloc, 5 Free; intrman 8 CpuDisableIntr,
  9 CpuEnableIntr; sifcmd 4 InitCmd, 8 SetCmdBuffer, 10 AddCmdHandler;
  sifman 7 SetDma, 8 DmaStat; stdio 4 printf; sysclib 11 memcmp, 12 memcpy,
  14 memset, 19 sprintf, 20 strcat, 21 strchr, 22 strcmp, 23 strcpy,
  27 strlen, 29 strncmp, 30 strncpy, 34 strstr, 36 strtol; thbase
  4 CreateThread, 5 DeleteThread, 6 StartThread, 10 TerminateThread,
  19 iReleaseWaitThread, 20 GetThreadId, 24 SleepThread, 25 WakeupThread,
  33 DelayThread, 34 GetSystemTime; thsemap 4 CreateSema, 5 DeleteSema,
  6 SignalSema, 8 WaitSema, 9 PollSema.
- INET (40): sysmem 4,5; intrman 17,18; loadcore 6 Register, 7 Release;
  stdio 4; sysclib 8 look_ctype_table, 12 memcpy, 19 sprintf, 22 strcmp,
  23 strcpy, 27 strlen, 29 strncmp, 36 strtol, 40 wmemcopy; thbase 4,5,6,8,10,
  14 ChangeThreadPriority, 22 ReferThreadStatus, 33 DelayThread,
  34 GetSystemTime, 35 SetAlarm, 37 CancelAlarm, 39 USec2SysClock,
  40 SysClock2USec; thevent 4,5,6,7,10; thsemap 4,5,6,8; cdvdman 24 ReadClock;
  modload 16 GetModuleIdList.
- INETCTL (49): inet 4,5 Address2String, 24,25, 27 GetRoutingTable,
  28 AddRouting, 29 DelRouting, 30, 31 AddNameServer, 32 DelNameServer,
  39 WaitInterfaceEvent, 40 SignalInterfaceEvent; netcnf 12 LoadConf,
  13 LoadDial, 14 MergeConf; loadcore 6,7; stdio 4; sysclib 8,16 bcopy,
  17 bzero, 19, 22, 27, 29, 36; thbase 4,5,6,10,14,22,33,34,40; thevent
  4,5,6, 8 ClearEventFlag, 10; thsemap 4,5,6,8; sysmem 4,5; intrman 17,18;
  modload 16.
- LGAUD (34): usbd 4 RegisterLdd, 5 UnregisterLdd, 6 ScanStaticDescriptor,
  7 SetPrivateData, 8 GetPrivateData, 9 OpenPipe, 10 ClosePipe,
  11 TransferPipe, 18 MultiIsochronousTransfer (`sceUsbd*`); sysmem 4,5;
  intrman 17,18; loadcore 6,7; modload 17 ReferModuleStatus,
  18 GetModuleIdListByName; sifcmd 14 InitRpc, 17 RegisterRpc, 19 SetRpcQueue,
  22 RpcLoop; stdio 4; sysclib 7 tolower, 14 memset, 27 strlen, 36 strtol;
  thbase 4,6, 9 ExitDeleteThread, 20 GetThreadId; thsemap 4,5,6,8.
- LIBNET (45): msifrpc 4 MInitRpc, 17 MEntryLoop; inet twenty: 4–13, 14
  Address2Name, 15 Control, 16 Poll, 24,25, 27 GetRoutingTable,
  30 GetNameServers, 36 ChangeThreadPriority, 38 GetLog, 41 AbortLog;
  inetctl 4–10 (SetConfiguration, UpInterface, DownInterface, SetAutoMode,
  RegisterEventHandler, UnregisterEventHandler, GetState); intrman 17,18;
  loadcore 6,7; sifcmd 14 InitRpc; stdio 4; sysclib 22 strcmp; thbase
  4,5,6,10,33; thsemap 4,5,6,8.
- MCMAN (33): loadcore 6,7; intrman 17,18; sio2man 24 signalExchange2,
  25 packetExchange, ?26, ?57, ?59; sysclib 12,14,20,22,23,27,29,30;
  stdio 4; thbase 33,35,39; thsemap 4,5,6, 7 iSignalSema, 8; modload ?13;
  ioman 20,21; secrman ?4,?5,?6; cdvdman 24.
- MCSERV (53): loadcore 6,7; intrman 17,18; sysclib 12,14,29,36; stdio 4;
  sifman 5 Init, 7 SetDma, 8 DmaStat, 29 CheckInit; sifcmd 14,17,19,22,
  23 GetOtherData, 24 RemoveRpc, 25 RemoveRpcQueue; thbase 4,5,6,10,14,20,22,
  33; thsemap 6,8; mcman 23 unnamed: 6–16,21–24,26,36–39,42,45,53.
- NETCNF (43): sysmem 4,5; loadcore 6,7; intrman 17,18; thbase 33; thsemap
  4,5,6,8; sysclib 8,12,14,16,17,19,20,21,22,23, 25 index, 27,29,36; ioman
  4 open, 5 close, 6 read, 7 write, 8 lseek, 10 remove, 11 mkdir, 12 rmdir,
  13 dopen, 14 dclose, 15 dread, 16 getstat, 17 chstat, 25 rename, 27 sync,
  31 devctl; stdio 4; cdvdman 22 _sceCdRI.
- PADMAN (38): sysmem 14 Kprintf; loadcore 6; intrman 17,18; stdio 4; sio2man
  11 get8270_recv2, ?46, ?51, ?52, ?57, ?58, ?60; thbase 4,5,6,8 ExitThread,
  20,22, 23 iReferThreadStatus; thevent 4,5,6,7,8,10; sifman 5,7,8,29;
  sifcmd 14,17,19,22; vblank 8 RegisterVblankHandler, 9 ReleaseVblankHandler;
  sysclib 8,29,36.
- PPP (43): netdev 4 RegisterNetDevice … 13 FreePkt (`sceInet*`, idx 4–13);
  intrman 17,18; loadcore 6,7; sysclib 8,12,20,22,23,27,29,30,36; thbase
  4,5,6,8,10,14,33,35,37,39; thevent 4,5,6,7,10; thsemap 4,5,6,8; modload 16.
- PPPOE (39): modem 4 RegisterDevice, 5 UnregisterDevice (`sceModem*`);
  netdev 6 AllocMem … 15 UnregisterPPPoE (idx 6–15); sysclib 8, 15 bcmp,
  16,17,22,29,36; thbase 4,5,6,8,10,35,37,39; thevent 4,5,6,7,10; thsemap
  4,5,6,8; intrman 17,18; modload 16.
- SIO2MAN (28): loadcore 6; intrman 4,5,6,7,17,18; stdio 4; dmacman 28 SetDMA,
  32 StartTransfer, 33 SetVal, 34 EnableDMAch, 35 DisableDMAch; thbase 4,6,20;
  thevent 4,6,7,8,10; thsemap 4,6,8, 11 ReferSemaStatus; sysclib 8,29,36.
- SMAP (42): netdev 4,5, 8 PktEnQ, 9 PktDeQ, 11 Printf, 12 AllocPkt,
  13 FreePkt; dev9 7 unnamed: 4,5,7,8,9,12,13; intrman 17,18; stdio 4;
  sysclib 8,16,17,22,29,36; thbase 4,5,6,10,14,33,35,37,39; thevent
  4,5,6,7,10; modload 16,17, 22 SearchModuleByName; loadcore 6,7.
- SPDUART (40): modem 4,5; netdev 11 Printf; dev9 4 unnamed: 4,7,8,11;
  intrman 17,18; loadcore 6,7; stdio 4; sysclib (req v1.4 — only module
  above v1.3) 8,16,17,19,22,23,27,29,36; thbase 4,5,6,10,14,24,33,35,37,39;
  thevent 4,5,6,7,10; ioman 4,5,6; modload 16.
- USBD (28): sysmem 4,5; loadcore 6,7; intrman 4,5,6,7,17,18; stdio 4; thbase
  4,5,6,10,14,33; thevent 4,5,6,7,10; thsemap 4,5,6,8; sysclib 16,17.
- USBKB (27): usbd 4–11 (as LGAUD) + 13 GetDeviceLocation; sysmem 4,5;
  intrman 17,18; sifcmd 14,17,19,22,24,25; stdio 4; sysclib 22,36; thbase
  4,5,6,10,20.
- VOIPF (39): lgaud 14 unnamed: 4–8,11–14,16–20; inet 6,7,8,11,12,13,15,24,25;
  intrman 8,9; sifcmd 14,17,19,22; sifman 7; stdio 4; sysclib 11,14,36;
  thbase 4,6,33; vblank 4 WaitVblankStart, 6 WaitVblank.

## 7. Gap rows (hex-scan limits → disassembler-brief inputs)

1. Unmapped import funcnos (no PCSX2 table entry): mcman ×23, dev9 ×9
   (7 SMAP + 4 SPDUART, overlap), lgaud ×14, sio2man ×8 (?26 ?46 ?51 ?52 ?57
   ?58 ?59 ?60), modload:13, secrman ×3. Names need a second export-table
   source or per-site disassembly.
2. SDRDRV CallRpc sid is by association (shared client struct 0x19f0 with the
   0x80000704 BindRpc), not by immediate — no CallRpc encodes its sid.
3. No on-disc server for sid 0x80000704 (SDRDRV's peer is EE-side); likewise
   the EE-side clients of every §3 server sid are out of T3 scope.
4. RegisterRpc arg0 (SifRpcData*): stack-built at SDRDRV/LGAUD/VOIPF
   (sp+0x38), s1-relative at SNDDRV (s1+0x6410, incoming pointer — not
   stack, still not statically meaningful); static structs at MCSERV
   (0x3718), PADMAN (s0+0x18 = 0x976c/0x984c), USBKB (s0+0x18 = 0x20ac).
5. SNDDRV serves SIF cmd cid 0 (@0x8ff8, cid from the jal delay slot
   `move a0,zero`) and SENDS SIF cmd cid 1 (@0x911c and @0x9188, each
   preceded immediately by `addiu a0,zero,1` at 0x90d0/0x913c). §13's
   "cmd handler cid 1" matches the send direction; the EE-side handler
   of cid 1 is out of T3 scope.
6. Module version (`.iopmod`) ≠ library interface version (export table):
   e.g. LIBSD mod v3.3 / lib v1.5, MSIFRPC mod v2.5 / lib v1.1, NETCNF mod
   v1.20 / lib v1.32, SIO2MAN mod v3.0 / lib v2.4, MCMAN mod v2.34 / lib v2.7.
   Required-version bytes tabled raw as major.minor; loader check semantics
   unverified (no boots per brief).
7. sio2man export slots 5–7 hold small values (20/40/60, in-text-range);
   counted live; bodies unexamined.
8. One false-positive `0x41c00000` at LGAUD+0x76ee excluded (non-printable
   name, zero slots); real table at 0x7f30.
9. RPC handler bodies and CallRpc fno dispatch (esp. SND 0x534E44 handler
   0x8bf0, SDR 0x80000701 handler 0x410) need a disassembler brief — T3
   records entry points only.
10. PADMAN imports `sdrdrv`? No — verified: nothing on disc imports sdrdrv,
    mcserv, or padman; nothing on disc serves 0x80000704. (Absence claims from
    exhaustive import-table + RegisterRpc-site scans above.)
11. Indirect calls: DRTYSCKF (48 jalr), SNDDRV (29), PADMAN (14), MSIFRPC (1),
    SDRDRV (1) use `jalr`; LGAUD/LIBNET/MCSERV/USBKB/VOIPF have none. Zero
    jalr sites resolve to a sifcmd stub within a 24-insn const window, so
    the direct-jal census above is complete against address-materializing
    callers; a stub address loaded via `lw` from a table would escape this
    check (no such table observed).
12. DRTYSCKF (468 syms) and VOIPF (120 syms) retain `.symtab`/`.mdebug`
    (rerun finding; SNDDRV's was already used). Unmined: handler names for
    VOIPF 0x890 / DRTYSCKF 0x17b8 and own-symbol names for the 14 unnamed
    `lgaud` imports — input for a disassembler brief, not re-scanned here.
13. PADMAN embeds the string ` SDR driver error: invalid priority %d`,
    also present in SDRDRV. Shared-source artefact or common-helper copy;
    recorded, not investigated.

## 8. Rerun verification log (second agent, same brief)

| Check | Result |
| --- | --- |
| ISO bytes / file count / all 22 sizes / all 22 MD5s / `file(1)` | match |
| Module name / version / entry ×22 (`.iopmod` + ELF header parse) | match |
| N imports + per-lib counts + full funcno lists ×22 | match incl. §6 |
| Export lib / version / slot count ×18 tables (5 modules none) | match |
| Export live sets | match except INETCTL 11 (was 12) and SIO2MAN NULLs {4,27} (was {0,27}) |
| RPC-S sid + call pc + handler ×8 sites (7 modules) | match (MCSERV confirmed after disasm fix) |
| RPC-C sid + client struct + fno (SDRDRV) | match (client 0x19f0, fno 0, 64 B) |
| CMD cids served (SNDDRV, MSIFRPC ×3, DRTYSCKF) | match |
| SND `SendCmd` cid 1 ×2, MSIF `SendCmd` ×4 | new (§3–§4) |
| SNDDRV symtab 364 + handler/stub names | match |
| Origin calls + stamps | match except DEV9 stamp `PsIIDEV9 2710` added |
| Reloc types | corrected: {32,26,HI16,LO16}, not 32-only |
| Symbol retention | corrected: 3 EA modules, not SNDDRV-only |
| `jalr`-hidden RPC sites | none found (see gap 11) |

---
T3 static brief. No leases taken, no boots, no fork changes, no adb. Evidence
committed `[T3]` with `Orchestrated-By: Muse Code` trailer; never pushed.
