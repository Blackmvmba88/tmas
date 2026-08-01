# BlackMamba Visual Index

A read-only visual change impact index for macOS and cross-platform software projects. It maps the files that control themes, colors, typography, motion, components and assets before anyone changes the interface.

The scanner never rewrites the target project. It only produces reviewable reports.

## What it indexes

- CSS, Sass, Less and Stylus
- Theme files and design-token candidates
- CSS custom-property definitions and usage
- HEX, RGB/RGBA and HSL/HSLA colors
- Keyframes, transitions and animation declarations
- React, Next.js, Vue, Nuxt, Svelte, Astro, SwiftUI, Compose and Flutter
- Tailwind, MUI, Chakra, Ant Design, styled-components and Emotion
- Framer Motion, GSAP, Lottie, Rive and Three.js
- Components, layouts, screens, views and entry files
- Images, icons, fonts, videos and editable design assets
- Byte-identical duplicate assets
- Basic import relationships for later automation

## Install on Mac

```bash
git clone https://github.com/Blackmvmba88/tmas.git
cd tmas
chmod +x install.sh
./install.sh
source ~/.zshrc
```

Scan any project and open the dashboard:

```bash
visual-index /path/to/project --open
```

You can also run it without installation:

```bash
python3 -m visual_index /path/to/project --open
```

## Generated reports

Every scan creates an isolated directory inside the target project:

```text
.visual-index/
├── VISUAL_INDEX.md       # Human-readable architecture map
├── visual-index.html     # Visual dashboard
└── visual-index.json     # Machine-readable automation input
```

## Useful commands

```bash
# Scan the current directory
visual-index .

# Open the dashboard automatically on macOS
visual-index . --open

# Write reports elsewhere
visual-index . --output reports/visual-system

# Inspect text files up to 8 MB
visual-index . --max-file-mb 8

# Exclude an additional generated directory
visual-index . --exclude generated

# Include hidden files and directories
visual-index . --include-hidden
```

## Architecture

```text
visual_index/
├── catalog.py    # Framework, extension and visual-pattern catalog
├── scanner.py    # Read-only filesystem and source scanner
├── render.py     # Markdown, HTML and JSON report generation
├── cli.py        # Command-line interface
└── __main__.py   # python -m visual_index entrypoint
```

## Safe visual-change workflow

```text
1. Scan the repository
2. Review priority visual files
3. Identify raw values and existing tokens
4. Define a semantic theme contract
5. Change tokens before individual components
6. Handle exceptional surfaces explicitly
7. Add reduced-motion behavior
8. Capture reference screenshots
9. Run visual regression checks
10. Merge only after review
```

## Validation

```bash
python3 -m compileall -q visual_index
python3 -m unittest discover -s tests -v
```

GitHub Actions runs both checks on pushes and pull requests.

## Roadmap

The JSON index is the foundation for the next layers:

- Semantic token generator
- Light, dark, high-contrast and BlackMamba themes
- Visual dependency graph
- Controlled palette migrations
- Screenshot route discovery
- Pull-request visual change reports
- Automated visual regression
