// N3 standalone host check for ps2_android_env.h (mirrors the MiniTest vectors).
#include "ps2_android_env.h"
#include <cassert>
#include <iostream>

int main()
{
    using ps2x::envFilePathForBootElf;
    using ps2x::parseEnvFileContent;

    auto e = parseEnvFileContent("# c\n\nPS2X_CD_IMAGE=a.iso\nPS2X_SKIP_MOVIE=1\nD = v \n");
    assert(e.size() == 3);
    assert(e[0].first == "PS2X_CD_IMAGE" && e[0].second == "a.iso");
    assert(e[1].first == "PS2X_SKIP_MOVIE" && e[1].second == "1");
    assert(e[2].first == "D" && e[2].second == "v");

    auto m = parseEnvFileContent("A=B=C\nNOEQUALS\n=nokey\nEMPTY=\n");
    assert(m.size() == 2);
    assert(m[0].first == "A" && m[0].second == "B=C");
    assert(m[1].first == "EMPTY" && m[1].second == "");
    assert(parseEnvFileContent("").empty());

    auto c = parseEnvFileContent("K=1\r\nJ=x\r\n");
    assert(c.size() == 2 && c[0].second == "1" && c[1].second == "x");

    assert(envFilePathForBootElf("/a/b/game.elf") == "/a/b/ps2x.env");
    assert(envFilePathForBootElf("game.elf") == "ps2x.env");
    assert(envFilePathForBootElf(nullptr) == "");
    assert(envFilePathForBootElf("") == "");

    std::cout << "N3-ENVCHECK-ALL-PASS\n";
    return 0;
}
