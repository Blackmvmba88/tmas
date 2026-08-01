import json
import tempfile
import unittest
from pathlib import Path

from visual_index.catalog import DEFAULT_EXCLUDES
from visual_index.cli import _write_neon_glass_artifacts
from visual_index.presets import build_neon_glass_preset
from visual_index.scanner import scan_project
from visual_index.semantic import build_semantic_system, contrast_ratio


class NeonGlassPresetTest(unittest.TestCase):
    def test_neon_glass_theme_is_accessible_and_registered(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data = scan_project(root, 1_000_000, DEFAULT_EXCLUDES, False)
            system = build_semantic_system(data)
            theme = system["themes"]["blackmamba-neon-glass"]

            self.assertGreaterEqual(contrast_ratio(theme["text"], theme["canvas"]), 4.5)
            self.assertGreaterEqual(contrast_ratio(theme["text-muted"], theme["canvas"]), 4.5)
            self.assertGreaterEqual(contrast_ratio(theme["accent"], theme["canvas"]), 3.0)
            self.assertGreaterEqual(contrast_ratio(theme["accent-secondary"], theme["canvas"]), 3.0)

    def test_writes_reviewable_preset_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            _write_neon_glass_artifacts(output)

            expected = (
                "blackmamba-neon-glass.json",
                "blackmamba-neon-glass.css",
                "blackmamba-neon-glass-demo.html",
            )
            for filename in expected:
                self.assertTrue((output / filename).exists(), filename)

            preset = json.loads((output / "blackmamba-neon-glass.json").read_text())
            self.assertEqual(preset["name"], "BlackMamba Neon Glass")
            self.assertEqual(set(preset["states"]), {"idle", "recording", "ready-to-send"})
            demo = (output / "blackmamba-neon-glass-demo.html").read_text()
            self.assertIn("Just start talking", demo)
            self.assertIn("Hold to record", demo)
            self.assertIn("prefers-reduced-motion", demo)


if __name__ == "__main__":
    unittest.main()
