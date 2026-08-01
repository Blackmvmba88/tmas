import tempfile
import unittest
from pathlib import Path

from visual_index.cli import _write_neon_glass_artifacts
from visual_index.corner_bloom import enhance_neon_glass_demo, render_corner_bloom_css


class CornerBloomTest(unittest.TestCase):
    def test_corner_layer_uses_four_localized_radial_gradients(self):
        css = render_corner_bloom_css()
        self.assertEqual(css.count("radial-gradient("), 4)
        self.assertIn("top left", css)
        self.assertIn("top right", css)
        self.assertIn("bottom left", css)
        self.assertIn("bottom right", css)
        self.assertIn("corner-bloom-active-opacity", css)

    def test_demo_injection_and_generated_artifact(self):
        document = "<html><style>.voice-panel {}</style></html>"
        enhanced = enhance_neon_glass_demo(document)
        self.assertIn(".voice-panel::before", enhanced)
        self.assertEqual(enhanced.count("</style>"), 1)

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            _write_neon_glass_artifacts(output)
            css_path = output / "blackmamba-neon-glass-corner-bloom.css"
            demo_path = output / "blackmamba-neon-glass-demo.html"
            self.assertTrue(css_path.exists())
            self.assertTrue(demo_path.exists())
            self.assertIn(".voice-panel::before", demo_path.read_text())


if __name__ == "__main__":
    unittest.main()
