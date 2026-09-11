"""Local preparation helpers; reconstruction itself is guided by the prompts."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def blender_executable(value: str | None = None) -> Path:
    found = shutil.which(value or "blender")
    if not found:
        raise FileNotFoundError(
            "Blender was not found. Add it to PATH or pass --blender /path/to/executable."
        )
    return Path(found).resolve()


def inventory(data: Path) -> dict:
    if not data.is_dir():
        raise NotADirectoryError(f"Input folder does not exist: {data}")
    files = []
    for path in sorted(data.rglob("*")):
        relative = path.relative_to(data)
        if path.is_symlink() or any(part.startswith(".") for part in relative.parts):
            continue
        if path.is_file():
            files.append({"path": relative.as_posix(), "bytes": path.stat().st_size})
    return {
        "file_count": len(files),
        "total_bytes": sum(item["bytes"] for item in files),
        "formats": dict(sorted(Counter(Path(item["path"]).suffix.lower() or "(none)"
                                       for item in files).items())),
        "files": files,
    }


def smoke(blender: Path, output: Path) -> Path:
    output.mkdir(parents=True, exist_ok=True)
    run = Path(tempfile.mkdtemp(prefix="smoke-", dir=output))
    for stage in ("create", "edit", "verify"):
        command = [str(blender), "--background", "--factory-startup",
                   "--python-exit-code", "1", "--python",
                   str(ROOT / "tools/blender_smoke.py"), "--",
                   "--directory", str(run), "--stage", stage]
        with (run / f"{stage}.log").open("w", encoding="utf-8") as log:
            subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
    return run / "result.json"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    doctor = commands.add_parser("doctor", help="Locate Blender and print its version")
    doctor.add_argument("--blender", help="Executable name or full executable path")
    source = commands.add_parser("inventory", help="List input files without importing them")
    source.add_argument("--data", type=Path, default=ROOT / "data")
    test = commands.add_parser("smoke", help="Create, reopen, edit and reopen a synthetic wall")
    test.add_argument("--blender", help="Executable name or full executable path")
    args = parser.parse_args()
    if args.command == "doctor":
        executable = blender_executable(args.blender)
        version = subprocess.check_output([str(executable), "--version"], text=True)
        print(json.dumps({"blender": str(executable), "version": version.splitlines()[0],
                          "ffmpeg": shutil.which("ffmpeg")}, indent=2))
    elif args.command == "inventory":
        data = args.data if args.data.is_absolute() else ROOT / args.data
        result = inventory(data.resolve())
        destination = ROOT / "output/source-inventory.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
        print(json.dumps({key: value for key, value in result.items() if key != "files"},
                         indent=2, ensure_ascii=False))
        print(f"Saved: {destination.relative_to(ROOT)}")
    else:
        result = smoke(blender_executable(args.blender), ROOT / "output")
        print(result.read_text())
        print(f"Saved: {result.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
