#!/usr/bin/env python3
"""
Build script for Michael Cunningham Studio site.

Nav and footer live once, in src/partials/. Every page's unique content
lives in src/ (mirroring the final site structure). This script stitches
them together and writes the final static HTML files that actually get
deployed (at the project root / sculptures/).

Usage:
    python3 build.py

After editing src/partials/nav.html or src/partials/footer.html,
or any page under src/, just re-run this script and re-deploy.
"""

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"
PARTIALS = SRC / "partials"

# (source file, output file, path prefix back to the homepage)
# Homepage links are same-page anchors ("#shop"); subpages need to get
# back to index.html first ("../index.html#shop").
PAGES = [
    (SRC / "index.html", ROOT / "index.html", ""),
    (SRC / "sculptures" / "hawk-metal-sculpture.html",
     ROOT / "sculptures" / "hawk-metal-sculpture.html", "../index.html"),
    (SRC / "sculptures" / "barn-owl-metal-sculpture.html",
     ROOT / "sculptures" / "barn-owl-metal-sculpture.html", "../index.html"),
    (SRC / "sculptures" / "franklin-sculpture.html",
     ROOT / "sculptures" / "franklin-sculpture.html", "../index.html"),
]


def load_partial(name: str, home_prefix: str = None) -> str:
    text = (PARTIALS / f"{name}.html").read_text().rstrip("\n")
    if home_prefix is not None:
        text = text.replace("{{HOME}}", home_prefix)
    return text


def css_version() -> str:
    """Short hash of styles.css so every content change busts the cache
    automatically, without anyone needing to remember to bump a version
    number by hand."""
    data = (ROOT / "styles.css").read_bytes()
    return hashlib.sha256(data).hexdigest()[:8]


def build_page(src_path: Path, out_path: Path, home_prefix: str, version: str) -> None:
    content = src_path.read_text()

    nav = load_partial("nav", home_prefix)
    footer = load_partial("footer")

    content = content.replace("<!-- INCLUDE:nav -->", nav)
    content = content.replace("<!-- INCLUDE:footer -->", footer)
    content = re.sub(
        r'(href="[^"]*styles\.css)(")',
        rf'\1?v={version}\2',
        content,
    )

    remaining = re.findall(r"<!-- INCLUDE:\w+ -->", content)
    if remaining:
        raise ValueError(f"{src_path}: unresolved include marker(s): {remaining}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content)
    print(f"built {out_path.relative_to(ROOT)}")


def main():
    version = css_version()
    for src_path, out_path, home_prefix in PAGES:
        build_page(src_path, out_path, home_prefix, version)
    print(f"done. (styles.css cache-bust version: {version})")


if __name__ == "__main__":
    main()
