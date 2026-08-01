import json
import tempfile
import unittest
from pathlib import Path

from visual_index.catalog import DEFAULT_EXCLUDES
from visual_index.graph import build_dependency_graph
from visual_index.render import write_reports
from visual_index.scanner import scan_project
from visual_index.semantic import build_semantic_system, contrast_ratio


class VisualIndexSmokeTest(unittest.TestCase):
    def _scan(self, root: Path):
        data = scan_project(root, 1_000_000, DEFAULT_EXCLUDES, False)
        data["meta"] = {
            "version": "test",
            "file_count": len(data["files"]),
            "generated_at": "now",
            "project_root": str(root),
        }
        return data

    def test_scans_tokens_colors_motion_and_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "styles.css").write_text(
                ":root { --brand: #ff00aa; --bg: #090b11; --text: #ffffff; }\n"
                ".button { color: var(--brand); transition: opacity .2s; }\n"
                "@keyframes pulse { from { opacity: 0 } to { opacity: 1 } }",
                encoding="utf-8",
            )
            data = self._scan(root)
            output = root / ".visual-index"
            write_reports(data, output)
            self.assertEqual(data["summary"]["unique_color_literals"], 3)
            self.assertEqual(data["summary"]["keyframes"], 1)
            for filename in (
                "visual-index.json", "visual-index.html", "VISUAL_INDEX.md",
                "semantic-tokens.json", "themes.css", "accessibility-audit.json",
                "dependency-graph.json", "dependency-graph.dot", "MIGRATION_PLAN.md",
            ):
                self.assertTrue((output / filename).exists(), filename)
            parsed = json.loads((output / "visual-index.json").read_text())
            self.assertIn("derived", parsed)

    def test_resolves_relative_dependency_graph(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src").mkdir()
            (root / "src" / "App.tsx").write_text(
                'import Button from "./Button"; export default Button;', encoding="utf-8"
            )
            (root / "src" / "Button.tsx").write_text(
                "export default function Button() {}", encoding="utf-8"
            )
            graph = build_dependency_graph(self._scan(root))
            self.assertEqual(graph["summary"]["internal_edges"], 1)
            self.assertEqual(graph["internal_edges"][0]["target"], "src/Button.tsx")

    def test_generated_themes_have_readable_primary_text(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "app.css").write_text(
                "body{background:#090b11;color:#f5f7ff}.cta{color:#2fe0b6}", encoding="utf-8"
            )
            semantic = build_semantic_system(self._scan(root))
            self.assertTrue(semantic["accessibility"]["all_required_checks_pass"])
            for tokens in semantic["themes"].values():
                self.assertGreaterEqual(contrast_ratio(tokens["text"], tokens["canvas"]), 4.5)


if __name__ == "__main__":
    unittest.main()
