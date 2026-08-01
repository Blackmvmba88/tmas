# BlackMamba Visual Index

A read-only macOS-friendly CLI that builds a complete **visual change impact index** before you modify themes, colors, typography, animation, assets, or UI components.

It does not rewrite project files. It only scans and creates reports.

## What it indexes

- Global CSS, Sass, Less and Stylus files
- Theme files and design-token candidates
- CSS custom properties and their usage
- Hex, RGB/RGBA and HSL/HSLA color literals
- Keyframes, transitions and animation declarations
- React, Vue, Svelte, Astro, SwiftUI, Compose and Flutter UI files
- Tailwind, MUI, Chakra, styled-components, Emotion and Ant Design signals
- Framer Motion, GSAP, Lottie, Rive, Three.js, Anime.js and React Spring
- Images, icons, fonts, videos and editable design assets
- Byte-identical duplicate assets
- Priority entry files, layouts, screens and theme scopes
- Basic import relationships for machine processing

## Fastest start on Mac

```bash
unzip blackmamba-visual-index.zip
cd blackmamba-visual-index
chmod +x install.sh
./install.sh
source ~/.zshrc
```

Then enter any project:

```bash
cd /path/to/your/project
visual-index . --open
```

The browser opens:

```text
.visual-index/visual-index.html
```

The same scan also creates:

```text
.visual-index/
├── VISUAL_INDEX.md       # Human review
├── visual-index.html     # Visual dashboard
└── visual-index.json     # Automation / agent input
```

## Run without installing

```bash
python3 visual_indexer.py /path/to/project --open
```

## Useful commands

```bash
# Scan current project
visual-index .

# Open dashboard after scan
visual-index . --open

# Put report in another folder
visual-index . --output reports/visual-system

# Inspect text files up to 8 MB
visual-index . --max-file-mb 8

# Exclude an extra generated directory
visual-index . --exclude generated

# Include hidden project folders
visual-index . --include-hidden
```

## Recommended workflow before visual changes

```text
1. Scan
2. Review priority files
3. Identify semantic tokens
4. Build theme contract
5. Change tokens first
6. Update exceptional components
7. Add motion policy and reduced-motion handling
8. Capture screenshots
9. Run visual regression
10. Merge
```

## Suggested repository integration

Add generated output to `.gitignore` when it is only local:

```gitignore
.visual-index/
```

Or commit `VISUAL_INDEX.md` when you want the repository to maintain a visual architecture map.

## Next layer

The JSON output is intentionally structured so a second tool can:

- Generate a central token file
- Produce light/dark/high-contrast themes
- Build a dependency graph
- Apply controlled palette migrations
- Create screenshot test routes
- Detect visual changes in pull requests
