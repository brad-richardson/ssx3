"""G17 lldb helpers: O2-argument capture at flush_descriptor_set():3505.

Stop triage (LOGE-trap skip, :3505 cond-bp capture, crash post-mortem)
+ G17_CAPTURE (vk_set / update_template / bindings + regs + bt).
DWARF-only, no expr compilation (same discipline as G15 g15walk.py).
"""
import lldb


def _frame_sym(frame):
    try:
        if frame.GetSymbol().IsValid():
            return frame.GetSymbol().GetName() or ""
    except Exception:
        pass
    return ""


def _line_of(frame):
    try:
        ls = frame.GetLineEntry()
        if ls.IsValid():
            return ls.GetLine()
    except Exception:
        pass
    return 0


def g17_capture(debugger, command, result, internal_dict):
    """Capture the O2 descriptor inputs at the selected frame.

    Expects the selected frame to be flush_descriptor_set (or, at a
    crash stop, call after selecting that frame). Prints: stop reason,
    bt, x0-x3 (device, vk_set, update_template, pData at the call),
    DWARF locals (set, vk_set, update_template), pData memory probe,
    and the null/wild naming lines.
    """
    try:
        target = debugger.GetSelectedTarget()
        process = target.GetProcess()
        thread = process.GetSelectedThread()
        frame = thread.GetSelectedFrame()
        print("G17-CAPTURE sym=%s line=%s" % (
            _frame_sym(frame), _line_of(frame)), file=result)
        debugger.HandleCommand("bt 12")
        debugger.HandleCommand("register read x0 x1 x2 x3")
        debugger.HandleCommand(
            "frame variable set vk_set update_template first_set set_count")
        # Name the bad input from registers (call args at the site).
        try:
            regs = {}
            for r in ("x0", "x1", "x2", "x3"):
                v = frame.FindRegister(r)
                regs[r] = v.GetValueAsUnsigned() if v.IsValid() else None
            names = {"x0": "device", "x1": "vk_set",
                     "x2": "update_template", "x3": "pData(bindings[set])"}
            for r in ("x0", "x1", "x2", "x3"):
                v = regs[r]
                tag = "NULL" if v == 0 else (
                    "UNREAD" if v is None else "nonzero")
                print("G17-ARG %s(%s)=%s %s" % (
                    r, names[r],
                    ("0x%x" % v) if v is not None else "?",
                    tag), file=result)
        except Exception as e:
            print("G17-ARG-EXC %s" % e, file=result)
        # Probe pData readability (first 64 bytes) via x3.
        try:
            x3 = frame.FindRegister("x3")
            pdata = x3.GetValueAsUnsigned() if x3.IsValid() else 0
            if pdata:
                err = lldb.SBError()
                n = process.ReadMemory(pdata, 64, err)
                if err.Success():
                    print("G17-PDATA 0x%x readable=64B head=%s" % (
                        pdata, n[:16].hex()), file=result)
                else:
                    print("G17-PDATA 0x%x UNREADABLE (%s)" % (
                        pdata, err.GetCString()), file=result)
            else:
                print("G17-PDATA x3==0 (null pData)", file=result)
        except Exception as e:
            print("G17-PDATA-EXC %s" % e, file=result)
        debugger.HandleCommand("image list")
    except Exception as e:
        print("G17-CAPTURE-EXC %s" % e, file=result)


def g17_triage(debugger, command, result, internal_dict):
    """Classify the current stop: LOGE trap -> skip; :3505 -> capture;
    crash -> post-mortem capture; exit -> report."""
    try:
        target = debugger.GetSelectedTarget()
        process = target.GetProcess()
        state = process.GetState()
        if state == lldb.eStateExited:
            print("TRIAGE: EXITED exit=%d" % process.GetExitStatus(),
                  file=result)
            try:
                debugger.HandleCommand("bt 4")
            except Exception:
                pass
            return
        thread = process.GetSelectedThread()
        if not thread.IsValid():
            print("TRIAGE: no-valid-thread state=%d" % state, file=result)
            return
        stop_reason = thread.GetStopReason()
        frame = thread.GetSelectedFrame()
        pc = frame.GetPC()
        sym = _frame_sym(frame)
        line = _line_of(frame)
        err = lldb.SBError()
        insn = process.ReadUnsignedFromMemory(pc, 4, err)
        if err.Fail():
            insn = 0
        is_brk = (insn & 0xffe00000) in (0xd4200000, 0xd4400000)
        print("TRIAGE pc=0x%x sym=%s line=%s insn=0x%08x reason=%d" % (
            pc, sym, line, insn, stop_reason), file=result)
        # Gate the skip on the symbol alone: debug_break() holds only the
        # __builtin_debugtrap (r1: insn-mask required Rd=11111, but BRK/HLT
        # encode Rd=00000, so every trap misclassified and re-trapped).
        if sym and "debug_break" in sym:
            debugger.HandleCommand("register write pc 0x%x" % (pc + 4))
            print("TRAP-SKIPPED pc now 0x%x; caller:" % (pc + 4),
                  file=result)
            debugger.HandleCommand("bt 4")
        elif line == 3505 or (sym and "flush_descriptor_set" in sym
                              and "(unsigned int," in sym):
            print("O2-SITE-STOP (:3505 cond-bp: null input); capture:",
                  file=result)
            g17_capture(debugger, "", result, internal_dict)
        elif stop_reason == lldb.eStopReasonBreakpoint:
            print("OTHER-BREAKPOINT (not :3505); bt:", file=result)
            debugger.HandleCommand("bt 8")
        else:
            print("CRASH-OR-SIGNAL-STOP; post-mortem:", file=result)
            debugger.HandleCommand("bt 16")
            debugger.HandleCommand("register read")
            # Select the flush_descriptor_set frame for input naming.
            found = False
            for i in range(thread.GetNumFrames()):
                fr = thread.GetFrameAtIndex(i)
                sn = _frame_sym(fr)
                if "flush_descriptor_set" in sn and "(unsigned int," in sn:
                    thread.SetSelectedFrame(i)
                    print("O2-FRAME #%d selected; capture:" % i,
                          file=result)
                    g17_capture(debugger, "", result, internal_dict)
                    found = True
                    break
            if not found:
                print("G17-NOTE no flush_descriptor_set frame on stack "
                      "(O1/O3-class crash); census skipped", file=result)
                debugger.HandleCommand("image list")
    except Exception as e:
        print("TRIAGE-EXC %s" % e, file=result)


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand(
        "command script add -f g17walk.g17_triage g17_triage")
    debugger.HandleCommand(
        "command script add -f g17walk.g17_capture g17_capture")
