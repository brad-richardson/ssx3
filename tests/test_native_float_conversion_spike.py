"""Verify that the isolated conversion experiment catches faults and stale evidence."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tools import native_float_conversion_spike as spike


class ConversionEvidenceTests(unittest.TestCase):
    def test_outside_output_is_rejected_before_execution(self):
        with tempfile.TemporaryDirectory() as temporary:
            outside = Path(temporary) / 'candidate'
            with self.assertRaisesRegex(ValueError, 'under local'):
                spike.prepare(outside)
            self.assertFalse(outside.exists())
            with self.assertRaisesRegex(ValueError, 'under local'):
                spike.run(argparse.Namespace(output=outside, command='check', exhaustive=False))

    def test_changed_binary_and_stale_correctness_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary, patch.object(spike, 'ROOT', Path(temporary).resolve()):
            output = Path(temporary) / 'local' / 'candidate'
            output.mkdir(parents=True)
            (output / 'check').write_bytes(b'original binary')
            (output / 'check.c').write_text('original harness')
            (output / 'reference-generated.h').write_text('reference header')
            (output / 'candidate-generated.h').write_text('candidate header')
            receipt = dict(binary_sha256=spike.sha(output / 'check'),
                           harness_sha256=spike.sha(output / 'check.c'),
                           original_header_sha256=spike.sha(output / 'reference-generated.h'),
                           candidate_header_sha256=spike.sha(output / 'candidate-generated.h'))
            (output / 'build.json').write_text(json.dumps(receipt))
            args = argparse.Namespace(output=output, command='bench', iterations=1048576)
            (output / 'check.json').write_text(json.dumps(dict(passed=True, binary_sha256='stale')))
            with self.assertRaisesRegex(ValueError, 'exact binary first'):
                spike.run(args)
            (output / 'check').write_bytes(b'changed binary')
            with self.assertRaisesRegex(ValueError, 'harness changed'):
                spike.run(args)


@unittest.skipUnless(spike.GENERATED.exists() and Path('/usr/bin/clang').exists(),
                     'Requires the local generated header and production Apple compiler')
class ConversionNativeOracleTests(unittest.TestCase):
    def test_checker_rejects_an_incorrect_normal_exponent(self):
        # The production helper is the oracle. A plausible one-bit-format bug
        # must cause the native differential checker to exit unsuccessfully.
        with tempfile.TemporaryDirectory(dir=spike.ROOT / 'local') as temporary:
            output = Path(temporary) / 'negative-control'
            receipt = spike.prepare(output)
            source = (output / 'check.c').read_text()
            self.assertEqual(source.count('exp + 896u'), 1)
            (output / 'check.c').write_text(source.replace('exp + 896u', 'exp + 895u'))
            subprocess.run(receipt['command'], check=True, capture_output=True, text=True)
            result = subprocess.run([str(output / 'check'), 'check'], capture_output=True,
                                    text=True, timeout=20)
            self.assertEqual(result.returncode, 2)
            self.assertIn('from mismatch', result.stderr)

    def test_unrelated_helpers_and_original_exceptional_paths_are_retained(self):
        original = spike.GENERATED.read_text()
        candidate = spike.split_helpers(original)
        start, end = spike.helper_span(original)
        self.assertTrue(candidate.startswith(original[:start]))
        self.assertTrue(candidate.endswith(original[end:]))
        expected = original[start:end].replace('static inline ',
                                               'static __attribute__((noinline, cold)) ')
        for direction in ('from', 'to'):
            name = f'dolrecomp_f32_{direction}_bits'
            expected = expected.replace(name, name + '_slow')
        self.assertEqual(candidate[start:start + len(expected)], expected)


if __name__ == '__main__':
    unittest.main()
