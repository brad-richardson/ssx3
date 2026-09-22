// N3: standalone MiniTest driver for the env parser TU (same harness as the suite).
#include "MiniTest.h"
void register_ps2_android_env_tests();
int main()
{
    register_ps2_android_env_tests();
    return MiniTest::Run();
}
