"""G15 lldb helpers: stop triage (LOGE-trap skip, trim census, crash capture)
+ watchpoint plant. DWARF-only, no expr compilation."""
import lldb


def _types(target, name):
    lst = target.FindTypes(name)
    if lst.GetSize() == 0:
        return None
    return lst.GetTypeAtIndex(0)


def _field_offset(typ, name):
    for i in range(typ.GetNumberOfFields()):
        f = typ.GetFieldAtIndex(i)
        if f.GetName() == name:
            return f.GetOffsetInBytes()
    return None


def _read_ptr(process, addr):
    err = lldb.SBError()
    v = process.ReadPointerFromMemory(addr, err)
    if err.Fail():
        return None
    return v


def _census_rows(debugger):
    """Return (rows, meta). rows: list of (f,i,j,pool,table,handle)."""
    target = debugger.GetSelectedTarget()
    process = target.GetProcess()
    frame = process.GetSelectedThread().GetSelectedFrame()
    this_var = frame.FindVariable("this")
    if not this_var.IsValid():
        return None, {"err": "no-this-in-frame"}
    this_addr = this_var.GetValueAsUnsigned()
    if not this_addr:
        return None, {"err": "this-is-null"}
    device = _read_ptr(process, this_addr + 0)
    meta = {"this": this_addr, "device": device}
    if not device:
        meta["err"] = "device-null-or-unreadable"
        return None, meta
    dev_t = _types(target, "Vulkan::Device")
    pf_t = _types(target, "Vulkan::Device::PerFrame")
    cp_t = _types(target, "Vulkan::CommandPool")
    if dev_t is None or pf_t is None or cp_t is None:
        meta["err"] = "FindTypes failed"
        return None, meta
    pf_off = _field_offset(dev_t, "per_frame")
    cp_off = _field_offset(pf_t, "cmd_pools")
    cp_size = cp_t.GetByteSize()
    meta.update({"pf_off": pf_off, "cp_off": cp_off, "cp_size": cp_size})
    if pf_off is None or cp_off is None or not cp_size:
        meta["err"] = "field offset missing"
        return None, meta
    begin = _read_ptr(process, device + pf_off)
    end = _read_ptr(process, device + pf_off + 8)
    if begin is None or end is None or end < begin:
        meta["err"] = "per_frame vector unreadable"
        return None, meta
    nframes = (end - begin) // 8
    meta["nframes"] = nframes
    rows = []
    for f in range(nframes):
        pf = _read_ptr(process, begin + f * 8)
        if pf is None:
            continue
        for i in range(5):  # QUEUE_INDEX_COUNT
            vbase = pf + cp_off + i * 24
            pbegin = _read_ptr(process, vbase)
            pend = _read_ptr(process, vbase + 8)
            if pbegin is None or pend is None or pend < pbegin:
                continue
            n = (pend - pbegin) // cp_size
            for j in range(n):
                pool = pbegin + j * cp_size
                table = _read_ptr(process, pool + 8)
                handle = _read_ptr(process, pool + 16)
                rows.append((f, i, j, pool, table, handle))
    return rows, meta


def _print_census(debugger, result):
    try:
        rows, meta = _census_rows(debugger)
    except Exception as e:
        print("CENSUS-EXC %s" % e, file=result)
        return
    if rows is None:
        print("CENSUS-N/A %s" % meta.get("err", "?"), file=result)
        return
    print("this=0x%x device=0x%x frames=%d pools=%d pool_size=%s" % (
        meta["this"], meta["device"], meta["nframes"], len(rows),
        meta["cp_size"]), file=result)
    for (f, i, j, pool, table, handle) in rows:
        mark = " <-- THIS" if pool == meta["this"] else ""
        t = "0x%x" % table if table is not None else "?"
        h = "0x%x" % handle if handle is not None else "?"
        print("f=%d i=%d j=%d pool=0x%x table=%s handle=%s%s" % (
            f, i, j, pool, t, h, mark), file=result)


def _print_buffers(debugger, result):
    try:
        process = debugger.GetSelectedTarget().GetProcess()
        frame = process.GetSelectedThread().GetSelectedFrame()
        this_var = frame.FindVariable("this")
        if not this_var.IsValid():
            print("BUFFERS-N/A no-this", file=result)
            return
        pool = this_var.GetValueAsUnsigned()
        if not pool:
            print("BUFFERS-N/A null-this", file=result)
            return
        err = lldb.SBError()
        dev = process.ReadPointerFromMemory(pool + 0, err)
        tab = process.ReadPointerFromMemory(pool + 8, err)
        hdl = process.ReadPointerFromMemory(pool + 16, err)
        print("pool=0x%x device=0x%x table=0x%x handle=0x%x" % (
            pool, dev or 0, tab or 0, hdl or 0), file=result)
        for name, off in (("buffers", 24), ("secondary", 48)):
            b = process.ReadPointerFromMemory(pool + off, err)
            e = process.ReadPointerFromMemory(pool + off + 8, err)
            c = process.ReadPointerFromMemory(pool + off + 16, err)
            if b is None or e is None or e < b or (e - b) > 4096:
                print("%s: UNREADABLE/SUSPECT b=0x%s e=0x%s" % (
                    name, "%x" % b if b else "?", "%x" % e if e else "?"),
                    file=result)
                continue
            n = (e - b) // 8
            first = []
            for k in range(min(n, 4)):
                v = process.ReadPointerFromMemory(b + k * 8, err)
                first.append("0x%x" % (v or 0))
            print("%s: n=%d cap_bytes=%d first=%s" % (
                name, n, (c - b) if c and b and c >= b else -1,
                ",".join(first)), file=result)
        ix = process.ReadUnsignedFromMemory(pool + 72, 4, err)
        six = process.ReadUnsignedFromMemory(pool + 76, 4, err)
        print("index=%d secondary_index=%d" % (ix, six), file=result)
    except Exception as e:
        print("BUFFERS-EXC %s" % e, file=result)


def g15_triage(debugger, command, result, internal_dict):
    """Classify the current stop: LOGE trap -> skip; trim -> census; else capture."""
    try:
        target = debugger.GetSelectedTarget()
        process = target.GetProcess()
        thread = process.GetSelectedThread()
        if not thread.IsValid():
            print("TRIAGE: no-valid-thread", file=result)
            return
        frame = thread.GetSelectedFrame()
        pc = frame.GetPC()
        sym = frame.GetSymbol().GetName() if frame.GetSymbol() else "?"
        err = lldb.SBError()
        insn = process.ReadUnsignedFromMemory(pc, 4, err)
        if err.Fail():
            insn = 0
        is_brk = (insn & 0xffe0001f) in (0xd420001f, 0xd440001f)
        print("TRIAGE pc=0x%x sym=%s insn=0x%08x" % (pc, sym, insn),
              file=result)
        if sym and "debug_break" in sym and is_brk:
            debugger.HandleCommand("register write pc 0x%x" % (pc + 4))
            print("TRAP-SKIPPED pc now 0x%x; caller:" % (pc + 4),
                  file=result)
            debugger.HandleCommand("bt 4")
        elif sym and "CommandPool" in sym and "trim" in sym:
            print("TRIM-STOP; census:", file=result)
            debugger.HandleCommand("bt 12")
            _print_census(debugger, result)
            _print_buffers(debugger, result)
        else:
            print("CRASH-OR-OTHER-STOP; capture:", file=result)
            debugger.HandleCommand("bt 16")
            debugger.HandleCommand("register read")
            debugger.HandleCommand("image list")
            for i in range(thread.GetNumFrames()):
                fr = thread.GetFrameAtIndex(i)
                sn = ""
                try:
                    if fr.GetSymbol().IsValid():
                        sn = fr.GetSymbol().GetName() or ""
                except Exception:
                    pass
                if "CommandPool" in sn and "trim" in sn:
                    thread.SetSelectedFrame(i)
                    print("TRIM-FRAME #%d selected; census+buffers:" % i,
                          file=result)
                    _print_census(debugger, result)
                    _print_buffers(debugger, result)
                    break
    except Exception as e:
        print("TRIAGE-EXC %s" % e, file=result)


def g15_watch_pool(debugger, command, result, internal_dict):
    try:
        parts = command.strip().split()
        if len(parts) != 2:
            print("usage: g15_watch_pool <frame> <queue>", file=result)
            return
        wf, wi = int(parts[0]), int(parts[1])
        rows, meta = _census_rows(debugger)
        if rows is None:
            print("CENSUS-N/A %s" % meta.get("err", "?"), file=result)
            return
        for (f, i, j, pool, table, handle) in rows:
            if f == wf and i == wi and j == 0:
                slot = pool + 8
                t = "0x%x" % table if table is not None else "?"
                print("target f=%d i=%d pool=0x%x table=%s slot=0x%x" % (
                    f, i, pool, t, slot), file=result)
                if table == 0:
                    print("ALREADY-NULL: write predates this breakpoint",
                          file=result)
                    return
                err = lldb.SBError()
                wp = debugger.GetSelectedTarget().WatchAddress(
                    slot, 8, False, True, err)
                if err.Fail() or not wp.IsValid():
                    print("WATCH-FAILED %s" % err.GetCString(), file=result)
                    return
                print("WATCH-OK id=%d addr=0x%x size=8 write-only" % (
                    wp.GetID(), slot), file=result)
                return
        print("POOL-NOT-FOUND f=%d i=%d" % (wf, wi), file=result)
    except Exception as e:
        print("WATCH-EXC %s" % e, file=result)


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand(
        "command script add -f g15walk.g15_triage g15_triage")
    debugger.HandleCommand(
        "command script add -f g15walk.g15_watch_pool g15_watch_pool")
