"""E27 Missions 1-3 receipts. STATIC autopsy: sources + the retained e26a logs."""
from e27_common import *

GEN = 'ps2xRuntime/src/runner'

m1 = dict(
 question='Name the function that walked the chunk list and tagged the two '
          'length fields from pc=0x3dff8c / ra=0x3dff90, and say what it does AFTER tagging.',
 walker=dict(
   symbol='sub_003DFED0', file=f'{GEN}/sub_003DFED0_0x3dfed0.cpp',
   guest_range='0x3dfed0 - 0x3e00d4',
   tag_store_line=257, tag_store_addr='0x3dff8c',
   tag_store_text='0x3dff8c: 0xae420004  sw $v0, 0x4($s2)   (delay slot of `jal func_3E5700` at 0x3dff88)',
   why_ra_is_pc_plus_4='the store is in the DELAY SLOT of the jal at 0x3dff88, so $ra '
                       '= 0x3dff90 is that jal\'s return address, not a caller frame. '
                       'The generated file carries `case 0x3dff90u: goto label_3dff90;` '
                       'at line 26, which is the same return address.',
   tagged_value='$v0 = $s1 | ($s5 << 24)  (0x3dff84 `or $v0, $s1, $v0`, with '
                '$v0 = $s5<<24 computed at 0x3dff3c)',
   s1='the chunk TOTAL length, loaded at 0x3e006c `lw $s1, 0x4($s2)`',
   s2='the CURRENT CHUNK HEADER pointer, loaded at 0x3e0058 `lw $s2, 0x54($s0)` '
      '-- i.e. the walk cursor lives at ctx0+0x54',
   s5='the return of func_3DFE88, the chunk-KIND lookup',
   matches_capture=dict(
     line_22351=dict(addr='0xd49af0', value='0x02000028',
                     chunk='SCHl header 0xd49aec, total 40 = 0x28', kind=2),
     line_22354=dict(addr='0xd49b18', value='0x0100381c',
                     chunk='MPCh header 0xd49b14, total 14364 = 0x381c', kind=1),
     arithmetic='(kind << 24) | total  reproduces both words exactly'),
 ),
 classifier=dict(
   symbol='sub_003DFE88', file=f'{GEN}/sub_003DFE88_0x3dfe88.cpp',
   guest_range='0x3dfe88 - 0x3dfecc',
   pseudocode=['magic = *chunk                       (0x3dfe94 lw $a1, 0x0($a1))',
               'n = state->[0x20]; if (n <= 0) return -2',
               'tbl = state->[0x1C]                  ; 12-byte rows {mask, match, kind}',
               'for i in 0..n-1:',
               '    if ((magic & tbl[i].mask) == tbl[i].match) return tbl[i].kind  (0x3dfeb8 lw $v0, 0x8($a0))',
               'return -2                             (0x3dfecc addiu $v0, $zero, -0x2)'],
   meaning='the top byte is the registered chunk KIND from a {mask,match,kind} '
           'table, not a free-running visited counter'),
 what_the_top_byte_means=dict(
   written_by='sub_003DFED0 at 0x3dff8c (and re-written 64-byte-aligned at 0x3e003c)',
   read_by_producer='sub_003DFED0 at 0x3e0074 `and $v0, $s1, 0xFF000000`: a chunk whose '
                    'length field still carries a nonzero top byte is treated as STILL '
                    'QUEUED, and the walker overwrites it with an 8-byte sentinel stub '
                    '(0x3e0084 len=8, 0x3e008c magic=$s6->[0x11c]) and then STOPS '
                    '(0x3e0044: magic == sentinel -> return 1)',
   read_by_consumer='sub_003E12E0 at 0x3e132c `and $s1, $v1, 0x00FFFFFF` then 0x3e1330 '
                    '`sw $s1, 0x4($s2)`: the dequeue STRIPS the kind byte and writes the '
                    'plain size back',
   verdict='the top byte is an OCCUPANCY bit carrying the kind: set when the walker '
           'publishes the chunk, cleared when the consumer dequeues it. It is the '
           'producer/consumer handshake of a single-buffer ring, stored in the chunk '
           'header itself.'),
 what_it_does_after_tagging=[
   '0x3dff88  jal func_3E5700($s0+4)          -- take the stream lock (the tag store IS its delay slot)',
   '0x3dff90  $s4 = ($s6->[4] == 4)           -- the stream-state guard',
   '0x3dffa4  slot = ctx0->[0x24] + ($s5<<4) - 0x10   -- the PER-KIND queue slot, 16 bytes',
   '0x3dffb4  slot->[8] += $s1                -- publish: add this chunk to the kind byte count',
   '0x3dffc4  if (slot->[8] == $s1) slot->[0xC] = $s2  -- first entry: set the head',
   '0x3dffdc  ctx0->[0x4C] += $s1             -- outstanding-byte accounting',
   '0x3dffe8  ctx0->[0x54] += $s1             -- ADVANCE THE CURSOR past this chunk',
   '0x3dfff4  if it crossed ctx0->[0x44] clear ctx0->[0x48]',
   '0x3dfff8  jal func_3E5760                 -- release the lock',
   '0x3e0040  loop back to 0x3e0058 unless magic == sentinel',
 ],
 loop_exits=['fewer than 8 bytes between cursor and ctx0->[0x58] (0x3e0064) -> return 0',
             'chunk body not fully resident: ctx0->[0x58] < cursor + len (0x3e00a0) -> return 0',
             'chunk magic == sentinel $s6->[0x11c] (0x3e0044) -> return 1',
             'stream state $s6->[4] == 4 (0x3e0000) -> re-tag 64-byte-aligned and return 0'],
 who_calls_the_walker=dict(
   symbol='sub_003E0170', file=f'{GEN}/sub_003E0170_0x3e0170.cpp',
   call_site='0x3e01ec  jal func_3DFED0',
   what_it_is='the READ-COMPLETION path: it adds the delivered byte count to '
              'ctx0->[0x170] (0x3e01e8) and to ctx0->[0x58] (the data end, 0x3e01f0) '
              'and only then runs the walker',
   consequence='the walker is driven by DATA ARRIVAL, never by consumption. Nothing on '
               'the consume path re-enters it.'),
 where_the_tagged_chunk_goes=[
   'sub_003DFED0  publishes it into the per-kind slot at ctx0->[0x24] + (kind-1)*16',
   'sub_003E12E0  dequeues the head (slot->[0xC]), STRIPS the kind byte, decrements '
   'slot->[8], and walks forward to the next chunk whose tag matches slot->[4] (the kind)',
   'sub_003AEAD0  wraps the dequeued chunk in a 3-word descriptor {+0 header, +4 payload '
   '= header+8, +8 total length} and stages it in the source object\'s one-slot pushback '
   'at 0x5487c0',
   'sub_003B06B0  pops that one slot (0x3b06c4 `sw $zero, 0x0($v0)`)',
   'sub_003B0B40  memcpy(dst=self->[0x7C], src=desc->[4], n=desc->[8]-8), zero-pads to '
   '((total+7) & ~0xF), then sceMpegAddBs(mpeg, dst, that size)',
 ],
 the_5040_derived_statically=dict(
   total=5036,
   es_bytes='$s0 = total - 8 = 5028   (0x3b0b94 addiu $s0, $s0, -0x8)',
   fed_size='$s2 = (total + 7) & ~0xF = 5040   (0x3b0b90 / 0x3b0b98 with $v1 = -0x10)',
   pad='the loop at 0x3b0bb8-0x3b0bd0 zero-fills from offset 5028 up to $s2 + 0x10; the '
       'first 12 of those zeros are inside the 5040 that is fed',
   agrees_with='E24 and E26 measured 5028 ES + 12 zero pad = 5040 from the bytes; the '
               'source produces exactly that arithmetic'),
)

m2 = dict(
 a=dict(
  question='Who calls GetPicture, in what loop? Is the call site one-shot, '
           'counter-bounded, or re-askable? What enforces "one producer firing per GetPicture"?',
  getpicture_thunk=dict(symbol='sub_00402A10', addr='0x402a10',
                        body='ps2_stubs::sceMpegGetPicture(rdram, ctx, runtime);'),
  call_sites_in_image=1,
  call_site=dict(symbol='sub_003B0FB8 (guest fn 0x3b0fb8)',
                 file=f'{GEN}/sub_003B0FB8_0x3b0fb8.cpp',
                 addr='0x3b1020  jal func_402A10   (ra = 0x3b1028)',
                 note='the park snapshot records thread 1 at pc=0x3b1028 ra=0x3b1028 '
                      'wait=Mpeg:0 -- byte-exactly this jal\'s return address'),
  enumeration='`grep -rl 0x402A10u` over all 9,454 generated sources returns exactly one '
              'file, sub_003B0FB8_0x3b0fb8.cpp. There is no other caller.',
  is_it_a_loop='YES -- but the loop is one level UP, in the second guest function that '
               'shares the same generated file.',
  the_loop=dict(
    symbol='sub_003B1050 (guest fn 0x3b1050, generated into sub_003B0FB8_0x3b0fb8.cpp)',
    body=['0x3b1070  if ($a1 != 0) release the previous picture through the vtable at $v0->[0x34]',
          '0x3b108c  jal func_402B38   -- the guard: v1 = (self+0x30)->[0x40]; return v1->[0]',
          '0x3b1094  if (guard != 0) break with v0 = 0',
          '0x3b109c  jal func_3B0FB8   -- THE GetPicture CALL (an intra-file `goto label_3b0fb8`)',
          '0x3b10a4  $v1 = self->[0x10]              -- the counter sub_003B0FB8 bumped at 0x3b103c',
          '0x3b10a8  $v1 = (unsigned)$v1 < $s1       -- $s1 is the requested picture count',
          '0x3b10ac  bnez $v1 -> 0x3b1070            -- *** RE-ASK: LOOP BACK ***'],
    verdict='COUNTER-BOUNDED and RE-ASKABLE. The guest is ONE backward branch '
            '(0x3b10ac) from calling sceMpegGetPicture again. It is not one-shot.'),
  counter=dict(field='self->[0x10]',
               incremented_at='0x3b1034/0x3b103c inside sub_003B0FB8, AFTER the GetPicture jal',
               bound='$s1, sub_003B1050\'s $a1 argument'),
  what_enforces_one_producer_firing_per_getpicture=dict(
    where='HOST side, ps2xRuntime/src/lib/Kernel/Stubs/MPEG.cpp (git-tracked, corroborated)',
    latch='g_mpeg_stub_state.nonStreamDeliveries -- an '
          'unordered_map<uint64_t, weak_ptr<MpegNonStreamDelivery>> keyed by '
          '(mpegAddr << 32) | type, with type == 1 (the IPU-busy input request)',
    guard='MPEG.cpp:2467-2481  `delivery = pending.lock(); if (requestInput && !delivery '
          '&& decodedFrames.empty() && !eofSeen && !streamEnded && !decoderFailed) '
          '{ ...make_shared...; dispatchInput = true; }`  -- a live delivery suppresses '
          'the dispatch',
    second_guard='MPEG.cpp:1759-1760  the invocation onComplete calls '
                 '`getMpegPicture(rdram, &parent, runtime, false)` -- requestInput=FALSE, '
                 'commented "continue this request without re-triggering it"',
    the_authors_own_words='MPEG.cpp:531  "One caller-owned request, retained by its '
                          'invocation/wait continuations."',
    self_sustaining='MPEG.cpp:2514 waitExternal captures `delivery` BY VALUE in the '
                    'resume lambda; EeScheduler.cpp:2120 moves that std::function into '
                    'the blocked thread\'s EeWaitState. So the shared_ptr that suppresses '
                    'the producer is owned by the very wait that is waiting for the '
                    'producer\'s result.'),
  feed_is_one_chunk_by_construction=dict(
    symbol='sub_003B0B40 (guest fn 0x3b0b40)',
    argument='straight-line: exactly one `jal func_3B06B0` (0x3b0b68, the pop) and '
             'exactly one `jal func_4029D0` (0x3b0c2c, sceMpegAddBs) per invocation. '
             'No loop, no counter.',
    addbs_call_sites_in_image=1),
  the_end_of_stream_branch=dict(
    addr='0x3b0b7c  beqz $s2 -> 0x3b0bdc',
    what_it_does='if the pop yields nothing, the guest builds 16 bytes of word '
                 '0xB7010000 (0x3b0be4 `lui $a0, 0xB701`, loop 0x3b0be8-0x3b0c00) and '
                 'feeds THAT. In little-endian memory 0xB7010000 is 00 00 01 B7 -- the '
                 'MPEG-2 sequence_end_code.',
    significance='the guest owns a path that emits a terminating start code by itself. '
                 'It is unreachable here for the same reason the next chunk is: the '
                 'callback is never invoked a second time.'),
 ),
 b=dict(
  question='From the e26a function log: what actually RAN on thread 1 after the feed?',
  log=dict(path='/Volumes/Extreme SSD/ps2recomp-spike/P1/run/ps2_log-e26a-1.txt',
           lines=3607246, unparsed_lines=0,
           sha256='d849775b9f8199ae65a701f90668ede247f7d9afd41d1e18b12e450ccf1024ec',
           equals_E26_committed_pin=True),
  the_feed_in_the_log=dict(
    line_3456124='>> sub_003B0FB8 enter   (depth 5) -- the ONLY entry in the whole run',
    line_3456125='>> sub_00402B38        -- sub_003B1050\'s loop guard, so this entry is '
                 'guest fn 0x3b1050',
    line_3456127='>> sub_003B10D0        -- called at 0x3b0fc8, i.e. guest fn 0x3b0fb8 '
                 'reached by the intra-file `goto label_3b0fb8` at 0x3b109c (no second '
                 'PS_LOG_ENTRY, because that call is compiled as a goto, not a dispatch)',
    line_3456129='<< sub_003B0FB8 exit   -- the C++ frame RETURNING because '
                 'dispatchGuestBranch(0x402A10) returned false: the MPEG HLE parked',
    line_3456130_to_3456134='the whole guest stack unwinds to depth 0 '
                            '(sub_003B0600 / sub_003AE450 / sub_002536C8 / sub_00253860 / sub_001A1CE8)',
    line_3456135='>> sub_003B0B10 enter AT DEPTH 0 -- the producer callback, entered by '
                 'the scheduler as a fresh GuestInvocation (RA forced to 0), exactly as '
                 'dispatchGuestNonStreamCallback builds it',
    line_3456136_to_3456225='the one feed: pop -> memcpy -> release -> AddBs'),
  static_vs_log=[
   dict(leg='the walker sub_003DFED0 runs again after the feed',
        static_prediction='NO -- the only caller is sub_003E0170, the read-completion path',
        log='AGREE. 16 enters, ALL in lines 3452090-3454855; last one 1,280 lines before '
            'the producer callback and 1,269 before the GetPicture frame. Zero after.'),
   dict(leg='the classifier sub_003DFE88 runs again after the feed',
        static_prediction='NO -- called only by the walker and by sub_003DFE18',
        log='AGREE. 56 enters, all 3452091-3454735. Zero after.'),
   dict(leg='the walker caller sub_003E0170 runs again after the feed',
        static_prediction='NO -- it is the CD read completion; no read completes',
        log='AGREE. 29 enters, last 3454849. Zero after.'),
   dict(leg='the feeder sub_003B0B40 runs again after the feed',
        static_prediction='NO -- reached only from the producer callback or the movie open',
        log='AGREE. 2 enters: 3455221 (the movie-open entry at guest 0x3b0c58, which '
            'never calls the pop) and 3456136 (the one real feed). Zero after.'),
   dict(leg='the pop sub_003B06B0 runs again after the feed',
        static_prediction='NO -- one call site, inside the feeder',
        log='AGREE. Exactly 1 enter in the whole run, at 3456137.'),
   dict(leg='the GetPicture call site sub_003B0FB8 runs again after the feed',
        static_prediction='the guest LOOP at 0x3b10ac would re-ask, but only once the '
                          'jal at 0x3b1020 returns',
        log='AGREE with the prediction\'s precondition and DISAGREE with any re-ask: '
            'exactly 1 enter, 3456124, and the frame never resumes. The guest never gets '
            'back to 0x3b10ac.'),
   dict(leg='the refill kick sub_003DCFC0 fires',
        static_prediction='only if ctx0->[0x4C] crosses BELOW ctx0->[0x44] in sub_003DFC48 '
                          'AND ctx0->[0x38] == 1',
        log='AGREE, and stronger: sub_003DCFC0 has ZERO enters in the entire 3.6 M-line '
            'log. The threshold was never crossed downward, not even once.'),
   dict(leg='sceMpegAddBs / sceMpegGetPicture thunks appear in the log',
        static_prediction='NO -- the HLE thunk files guard PS_LOG_ENTRY with #ifdef '
                          '_DEBUG, not PS2_FUNCTION_LOG_TRACKER',
        log='LOG-SILENT, as predicted: 0 enters each. Their execution is evidenced by the '
            'boot log instead ([MPEG:feedES] x1, [MPEG:feed] x1, [MPEG:GetPicture] x1).'),
  ],
  after_the_feed=dict(
    boundary_line=3456226,
    boundary='the line on which the ONE producer callback sub_003B0B10 exits',
    lines_after=151020,
    distinct_symbols_after=16,
    symbols='sub_003E4DB8, sub_003825C0, sub_003825F8, sub_003C1980, sub_0031A490, '
            'sub_0031ABD0, sub_00317520, sub_00423DD0, sub_00423DE0, sub_0031AC08, '
            'sub_00317500, sub_00317348, sub_00227F58, sub_00326B88, sub_00326EB0, sub_0031A6B8',
    shape='4,195 identical iterations of ONE interrupt-driven cycle (two of the symbols '
          'run 8,390 = 2x). Not one MPEG, stream, chunk-walk, descriptor or CD symbol '
          'appears.',
    verdict='thread 1 executes NOTHING after the feed. The post-park tail is a single '
            'timer loop, which is E26\'s sema-31 result seen from the function log.'),
  boot_log_counts=dict(feedES=1, feed=1, GetPicture_wait=1, GetPicture_FRAME=0,
                       IsEnd=0, CdStreamStart=0, CdStreamEof=0, demux=0,
                       note='every one of these trace counters is capped at 32 in '
                            'MPEG.cpp, so a count of 1 is a true count and not a cap'),
 ),
)

m3 = dict(
 question='Is there a code path by which the guest COULD re-ask, or is the one-shot structural?',
 headline='The guest re-ask is NOT one-shot -- it is one backward branch away, and the '
          'chunk it would get is already the head of the queue. What is structural is the '
          'HOST-side suppression, and it is held alive by the wait it is blocking.',
 the_guest_re_ask_path=dict(
   exists=True,
   function='sub_003B1050 (guest fn 0x3b1050, inside sub_003B0FB8_0x3b0fb8.cpp)',
   branch='0x3b10ac  bnez $v1, -> 0x3b1070',
   condition='(unsigned)self->[0x10] < $s1, i.e. pictures served so far < pictures requested',
   trigger='the ONLY thing it needs is for the `jal func_402A10` at 0x3b1020 to RETURN. '
           'Nothing else. No register, no callback, no semaphore.',
   what_it_would_get=dict(
     next_chunk='0xd49b14, the second MPCh',
     why='sub_003E12E0 already advanced the kind-1 slot head to it when it dequeued '
         'chunk0: 0x3e1360 `$a2 = $s2 + $s1` = 0xd48740 + 5036 = 0xd49aec (SCHl, tag '
         '0x02 != kind 1) then the 0x3e1384 walk adds 0x28 to reach 0xd49b14, whose tag '
         '0x0100381c matches (slot->[4] << 24) = 0x01000000, so 0x3e13c8 '
         '`sw $a2, 0xC($t1)` parks the head THERE',
     consequence='the terminating start code E26 found at 0xd49b1c is the payload of the '
                 'chunk the queue head is ALREADY pointing at. The guest is one '
                 'func_3E12E0 call from it.'),
   second_guest_path='if the queue were empty instead, sub_003B0B40 0x3b0b7c takes the '
                     '0x3b0bdc branch and feeds 16 bytes of 00 00 01 B7 '
                     '(sequence_end_code) on its own.'),
 the_structural_one_shot=dict(
   where='the HOST, not the guest',
   construct='g_mpeg_stub_state.nonStreamDeliveries[(mpegAddr << 32) | 1], a '
             'weak_ptr<MpegNonStreamDelivery>',
   mechanism=[
     '1. GetPicture (requestInput=true) finds the key empty, creates the delivery and '
        'dispatches the guest producer once (MPEG.cpp:2464-2493).',
     '2. The producer feeds one chunk and returns; onComplete re-enters '
        'getMpegPicture with requestInput=FALSE (MPEG.cpp:1760).',
     '3. decodedFrames is empty, so getMpegPicture calls waitExternal with a resume '
        'lambda that CAPTURES the delivery shared_ptr by value (MPEG.cpp:2514-2526).',
     '4. EeScheduler::waitExternal moves that std::function into the blocked thread\'s '
        'EeWaitState (EeScheduler.cpp:2120), so the shared_ptr outlives the call.',
     '5. pending.lock() therefore stays non-null for the whole park, so any further '
        'GetPicture -- the resume path or a fresh guest call -- takes the '
        '`!delivery` == false branch and dispatches no producer.'],
   verdict='the suppressing token is owned by the wait it suppresses. It is not a '
           'mutual wait between two parties; it is a single party holding the key to '
           'its own door.'),
 every_wake_site_enumerated=[
  dict(site='sceMpegAddBs -> completeExternalWait (MPEG.cpp:2058)',
       condition='decodedFrames grew, or streamEnded, or decoderFailed',
       reachable='only from sub_003B0B40, only from the producer callback -> circular',
       status='EXCLUDED (and in this run wakePictureWaiter was false: 0 new frames)'),
  dict(site='notifyMpegCdStreamEof (MPEG.cpp:1999)', condition='CD stream EOF',
       reachable='driven by thread 1\'s CD stream reads', status='EXCLUDED; 0 CdStreamEof lines'),
  dict(site='sceMpegFlush (MPEG.cpp:2023)', condition='guest call', reachable='thread 1', status='EXCLUDED'),
  dict(site='sceMpegDelete (MPEG.cpp:2239) + invalidateNonStreamDeliveries (2235)',
       condition='guest call', reachable='thread 1', status='EXCLUDED'),
  dict(site='sceMpegCreate -> invalidateNonStreamDeliveries (MPEG.cpp:2165)',
       condition='guest call', reachable='thread 1', status='EXCLUDED'),
  dict(site='sceMpegReset -> invalidateNonStreamDeliveries (MPEG.cpp:2718)',
       condition='guest call', reachable='thread 1', status='EXCLUDED'),
  dict(site='sceMpegDemuxPss / PssRing (MPEG.cpp:2285/2291/2378/2384)',
       condition='the PSS path', reachable='this title uses the ES path; 0 demux lines',
       status='EXCLUDED'),
  dict(site='a timeout on the Mpeg wait', condition='none',
       reachable='waitExternal takes no timeout argument',
       status='EXCLUDED BY CONSTRUCTION'),
 ],
 which_leg_of_the_mutual_wait_breaks=dict(
  leg_1='one GetPicture feeds exactly one chunk -- HOLDS, and E27 names both halves: '
        'guest-side sub_003B0B40 is straight-line with one pop and one AddBs; host-side '
        'the nonStreamDeliveries latch permits one producer dispatch per live request.',
  leg_2='GetPicture does not return until a frame appears -- HOLDS: getMpegPicture calls '
        'waitExternal whenever decodedFrames is empty and no EOF/end/failure is set.',
  leg_3='the parser cannot emit until the next start code -- E24/E26\'s bytes; E27 did '
        'not re-test it.',
  the_unstated_leg='"...and so each side is waiting for the other". THIS is the leg that '
                   'breaks. The guest is not waiting for anything it could not do: it '
                   'holds the next chunk at the head of its own queue and a live loop '
                   'branch to ask for it. It is BLOCKED INSIDE the host call, and the '
                   'host call is holding the token that stops the guest being asked. '
                   'The symmetry E26 tabled is not there.'),
 what_E28_would_observe=(
  'A dynamic capture cannot add much on the guest side -- the static case is closed -- so '
  'the one thing worth a boot is the HOST side, and it needs no new guest instrumentation. '
  'Arm a watch on the kind-1 queue slot (ctx0->[0x24]+0: the byte count at +8 and the head '
  'at +0xC) and on the chunk header 0xd49b14/0xd49b18, and log, from inside MPEG.cpp, every '
  'entry to getMpegPicture with its requestInput flag and the result of pending.lock(), plus '
  'every completeExternalWait(kMpegPictureWaitType, ...) call with its caller. The '
  'prediction E27 makes, which that capture would confirm or kill in one boot: the slot head '
  'reads 0xd49b14 with a byte count of at least 14,364 from the moment of the feed onward and '
  'never changes; 0xd49b18 still reads 0x0100381c at the park; getMpegPicture is entered '
  'exactly twice (requestInput=true then false) and pending.lock() is non-null on the second; '
  'and completeExternalWait for the picture wait is called zero times after the feed. That is '
  'E28 s brief to write, not E27 s -- named here in one paragraph and designed nowhere.'),
)

save('mission-1-walker.json', dict(utc=utc(), **m1))
save('mission-2-feedonce.json', dict(utc=utc(), **m2))
save('mission-3-reask.json', dict(utc=utc(), **m3))
print('wrote mission-1-walker.json mission-2-feedonce.json mission-3-reask.json')
print('# E27 MISSIONS TAIL COMPLETE')
