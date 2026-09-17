import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.native_gamecube import CORE_STACK

ROOT = Path(__file__).resolve().parent.parent
PINS = json.loads((ROOT / "native/dependencies.json").read_text())
SOURCE = ROOT / "third_party/ModernGekko"
CORE = SOURCE / "vendor/dolphin"

# Full Android stacks, bottom to top. The desktop CORE_STACK comes first on
# the inner tree (the Android build consumes the same vendor sources), then
# the headless/EGL/Vulkan bring-up layers.
INNER_ANDROID_STACK = tuple(CORE_STACK) + (
    "recompcore-android-headless.patch",
    "recompcore-android-egl.patch",
    "recompcore-android-vulkan.patch",
)
OUTER_ANDROID_STACK = (
    "moderngekko-platform.patch",
    "moderngekko-android-headless.patch",
    "moderngekko-android-egl.patch",
)


def apply_stack(repo, revision, stack):
    """Apply every patch in order to a pristine worktree; raise on failure."""
    tmp = tempfile.mkdtemp(prefix="android-stack-")
    worktree = str(Path(tmp) / "tree")
    subprocess.run(["git", "-C", str(repo), "worktree", "add", "--detach", worktree, revision],
                   check=True, capture_output=True, text=True)
    try:
        for name in stack:
            patch = ROOT / "native/patches" / name
            result = subprocess.run(["git", "-C", worktree, "apply", str(patch)],
                                    capture_output=True, text=True)
            if result.returncode != 0:
                raise AssertionError(f"{name} failed to apply:\n{result.stderr}")
    finally:
        subprocess.run(["git", "-C", str(repo), "worktree", "remove", "--force", worktree],
                       capture_output=True)


class AndroidPatchStack(unittest.TestCase):
    def test_inner_stack_applies_in_order(self):
        if not (CORE / ".git").exists():
            self.skipTest("ModernGekko checkout not present")
        apply_stack(CORE, PINS["recompcore_revision"], INNER_ANDROID_STACK)

    def test_outer_stack_applies_in_order(self):
        if not (SOURCE / ".git").exists():
            self.skipTest("ModernGekko checkout not present")
        apply_stack(SOURCE, PINS["moderngekko"]["revision"], OUTER_ANDROID_STACK)


if __name__ == "__main__":
    unittest.main()
