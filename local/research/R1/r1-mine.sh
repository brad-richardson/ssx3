#!/usr/bin/env bash
# R1 mine: small excerpts from a big emulog. Args: TAG EMULOG OUTFILE.
set -x
TAG=$1; E=$2; O=$3
{
echo "=== $TAG loader lines ==="
grep -n "SYSTEM.CNF\|cdvdLoadElf\|Initializing Elf\|ELF Loading\|EntryPoint" $E
echo "=== $TAG ExecPS2 context ==="
grep -n "Bios call: ExecPS2" $E
echo "=== $TAG (74) lines ==="
grep -n " (74) pc=" $E
echo "=== $TAG (5b) lines ==="
grep -n " (5b) pc=" $E
echo "=== $TAG (5a) lines ==="
grep -n " (5a) pc=" $E
echo "=== $TAG (64) lines ==="
grep -n " (64) pc=" $E
echo "=== $TAG first 3 + last 3 EE lines ==="
grep -n -m3 "Bios call:" $E
echo "=== $TAG tail EE ==="
grep -n "Bios call:" $E | tail -n 3
echo "=== $TAG misc ==="
grep -c "Bios call:" $E
grep -c "WaitVblankStart" $E
grep -n -m2 "ReBootStart\|sceCdInit" $E
tail -n 5 $E
} > $O 2>&1
wc -l $O
