import unittest
from pathlib import Path

from tools import gamecube_telemetry, live_course_request

ROOT = Path(__file__).resolve().parent.parent
COURSE_PATCH = (ROOT / "native/patches/recompcore-course-redirect.patch").read_text()
PLATFORM_PATCH = (ROOT / "native/patches/moderngekko-platform.patch").read_text()
APP_MM = (ROOT / "native/ios/App.mm").read_text()


class CoursePatchWiring(unittest.TestCase):
    def test_temp_polling_trigger_is_gone(self):
        self.assertNotIn("SSX3_TEST", COURSE_PATCH)
        self.assertNotIn("MaybeArmLiveSwitchWatcher", COURSE_PATCH)
        self.assertNotIn("live-switch watcher", COURSE_PATCH)

    def test_boot_hook_still_applies_env_manifest(self):
        self.assertIn("SSX3::ApplyCourseManifest(system)", COURSE_PATCH)
        self.assertIn('std::getenv("SSX_COURSE_MANIFEST")', COURSE_PATCH)

    def test_live_apply_path_present(self):
        for symbol in ("ApplyCourseManifestLive", "ApplyPendingCourseManifest",
                       "QueueCourseManifest", "ClearPendingCourseManifest",
                       "HasPendingCourseManifest", "ConsumeCourseRequestFile",
                       "RideLoaded", "DeferredRideLoaded"):
            with self.subTest(symbol=symbol):
                self.assertIn(symbol, COURSE_PATCH)

    def test_table_reverify_kept(self):
        self.assertIn("TablesLookRight", COURSE_PATCH)
        self.assertIn("EVENT_COUNT", COURSE_PATCH)

    def test_guard_uses_validated_telemetry_chain(self):
        # The mid-ride guard mirrors tools/gamecube_telemetry.py's watched
        # chain and bounds: game singleton -> race -> rider manager -> rider,
        # position words, MEM1 range, coordinate limit.
        root, *offsets = gamecube_telemetry.RIDER.split()
        self.assertIn(f"0x{root}u", COURSE_PATCH.lower())
        for offset in offsets:
            with self.subTest(offset=offset):
                self.assertIn(f"0x{offset}u", COURSE_PATCH)
        for field in ("240", "0x718", "0xd30"):
            with self.subTest(field=field):
                self.assertIn(field, COURSE_PATCH)
        # y/z are strided words past x, matching the telemetry's 244/248.
        self.assertIn("RIDER_POS_X + 4u", COURSE_PATCH)
        self.assertIn("0x80000000", COURSE_PATCH)
        self.assertIn("0x81800000", COURSE_PATCH)
        self.assertIn("1e7", COURSE_PATCH)


class DesktopWiring(unittest.TestCase):
    def test_request_file_trigger_present(self):
        self.assertIn("SSX3_COURSE_REQUEST", PLATFORM_PATCH)
        self.assertIn("ConsumeCourseRequestFile", PLATFORM_PATCH)
        self.assertIn("ApplyPendingCourseManifest", PLATFORM_PATCH)

    def test_apply_runs_under_a_guard_on_existing_thread(self):
        self.assertIn("Core::CPUThreadGuard guard(system)", PLATFORM_PATCH)
        # No new thread: the pump rides the existing title/metrics thread, so
        # no added line spawns one.
        added = [line for line in PLATFORM_PATCH.splitlines()
                 if line.startswith("+") and not line.startswith("+++")]
        spawns = [line for line in added
                  if "title_thread" not in line and "this_thread" not in line
                  and ("std::jthread" in line or "std::thread" in line)]
        self.assertEqual(spawns, [])


class IOSWiring(unittest.TestCase):
    def test_course_row_applies_live(self):
        self.assertIn("Core/Boot/Ssx3CoursePatch.h", APP_MM)
        self.assertIn("ApplyCourseManifestLive", APP_MM)
        self.assertIn("ApplyPendingCourseManifest", APP_MM)
        self.assertIn("CPUThreadGuard", APP_MM)


class CourseRequestProtocol(unittest.TestCase):
    def test_files_manifest_atomically(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "event5.txt"
            manifest.write_text("event = 5\narchive = alo\n")
            request = Path(directory) / "run-001.request"
            live_course_request.write_request(request, manifest)
            self.assertEqual(request.read_text(), str(manifest) + "\n")
            # No half-written producer litter beside the request.
            self.assertEqual(sorted(p.name for p in Path(directory).iterdir()),
                             ["event5.txt", "run-001.request"])

    def test_stock_request(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            request = Path(directory) / "run-001.request"
            live_course_request.write_request(request, live_course_request.STOCK)
            self.assertEqual(request.read_text(), "stock\n")

    def test_refuses_to_clobber_a_queued_request(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "event5.txt"
            manifest.write_text("event = 5\n")
            request = Path(directory) / "run-001.request"
            live_course_request.write_request(request, manifest)
            with self.assertRaises(FileExistsError):
                live_course_request.write_request(request, manifest)

    def test_missing_manifest_fails_before_any_write(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            request = Path(directory) / "run-001.request"
            with self.assertRaises(FileNotFoundError):
                live_course_request.write_request(request, Path(directory) / "absent.txt")
            self.assertFalse(request.exists())
            self.assertEqual(list(Path(directory).iterdir()), [])


if __name__ == "__main__":
    unittest.main()
