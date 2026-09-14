"""Validate the isolated arithmetic experiment and its acceptance gate."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('float_classify_spike', ROOT / 'tools/native_float_classify_spike.py')
SPIKE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SPIKE)
SOURCE = SPIKE.GXRUNTIME / 'src/core/cpu_interpreter_float.c'


@unittest.skipUnless(SOURCE.exists(), 'requires the pinned GXRuntime checkout')
class ClassifierTransformationTest(unittest.TestCase):
    def test_only_two_normal_classifier_returns_are_inserted(self):
        original = SOURCE.read_text()
        candidate = SPIKE.transform(original)
        for mask in ('0x7F800000u', '0x7FF0000000000000ull'):
            addition = ('    if (__builtin_expect(exponent != 0 && exponent != ' + mask + ', 1))\n'
                        '        return 4u << sign;\n')
            self.assertEqual(candidate.count(addition), 1)
            candidate = candidate.replace(addition, '')
        self.assertEqual(candidate, original)

    def test_changed_classifier_or_repeat_transform_is_rejected(self):
        original = SOURCE.read_text()
        with self.assertRaises(ValueError):
            SPIKE.transform(SPIKE.transform(original))
        with self.assertRaises(ValueError):
            SPIKE.transform(original.replace('return sign ? 0x08u : 0x04u;', 'return 0;'))

    def test_scoped_change_only_redirects_generated_fma(self):
        original = SOURCE.read_text()
        scoped = SPIKE.transform_scoped(original)
        for name in ('classify_f32', 'classify_f64'):
            start = scoped.index('static u32 generated_fma_' + name + '(')
            end = scoped.index('\n}', start) + 2
            self.assertIn('__builtin_expect', scoped[start:end])
            scoped = scoped[:start] + scoped[end + 2:]
        marker = 'set_fprf(cpu, single ? generated_fma_classify_f32((f32)result) : generated_fma_classify_f64(result));'
        self.assertEqual(scoped.count(marker), 1)
        scoped = scoped.replace(marker, marker.replace('generated_fma_', ''))
        self.assertEqual(scoped, original)


@unittest.skipUnless(platform.system() == 'Darwin' and platform.machine() == 'arm64' and
                     shutil.which('clang') and SOURCE.exists(), 'requires Apple Silicon and pinned GXRuntime')
class ClassifierDifferentialTest(unittest.TestCase):
    def test_cpu_state_flags_receipts_and_missing_acceptance(self):
        local = ROOT / 'local'
        local.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='float-classify-test-', dir=local) as directory:
            output = Path(directory) / 'build'
            with contextlib.redirect_stdout(io.StringIO()):
                SPIKE.prepare(SimpleNamespace(output=output, compiler='/usr/bin/clang'))
                with self.assertRaisesRegex(ValueError, 'differential check'):
                    SPIKE.run(SimpleNamespace(command='bench', output=output, rounds=1, iterations=1000))
                SPIKE.run(SimpleNamespace(command='check', output=output))
            result = json.loads((output / 'check.json').read_text())
            self.assertTrue(result['passed'])
            self.assertTrue(result['host_fpcr_fpsr_compared'])
            self.assertGreaterEqual(result['classifier_category_cases'], 233984)
            self.assertGreaterEqual(result['arithmetic_cases'], 431856)
            self.assertGreaterEqual(result['candidate_comparisons'], 863712)
            self.assertGreater(result['cpu_state_bytes'], 3000)

            # This is a protocol/consistency check; these short timings have no
            # performance interpretation.
            with contextlib.redirect_stdout(io.StringIO()):
                SPIKE.run(SimpleNamespace(command='bench', output=output, rounds=1, iterations=1000))
            benchmark = json.loads((output / 'benchmark.json').read_text())
            self.assertEqual({r['variant'] for r in benchmark['rounds']}, {'reference', 'candidate', 'scoped'})
            self.assertEqual(len(benchmark['summary']), 10)

            # Deliberately corrupt an unrelated guest register. A value-only
            # comparison would pass; the complete CPU-state check must reject it.
            candidate = output / 'scoped.c'
            source = candidate.read_text()
            marker = 'void set_fprf(CPUState* cpu, u32 value) {'
            self.assertEqual(source.count(marker), 1)
            candidate.write_text(source.replace(marker, marker + '\n    cpu->cr ^= 1u;'))
            with self.assertRaisesRegex(ValueError, 'receipt mismatch: scoped.c'):
                SPIKE.run(SimpleNamespace(command='check', output=output))
            command = json.loads((output / 'build.json').read_text())['commands'][0]
            compiled = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(compiled.returncode, 0, compiled.stdout + compiled.stderr)
            rejected = subprocess.run([str(output / 'harness'), 'check'], capture_output=True, text=True)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn('Mismatch op=', rejected.stderr)


if __name__ == '__main__':
    unittest.main()
