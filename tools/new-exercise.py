#!/usr/bin/env python3
"""Create a new exercise page and wire it into the navbar.

Usage:
    python3 tools/new-exercise.py inclass 1
    python3 tools/new-exercise.py handson 2
    python3 tools/new-exercise.py takehome 1

Optionally add a title:
    python3 tools/new-exercise.py inclass 1 "Spatial Weights"
"""
import sys, pathlib, re, datetime

KINDS = {
    "handson":  ("Hands-on_Ex",  "Hands-on_Ex",  "Hands-on Exercises",  "Hands-on Ex"),
    "inclass":  ("In-class_Ex",  "In-class_Ex",  "In-class Exercises",  "In-class Ex"),
    "takehome": ("Take-home_Ex", "Take-home_Ex", "Take-home Exercises", "Take-home Ex"),
}

def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    kind = sys.argv[1].lower().replace("-", "").replace("_", "")
    if kind not in KINDS:
        print(f"kind must be one of: {', '.join(KINDS)}"); sys.exit(1)
    num = f"{int(sys.argv[2]):02d}"
    title_extra = sys.argv[3] if len(sys.argv) > 3 else ""

    folder, prefix, menu_label, page_label = KINDS[kind]
    root = pathlib.Path(__file__).resolve().parent.parent
    exdir = root / folder / f"{prefix}{num}"
    qmd = exdir / f"{prefix}{num}.qmd"

    if qmd.exists():
        print(f"! {qmd.relative_to(root)} already exists. Nothing changed."); sys.exit(1)

    (exdir / "data").mkdir(parents=True, exist_ok=True)

    subtitle = f'\nsubtitle: "{title_extra}"' if title_extra else ""
    qmd.write_text(f'''---
title: "{page_label} {int(num)}"{subtitle}
author: "An Loc"
date: "last-modified"
date-format: "D MMM YYYY"
execute:
  echo: true
  warning: false
  message: false
  freeze: true
---

# Overview

*What this exercise covers.*

# Getting started

```{{r}}
pacman::p_load(sf, tmap, tidyverse)
```

# The data

```{{r}}
#| eval: false
# st_read("data/...")
```

# Analysis

# Reflection
''')

    # --- navbar ---
    yml = root / "_quarto.yml"
    text = yml.read_text()
    href = f"{folder}/{prefix}{num}/{prefix}{num}.qmd"
    entry_title = f"{page_label} {int(num)}" + (f": {title_extra}" if title_extra else "")

    # find the menu block for this section
    pat = re.compile(
        r'(      - text: "' + re.escape(menu_label) + r'"\n        menu:\n)((?:          .*\n)*)')
    m = pat.search(text)
    new_item = f'          - text: "{entry_title}"\n            href: {href}\n'
    if m:
        body = m.group(2)
        body = re.sub(r'          - text: "\(none yet\)"\n            href: index\.qmd\n', '', body)
        text = text[:m.start()] + m.group(1) + body + new_item + text[m.end():]
        yml.write_text(text)
        nav = "added to navbar"
    else:
        nav = f"! could not find the '{menu_label}' menu in _quarto.yml - add it by hand"

    print(f"created  {qmd.relative_to(root)}")
    print(f"created  {(exdir/'data').relative_to(root)}/")
    print(f"navbar   {nav}")
    print()
    print("next:")
    print(f"  open {qmd.relative_to(root)} in RStudio and write it")
    print(f"  ./tools/publish.sh \"{entry_title}\"")

if __name__ == "__main__":
    main()
