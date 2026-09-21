#!/usr/bin/env python3
"""G12 H3 brace fix: the applied H3 left `return;` unconditional. Wrap in braces."""
HW = "/home/brad/pcsx2-g7/pcsx2/pcsx2/GS/Renderers/HW/GSRendererHW.cpp"

FIND = ("m_env.PRIM.PRIM != GS_POINTLIST)\n"
        '\t\tConsole.WriteLn("G12_SKIP n=%llu reason=blackpoint", static_cast<unsigned long long>(s_n));\n'
        "\t\treturn;\n")
REPL = ("m_env.PRIM.PRIM != GS_POINTLIST)\n"
        "\t\t{\n"
        '\t\t\tConsole.WriteLn("G12_SKIP n=%llu reason=blackpoint", static_cast<unsigned long long>(s_n));\n'
        "\t\t\treturn;\n"
        "\t\t}\n")


def main():
    hw = open(HW, encoding="utf-8").read()
    n = hw.count(FIND)
    assert n == 1, f"H3fix: anchor count={n}, want 1"
    open(HW, "w", encoding="utf-8").write(hw.replace(FIND, REPL, 1))
    print("G12 H3 brace fix applied")


if __name__ == "__main__":
    main()
