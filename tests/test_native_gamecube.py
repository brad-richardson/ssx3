import argparse
import json
import os
import unittest
import tempfile
from pathlib import Path
from unittest import mock

from tools import native_gamecube
from tools.native_gamecube import CORE_STACK, ROOT, idle_pc_ini_line, launch, patch_files, runtime_evidence, verify_runtime_execution, verify_rendered_frames, runtime_fault, wait_for_runtime


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


class TexturePackPolicy(unittest.TestCase):
    def test_launch_with_pack_refuses_without_policy_override(self):
        args = argparse.Namespace(texture_pack=Path("whatever"))
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "asset-policy"):
                launch(args)


class PatchStack(unittest.TestCase):
    def test_patch_files_lists_touched_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            patch = Path(tmp) / "sample.patch"
            patch.write_text("diff --git a/Source/Foo.cpp b/Source/Foo.cpp\n"
                             "--- a/Source/Foo.cpp\n"
                             "+++ b/Source/Foo.cpp\n"
                             "@@ -1 +1 @@\n"
                             "-a\n+b\n"
                             "diff --git a/Source/New.h b/Source/New.h\n"
                             "new file mode 100644\n")
            self.assertEqual(patch_files(patch), ["Source/Foo.cpp", "Source/New.h"])

    def test_core_stack_patches_exist(self):
        self.assertTrue(CORE_STACK)
        for name in CORE_STACK:
            with self.subTest(patch=name):
                self.assertTrue((ROOT / "native/patches" / name).is_file())


class IdleSkipDefault(unittest.TestCase):
    def test_idle_skip_defaults_off_with_env_opt_in(self):
        self.assertEqual(idle_pc_ini_line({}), "")
        self.assertEqual(idle_pc_ini_line({"SSX3_IDLE_PC": "0x80288ED4"}),
                         "StaticRecompIdlePC = 0x80288ED4\n")
        self.assertEqual(idle_pc_ini_line({"SSX3_IDLE_PC": ""}), "")


class FastFpDefault(unittest.TestCase):
    def test_module_build_enables_fast_fp_without_flag(self):
        from tools.native_float_conversion_spike import split_helpers
        fixture = Path(__file__).resolve().parent / "float-conversion-original-generated.h"
        with tempfile.TemporaryDirectory() as tmp:
            module_dir = Path(tmp) / "module"
            (module_dir / "codegen/generated").mkdir(parents=True)
            (module_dir / "codegen/generated/generated.h").write_text(split_helpers(fixture.read_text()))
            dol = Path(tmp) / "main.dol"
            identity = {"dol_sha256": native_gamecube.PINS["dol_sha256"],
                        "dolrecomp_revision": native_gamecube.PINS["dolrecomp_revision"],
                        "generator_sha256": "H" * 64, "backend": "c"}
            (module_dir / "generation.json").write_text(json.dumps(identity))
            args = argparse.Namespace(jobs=4, opt_level="2", dol=dol, fast_fp=False)
            def fake_sha(path):
                return native_gamecube.PINS["dol_sha256"] if Path(path).name == "main.dol" else "H" * 64
            with mock.patch.object(native_gamecube, "MODULE", module_dir), \
                    mock.patch.object(native_gamecube, "check_pins"), \
                    mock.patch.object(native_gamecube, "sha256", side_effect=fake_sha), \
                    mock.patch.object(native_gamecube, "executable", return_value=Path(tmp) / "tool"), \
                    mock.patch.object(native_gamecube, "ninja", return_value=Path(tmp) / "ninja"), \
                    mock.patch.object(native_gamecube, "run") as run_mock:
                native_gamecube.module(args)
            configure = run_mock.call_args_list[0].args[0]
            self.assertIn("-DRECOMPCORE_FAST_FP=ON", configure)
            manifest = json.loads((module_dir / "manifest.json").read_text())
            self.assertTrue(manifest["fast_fp"])


class ConversionSplitDefault(unittest.TestCase):
    # Fixture provenance: exact verified-GXBE69-rev0 generated.h
    # (sha 05b40083...), the input the conversion spike checked. The expected
    # candidate (dcac6fc8...) is the spike's verified output; a mismatch here
    # means the transform drifted and must be re-spiked, not adjusted.
    FIXTURE = Path(__file__).resolve().parent / "float-conversion-original-generated.h"
    ORIGINAL = "05b40083d151a9db2098c8746e637b1ecbae62d73213b26b94b74945fa1b5a1f"
    CANDIDATE = "dcac6fc866a0e49d9f5875c7c5a4a045e11209472f2123a0fc96062adee922d8"

    def run_module(self, module_dir, header_bytes):
        (module_dir / "codegen/generated").mkdir(parents=True)
        (module_dir / "codegen/generated/generated.h").write_bytes(header_bytes)
        identity = {"dol_sha256": native_gamecube.PINS["dol_sha256"],
                    "dolrecomp_revision": native_gamecube.PINS["dolrecomp_revision"],
                    "generator_sha256": "H" * 64, "backend": "c"}
        (module_dir / "generation.json").write_text(json.dumps(identity))
        dol = module_dir / "main.dol"
        args = argparse.Namespace(jobs=4, opt_level="2", dol=dol, fast_fp=False)
        def fake_sha(path):
            return native_gamecube.PINS["dol_sha256"] if Path(path).name == "main.dol" else "H" * 64
        with mock.patch.object(native_gamecube, "MODULE", module_dir), \
                mock.patch.object(native_gamecube, "check_pins"), \
                mock.patch.object(native_gamecube, "sha256", side_effect=fake_sha), \
                mock.patch.object(native_gamecube, "executable", return_value=module_dir / "tool"), \
                mock.patch.object(native_gamecube, "ninja", return_value=module_dir / "ninja"), \
                mock.patch.object(native_gamecube, "run"):
            native_gamecube.module(args)
        return json.loads((module_dir / "manifest.json").read_text())

    def test_applies_proven_split_to_original_header(self):
        import hashlib
        with tempfile.TemporaryDirectory() as tmp:
            manifest = self.run_module(Path(tmp) / "module", self.FIXTURE.read_bytes())
            header = (Path(tmp) / "module/codegen/generated/generated.h").read_bytes()
            self.assertEqual(hashlib.sha256(header).hexdigest(), self.CANDIDATE)
            self.assertTrue(manifest["conversion_split"])
            self.assertEqual(manifest["generated_header_sha256"], self.CANDIDATE)

    def test_keeps_existing_candidate_header(self):
        import hashlib
        from tools.native_float_conversion_spike import split_helpers
        with tempfile.TemporaryDirectory() as tmp:
            candidate = split_helpers(self.FIXTURE.read_text()).encode()
            self.assertEqual(hashlib.sha256(candidate).hexdigest(), self.CANDIDATE)
            manifest = self.run_module(Path(tmp) / "module", candidate)
            header = (Path(tmp) / "module/codegen/generated/generated.h").read_bytes()
            self.assertEqual(header, candidate)
            self.assertTrue(manifest["conversion_split"])

    def test_refuses_unknown_header(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(RuntimeError, "neither the verified original nor the candidate"):
                self.run_module(Path(tmp) / "module", b"// unknown header state\n")


if __name__ == "__main__":
    unittest.main()
