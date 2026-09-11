"""Validate generated pages, local links, fragments, and language switches."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1] / "output" / "site"


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids = set()
        self.links = []
        self.language = None
        self.switches = []
        self.headings = 0
        self.errors = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            if attrs["id"] in self.ids:
                self.errors.append(f"duplicate ID: {attrs['id']}")
            self.ids.add(attrs["id"])
        if tag == "html":
            self.language = attrs.get("lang")
        if tag == "h1":
            self.headings += 1
        if tag == "img" and not attrs.get("alt"):
            self.errors.append("image without alternative text")
        if "language-switch" in attrs.get("class", "").split():
            self.switches.append(attrs.get("href", ""))
        for name in ("href", "src"):
            if attrs.get(name):
                self.links.append(attrs[name])


def main():
    pages = {path: Page(path.read_text(encoding="utf-8")) for path in ROOT.rglob("*.html")}
    if len(pages) != 20:
        raise SystemExit(f"Expected 20 bilingual pages; found {len(pages)}. Run tools/build_site.py first.")
    errors = []
    assets = {"assets/style.css", "assets/overview.jpg", "assets/plan.png", "assets/source-comparison.jpg"}
    for path in ROOT.rglob("*"):
        if path.is_symlink() or (path.is_file() and path not in pages and path.relative_to(ROOT).as_posix() not in assets):
            errors.append(f"Unexpected export: {path.relative_to(ROOT)}")
    checked = 0
    for path, page in pages.items():
        name = path.relative_to(ROOT).as_posix()
        errors.extend(f"{name}: {error}" for error in page.errors)
        expected_language = "en" if name.startswith("en/") else "zh-CN"
        if page.language != expected_language or page.headings != 1:
            errors.append(f"{name}: incorrect language or H1 count")
        if len(page.switches) != 1:
            errors.append(f"{name}: expected one language switch")
        else:
            other_path = (path.parent / page.switches[0]).resolve()
            other = pages.get(other_path)
            if not other or other.language == page.language or len(other.switches) != 1 or (other_path.parent / other.switches[0]).resolve() != path:
                errors.append(f"{name}: language switch does not link to its counterpart and back")
        for link in page.links:
            url = urlsplit(link)
            if url.scheme or url.netloc:
                continue
            if url.path.startswith("/"):
                errors.append(f"{name}: root-relative URL would escape the GitHub project path: {link}")
                continue
            target = (path.parent / unquote(url.path)).resolve() if url.path else path
            if not target.is_relative_to(ROOT) or not target.is_file():
                errors.append(f"{name}: broken local link: {link}")
            elif url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
                errors.append(f"{name}: missing fragment: {link}")
            checked += 1
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Site OK: {len(pages)} pages, {checked} local links, reciprocal language switches, and approved assets.")


if __name__ == "__main__":
    main()
