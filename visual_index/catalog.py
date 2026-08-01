from __future__ import annotations

import re

DEFAULT_EXCLUDES = {
    ".git", ".svn", ".hg", ".idea", ".vscode", "node_modules", "vendor",
    "Pods", "DerivedData", "dist", "build", "coverage", ".next", ".nuxt",
    ".svelte-kit", ".turbo", ".cache", ".parcel-cache", "__pycache__",
    ".pytest_cache", ".visual-index", ".venv",
}

TEXT_EXTENSIONS = {
    ".css", ".scss", ".sass", ".less", ".styl", ".js", ".jsx", ".ts",
    ".tsx", ".mjs", ".cjs", ".vue", ".svelte", ".astro", ".html", ".htm",
    ".json", ".json5", ".yaml", ".yml", ".toml", ".md", ".mdx", ".swift",
    ".kt", ".kts", ".dart", ".xml",
}

ASSET_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".avif", ".svg", ".ico",
    ".pdf", ".ai", ".psd", ".sketch", ".fig", ".mp4", ".mov", ".webm",
    ".m4v", ".lottie", ".riv",
}
FONT_EXTENSIONS = {".ttf", ".otf", ".woff", ".woff2", ".eot"}

CATEGORY_EXTENSIONS = {
    "styles": {".css", ".scss", ".sass", ".less", ".styl"},
    "components": {".jsx", ".tsx", ".vue", ".svelte", ".astro", ".swift", ".kt", ".dart"},
    "markup": {".html", ".htm", ".mdx"},
    "tokens_and_data": {".json", ".json5", ".yaml", ".yml", ".toml"},
    "scripts": {".js", ".ts", ".mjs", ".cjs"},
    "documentation": {".md"},
}

PRIORITY_NAMES = {
    "package.json", "theme.json", "tokens.json", "design-tokens.json",
    "tailwind.config.js", "tailwind.config.ts", "tailwind.config.cjs",
    "postcss.config.js", "postcss.config.cjs", "vite.config.js", "vite.config.ts",
    "next.config.js", "next.config.mjs", "nuxt.config.ts", "svelte.config.js",
    "astro.config.mjs", "styles.css", "globals.css", "global.css", "app.css",
    "index.css", "colors.xml", "themes.xml", "styles.xml", "Info.plist",
    "Package.swift", "pubspec.yaml",
}

FRAMEWORK_PATTERNS = {
    "Tailwind CSS": (r"\btailwindcss\b", r"@tailwind\s+(?:base|components|utilities)"),
    "Material UI": (r"@mui/", r"\bcreateTheme\s*\("),
    "Chakra UI": (r"@chakra-ui/", r"\bextendTheme\s*\("),
    "Ant Design": (r"\bantd\b", r"ConfigProvider"),
    "styled-components": (r"styled-components", r"\bstyled\.[A-Za-z]+\s*`"),
    "Emotion": (r"@emotion/", r"\bcss\s*`"),
    "Framer Motion": (r"framer-motion", r"\bmotion\.[A-Za-z]+"),
    "GSAP": (r"\bgsap\b", r"\bTimelineMax\b"),
    "Lottie": (r"lottie-web", r"lottie-react", r"\.lottie\b"),
    "Rive": (r"@rive-app/", r"\.riv\b"),
    "Three.js": (r"\bthree\b", r"@react-three/"),
    "React": (r"['\"]react['\"]", r"\bReact\."),
    "Next.js": (r"['\"]next['\"]", r"\bnext/"),
    "Vue": (r"['\"]vue['\"]", r"<template>"),
    "Nuxt": (r"['\"]nuxt['\"]", r"\bdefineNuxtConfig\b"),
    "Svelte": (r"['\"]svelte['\"]", r"<svelte:"),
    "Astro": (r"['\"]astro['\"]", r"Astro\."),
    "SwiftUI": (r"\bimport\s+SwiftUI\b", r"\bColor\("),
    "Jetpack Compose": (r"androidx\.compose", r"@Composable"),
    "Flutter": (r"package:flutter/", r"\bMaterialApp\s*\("),
}

COLOR_PATTERNS = {
    "hex": re.compile(r"(?<![\w-])#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})(?![\w-])"),
    "rgb": re.compile(r"\brgba?\([^)]{3,80}\)", re.IGNORECASE),
    "hsl": re.compile(r"\bhsla?\([^)]{3,80}\)", re.IGNORECASE),
}
CSS_VAR_DEF = re.compile(r"(--[\w-]+)\s*:\s*([^;}{]+)")
CSS_VAR_USE = re.compile(r"var\(\s*(--[\w-]+)")
KEYFRAMES = re.compile(r"@(?:-webkit-)?keyframes\s+([\w-]+)")
MOTION_DECLARATION = re.compile(r"\b(?:transition|animation)(?:-[\w-]+)?\s*:", re.IGNORECASE)
IMPORT_RE = re.compile(r"(?:import\s+(?:[^'\"]+\s+from\s+)?|require\s*\()\s*['\"]([^'\"]+)['\"]")
