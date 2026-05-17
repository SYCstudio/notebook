#!/usr/bin/env python3
"""
Scan Markdown files for Obsidian-style image wikilinks, move referenced files from
each note's local ``assets/`` folder to a destination directory, and rewrite links.

Wikilink forms supported (display text after ``|`` is preserved):

  ![[assets/photo.jpg]]
  ![[assets/photo.jpg|1000]]
  ![[assets/photo.jpg|caption]]

Requires images to live under ``<md-parent>/assets/`` as referenced in the link.

Usage (from repo root):

  python scripts/move_md_assets.py --source-dir content/foo --dest-dir content/shared/assets --dry-run
  python scripts/move_md_assets.py --source-dir content/foo --dest-dir content/shared/assets
  python scripts/move_md_assets.py --source-file "content/foo/Note.md" --dest-dir assets
  python scripts/move_md_assets.py --source-dir content/foo --dest-dir pool --link-prefix pool
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
from pathlib import Path

# ![[path]] or ![[path|display]]
WIKILINK_IMAGE_RE = re.compile(r"!\[\[([^\]|#]+)(?:\|([^\]]*))?\]\]")

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp", ".avif"}


def normalize_link_path(link_path: str) -> str:
    return link_path.strip().replace("\\", "/")


def is_local_assets_link(link_path: str) -> bool:
    p = normalize_link_path(link_path)
    return p.startswith("assets/")


def asset_source_path(md_parent: Path, link_path: str) -> Path:
    return (md_parent / normalize_link_path(link_path)).resolve()


def is_image_path(path: Path) -> bool:
    return path.suffix.lower() in IMAGE_SUFFIXES


def wikilink_target(
    project_root: Path,
    dest_file: Path,
    link_prefix: str | None,
) -> str:
    if link_prefix is not None:
        prefix = link_prefix.strip("/").replace("\\", "/")
        return f"{prefix}/{dest_file.name}" if prefix else dest_file.name
    return Path(os.path.relpath(dest_file, project_root)).as_posix()


def format_wikilink(target: str, display: str | None) -> str:
    if display is None:
        return f"![[{target}]]"
    return f"![[{target}|{display}]]"


def collect_markdown_files(source_dir: Path, recursive: bool) -> list[Path]:
    if recursive:
        return sorted(source_dir.rglob("*.md"))
    return sorted(source_dir.glob("*.md"))


def resolve_markdown_sources(
    source_dir: Path | None,
    source_file: Path | None,
    recursive: bool,
) -> tuple[list[Path], Path]:
    if source_file is not None:
        md = source_file.resolve()
        if not md.is_file():
            print(f"--source-file is not a file: {md}", file=sys.stderr)
            raise SystemExit(2)
        if md.suffix.lower() != ".md":
            print(f"--source-file must be a .md file: {md}", file=sys.stderr)
            raise SystemExit(2)
        return [md], md.parent

    assert source_dir is not None
    root = source_dir.resolve()
    if not root.is_dir():
        print(f"--source-dir is not a directory: {root}", file=sys.stderr)
        raise SystemExit(2)
    return collect_markdown_files(root, recursive), root


def choose_dest_path(
    src: Path,
    dest_dir: Path,
    on_collision: str,
    moved: dict[Path, Path],
) -> Path | None:
    if src in moved:
        return moved[src]

    dest = dest_dir / src.name
    if dest.exists():
        try:
            same = src.read_bytes() == dest.read_bytes()
        except OSError:
            same = False
        if same:
            moved[src] = dest
            return dest
        if on_collision == "skip":
            print(f"skip (dest exists, differs): {dest}", file=sys.stderr)
            return None
        if on_collision == "error":
            print(f"error: destination exists: {dest}", file=sys.stderr)
            return None
        # rename: append _1, _2, ...
        stem, suffix = src.stem, src.suffix
        n = 1
        while dest.exists():
            dest = dest_dir / f"{stem}_{n}{suffix}"
            n += 1

    moved[src] = dest
    return dest


def process_markdown(
    md_path: Path,
    dest_dir: Path,
    project_root: Path,
    link_prefix: str | None,
    on_collision: str,
    dry_run: bool,
    moved: dict[Path, Path],
    stats: dict[str, int],
) -> bool:
    md_parent = md_path.parent
    text = md_path.read_text(encoding="utf-8")
    changed = False

    def replace_match(match: re.Match[str]) -> str:
        nonlocal changed
        raw_path = match.group(1)
        display = match.group(2)

        if not is_local_assets_link(raw_path):
            return match.group(0)

        src = asset_source_path(md_parent, raw_path)
        if not is_image_path(src):
            return match.group(0)

        already_handled = src in moved
        if already_handled:
            dest = moved[src]
        elif not src.is_file():
            print(f"warning: missing image {src} (in {md_path})", file=sys.stderr)
            stats["missing"] += 1
            return match.group(0)
        else:
            dest = choose_dest_path(src, dest_dir, on_collision, moved)

        if dest is None:
            stats["skipped"] += 1
            return match.group(0)

        if not already_handled:
            if dry_run:
                print(f"  would move: {src} -> {dest}")
                stats["moved"] += 1
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                if src == dest:
                    pass
                elif dest.exists():
                    try:
                        if src.read_bytes() == dest.read_bytes():
                            src.unlink(missing_ok=True)
                            stats["moved"] += 1
                    except OSError as e:
                        print(f"warning: could not dedupe {src}: {e}", file=sys.stderr)
                else:
                    shutil.move(str(src), str(dest))
                    stats["moved"] += 1

        new_target = wikilink_target(project_root, dest, link_prefix)
        old = match.group(0)
        new = format_wikilink(new_target, display)
        if new != old:
            changed = True
        return new

    new_text = WIKILINK_IMAGE_RE.sub(replace_match, text)
    if changed:
        stats["md_updated"] += 1
        if not dry_run:
            md_path.write_text(new_text, encoding="utf-8", newline="")
        else:
            print(f"  would update: {md_path}")
    return changed


def prune_empty_assets_dirs(source_dir: Path, dry_run: bool) -> int:
    removed = 0
    for assets_dir in sorted(source_dir.rglob("assets")):
        if not assets_dir.is_dir():
            continue
        try:
            if any(assets_dir.iterdir()):
                continue
        except OSError:
            continue
        removed += 1
        if dry_run:
            print(f"  would remove empty dir: {assets_dir}")
        else:
            assets_dir.rmdir()
            print(f"  removed empty dir: {assets_dir}")
    return removed


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    default_root = script_dir.parent

    ap = argparse.ArgumentParser(
        description="Move wikilinked assets from Markdown notes to a destination folder and rewrite links.",
    )
    source = ap.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--source-dir",
        type=Path,
        help="Directory containing .md files to scan",
    )
    source.add_argument(
        "--source-file",
        type=Path,
        help="Single .md file to process",
    )
    ap.add_argument(
        "--dest-dir",
        type=Path,
        required=True,
        help="Directory to move images into (created if missing)",
    )
    ap.add_argument(
        "--link-prefix",
        type=str,
        default=None,
        metavar="PREFIX",
        help=(
            "Fixed wikilink path prefix after move, e.g. 'shared/assets' -> ![[shared/assets/foo.jpg]]. "
            "Default: path relative to the project root (parent of scripts/)"
        ),
    )
    ap.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Project root for wikilink paths (default: parent directory of this script)",
    )
    ap.add_argument(
        "--no-recursive",
        action="store_true",
        help="Only scan .md files directly under --source-dir, not subfolders",
    )
    ap.add_argument(
        "--on-collision",
        choices=("rename", "skip", "error"),
        default="rename",
        help="When dest filename already exists with different content (default: rename)",
    )
    ap.add_argument(
        "--prune-empty-assets",
        action="store_true",
        help=(
            "Remove empty 'assets' directories after moving "
            "(under --source-dir, or under the --source-file parent directory)"
        ),
    )
    ap.add_argument("--dry-run", action="store_true", help="Print actions only; do not move or edit files")
    args = ap.parse_args()

    project_root = (args.project_root or default_root).resolve()
    dest_dir = args.dest_dir.resolve()

    md_files, prune_root = resolve_markdown_sources(
        args.source_dir,
        args.source_file,
        recursive=not args.no_recursive,
    )
    if not md_files:
        print(f"No .md files under {prune_root}", file=sys.stderr)
        return 0

    if not args.dry_run:
        dest_dir.mkdir(parents=True, exist_ok=True)

    moved: dict[Path, Path] = {}
    stats = {"moved": 0, "md_updated": 0, "missing": 0, "skipped": 0}

    prefix = f"{'[dry-run] ' if args.dry_run else ''}"
    print(f"{prefix}Scan {len(md_files)} markdown file(s)")
    print(f"{prefix}Destination: {dest_dir}")

    for md in md_files:
        process_markdown(
            md,
            dest_dir,
            project_root,
            args.link_prefix,
            args.on_collision,
            args.dry_run,
            moved,
            stats,
        )

    if args.prune_empty_assets:
        n = prune_empty_assets_dirs(prune_root, args.dry_run)
        print(f"{prefix}Empty assets dirs: {n}")

    print(
        f"Done: {stats['moved']} image(s) moved, "
        f"{stats['md_updated']} markdown file(s) updated, "
        f"{stats['missing']} missing, "
        f"{stats['skipped']} skipped (collision)"
    )
    return 1 if stats["skipped"] and args.on_collision == "error" else 0


if __name__ == "__main__":
    raise SystemExit(main())
