import argparse
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tools import mobile_gamecube


class DeviceLaunch(unittest.TestCase):
    def test_fast_boot_modes_and_state_anchor_require_explicit_launch_authorization(self):
        for argv in (["collect","--debug-main-menu"], ["install","--normal-boot"],
                     ["launch","--debug-main-menu","--normal-boot"]):
            with self.subTest(argv=argv), mock.patch("sys.argv",["mobile_gamecube.py",*argv,"--device","PHONE"]), \
                    mock.patch.object(mobile_gamecube,"command") as command:
                with self.assertRaises(SystemExit) as stopped:mobile_gamecube.main()
                self.assertEqual(stopped.exception.code,2);command.assert_not_called()
        for simulator in (False,True):
            with self.subTest(simulator=simulator), tempfile.TemporaryDirectory() as tmp, \
                    mock.patch.object(mobile_gamecube,"REPORTS",Path(tmp)), \
                    mock.patch.object(mobile_gamecube,"copy_to") as copy, \
                    mock.patch.object(mobile_gamecube,"simulator_documents",return_value=Path(tmp)) as documents, \
                    mock.patch.object(mobile_gamecube,"command") as command:
                args=argparse.Namespace(device="DEVICE",simulator=simulator,
                    sequence=Path("native/ios/main-menu-smoke.json"),debug_main_menu=False)
                with self.assertRaisesRegex(ValueError,"debug-main-menu"):mobile_gamecube.launch(args)
                copy.assert_not_called();documents.assert_not_called();command.assert_not_called()
                args.debug_main_menu=True;mobile_gamecube.launch(args)
                argv=command.call_args.args[0]
                self.assertEqual(argv[argv.index(mobile_gamecube.BUNDLE)+1:],
                    ([] if simulator else ["--"])+["-ssxAutoTest","-ssxDebugMainMenu"])
                args.sequence=None;args.debug_main_menu=False;args.normal_boot=True
                mobile_gamecube.launch(args);argv=command.call_args.args[0]
                self.assertEqual(argv[argv.index(mobile_gamecube.BUNDLE)+1:],
                    ([] if simulator else ["--"])+["-ssxNormalBoot"])

    def test_internal_scale_rejects_invalid_values_before_device_changes(self):
        for simulator in (False, True):
            for scale in (0, 5, 1.5, "2", True):
                with self.subTest(simulator=simulator, scale=scale), \
                        mock.patch.object(mobile_gamecube, "copy_to") as copy, \
                        mock.patch.object(mobile_gamecube, "simulator_documents") as documents, \
                        mock.patch.object(mobile_gamecube, "command") as command:
                    with self.assertRaisesRegex(ValueError, "internal-scale"):
                        mobile_gamecube.launch(argparse.Namespace(device="DEVICE", simulator=simulator,
                            sequence=Path("native/ios/snow-jam-smoke.json"), internal_scale=scale))
                    copy.assert_not_called()
                    documents.assert_not_called()
                    command.assert_not_called()

    def test_internal_scale_parser_rejects_nonlaunch_and_invalid_choices(self):
        for operation, scale in (("collect", "2"), ("install", "1"), ("launch", "0"),
                                 ("launch", "5"), ("launch", "1.5")):
            with self.subTest(operation=operation, scale=scale), \
                    mock.patch("sys.argv", ["mobile_gamecube.py", operation, "--device", "PHONE",
                                           "--internal-scale", scale]), \
                    mock.patch.object(mobile_gamecube, operation) as perform:
                with self.assertRaises(SystemExit) as stopped:
                    mobile_gamecube.main()
                self.assertEqual(stopped.exception.code, 2)
                perform.assert_not_called()

    def test_internal_scale_parser_forwards_integer_and_leaves_default_unspecified(self):
        for scale in (None, 1, 2):
            argv=["mobile_gamecube.py", "launch", "--device", "PHONE"]
            if scale is not None:
                argv.extend(["--internal-scale", str(scale)])
            with self.subTest(scale=scale), mock.patch("sys.argv", argv), \
                    mock.patch.object(mobile_gamecube, "launch") as launch:
                mobile_gamecube.main()
                self.assertEqual(launch.call_args.args[0].internal_scale, scale)

    def test_internal_scale_reaches_app_independently_of_output_and_automation(self):
        for simulator in (False, True):
            for scale in (1, 2):
                for output in (None, "three-quarter", "match-internal", "half"):
                    for sequence in (None, Path("native/ios/snow-jam-smoke.json")):
                        with self.subTest(simulator=simulator, scale=scale, output=output, sequence=sequence), \
                                tempfile.TemporaryDirectory() as tmp, \
                                mock.patch.object(mobile_gamecube, "REPORTS", Path(tmp)), \
                                mock.patch.object(mobile_gamecube, "simulator_documents", return_value=Path(tmp)), \
                                mock.patch.object(mobile_gamecube, "copy_to"), \
                                mock.patch.object(mobile_gamecube, "command") as command:
                            mobile_gamecube.launch(argparse.Namespace(device="DEVICE", simulator=simulator,
                                sequence=sequence, output_scale=output, internal_scale=scale))
                            argv=command.call_args.args[0]
                            flags=[] if simulator else ["--"]
                            if sequence:
                                flags.append("-ssxAutoTest")
                            if output:
                                flags.extend(["-ssxOutputScale", output])
                            flags.extend(["-ssxInternalScale", str(scale)])
                            self.assertEqual(argv[argv.index(mobile_gamecube.BUNDLE)+1:], flags)

    def test_null_audio_rejects_phone_unbounded_and_other_operations_before_device_changes(self):
        for simulator, sequence in ((False, Path("native/ios/snow-jam-smoke.json")), (True, None)):
            with self.subTest(simulator=simulator, sequence=sequence), \
                    mock.patch.object(mobile_gamecube, "copy_to") as copy, \
                    mock.patch.object(mobile_gamecube, "simulator_documents") as documents, \
                    mock.patch.object(mobile_gamecube, "command") as command:
                with self.assertRaises(ValueError):
                    mobile_gamecube.launch(argparse.Namespace(device="DEVICE", simulator=simulator,
                        sequence=sequence, simulator_null_audio=True))
                copy.assert_not_called()
                documents.assert_not_called()
                command.assert_not_called()
        with mock.patch("sys.argv", ["mobile_gamecube.py", "collect", "--simulator", "--device", "SIM",
                "--sequence", "native/ios/snow-jam-smoke.json", "--simulator-null-audio"]), \
                mock.patch.object(mobile_gamecube, "collect") as collect, \
                mock.patch.object(mobile_gamecube, "command") as command:
            with self.assertRaises(SystemExit) as stopped:
                mobile_gamecube.main()
            self.assertEqual(stopped.exception.code, 2)
            collect.assert_not_called()
            command.assert_not_called()

    def test_null_audio_requires_valid_sequence_and_forwards_simulator_flag(self):
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(mobile_gamecube, "simulator_documents", return_value=Path(tmp)), \
                mock.patch.object(mobile_gamecube, "copy_to") as phone_copy, \
                mock.patch.object(mobile_gamecube, "command") as command:
            sequence=Path(tmp)/"sequence.json"
            sequence.write_text(json.dumps(dict(duration=0, events=[])))
            args=argparse.Namespace(device="SIM", simulator=True, sequence=sequence,
                simulator_null_audio=True, output_scale="half", smoothing_at=155)
            with self.assertRaises(ValueError):
                mobile_gamecube.launch(args)
            self.assertFalse((Path(tmp)/"test-sequence.json").exists())
            command.assert_not_called()
            sequence.write_text(json.dumps(dict(duration=200, events=[])))
            mobile_gamecube.launch(args)
            argv=command.call_args.args[0]
            self.assertEqual(argv[argv.index(mobile_gamecube.BUNDLE)+1:],
                ["-ssxAutoTest", "-ssxOutputScale", "half", "-ssxSmoothingAt", "155", "-ssxNullAudio"])
            self.assertEqual((Path(tmp)/"test-sequence.json").read_bytes(),sequence.read_bytes())
            phone_copy.assert_not_called()

    def test_scheduled_trial_requires_bounded_sequence_before_device_changes(self):
        for sequence, at in ((None, 10), (Path("native/ios/snow-jam-smoke.json"), float('nan')),
                             (Path("native/ios/snow-jam-smoke.json"), -1),
                             (Path("native/ios/snow-jam-smoke.json"), 201)):
            with self.subTest(sequence=sequence, at=at), \
                    mock.patch.object(mobile_gamecube, "copy_to") as copy, \
                    mock.patch.object(mobile_gamecube, "command") as command:
                with self.assertRaises(ValueError):
                    mobile_gamecube.launch(argparse.Namespace(device="PHONE", simulator=False,
                                                             sequence=sequence, smoothing_at=at))
                copy.assert_not_called()
                command.assert_not_called()

    def test_scheduled_f_trial_requires_bounded_sequence_before_device_changes(self):
        for sequence, at in ((None, 10), (Path("native/ios/snow-jam-smoke.json"), float('nan')),
                             (Path("native/ios/snow-jam-smoke.json"), -1),
                             (Path("native/ios/snow-jam-smoke.json"), 201)):
            with self.subTest(sequence=sequence, at=at), \
                    mock.patch.object(mobile_gamecube, "copy_to") as copy, \
                    mock.patch.object(mobile_gamecube, "command") as command:
                with self.assertRaises(ValueError):
                    mobile_gamecube.launch(argparse.Namespace(device="PHONE", simulator=False,
                                                             sequence=sequence, f_at=at))
                copy.assert_not_called()
                command.assert_not_called()

    def test_f_at_applies_only_to_launch(self):
        with mock.patch("sys.argv", ["mobile_gamecube.py", "collect", "--device", "PHONE",
                "--f-at", "10"]), \
                mock.patch.object(mobile_gamecube, "collect") as collect, \
                mock.patch.object(mobile_gamecube, "command") as command:
            with self.assertRaises(SystemExit) as stopped:
                mobile_gamecube.main()
            self.assertEqual(stopped.exception.code, 2)
            collect.assert_not_called()
            command.assert_not_called()

    def test_f_flag_reaches_app_after_argument_separator(self):
        args = argparse.Namespace(device="PHONE", simulator=False,
                                  sequence=Path("native/ios/snow-jam-smoke.json"), f_at=155.0)
        calls = []
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(mobile_gamecube, "REPORTS", Path(tmp)), \
                mock.patch.object(mobile_gamecube, "copy_to"), \
                mock.patch.object(mobile_gamecube, "command", side_effect=lambda c: calls.append(c)):
            mobile_gamecube.launch(args)
        self.assertEqual(len(calls), 1)
        command = calls[0]
        bundle = command.index(mobile_gamecube.BUNDLE)
        self.assertEqual(command[bundle + 1:], ["--", "-ssxAutoTest", "-ssxFAt", "155.0"])

    def test_app_flags_follow_argument_separator(self):
        # devicectl parsed "-ssxAutoTest" as its own "-t" option until "--" was added.
        args = argparse.Namespace(device="PHONE", simulator=False,
                                  sequence=Path("native/ios/snow-jam-smoke.json"), smoothing_at=155.0)
        calls = []
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(mobile_gamecube, "REPORTS", Path(tmp)), \
                mock.patch.object(mobile_gamecube, "copy_to"), \
                mock.patch.object(mobile_gamecube, "command", side_effect=lambda c: calls.append(c)):
            mobile_gamecube.launch(args)
        self.assertEqual(len(calls), 1)
        command = calls[0]
        bundle = command.index(mobile_gamecube.BUNDLE)
        self.assertEqual(command[bundle + 1:], ["--", "-ssxAutoTest", "-ssxSmoothingAt", "155.0"])

    def test_course_manifest_and_textures_apply_only_to_launch(self):
        for argv in (["mobile_gamecube.py", "collect", "--device", "PHONE",
                     "--course-manifest", "stock"],
                    ["mobile_gamecube.py", "collect", "--device", "PHONE",
                     "--textures", "stock"],
                    ["mobile_gamecube.py", "launch", "--device", "PHONE",
                     "--textures", "upscaled"]):
            with self.subTest(argv=argv), \
                    mock.patch("sys.argv", argv), \
                    mock.patch.object(mobile_gamecube, "collect") as collect, \
                    mock.patch.object(mobile_gamecube, "command") as command:
                with self.assertRaises(SystemExit) as stopped:
                    mobile_gamecube.main()
                self.assertEqual(stopped.exception.code, 2)
                collect.assert_not_called()
                command.assert_not_called()

    def test_course_manifest_rejects_non_bare_names_before_device_changes(self):
        for name in ("../Garibaldi.txt", ".hidden", "sub/dir.txt"):
            with self.subTest(name=name), \
                    mock.patch.object(mobile_gamecube, "copy_to") as copy, \
                    mock.patch.object(mobile_gamecube, "command") as command:
                with self.assertRaises(ValueError):
                    mobile_gamecube.launch(argparse.Namespace(device="PHONE", simulator=False,
                                                              sequence=None, course_manifest=name))
                copy.assert_not_called()
                command.assert_not_called()

    def test_audio_dump_applies_only_to_launch_and_reaches_app(self):
        with mock.patch("sys.argv", ["mobile_gamecube.py", "collect", "--device", "PHONE",
                "--audio-dump"]), \
                mock.patch.object(mobile_gamecube, "collect") as collect, \
                mock.patch.object(mobile_gamecube, "command") as command:
            with self.assertRaises(SystemExit) as stopped:
                mobile_gamecube.main()
            self.assertEqual(stopped.exception.code, 2)
            collect.assert_not_called()
            command.assert_not_called()
        args = argparse.Namespace(device="PHONE", simulator=False, sequence=None, audio_dump=True)
        calls = []
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(mobile_gamecube, "REPORTS", Path(tmp)), \
                mock.patch.object(mobile_gamecube, "copy_to"), \
                mock.patch.object(mobile_gamecube, "command", side_effect=lambda c: calls.append(c)):
            mobile_gamecube.launch(args)
        command = calls[0]
        bundle = command.index(mobile_gamecube.BUNDLE)
        self.assertEqual(command[bundle + 1:], ["--", "-ssxAudioDump"])

    def test_boot_overrides_reach_app_without_sequence(self):
        args = argparse.Namespace(device="PHONE", simulator=False, sequence=None,
                                  course_manifest="stock", textures="stock")
        calls = []
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(mobile_gamecube, "REPORTS", Path(tmp)), \
                mock.patch.object(mobile_gamecube, "copy_to"), \
                mock.patch.object(mobile_gamecube, "command", side_effect=lambda c: calls.append(c)):
            mobile_gamecube.launch(args)
        self.assertEqual(len(calls), 1)
        command = calls[0]
        bundle = command.index(mobile_gamecube.BUNDLE)
        self.assertEqual(command[bundle + 1:],
                         ["--", "-ssxCourseManifest", "stock", "-ssxTextures", "stock"])
        self.assertNotIn("--", command[:bundle])

    def test_resolution_option_reaches_app_with_and_without_sequence(self):
        for simulator in (False, True):
            for scale in ("full", "three-quarter", "match-internal", "half"):
                for sequence in (None, Path("native/ios/snow-jam-smoke.json")):
                    with self.subTest(simulator=simulator, scale=scale, sequence=sequence), \
                            tempfile.TemporaryDirectory() as tmp, \
                            mock.patch.object(mobile_gamecube, "REPORTS", Path(tmp)), \
                            mock.patch.object(mobile_gamecube, "simulator_documents", return_value=Path(tmp)), \
                            mock.patch.object(mobile_gamecube, "copy_to"), \
                            mock.patch.object(mobile_gamecube, "command") as command:
                        args = argparse.Namespace(device="DEVICE", simulator=simulator,
                                                  sequence=sequence, output_scale=scale)
                        mobile_gamecube.launch(args)
                        argv = command.call_args.args[0]
                        flags = ([] if simulator else ["--"])
                        if sequence:
                            flags.append("-ssxAutoTest")
                        flags.extend(["-ssxOutputScale", scale])
                        self.assertEqual(argv[argv.index(mobile_gamecube.BUNDLE)+1:], flags)


class WorldPush(unittest.TestCase):
    def test_world_copies_one_bigf_archive_into_the_container(self):
        with tempfile.TemporaryDirectory() as tmp:
            world = Path(tmp) / "BAM.BIG"
            world.write_bytes(b"BIGF" + bytes(12))
            args = argparse.Namespace(device="PHONE", simulator=False, world=world)
            calls = []
            with mock.patch.object(mobile_gamecube, "REPORTS", Path(tmp)/'reports'), \
                 mock.patch.object(mobile_gamecube, "copy_to", side_effect=lambda a, s, d, timeout=0: calls.append((s, d))):
                mobile_gamecube.world(args)
            self.assertEqual(calls[0], (world, "Documents/Game/files/data/worlds/bam.big"))
            self.assertEqual(calls[1][1], 'Documents/course-build.json')
            metadata=json.loads(calls[1][0].read_text())
            self.assertEqual(metadata['archive_sha256'],mobile_gamecube.native.sha256(world))
            self.assertEqual(metadata['build'],world.parent.name)
            (world.parent/'experiment.json').write_text(json.dumps({'output_sha256':'wrong'}))
            with self.assertRaisesRegex(RuntimeError,'recipe'):
                mobile_gamecube.world(args)
            world.write_bytes(b"nope")
            with self.assertRaises(RuntimeError):
                mobile_gamecube.world(args)


if __name__ == "__main__":
    unittest.main()
