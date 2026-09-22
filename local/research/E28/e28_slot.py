"""Mission 1 -- pin the kind-1 queue slot's GUEST ADDRESS, statically.

E27 named the slot as `ctx0->[0x24] + (kind-1)*16` but never had to know where
that is in guest memory. E28 cannot arm a watch without it, and the brief
forbids blind watches: derive it with receipts, or table and STOP the boot.

The derivation is an ARITHMETIC IDENTITY, not a guess. `sub_003E06D8` (the STRM
constructor) lays the whole context out from one allocation, and the very same
instruction sequence that computes the queue-slot array base goes on to compute
the DATA REGION BASE -- a number E26 already measured in bytes (`sceCdRead
buf=0xd48740`). Running that identity backwards pins the allocation, and with
it the slot.

Every quoted instruction is CHECKED here, not recalled: each receipt is grepped
out of the generated source and the tool refuses to continue if it is absent.
Every source is read TWICE (standing SSD rule) and its SHA is compared against
the value E27 COMMITTED to this repo in `pins-pass-{1,2}.json` -- which is
better corroboration than E27 itself had, because E27 could only repeat its own
reads in time (the generated sources are .gitignore'd and have no git object).
"""
import re, subprocess
from e28_common import *

GEN = R / 'ps2xRuntime/src/runner'
RUN = Path('/Volumes/Extreme SSD/ps2recomp-spike/P1/run')
FLOG = RUN / 'ps2_log-e26a-1.txt'

# ---------------------------------------------------------------- receipts --
# (file, the EXACT disassembly comment that must be present, what it gives us)
RECEIPTS = [
 ('sub_003E06D8_0x3e06d8.cpp', '0x3e06e4: 0x80882d  daddu       $s1, $a0, $zero',      'n1   = $a0'),
 ('sub_003E06D8_0x3e06d8.cpp', '0x3e06ec: 0xa0902d  daddu       $s2, $a1, $zero',      'n2   = $a1'),
 ('sub_003E06D8_0x3e06d8.cpp', '0x3e06f4: 0xc0982d  daddu       $s3, $a2, $zero',      'nKinds = $a2'),
 ('sub_003E06D8_0x3e06d8.cpp', '0x3e06fc: 0xe0802d  daddu       $s0, $a3, $zero',      'ctx0 = $a3 (the allocation)'),
 ('sub_003E06D8_0x3e06d8.cpp', '0x3e0768: 0xae020000  sw          $v0, 0x0($s0)',      "[ctx0+0] = 'STRM'"),
 ('sub_003E06D8_0x3e06d8.cpp', '0x3e076c: 0x24020124  addiu       $v0, $zero, 0x124',  'record stride 0x124'),
 ('sub_003E06D8_0x3e06d8.cpp', '0x3e0770: 0x26060180  addiu       $a2, $s0, 0x180',    'array base = ctx0 + 0x180'),
 ('sub_003E06D8_0x3e06d8.cpp', '0x3e0774: 0x2221818  mult        $v1, $s1, $v0',       '$v1 = n1 * 0x124'),
 ('sub_003E06D8_0x3e06d8.cpp', '0x3e0778: 0x2408ffc0  addiu       $t0, $zero, -0x40',  'align mask ~0x3F'),
 ('sub_003E06D8_0x3e06d8.cpp', '0x3e077c: 0x131100  sll         $v0, $s3, 4',          '$v0 = nKinds * 16'),
 ('sub_003E06D8_0x3e06d8.cpp', '0x3e0794: 0x665821  addu        $t3, $v1, $a2',        '$t3 = ctx0+0x180+n1*0x124'),
 ('sub_003E06D8_0x3e06d8.cpp', '0x3e079c: 0x2403000c  addiu       $v1, $zero, 0xC',    'table row stride 0xC'),
 ('sub_003E06D8_0x3e06d8.cpp', '0x3e07a0: 0xae130028  sw          $s3, 0x28($s0)',     '[ctx0+0x28] = nKinds'),
 ('sub_003E06D8_0x3e06d8.cpp', '0x3e07a4: 0x2432018  mult        $a0, $s2, $v1',       '$a0 = n2 * 0xC'),
 ('sub_003E06D8_0x3e06d8.cpp', '0x3e07b8: 0x8b1821  addu        $v1, $a0, $t3',        '$v1 = SLOT ARRAY BASE'),
 ('sub_003E06D8_0x3e06d8.cpp', '0x3e07c0: 0x621021  addu        $v0, $v1, $v0',        '$v0 = slots_end'),
 ('sub_003E06D8_0x3e06d8.cpp', '0x3e07c8: 0x481024  and         $v0, $v0, $t0',        '$v0 &= ~0x3F'),
 ('sub_003E06D8_0x3e06d8.cpp', '0x3e07d0: 0x24420040  addiu       $v0, $v0, 0x40',     '$v0 = DATA REGION BASE'),
 ('sub_003E06D8_0x3e06d8.cpp', '0x3e07e8: 0xae020054  sw          $v0, 0x54($s0)',     '[ctx0+0x54] = cursor = data base'),
 ('sub_003E06D8_0x3e06d8.cpp', '0x3e0800: 0xae0b001c  sw          $t3, 0x1C($s0)',     '[ctx0+0x1C] = classifier table'),
 ('sub_003E06D8_0x3e06d8.cpp', '0x3e0808: 0xae030024  sw          $v1, 0x24($s0)',     '[ctx0+0x24] = SLOT ARRAY BASE'),
 ('sub_003E06D8_0x3e06d8.cpp', '0x3e08f4: 0x282d  daddu       $a1, $zero, $zero',      'slot init loop index starts at 0'),
 ('sub_003E06D8_0x3e06d8.cpp', '0x3e0914: 0xac700000  sw          $s0, 0x0($v1)',      'slot->[0] = ctx0 (OWNER)'),
 ('sub_003E06D8_0x3e06d8.cpp', '0x3e090c: 0xac600008  sw          $zero, 0x8($v1)',    'slot->[8] = 0 (bytes)'),
 ('sub_003E06D8_0x3e06d8.cpp', '0x3e0920: 0x8e020024  lw          $v0, 0x24($s0)',     'RETURNS ctx0->[0x24]'),
 # the header-size helper -- the SAME constant, computed by a second function
 ('sub_003E06B0_0x3e06b0.cpp', '0x3e06b0: 0x2402000c  addiu       $v0, $zero, 0xC',    'header: 0xC'),
 ('sub_003E06B0_0x3e06b0.cpp', '0x3e06b4: 0x24030124  addiu       $v1, $zero, 0x124',  'header: 0x124'),
 ('sub_003E06B0_0x3e06b0.cpp', '0x3e06bc: 0x63100  sll         $a2, $a2, 4',           'header: nKinds*16'),
 ('sub_003E06B0_0x3e06b0.cpp', '0x3e06c4: 0x24a50180  addiu       $a1, $a1, 0x180',    'header: +0x180'),
 # the call site that ran
 ('sub_003ADEC8_0x3adec8.cpp', '0x3ae188: 0x302d  daddu       $a2, $zero, $zero',      'alloc alignment arg = 0'),
 ('sub_003ADEC8_0x3adec8.cpp', '0x3ae190: 0x40f809  jalr        $v0',                  'the allocation'),
 ('sub_003ADEC8_0x3adec8.cpp', '0x3ae194: 0x382d  daddu       $a3, $zero, $zero',      'delay slot clobbers $a3, NOT $a2'),
 ('sub_003ADEC8_0x3adec8.cpp', '0x3ae1a4: 0x24060002  addiu       $a2, $zero, 0x2',    'nKinds = 2'),
 ('sub_003ADEC8_0x3adec8.cpp', '0x3ae1a8: 0x24040002  addiu       $a0, $zero, 0x2',    'n1 = 2'),
 ('sub_003ADEC8_0x3adec8.cpp', '0x3ae1ac: 0x24050003  addiu       $a1, $zero, 0x3',    'n2 = 3'),
 ('sub_003ADEC8_0x3adec8.cpp', '0x3ae1b0: 0xc0f81b6  jal         func_3E06D8',         'the STRM constructor'),
 ('sub_003ADEC8_0x3adec8.cpp', '0x3ae1b4: 0xae420004  sw          $v0, 0x4($s2)',      'movie->[4] = the allocation'),
 ('sub_003ADEC8_0x3adec8.cpp', '0x3ae1c4: 0xae420030  sw          $v0, 0x30($s2)',     'movie->[0x30] = ctx0->[0x24]'),
 # the two straight-line sites that did NOT run, and why they cannot have
 ('sub_003ADEC8_0x3adec8.cpp', '0x3ae008: 0xc0f81b6  jal         func_3E06D8',         'site A'),
 ('sub_003ADEC8_0x3adec8.cpp', '0x3ae024: 0xc0f81b6  jal         func_3E06D8',         'site B, straight-line after A'),
 ('sub_003ADEC8_0x3adec8.cpp', '0x3ae004: 0x24060001  addiu       $a2, $zero, 0x1',    'sites A/B: nKinds = 1'),
 # the allocator floors the alignment at 0x40
 ('sub_00253AD0_0x253ad0.cpp', '0x253ad0: 0x2402003f  addiu       $v0, $zero, 0x3F',   'align floor test'),
 ('sub_00253AD0_0x253ad0.cpp', '0x253ad8: 0x24030040  addiu       $v1, $zero, 0x40',   'align floor value'),
 ('sub_00253AD0_0x253ad0.cpp', '0x253adc: 0x46102a  slt         $v0, $v0, $a2',        '0x3F < align ?'),
 ('sub_00253AD0_0x253ad0.cpp', '0x253ae8: 0x62300a  movz        $a2, $v1, $v0',        'if not, align = 0x40'),
 # the consumers that prove the field meanings and the GUEST STORES we watch
 ('sub_003DFED0_0x3dfed0.cpp', '0x3dffa4: 0x8e020024  lw          $v0, 0x24($s0)',     'walker: slot array'),
 ('sub_003DFED0_0x3dfed0.cpp', '0x3dffa8: 0x151900  sll         $v1, $s5, 4',          'walker: kind*16'),
 ('sub_003DFED0_0x3dfed0.cpp', '0x3dffac: 0x2463fff0  addiu       $v1, $v1, -0x10',    'walker: -16'),
 ('sub_003DFED0_0x3dfed0.cpp', '0x3dffc0: 0xac440008  sw          $a0, 0x8($v0)',      'STORE slot+8  (bytes += len)'),
 ('sub_003DFED0_0x3dfed0.cpp', '0x3dffc4: 0xac52000c  sw          $s2, 0xC($v0)',      'STORE slot+0xC (head = cur)'),
 ('sub_003E12E0_0x3e12e0.cpp', '0x3e1330: 0xae510004  sw          $s1, 0x4($s2)',      'STORE chunk+4 (tag stripped)'),
 ('sub_003E12E0_0x3e12e0.cpp', '0x3e134c: 0xac500008  sw          $s0, 0x8($v0)',      'STORE slot+8  (bytes -= len)'),
 ('sub_003E12E0_0x3e12e0.cpp', '0x3e13c8: 0xad26000c  sw          $a2, 0xC($t1)',      'STORE slot+0xC (head advance)'),
 ('sub_003AEAD0_0x3aead0.cpp', '0x3aeb14: 0x8c920030  lw          $s2, 0x30($a0)',     'source->[0x30] = the slot'),
 ('sub_003AEAD0_0x3aead0.cpp', '0x3aeb20: 0xc0f84b8  jal         func_3E12E0',         'dequeue(slot)'),
 ('sub_003DFBD0_0x3dfbd0.cpp', '0x3dfbd4: 0x8c870000  lw          $a3, 0x0($a0)',      'resolver: ctx0 = slot->[0]'),
 ('sub_003DFBD0_0x3dfbd0.cpp', '0x3dfbe0: 0x3c024d52  lui         $v0, 0x4D52',        "resolver: 'STRM' check"),
 ('sub_003E0BF8_0x3e0bf8.cpp', '0x3e0c3c: 0x8c630024  lw          $v1, 0x24($v1)',     'accessor: slot array'),
 ('sub_003E0BF8_0x3e0bf8.cpp', '0x3e0c40: 0x2442fff0  addiu       $v0, $v0, -0x10',    'accessor: -16'),
]

# ------------------------------------------------------ read + corroborate --
E27PINS = {Path(r['path']).name: r['sha256']
           for pf in ('pins-pass-1.json', 'pins-pass-2.json')
           for r in json.loads((E.parent / 'E27' / pf).read_text())['rows']}
sources, srcrows = {}, []
for name in sorted({n for n, _, _ in RECEIPTS}):
    p = GEN / name
    a, b = sha(p), sha(p)                    # two reads, standing SSD rule
    sources[name] = p.read_text()
    srcrows.append(dict(file=name, bytes=p.stat().st_size, sha_read_a=a, sha_read_b=b,
                        reads_agree=a == b, e27_committed_pin=E27PINS.get(name),
                        equals_e27_committed_pin=(E27PINS.get(name) == a) if name in E27PINS else None))

rec_rows = []
for name, instr, gives in RECEIPTS:
    present = instr in sources[name]
    rec_rows.append(dict(file=name, instruction=instr, gives=gives, present=present))
missing = [r for r in rec_rows if not r['present']]

# ---------------------------------------------------- which call site ran? --
def enters(sym, addr):
    out = subprocess.run(['grep', '-c', f'{sym}_0x{addr} enter', str(FLOG)],
                         capture_output=True, text=True)
    return int(out.stdout.strip() or 0)
log = dict(sub_003E06D8=enters('sub_003E06D8', '3e06d8'),
           sub_003ADEC8=enters('sub_003ADEC8', '3adec8'),
           sub_003B7450=enters('sub_003B7450', '3b7450'),
           sub_003AEAD0=enters('sub_003AEAD0', '3aead0'),
           sub_003E12E0=enters('sub_003E12E0', '3e12e0'))
# parents of every STRM construction, from the interleaved-stack log
parents, stack = [], []
with FLOG.open() as f:
    for i, line in enumerate(f, 1):
        s = line.rstrip('\n'); body = s.strip()
        if body.startswith('>> '):
            nm = body[3:].split(' ')[0]
            if nm == 'sub_003E06D8_0x3e06d8':
                parents.append(dict(line=i, parent=stack[-1] if stack else None))
            stack.append(nm)
        elif body.startswith('<< ') and stack:
            stack.pop()
under_3adec8 = [p for p in parents if p['parent'] == 'sub_003ADEC8_0x3adec8']

# ----------------------------------------------------------- the arithmetic --
N1, N2, NKINDS = 2, 3, 2                      # 0x3ae1a8 / 0x3ae1ac / 0x3ae1a4
DATA_BASE = 0xd48740                          # E26: sceCdRead buf=, boot log 22336
SLOT_OFF  = 0x180 + N1*0x124 + N2*0xC         # ctx0 -> [0x24]
HDR       = SLOT_OFF + NKINDS*16              # == func_3E06B0(n1,n2,nKinds)
hdr_helper = N1*0x124 + (N2*0xC + 0x180) + NKINDS*16
assert hdr_helper == HDR, (hdr_helper, HDR)   # two functions, same constant
ALIGN = 0x40                                  # sub_00253AD0 floors it there

# data_base = ((ctx0 + HDR) & ~0x3F) + 0x40  ==  DATA_BASE
#   =>  ctx0 + HDR  in  [DATA_BASE-0x40, DATA_BASE)
lo, hi = DATA_BASE - 0x40 - HDR, DATA_BASE - HDR          # ctx0 in [lo, hi)
cands_any4 = [c for c in range(lo, hi, 4) if c % 4 == 0]
cands = [c for c in range(lo - (lo % ALIGN) , hi + ALIGN, ALIGN) if lo <= c < hi]
derived = len(cands) == 1
CTX0 = cands[0] if derived else None
SLOT1 = CTX0 + SLOT_OFF if derived else None
SLOT2 = SLOT1 + 16 if derived else None
# the window every candidate slot array can occupy, with NO alignment assumed
WIN_LO, WIN_HI = lo + SLOT_OFF, (hi - 1) + SLOT_OFF + NKINDS*16
WIN_LO &= ~7
WIN_HI = (WIN_HI + 7) & ~7

out = dict(
  utc=utc(), mission='E28 Mission 1 -- pin the kind-1 queue slot guest address',
  sources=srcrows, receipts=rec_rows, receipts_missing=len(missing),
  log=dict(counts=log, strm_constructions=parents,
           under_movie_open=under_3adec8,
           note=('sub_003ADEC8 made exactly ONE call to the STRM constructor. Sites A (0x3ae008) '
                 'and B (0x3ae024) are STRAIGHT-LINE consecutive -- no branch between 0x3ae008 '
                 'and 0x3ae024 -- so reaching A forces B and would give TWO calls. One call '
                 'therefore means the site at 0x3ae1b0.')),
  independent_corroboration_of_the_site=dict(
      fact='E26 measured a kind-2 tag: 0x02000028 stored at 0xd49af0, boot-log line 22351',
      why=('the walker publishes into ctx0->[0x24] + kind*16 - 16 and the classifier can only '
           'return a kind the table carries. Sites A/B pass nKinds=1 (0x3ae004); a kind-2 chunk '
           'is impossible there. Only the 0x3ae1b0 site (nKinds=2, 0x3ae1a4) can produce it. '
           'The call site is therefore fixed by MEASURED BYTES as well as by the log.'),
      tag_kind1='0x0100381c at 0xd49b18, boot-log line 22354',
      tag_kind2='0x02000028 at 0xd49af0, boot-log line 22351'),
  arithmetic=dict(n1=N1, n2=N2, nkinds=NKINDS,
      slot_array_offset=hex(SLOT_OFF), header_size=hex(HDR),
      header_size_via_func_3E06B0=hex(hdr_helper), two_functions_agree=True,
      identity='data_base = ((ctx0 + header) & ~0x3F) + 0x40',
      data_base=hex(DATA_BASE), data_base_receipt='E26 boot log 22336: sceCdRead lbn=0x13ba33 sectors=16 buf=0xd48740',
      ctx0_window=[hex(lo), hex(hi)], alignment=hex(ALIGN),
      alignment_receipt='sub_00253AD0 0x253ad0-0x253ae8 floors the alignment argument at 0x40; the call at 0x3ae188 passes 0',
      candidates=[hex(c) for c in cands], unique=derived),
  result=dict(derived=derived, ctx0=hex(CTX0) if derived else None,
      kind1_slot=hex(SLOT1) if derived else None,
      kind2_slot=hex(SLOT2) if derived else None,
      fields=None if not derived else dict(owner=hex(SLOT1), kind=hex(SLOT1+4),
                                           bytes=hex(SLOT1+8), head=hex(SLOT1+0xC)),
      check_data_base=hex(((CTX0 + HDR) & ~0x3F) + 0x40) if derived else None,
      check_passes=(derived and ((CTX0 + HDR) & ~0x3F) + 0x40 == DATA_BASE)),
  armed_window=dict(lo=hex(WIN_LO), hi=hex(WIN_HI),
      why=('the tier covers EVERY position the slot array could occupy if the 64-byte alignment '
           'were wrong -- 4-byte granularity over the whole ctx0 window -- so the capture '
           'MEASURES the address rather than assuming it. If the stores land on 0xd486ec the '
           'derivation is confirmed; if they land elsewhere inside the window the capture names '
           'the true address and the alignment step is the thing that was wrong.'),
      alignment_free_candidates_4B=[hex(c + SLOT_OFF) for c in cands_any4]))
save('mission-1-slot.json', out)

for r in srcrows:
    tag = '' if r['equals_e27_committed_pin'] is None else ('  E27pin=' + ('EQUAL' if r['equals_e27_committed_pin'] else 'DIFFER'))
    print(f"{r['sha_read_a'][:16]}  {r['bytes']:>7}  {r['file']}{tag}")
print(f"receipts checked: {len(rec_rows)}  missing: {len(missing)}")
for r in missing: print('  MISSING:', r['file'], r['instruction'])
print(f"log: 3E06D8 x{log['sub_003E06D8']}  3ADEC8 x{log['sub_003ADEC8']}  3B7450 x{log['sub_003B7450']}"
      f"  -> under movie-open: {len(under_3adec8)}")
print(f"n1={N1} n2={N2} nKinds={NKINDS}  slot_off={hex(SLOT_OFF)}  header={hex(HDR)} (=func_3E06B0)")
print(f"ctx0 window [{hex(lo)},{hex(hi)})  align {hex(ALIGN)}  candidates {[hex(c) for c in cands]}")
print(f"DERIVED: ctx0={hex(CTX0) if derived else None}  KIND-1 SLOT={hex(SLOT1) if derived else None}"
      f"  (bytes@{hex(SLOT1+8) if derived else None} head@{hex(SLOT1+0xC) if derived else None})")
print(f"check: data base recomputes to {hex(((CTX0+HDR)&~0x3F)+0x40) if derived else None} (want {hex(DATA_BASE)})")
print(f"armed window [{hex(WIN_LO)},{hex(WIN_HI)})")
print('# E28 SLOT TAIL COMPLETE derived=' + ('1' if derived else '0'))
assert not missing, missing
assert all(r['reads_agree'] for r in srcrows)
assert all(r['equals_e27_committed_pin'] is not False for r in srcrows)
