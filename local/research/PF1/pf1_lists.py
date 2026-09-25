#!/usr/bin/env python3
"""Walk the EA intrusive lists named in PF1 from an RDRAM dump.
Usage: pf1_lists.py RAM list_head_addr [...]   (H at +0, T at +0xc; nodes: prev +0, next +4, vptr +8)
"""
import struct, sys
ram = open(sys.argv[1], 'rb').read()
u = lambda a: struct.unpack_from('<I', ram, a & 0x1ffffff)[0]
for h in (int(x, 0) for x in sys.argv[2:]):
    print('list H=0x%x: H.prev=0x%x H.next=0x%x [+8]=0x%x T.prev(+0xc)=0x%x T.next(+0x10)=0x%x' %
          (h, u(h), u(h + 4), u(h + 8), u(h + 12), u(h + 16)))
    n, seen = u(h + 4), 0
    while seen < 40:
        nxt, prv = u(n + 4), u(n)
        if nxt == n or prv == n:
            print('  sentinel 0x%x' % n); break
        print('  node 0x%x prev=0x%x next=0x%x vptr(+8)=0x%x [+0x48]=0x%x [+0x54]=0x%x' %
              (n, prv, nxt, u(n + 8), u(n + 0x48), u(n + 0x54)))
        n, seen = nxt, seen + 1
