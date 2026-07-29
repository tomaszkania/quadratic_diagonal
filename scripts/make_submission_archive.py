#!/usr/bin/env python3
"""Build deterministic TOMS article and software-component submission files."""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import stat
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Replaced per repository.
PACKAGE = "quadratic_diagonal"
ARTICLE_STEM = "exact_diagonal_representability_real_quadratic"
PACKAGE_INIT = ROOT / "src" / PACKAGE / "__init__.py"
ARTICLE_PDF = ROOT / "paper" / f"{ARTICLE_STEM}.pdf"

FIXED_ZIP_TIME = (2026, 7, 26, 0, 0, 0)
EXCLUDED_DIR_NAMES = {
    ".git",
    ".github-cache",
    ".ipynb_checkpoints",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "build",
    "submission",
}
EXCLUDED_SUFFIXES = {
    ".aux",
    ".blg",
    ".fdb_latexmk",
    ".fls",
    ".log",
    ".out",
    ".pyc",
    ".pyo",
    ".synctex.gz",
    ".toc",
}


def read_version() -> str:
    """Read the version exported by the package.

    Returns
    -------
    str
        Package version.

    Raises
    ------
    RuntimeError
        If ``__version__`` cannot be read.
    """
    text = PACKAGE_INIT.read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', text)
    if match is None:
        raise RuntimeError(f"Could not read __version__ from {PACKAGE_INIT}")
    return match.group(1)


def is_excluded(path: Path) -> bool:
    """Return whether a path is a transient build artefact.

    Parameters
    ----------
    path : pathlib.Path
        Absolute path under the repository root.

    Returns
    -------
    bool
        Whether the path should be omitted.
    """
    relative = path.relative_to(ROOT)
    if set(relative.parts) & EXCLUDED_DIR_NAMES:
        return True
    if any(part.endswith(".egg-info") for part in relative.parts):
        return True
    if any(path.name.endswith(suffix) for suffix in EXCLUDED_SUFFIXES):
        return True
    return False


def iter_archive_files() -> list[Path]:
    """Return sorted regular files included in the software component.

    Returns
    -------
    list[pathlib.Path]
        Included files.
    """
    return [
        path
        for path in sorted(ROOT.rglob("*"))
        if path.is_file() and not is_excluded(path)
    ]


def sha256(path: Path) -> str:
    """Compute a SHA-256 digest.

    Parameters
    ----------
    path : pathlib.Path
        File to hash.

    Returns
    -------
    str
        Lower-case hexadecimal digest.
    """
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _zip_info(name: str, executable: bool = False) -> zipfile.ZipInfo:
    """Create deterministic ZIP metadata for one member."""
    info = zipfile.ZipInfo(name, date_time=FIXED_ZIP_TIME)
    mode = 0o755 if executable else 0o644
    info.external_attr = (stat.S_IFREG | mode) << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    return info


def _is_executable(path: Path) -> bool:
    """Return whether an archived source file should be executable."""
    if path.suffix in {".py", ".sh"}:
        first_line = path.read_bytes().splitlines()[:1]
        return bool(first_line and first_line[0].startswith(b"#!"))
    return bool(path.stat().st_mode & os.X_OK)


def build_submission() -> tuple[Path, Path, Path]:
    """Build the article copy, software ZIP, and external checksum.

    Returns
    -------
    tuple[pathlib.Path, pathlib.Path, pathlib.Path]
        Article PDF, software ZIP, and checksum-file paths.

    Raises
    ------
    FileNotFoundError
        If the compiled article is missing.
    """
    if not ARTICLE_PDF.is_file():
        raise FileNotFoundError(f"Compile the article first: missing {ARTICLE_PDF}")

    version = read_version()
    submission = ROOT / "submission"
    if submission.exists():
        shutil.rmtree(submission)
    submission.mkdir()

    article_out = submission / f"{PACKAGE}_algorithm_article.pdf"
    shutil.copy2(ARTICLE_PDF, article_out)

    prefix = f"{PACKAGE}-{version}"
    archive = submission / f"{PACKAGE}-{version}-toms-software.zip"
    files = iter_archive_files()
    checksum_lines: list[str] = []

    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in files:
            relative = path.relative_to(ROOT).as_posix()
            data = path.read_bytes()
            checksum_lines.append(f"{hashlib.sha256(data).hexdigest()}  {relative}")
            zf.writestr(
                _zip_info(f"{prefix}/{relative}", executable=_is_executable(path)),
                data,
            )
        checksums = ("\n".join(checksum_lines) + "\n").encode("utf-8")
        zf.writestr(_zip_info(f"{prefix}/CHECKSUMS.sha256"), checksums)

    checksum_out = archive.with_suffix(archive.suffix + ".sha256")
    checksum_out.write_text(f"{sha256(archive)}  {archive.name}\n", encoding="utf-8")

    contents = submission / "CONTENTS.txt"
    contents.write_text(
        f"TOMS submission files for {PACKAGE} {version}\n"
        f"Article: {article_out.name}\n"
        f"Software: {archive.name}\n"
        f"SHA-256: {checksum_out.name}\n"
        f"Top-level ZIP directory: {prefix}/\n",
        encoding="utf-8",
    )
    return article_out, archive, checksum_out


def main() -> None:
    """Build and report all submission files."""
    for path in build_submission():
        print(path)


if __name__ == "__main__":
    main()
