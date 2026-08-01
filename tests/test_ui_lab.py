import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "ui-lab"


class UiComponentLabTest(unittest.TestCase):
    def test_lab_assets_exist_and_are_offline(self):
        expected = [LAB / "index.html", LAB / "styles.css", LAB / "app.js"]
        for path in expected:
            self.assertTrue(path.is_file(), path)

        index = (LAB / "index.html").read_text(encoding="utf-8")
        self.assertIn("UI Component Lab", index)
        self.assertIn('id="componentGrid"', index)
        self.assertIn('id="exportButton"', index)
        self.assertNotIn("https://", index)
        self.assertNotIn("http://", index)

    def test_catalog_contains_twelve_reviewable_candidates(self):
        script = (LAB / "app.js").read_text(encoding="utf-8")
        ids = re.findall(r'id: "(BM-[A-Z]+-\d{3})"', script)
        self.assertEqual(len(ids), 12)
        self.assertEqual(len(set(ids)), 12)
        self.assertIn("score", script)
        self.assertIn("approved", script)
        self.assertIn("revise", script)
        self.assertIn("rejected", script)
        self.assertIn("localStorage", script)
        self.assertIn("exportReviews", script)

    def test_visual_states_and_accessibility_contract(self):
        css = (LAB / "styles.css").read_text(encoding="utf-8")
        html = (LAB / "index.html").read_text(encoding="utf-8")
        self.assertIn(":focus-visible", css)
        self.assertIn("prefers-reduced-motion", css)
        self.assertIn(".demo-button.liquid-chrome", css)
        self.assertIn(".demo-button.neon-amber", css)
        self.assertIn(".demo-toggle[aria-pressed=\"true\"]", css)
        self.assertIn("aria-live=\"polite\"", html)
        self.assertIn("aria-label=\"Evaluación\"", html)

    def test_preview_server_binds_only_to_loopback(self):
        server = (ROOT / "serve-ui-lab.py").read_text(encoding="utf-8")
        self.assertIn('("127.0.0.1", port)', server)
        self.assertIn("http://127.0.0.1", server)
        self.assertNotIn("0.0.0.0", server)
        self.assertNotIn("file://", server)
        self.assertNotIn("about:blank", server)
        self.assertIn("1024 <= port <= 65535", server)


if __name__ == "__main__":
    unittest.main()
