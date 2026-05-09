#!/usr/bin/env python3
"""
Convert PNG images under given asset directories to JPEG, then rewrite Markdown links.

Requires: pip install pillow

Usage (from repo root):
  python3 scripts/png_to_jpg.py --dry-run
  python3 scripts/png_to_jpg.py
  python3 scripts/png_to_jpg.py --keep-png
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Missing dependency: pip install pillow", file=sys.stderr)
    sys.exit(1)


def png_to_jpeg(src: Path, dest: Path, quality: int, dry_run: bool) -> None:
    if dry_run:
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as im:
        if im.mode == "LA":
            im = im.convert("RGBA")
        if im.mode == "RGBA":
            background = Image.new("RGB", im.size, (255, 255, 255))
            background.paste(im, mask=im.split()[-1])
            background.save(dest, "JPEG", quality=quality, optimize=True)
        elif im.mode == "P" and "transparency" in im.info:
            im = im.convert("RGBA")
            background = Image.new("RGB", im.size, (255, 255, 255))
            background.paste(im, mask=im.split()[-1])
            background.save(dest, "JPEG", quality=quality, optimize=True)
        else:
            im.convert("RGB").save(dest, "JPEG", quality=quality, optimize=True)


def collect_pngs(dirs: list[Path]) -> list[Path]:
    out: list[Path] = []
    for d in dirs:
        if not d.is_dir():
            continue
        for p in d.rglob("*"):
            if p.is_file() and p.suffix.lower() == ".png":
                out.append(p)
    return sorted(out)


def rel_posix(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    default_root = script_dir.parent

    ap = argparse.ArgumentParser(description="Convert PNG to JPG and fix Markdown references.")
    ap.add_argument("--repo-root", type=Path, default=default_root, help="Repository root (default: parent of scripts/)")
    ap.add_argument(
        "--asset-dir",
        action="append",
        dest="asset_dirs",
        metavar="DIR",
        help="Directory to scan for PNG (repeatable). Default: assets attachment",
    )
    ap.add_argument(
        "--markdown-dir",
        action="append",
        dest="markdown_dirs",
        metavar="DIR",
        help="Root for .md files (repeatable). Default: content",
    )
    ap.add_argument("--quality", type=int, default=85, metavar="N", help="JPEG quality 1–95 (default 85)")
    ap.add_argument("--dry-run", action="store_true", help="Print actions only; do not write files")
    ap.add_argument("--keep-png", action="store_true", help="Keep original PNG after conversion")
    ap.add_argument("--overwrite", action="store_true", help="Overwrite existing .jpg if present")
    args = ap.parse_args()
    if not 1 <= args.quality <= 95:
        print("--quality must be between 1 and 95", file=sys.stderr)
        return 2

    root: Path = args.repo_root.resolve()
    asset_dirs = [root / d for d in (args.asset_dirs or ["assets", "attachment"])]
    md_dirs = [root / d for d in (args.markdown_dirs or ["content"])]

    pngs = collect_pngs(asset_dirs)
    if not pngs:
        print("No PNG files found.", file=sys.stderr)
        return 0

    pairs: list[tuple[Path, Path, str, str]] = []
    for png in pngs:
        jpg = png.with_suffix(".jpg")
        if jpg.exists() and not args.overwrite:
            print(f"skip (jpg exists): {rel_posix(jpg, root)}", file=sys.stderr)
            continue
        rel_png = rel_posix(png, root)
        rel_jpg = rel_posix(jpg, root)
        pairs.append((png, jpg, rel_png, rel_jpg))

    if not pairs:
        print("Nothing to convert (all skipped or no PNG).")
        return 0

    print(f"{'[dry-run] ' if args.dry_run else ''}Convert {len(pairs)} PNG → JPEG")
    for png, jpg, rel_png, rel_jpg in pairs:
        print(f"  {rel_png} → {rel_jpg}")

    for png, jpg, _, _ in pairs:
        try:
            png_to_jpeg(png, jpg, args.quality, args.dry_run)
        except OSError as e:
            print(f"error converting {png}: {e}", file=sys.stderr)
            return 1

    # Longer paths first so we never replace a shorter substring incorrectly
    by_rel_len = sorted(pairs, key=lambda t: len(t[2]), reverse=True)

    md_files: list[Path] = []
    for md_root in md_dirs:
        if not md_root.is_dir():
            continue
        md_files.extend(sorted(md_root.rglob("*.md")))

    changed = 0
    for md in md_files:
        text = md.read_text(encoding="utf-8")
        orig = text
        for _, _, rel_png, rel_jpg in by_rel_len:
            text = text.replace(rel_png, rel_jpg)
            # Obsidian / some editors use backslashes on Windows paths in rare cases
            text = text.replace(rel_png.replace("/", "\\"), rel_jpg.replace("/", "\\"))
        if text != orig:
            changed += 1
            if not args.dry_run:
                md.write_text(text, encoding="utf-8", newline="")
            print(f"  update md: {rel_posix(md, root)}")

    print(f"Markdown files touched: {changed}")

    if not args.keep_png and not args.dry_run:
        for png, _, _, _ in pairs:
            png.unlink(missing_ok=True)
            print(f"  removed: {rel_posix(png, root)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
