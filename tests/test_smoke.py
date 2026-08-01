import json
import tempfile
import unittest
from pathlib import Path

from visual_index.catalog import DEFAULT_EXCLUDES
from visual_index.render import write_reports
from visual_index.scanner import scan_project


class VisualIndexSmokeTest(unittest.TestCase):
    def test_scans_tokens_colors_and_motion(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "styles.css").write_text(
                ":root { --brand: #ff00aa; }\n.button { color: var(--brand); transition: opacity .2s; }\n"
                "@keyframes pulse { from { opacity: 0 } to { opacity: 1 } }",
                encoding="utf-8",
            )
            data = scan_project(root, 1_000_000, DEFAULT_EXCLUDES, False)
            data["meta"] = {
                "version": "test",
                "file_count": len(data["files"]),
                "generated_at": "now",
                "project_root": str(root),
            }
            output = root / ".visual-index"
            write_reports(data, output)
            self.assertEqual(data["summary"]["unique_color_literals"], 1)
            self.assertEqual(data["summary"]["keyframes"], 1)
            self.assertTrue((output / "visual-index.json").exists())
            parsed = json.loads((output / "visual-index.json").read_text())
            self.assertEqual(parsed["summary"]["css_variables_defined"], 1)


if __name__ == "__main__":
    unittest.main()
