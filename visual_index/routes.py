from __future__ import annotations

import re
from pathlib import PurePosixPath
from typing import Any

PAGE_EXTENSIONS = {".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte", ".astro", ".html", ".htm"}


def _segment(value: str) -> tuple[str | None, bool]:
    if not value or value.startswith("(") or value.startswith("@"):
        return None, False
    if value.startswith("[[...") and value.endswith("]]" ):
        return f"*{value[5:-2]}?", True
    if value.startswith("[...") and value.endswith("]"):
        return f"*{value[4:-1]}", True
    if value.startswith("[") and value.endswith("]"):
        return f":{value[1:-1]}", True
    return value, False


def _route_from_parts(parts: list[str]) -> tuple[str, bool]:
    converted: list[str] = []
    dynamic = False
    for part in parts:
        segment, is_dynamic = _segment(part)
        dynamic = dynamic or is_dynamic
        if segment is not None:
            converted.append(segment)
    if converted and converted[-1] == "index":
        converted.pop()
    route = "/" + "/".join(converted)
    return route or "/", dynamic


def _match_route(path: str) -> tuple[str, str, bool] | None:
    pure = PurePosixPath(path)
    suffix = pure.suffix.lower()
    if suffix not in PAGE_EXTENSIONS:
        return None
    parts = list(pure.parts)
    stem = pure.stem

    for prefix in (("app",), ("src", "app")):
        if tuple(parts[: len(prefix)]) == prefix and stem == "page":
            route, dynamic = _route_from_parts(parts[len(prefix):-1])
            return route, "next-app", dynamic

    if len(parts) >= 3 and parts[:2] == ["src", "routes"] and stem == "+page":
        route, dynamic = _route_from_parts(parts[2:-1])
        return route, "sveltekit", dynamic

    if len(parts) >= 3 and parts[:2] == ["src", "pages"] and suffix == ".astro":
        route, dynamic = _route_from_parts(parts[2:-1] + [stem])
        return route, "astro", dynamic

    for prefix in (("pages",), ("src", "pages")):
        if tuple(parts[: len(prefix)]) == prefix:
            if stem.startswith("_"):
                return None
            route, dynamic = _route_from_parts(parts[len(prefix):-1] + [stem])
            kind = "nuxt-pages" if suffix == ".vue" else "next-pages"
            return route, kind, dynamic

    if suffix in {".html", ".htm"} and len(parts) <= 3:
        route, dynamic = _route_from_parts(parts[:-1] + [stem])
        return route, "static-html", dynamic
    return None


def discover_visual_targets(data: dict[str, Any], semantic: dict[str, Any]) -> dict[str, Any]:
    routes: dict[tuple[str, str], dict[str, Any]] = {}
    stories = []
    for item in data["files"]:
        path = item["path"]
        if re.search(r"\.stories\.[cm]?[jt]sx?$", path):
            stories.append({"source": path, "kind": "storybook"})
        matched = _match_route(path)
        if matched:
            route, kind, dynamic = matched
            routes[(route, kind)] = {
                "route": route,
                "source": path,
                "kind": kind,
                "dynamic": dynamic,
                "enabled": not dynamic,
            }
    route_list = sorted(routes.values(), key=lambda item: (item["route"], item["kind"]))
    themes = list(semantic["themes"])
    viewports = [
        {"name": "desktop", "width": 1440, "height": 900},
        {"name": "tablet", "width": 834, "height": 1112},
        {"name": "mobile", "width": 390, "height": 844},
    ]
    enabled = [route for route in route_list if route["enabled"]]
    return {
        "schema_version": 1,
        "base_url": "http://127.0.0.1:3000",
        "routes": route_list,
        "stories": sorted(stories, key=lambda item: item["source"]),
        "themes": themes,
        "viewports": viewports,
        "capture_count": len(enabled) * len(themes) * len(viewports),
        "dynamic_routes_require_examples": any(route["dynamic"] for route in route_list),
    }


def render_playwright_spec(plan: dict[str, Any]) -> str:
    routes = [item["route"] for item in plan["routes"] if item["enabled"]]
    return f'''import {{ expect, test }} from "@playwright/test";

const routes = {routes!r};
const themes = {plan["themes"]!r};
const viewports = {plan["viewports"]!r};

for (const route of routes) {{
  for (const theme of themes) {{
    for (const viewport of viewports) {{
      test(`${{route}} · ${{theme}} · ${{viewport.name}}`, async ({{ page }}) => {{
        await page.setViewportSize({{ width: viewport.width, height: viewport.height }});
        await page.goto(route);
        await page.evaluate((value) => document.documentElement.dataset.theme = value, theme);
        await page.emulateMedia({{ reducedMotion: "reduce" }});
        await expect(page).toHaveScreenshot(
          `${{route.replaceAll("/", "_") || "home"}}--${{theme}}--${{viewport.name}}.png`,
          {{ fullPage: true, animations: "disabled" }}
        );
      }});
    }}
  }}
}}
'''


def render_playwright_config(plan: dict[str, Any]) -> str:
    return f'''import {{ defineConfig }} from "@playwright/test";

export default defineConfig({{
  testDir: ".",
  testMatch: "visual-regression.spec.ts",
  use: {{
    baseURL: "{plan['base_url']}",
    colorScheme: "dark",
    locale: "en-US",
    timezoneId: "UTC",
    serviceWorkers: "block",
  }},
  expect: {{ toHaveScreenshot: {{ maxDiffPixelRatio: 0.01 }} }},
  reporter: [["html", {{ outputFolder: "playwright-report" }}]],
}});
'''


def render_visual_regression_markdown(plan: dict[str, Any]) -> str:
    lines = [
        "# Visual Regression Plan", "",
        f"**Base URL:** `{plan['base_url']}`", "",
        f"**Planned captures:** {plan['capture_count']}", "",
        "## Routes", "",
        "| Route | Source | Router | Enabled |", "|---|---|---|---|",
    ]
    for route in plan["routes"]:
        lines.append(f"| `{route['route']}` | `{route['source']}` | {route['kind']} | {route['enabled']} |")
    if not plan["routes"]:
        lines.append("| _None detected_ | | | |")
    lines += ["", "## Capture matrix", ""]
    lines.append("- Themes: " + ", ".join(f"`{theme}`" for theme in plan["themes"]))
    lines.append("- Viewports: " + ", ".join(
        f"`{item['name']} {item['width']}×{item['height']}`" for item in plan["viewports"]
    ))
    if plan["dynamic_routes_require_examples"]:
        lines += ["", "> Dynamic routes are disabled until concrete example URLs are supplied."]
    return "\n".join(lines) + "\n"
