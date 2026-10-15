import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "native_vu"))
from run_gameplay_validation import (
    dead_flag_environment,
    gs_cut_environment,
    vblank_environment,
    vif_fence_profile_environment,
)


class GameplayValidationEnvironmentTests(unittest.TestCase):
    def test_dead_flag_elimination_is_opt_in(self):
        self.assertEqual(dead_flag_environment(False), [])
        self.assertEqual(
            dead_flag_environment(True),
            ["--env", "NOBLE_VU_DEAD_FLAG_ELIMINATION=1"],
        )

    def test_vif_fence_profile_is_forwarded_with_a_gameplay_gate(self):
        self.assertEqual(vif_fence_profile_environment(False, Path("ready")), [])
        self.assertEqual(
            vif_fence_profile_environment(True, Path("ready")),
            [
                "--env",
                "PS2_VIF1_FENCE_PROFILE=1",
                "--env",
                "PS2_VIF1_FENCE_PROFILE_GATE=ready",
            ],
        )

    def test_gs_cuts_are_forwarded_with_a_gameplay_gate(self):
        gate = Path("gs_cut_ready")
        self.assertEqual(gs_cut_environment(False, False, gate), [])
        self.assertEqual(
            gs_cut_environment(True, False, gate),
            [
                "--env",
                "PS2_GS_PGS_SKIP_FULLSCREEN_BLENDS=1",
                "--env",
                "PS2_GS_PGS_DIAGNOSTIC_GATE=gs_cut_ready",
            ],
        )
        self.assertEqual(
            gs_cut_environment(False, True, gate),
            [
                "--env",
                "PS2_GS_PGS_SUPPRESS_TEXTURE_INVALIDATION=1",
                "--env",
                "PS2_GS_PGS_DIAGNOSTIC_GATE=gs_cut_ready",
            ],
        )

    def test_unpaced_vblank_is_forwarded_only_when_requested(self):
        self.assertEqual(vblank_environment(False), [])
        self.assertEqual(
            vblank_environment(True),
            ["--env", "PS2_VBLANK_DIAGNOSTIC_UNPACED=1"],
        )

    def test_unpaced_vblank_can_be_gated_until_gameplay(self):
        self.assertEqual(
            vblank_environment(True, Path("measurement_ready")),
            [
                "--env",
                "PS2_VBLANK_DIAGNOSTIC_UNPACED=1",
                "--env",
                "PS2_VBLANK_DIAGNOSTIC_GATE=measurement_ready",
            ],
        )


if __name__ == "__main__":
    unittest.main()
