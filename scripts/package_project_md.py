#!/usr/bin/env python3
"""Bundle the repository into a single markdown file."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "AI_Investment_Agent_PROJECT_PACKAGE.md"

SKIP_DIRS = {
    ".git",
    ".pytest_cache",
    ".cursor",
    "__pycache__",
    "data",
    "venv",
    ".venv",
    "node_modules",
    "htmlcov",
    "dist",
    "build",
}

SKIP_FILES = {
    ".env",
    OUT.name,
    "package_project_md.py",
}

INCLUDE_EXTENSIONS = {
    ".py",
    ".md",
    ".html",
    ".css",
    ".sh",
    ".command",
    ".txt",
    ".json",
    ".example",
    ".toml",
    ".yaml",
    ".yml",
    ".ini",
    ".cfg",
}

# Always include these root files even without extension match
FORCE_INCLUDE = {
    "requirements.txt",
    ".gitignore",
    ".env.example",
}


def should_include(path: Path) -> bool:
    if path.name in SKIP_FILES:
        return False
    if path.name.startswith(".") and path.name not in {".env.example", ".gitignore"}:
        return False
    if path.suffix in INCLUDE_EXTENSIONS or path.name in FORCE_INCLUDE:
        return True
    return False


def collect_files() -> list[Path]:
    files: list[Path] = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        if should_include(path):
            files.append(path)
    return files


def lang_for(path: Path) -> str:
    ext = path.suffix.lower()
    return {
        ".py": "python",
        ".sh": "bash",
        ".command": "bash",
        ".html": "html",
        ".css": "css",
        ".json": "json",
        ".md": "markdown",
        ".txt": "text",
    }.get(ext, "text")


def main() -> None:
    files = collect_files()
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    branch = "cursor/patch-investment-agent-spec-cd1d"

    lines: list[str] = [
        "# AI Investment Agent — Complete Project Package",
        "",
        f"**Generated:** {now}  ",
        f"**Branch:** `{branch}`  ",
        f"**Files included:** {len(files)}  ",
        "",
        "> Single-file export of the Home-Repository codebase (docs, source, scripts, tests).",
        "> Secrets excluded: `.env`, `data/`, databases, caches.",
        "",
        "---",
        "",
        "## Table of Contents",
        "",
    ]

    for i, path in enumerate(files, 1):
        rel = path.relative_to(ROOT).as_posix()
        anchor = rel.replace("/", "-").replace(".", "-").lower()
        lines.append(f"{i}. [{rel}](#{anchor})")

    lines.extend(["", "---", ""])

    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        anchor = rel.replace("/", "-").replace(".", "-").lower()
        lines.extend([
            f"<a id=\"{anchor}\"></a>",
            f"## `{rel}`",
            "",
        ])
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            lines.extend(["*(binary or non-UTF-8 file omitted)*", ""])
            continue

        if path.suffix == ".md" and path.name != OUT.name:
            lines.append(content.rstrip())
            lines.append("")
        else:
            lang = lang_for(path)
            lines.extend([f"```{lang}", content.rstrip(), "```", ""])

        lines.extend(["", "---", ""])

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(str(OUT.resolve()))
    print(f"Size: {OUT.stat().st_size:,} bytes")
    print(f"Files: {len(files)}")


if __name__ == "__main__":
    main()
