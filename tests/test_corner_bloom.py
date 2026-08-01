import tempfile
import unittest
from pathlib import Path

from visual_index.cli import _write_neon_glass_artifacts
from visual_index.corner_bloom import enhance_neon_glass_demo, render_corner_bloom_css
from visual_index.local_preview import render_local_preview_runner


class CornerBloomTest(unittest.TestCase):
    def test_corner_layer_uses_four_localized_radial_gradients(self):
        css = render_corner_bloom_css()
        self.assertEqual(css.count("radial-gradient("), 4)
        self.assertIn("top left", css)
        self.assertIn("top right", css)
        self.assertIn("bottom left", css)
        self.assertIn("bottom right", css)
        self.assertIn("corner-bloom-active-opacity", css)
        self.assertNotIn("linear-gradient(", css)

    def test_demo_injection_and_generated_artifacts(self):
        document = "<html><style>.voice-panel {}</style></html>"
        enhanced = enhance_neon_glass_demo(document)
        self.assertIn(".voice-panel::before", enhanced)
        self.assertEqual(enhanced.count("</style>"), 1)

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            _write_neon_glass_artifacts(output)
            css_path = output / "blackmamba-neon-glass-corner-bloom.css"
            demo_path = output / "blackmamba-neon-glass-demo.html"
            runner_path = output / "serve-neon-glass-demo.sh"
            self.assertTrue(css_path.exists())
            self.assertTrue(demo_path.exists())
            self.assertTrue(runner_path.exists())
            self.assertTrue(runner_path.stat().st_mode & 0o111)
            self.assertIn(".voice-panel::before", demo_path.read_text())

    def test_local_preview_uses_loopback_http_not_blank_or_file_urls(self):
        runner = render_local_preview_runner()
        self.assertIn("http://127.0.0.1:${PORT}/blackmamba-neon-glass-demo.html", runner)
        self.assertIn("python3 -m http.server", runner)
        self.assertIn("--bind 127.0.0.1", runner)
        self.assertNotIn("about:blank", runner)
        self.assertNotIn("file://", runner)

    def test_preview_port_validation(self):
        with self.assertRaises(ValueError):
            render_local_preview_runner(80)
        with self.assertRaises(ValueError):
            render_local_preview_runner(70000)


if __name__ == "__main__":
    unittest.main()
