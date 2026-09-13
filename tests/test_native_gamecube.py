import unittest
import tempfile
from pathlib import Path

from tools.native_gamecube import runtime_evidence, verify_runtime_execution, verify_rendered_frames, runtime_fault, wait_for_runtime


class RuntimeEvidence(unittest.TestCase):
    def test_known_faults_stop_without_confusing_watcher_startup_messages(self):
        self.assertIsNone(runtime_fault(b'Unable to resolve read address 803da1f8 PC 958'))
        for line in [b'Invalid write to 0x81800000', b'Unknown Pointer 0x80001', b'GFX FIFO: Unknown Opcode',
                     b'[staticrecomp] unknown guest instruction pc=0x00000400',
                     b'IntCPU: Unknown instruction 01fe01fe']:
            self.assertIsNotNone(runtime_fault(line))

    def test_unknown_instruction_fails_even_with_shutdown_counters(self):
        evidence = runtime_evidence('[staticrecomp] module loaded: game\n'
                                    '[staticrecomp] unknown guest instruction pc=0x400\n'
                                    '[staticrecomp] shutdown: native=400 smc_failed=0\n')
        with self.assertRaisesRegex(RuntimeError, 'unknown guest instructions'):
            verify_runtime_execution(evidence)

    def test_fault_across_log_read_boundary_kills_owned_diagnostic(self):
        class Process:
            args = ['isolated-test']
            returncode = None
            def poll(self): return self.returncode
            def kill(self): self.returncode = -9
            def wait(self): return self.returncode
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'runtime.log'
            path.write_bytes(b' '*(1024*1024-5)+b'Invalid write to 0x81800000')
            code, reason = wait_for_runtime(Process(), path, 1)
            self.assertEqual(code, -9)
            self.assertEqual(reason, 'Invalid write to')

    def test_malformed_gpu_commands_fail_without_a_memory_error(self):
        evidence = runtime_evidence(
            '[staticrecomp] module loaded: game\n'
            'GFX FIFO: Unknown Opcode (0xff @ 0x1234, preprocess=false).\n'
            '[staticrecomp] shutdown: native=400 smc_failed=0\n')
        self.assertEqual(evidence['invalid_memory_accesses'], 0)
        with self.assertRaisesRegex(RuntimeError, 'malformed GPU'):
            verify_runtime_execution(evidence)

    def test_stale_rendering_cannot_pass_with_healthy_cached_fps(self):
        for age in (None, 200):
            with self.subTest(age=age), self.assertRaisesRegex(RuntimeError, 'stopped producing screenshots'):
                verify_rendered_frames(dict(last_screenshot_age_seconds=age), 300)
        verify_rendered_frames(dict(last_screenshot_age_seconds=20), 300)
        verify_rendered_frames(dict(last_screenshot_age_seconds=None), 10)

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

    def test_video_startup_failure_cannot_pass_with_zero_counters(self):
        evidence = runtime_evidence('[staticrecomp] module loaded: game\n'
                                    'Failed to initialize video backend!\n'
                                    '[staticrecomp] shutdown: native=0 fallback=0 smc_failed=0\n')
        with self.assertRaisesRegex(RuntimeError, 'never executed'):
            verify_runtime_execution(evidence)

    def test_running_game_with_invalid_accesses_cannot_pass(self):
        prefix = '[staticrecomp] module loaded: game\n[staticrecomp] shutdown: native=400 smc_failed=0\n'
        good = runtime_evidence(prefix)
        verify_runtime_execution(good)
        bad = runtime_evidence(prefix + 'Invalid read from 0x00000000, PC = 0x8024d314.\n')
        self.assertEqual(bad['invalid_memory_accesses'], 1)
        with self.assertRaisesRegex(RuntimeError, 'invalid memory'):
            verify_runtime_execution(bad)

    def test_unknown_graphics_pointer_cannot_pass(self):
        evidence = runtime_evidence(
            '[staticrecomp] module loaded: game\n'
            'Unknown Pointer 0x02262624 PC 0x8029f4d4 LR 0x80230ad8\n'
            '[staticrecomp] shutdown: native=400 smc_failed=0\n')
        self.assertEqual(evidence['invalid_memory_accesses'], 1)
        with self.assertRaisesRegex(RuntimeError, 'invalid memory'):
            verify_runtime_execution(evidence)


if __name__ == "__main__":
    unittest.main()
