"""Check files Git would publish; never inspect ignored raw data or output."""
import ast
import hashlib
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def parse_lfs_pointer(content: bytes):
    match = re.fullmatch(
        rb"version https://git-lfs.github.com/spec/v1\n"
        rb"oid sha256:([0-9a-f]{64})\nsize ([0-9]+)\n", content)
    return (match[1].decode(), int(match[2])) if match else None


def check_lfs_content(path: Path, pointer: bytes) -> None:
    expected = parse_lfs_pointer(pointer)
    if expected is None:
        raise ValueError("Git index must contain an LFS pointer, not the binary")
    with path.open("rb") as stream:
        head = stream.read(1024)
        working_pointer = parse_lfs_pointer(head)
        if working_pointer is not None:
            if working_pointer != expected:
                raise ValueError("working-tree pointer differs from Git index")
            return
        if path.stat().st_size != expected[1]:
            raise ValueError("LFS binary size differs from Git pointer")
        digest = hashlib.sha256(head)
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
        if digest.hexdigest() != expected[0]:
            raise ValueError("LFS binary SHA256 differs from Git pointer")


def main() -> None:
    result = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=ROOT)
    names = sorted(set(result.decode().split("\0")) - {""})
    public = set(names)
    attributes = subprocess.check_output(
        ["git", "check-attr", "-z", "filter", "--", *names], cwd=ROOT).decode().split("\0")
    lfs = {attributes[i] for i in range(0, len(attributes) - 1, 3)
           if attributes[i + 2] == "lfs"}
    problems = []
    total = 0
    personal_path = re.compile(r"/(?:Users|home)/[^/\s]+/|[A-Za-z]:\\Users\\[^\\\s]+\\")
    secret = re.compile(r"AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{30,}|"
                        r"sk-[A-Za-z0-9]{24,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")
    for name in names:
        path = ROOT / name
        if name.split("/")[0] in {"data", "output", "research"}:
            problems.append(f"{name}: private/generated directory included")
        if path.is_symlink():
            problems.append(f"{name}: symlink in public files")
            continue
        if not path.is_file():
            problems.append(f"{name}: tracked file is missing")
            continue
        size = path.stat().st_size
        total += size
        if name in lfs:
            staged_size = subprocess.run(
                ["git", "cat-file", "-s", f":{name}"], cwd=ROOT,
                capture_output=True, text=True)
            if staged_size.returncode != 0:
                problems.append(f"{name}: stage this LFS file to verify its pointer")
            elif int(staged_size.stdout) > 1024:
                problems.append(f"{name}: binary in Git index; re-add after enabling LFS")
            else:
                pointer = subprocess.check_output(["git", "show", f":{name}"], cwd=ROOT)
                try:
                    check_lfs_content(path, pointer)
                except ValueError as error:
                    problems.append(f"{name}: {error}")
        elif size > 50 * 1024 * 1024:
            problems.append(f"{name}: files over 50 MiB must use Git LFS")
        if path.suffix not in {".md", ".txt", ".py", ".json", ".yml", ".yaml"}:
            continue
        text = path.read_text(encoding="utf-8")
        if personal_path.search(text):
            problems.append(f"{name}: personal machine path")
        if secret.search(text):
            problems.append(f"{name}: possible credential (value omitted)")
        if path.suffix == ".py":
            try:
                ast.parse(text, filename=name)
            except SyntaxError as error:
                problems.append(f"{name}:{error.lineno}: Python syntax error")
        if path.suffix == ".md":
            for link in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text):
                if link.startswith(("https://", "http://", "mailto:", "#")):
                    continue
                target = (path.parent / link.split("#", 1)[0]).resolve()
                if not target.is_relative_to(ROOT):
                    problems.append(f"{name}: link leaves the repository")
                elif not target.exists():
                    problems.append(f"{name}: missing link {link}")
                elif target.is_file() and target.relative_to(ROOT).as_posix() not in public:
                    problems.append(f"{name}: link points to an excluded file: {link}")
    if problems:
        raise SystemExit("\n".join(problems))
    print(f"Public tree OK: {len(names)} files, {total / 1024 / 1024:.2f} MiB")
    print(f"{len(lfs)} LFS pointers checked against the index and working files.")
    print("Python syntax, local Markdown links, size and basic credential/path checks passed.")


if __name__ == "__main__":
    main()
