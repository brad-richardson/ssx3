import unittest

from tools.native_gamecube import runtime_evidence


class RuntimeEvidence(unittest.TestCase):
    def test_missing_shutdown_is_unknown_not_zero(self):
        result = runtime_evidence("[staticrecomp] module loaded: game\n")
        self.assertTrue(result["module_loaded"])
        self.assertIsNone(result["shutdown_counters"])
        self.assertIsNone(result["fallback_jit_runs"])

    def test_preserve_counter_units_and_performance(self):
        result = runtime_evidence(
            "[staticrecomp] fallback mode: interpreter\n"
            "[ssx3-metrics] sample=5 fps=30.000 vps=60.000 speed=1.000000\n"
            "[staticrecomp] fallback_jit_runs=0\n"
            "[staticrecomp] shutdown: native=400 fallback=17 hook_fb=9\n"
            "[staticrecomp] fallback-site pc=80000100 samples=5\n")
        self.assertEqual(result["shutdown_counters"], {"native": 400, "fallback": 17, "hook_fb": 9})
        self.assertEqual(result["fallback_jit_runs"], 0)
        self.assertEqual(result["performance_samples"][0]["speed"], 1)
        self.assertEqual(result["sites"][0]["pc"], "0x80000100")


if __name__ == "__main__":
    unittest.main()
