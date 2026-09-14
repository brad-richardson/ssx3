"""Synthetic evidence binding checks; these never invoke a compiler or game."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import native_float_conversion_spike as conversion
from tools import native_float_module_spike as module


class ConversionEvidenceBindingTests(unittest.TestCase):
    def fixture(self, root):
        output = root/'local/conversion'
        output.mkdir(parents=True)
        values = {'reference-generated.h': ('original_header_sha256', b'original header'),
                  'candidate-generated.h': ('candidate_header_sha256', b'candidate header'),
                  'check.c': ('harness_sha256', b'compiled source'),
                  'check': ('binary_sha256', b'compiled binary')}
        receipt = {}
        for name, (key, data) in values.items():
            (output/name).write_bytes(data)
            receipt[key] = conversion.sha(output/name)
        (output/'build.json').write_text(json.dumps(receipt))
        (output/'check.json').write_text(json.dumps(dict(passed=True, binary_sha256=receipt['binary_sha256'])))
        return output, receipt

    def test_verifier_binds_both_headers_harness_and_binary(self):
        for changed in ('reference-generated.h', 'candidate-generated.h', 'check.c', 'check'):
            with self.subTest(changed=changed), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary).resolve()
                with patch.object(conversion, 'ROOT', root):
                    output, receipt = self.fixture(root)
                    self.assertEqual(conversion.verify_conversion_receipt(output), receipt['candidate_header_sha256'])
                    (output/changed).write_bytes(b'changed after successful check')
                    with self.assertRaisesRegex(ValueError, 'changed|mismatch'):
                        conversion.verify_conversion_receipt(output)

    def test_verifier_requires_a_true_check_for_the_exact_binary(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            with patch.object(conversion, 'ROOT', root):
                output, receipt = self.fixture(root)
                for check in (dict(passed=True, binary_sha256='stale'),
                              dict(passed='true', binary_sha256=receipt['binary_sha256']),
                              dict(passed=False, binary_sha256=receipt['binary_sha256'])):
                    (output/'check.json').write_text(json.dumps(check))
                    with self.assertRaisesRegex(ValueError, 'exact binary first'):
                        conversion.verify_conversion_receipt(output)
                (output/'check.json').unlink()
                with self.assertRaisesRegex(ValueError, 'exact binary first'):
                    conversion.verify_conversion_receipt(output)
                self.assertEqual(conversion.verify_conversion_receipt(output, require_check=False),
                                 receipt['candidate_header_sha256'])

    def test_mismatched_module_candidate_is_rejected_before_recipes_or_copies(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            evidence, _ = self.fixture(root)
            generated = root/'generated'
            generated.mkdir()
            (generated/'generated.h').write_text('original header')
            output = root/'local/module'
            with patch.object(conversion, 'ROOT', root), patch.object(module, 'ROOT', root), \
                    patch.object(module, 'GENERATED', generated), \
                    patch.object(module, 'split_helpers', return_value='different candidate'), \
                    patch.object(module, 'recipes') as recipes:
                with self.assertRaisesRegex(ValueError, 'differs from verified conversion evidence'):
                    module.prepare(output, conversion_evidence=evidence)
                recipes.assert_not_called()
                self.assertFalse(output.exists())

    def test_build_rechecks_bound_evidence_and_private_header(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            evidence, receipt = self.fixture(root)
            output = root/'local/module'
            (output/'generated').mkdir(parents=True)
            private_header = output/'generated/generated.h'
            private_header.write_bytes((evidence/'candidate-generated.h').read_bytes())
            report = dict(schema=2, output=str(output), original_objects=[], toolchain={},
                          production_sources={}, private_inputs={},
                          baseline=dict(path=str(evidence/'check'), sha256=receipt['binary_sha256']),
                          conversion_evidence=dict(path=str(evidence),
                              candidate_header_sha256=receipt['candidate_header_sha256'],
                              build_receipt_sha256=conversion.sha(evidence/'build.json'),
                              check_receipt_sha256=conversion.sha(evidence/'check.json')))
            with patch.object(conversion, 'ROOT', root), patch.object(module, 'ROOT', root):
                module.verify_inputs(report)
                private_header.write_bytes(b'changed private candidate')
                with self.assertRaisesRegex(ValueError, 'Private candidate header differs'):
                    module.verify_inputs(report)
                private_header.write_bytes((evidence/'candidate-generated.h').read_bytes())
                (evidence/'check.json').write_text('{}')
                with self.assertRaisesRegex(ValueError, 'Bound conversion evidence changed'):
                    module.verify_inputs(report)

    def test_prepare_requires_evidence_and_build_uses_its_bound_manifest(self):
        output = str(module.ROOT/'local/example')
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                module.parse_args(['prepare', '--output', output])
            with self.assertRaises(SystemExit):
                module.parse_args(['build', '--output', output, '--conversion-evidence', output])
        prepared = module.parse_args(['prepare', '--output', output, '--conversion-evidence', output])
        self.assertEqual(prepared.conversion_evidence, Path(output))
        self.assertIsNone(module.parse_args(['build', '--output', output]).conversion_evidence)

    def test_build_rejects_an_unbound_legacy_manifest_before_execution(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            output = root/'local/module'
            output.mkdir(parents=True)
            (output/'manifest.json').write_text(json.dumps(dict(schema=1, status='prepared', output=str(output))))
            with patch.object(module, 'ROOT', root), patch.object(module, 'recipes') as recipes:
                with self.assertRaisesRegex(ValueError, 'bound conversion evidence'):
                    module.build(output)
                recipes.assert_not_called()


if __name__ == '__main__':
    unittest.main()
