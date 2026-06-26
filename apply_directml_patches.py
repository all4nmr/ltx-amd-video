#!/usr/bin/env python3
"""
apply_directml_patches.py — Auto-patcher for LTX-2 OPTIMIZED.

Scans the LTX-2 OPTIMIZED codebase and applies the necessary
changes to support AMD DirectML on Windows.

Run from the project root:

    python apply_directml_patches.py [--dry-run]

What it patches:
  1. Replace ``torch.cuda.is_available()`` with device helper.
  2. Replace ``torch.device("cuda")`` with resolved device.
  3. Replace ``.to("cuda")`` / ``.cuda()`` with device-aware.
  4. Replace ``cuda.synchronize()`` with sync_device().
  5. Replace ``torch.cuda.empty_cache()`` with cleanup_memory().
"""

import argparse
import fnmatch
import logging
import os
import re

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("directml_patch")

IGNORE_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules", "dist"}
TARGET_PATTERNS = ["*.py"]

# ── Replacement rules ──────────────────────────────────────────────────────
# Each rule: (regex_pattern, replacement_template)
# The replacement can reference groups with \\1, \\2, etc.

RULES: list[tuple[str, str, str]] = [
    # 1. torch.cuda.is_available() → helpers.get_device() logic
    (
        r"torch\.cuda\.is_available\(\)",
        "helpers.is_directml(getattr(helpers, 'device', None)) or torch.cuda.is_available()",
        "cuda.is_available → device-agnostic",
    ),
    # 2. torch.device(\"cuda\") → helpers.get_device()
    (
        r"""torch\.device\(["']cuda["']\)""",
        "getattr(helpers, 'device', torch.device('cuda' if torch.cuda.is_available() else 'cpu'))",
        "torch.device('cuda') → helpers.device",
    ),
    # 3. .to("cuda")  →  .to(helpers.device)
    (
        r"""\.to\(["']cuda["']\)""",
        ".to(getattr(helpers, 'device', torch.device('cuda')))",
        ".to('cuda') → .to(helpers.device)",
    ),
    # 4. .cuda()  →  .to(helpers.device)
    (
        r"""\.cuda\(\)""",
        ".to(getattr(helpers, 'device', torch.device('cuda')))",
        ".cuda() → .to(helpers.device)",
    ),
    # 5. torch.cuda.synchronize()  →  helpers.sync_device()
    (
        r"""torch\.cuda\.synchronize\(\)""",
        "helpers.sync_device()",
        "cuda.synchronize → helpers.sync_device",
    ),
    # 6. torch.cuda.empty_cache()  →  helpers.cleanup_memory()
    (
        r"""torch\.cuda\.empty_cache\(\)""",
        "helpers.cleanup_memory()",
        "cuda.empty_cache → helpers.cleanup_memory",
    ),
    # 7. import torch (add helpers import)
    # This is handled separately — we insert the import after the last
    # existing import line.
]

IMPORT_STATEMENT = "from helpers import device, sync_device, cleanup_memory\n"


def _find_and_patch_file(filepath: str, dry_run: bool = False) -> list[str]:
    """Apply all RULES to *filepath*.  Returns list of applied rule names."""
    with open(filepath, "r", encoding="utf-8") as fh:
        original = fh.read()

    modified = original
    applied: list[str] = []

    for pattern, replacement, name in RULES:
        new_text, count = re.subn(pattern, replacement, modified)
        if count > 0:
            applied.append(f"{name} ({count}x)")
            modified = new_text

    # Add helpers import if not present
    if "from helpers import" not in modified and "import helpers" not in modified:
        # Insert after the last import line
        import_end = 0
        for m in re.finditer(r"^(import |from )", modified, re.MULTILINE):
            import_end = m.end()
        # Find the end of the line containing the last import
        if import_end > 0:
            rest = modified[import_end:]
            eol = rest.find("\n")
            if eol >= 0:
                insert_at = import_end + eol + 1
                modified = modified[:insert_at] + IMPORT_STATEMENT + modified[insert_at:]
                applied.append("added helpers import")

    if modified != original:
        if dry_run:
            logger.info("  [DRY-RUN] Would patch %s: %s", filepath, ", ".join(applied))
        else:
            with open(filepath, "w", encoding="utf-8") as fh:
                fh.write(modified)
            logger.info("  Patched %s: %s", filepath, ", ".join(applied))
        return applied
    return []


def main():
    parser = argparse.ArgumentParser(
        description="Apply DirectML patches to LTX-2 OPTIMIZED codebase"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change without writing",
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Project root directory (default: current dir)",
    )
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    logger.info("Scanning %s for Python files...", root)

    total_patched = 0
    total_files = 0

    for dirpath, dirnames, filenames in os.walk(root):
        # Skip ignored directories
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]

        for fname in filenames:
            if not any(fnmatch.fnmatch(fname, p) for p in TARGET_PATTERNS):
                continue
            fpath = os.path.join(dirpath, fname)

            # Skip the patcher itself and helpers
            if os.path.basename(fpath) in (
                "apply_directml_patches.py",
                "helpers.py",
            ):
                continue

            applied = _find_and_patch_file(fpath, dry_run=args.dry_run)
            if applied:
                total_files += 1
                total_patched += len(applied)

    logger.info(
        "Done. %d files patched (%d total changes).",
        total_files,
        total_patched,
    )
    if args.dry_run:
        logger.info("Run without --dry-run to apply changes.")


if __name__ == "__main__":
    main()
