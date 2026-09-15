"""Validate generated pages, local links, fragments, and language switches."""
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1] / "output" / "site"


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids = set()
        self.links = []
        self.language = None
        self.redirect = None
        self.switches = []
        self.headings = 0
        self.errors = []
        self.iframes = []
        self.videos = []
        self.models = []
        self.imports = {}
        self.in_importmap = False
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            if attrs["id"] in self.ids:
                self.errors.append(f"duplicate ID: {attrs['id']}")
            self.ids.add(attrs["id"])
        if tag == "html":
            self.language = attrs.get("lang")
        if tag == "meta" and attrs.get("http-equiv", "").lower() == "refresh":
            self.redirect = attrs.get("content")
        if tag == "h1":
            self.headings += 1
        if tag == "iframe":
            self.iframes.append(attrs)
        if tag == "video":
            self.videos.append(attrs)
        if "data-model-src" in attrs:
            self.models.append(attrs["data-model-src"])
            self.links.append(attrs["data-model-src"])
        if tag == "script" and attrs.get("type") == "importmap":
            self.in_importmap = True
        if tag == "img" and not attrs.get("alt"):
            self.errors.append("image without alternative text")
        if "language-switch" in attrs.get("class", "").split():
            self.switches.append(attrs.get("href", ""))
        for name in ("href", "src"):
            if attrs.get(name):
                self.links.append(attrs[name])
        if tag == "a" and urlsplit(attrs.get("href", "")).hostname == "realsee.ai":
            self.errors.append("original-space link leaves the embedded tour")

    def handle_data(self, data):
        if self.in_importmap:
            self.imports = json.loads(data)["imports"]
            self.links.extend(self.imports.values())

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_importmap = False


def main():
    pages = {path: Page(path.read_text(encoding="utf-8")) for path in ROOT.rglob("*.html")}
    if len(pages) != 23:
        raise SystemExit(f"Expected 22 bilingual pages and 1 redirect; found {len(pages)}. Run tools/build_site.py first.")
    errors = []
    assets = {"assets/style.css", "assets/overview.jpg", "assets/plan.png", "assets/source-comparison.jpg",
              "assets/scene-viewer.js", "assets/DRACO_LICENSE.txt", "assets/reconstruction_web.glb", "assets/reconstruction_roaming.mp4"}
    assets.update("vendor/three/" + name for name in (
        "LICENSE", "build/three.module.js", "build/three.core.js", "examples/jsm/controls/OrbitControls.js",
        "examples/jsm/loaders/GLTFLoader.js", "examples/jsm/loaders/DRACOLoader.js",
        "examples/jsm/utils/BufferGeometryUtils.js", "examples/jsm/utils/SkeletonUtils.js",
        "examples/jsm/environments/RoomEnvironment.js", "examples/jsm/libs/draco/README.md",
        "examples/jsm/libs/draco/gltf/draco_decoder.js", "examples/jsm/libs/draco/gltf/draco_wasm_wrapper.js",
        "examples/jsm/libs/draco/gltf/draco_decoder.wasm"))
    for name in assets:
        if not (ROOT / name).is_file():
            errors.append(f"Missing site asset: {name}")
    for path in ROOT.rglob("*"):
        if path.is_symlink() or (path.is_file() and path not in pages and path.relative_to(ROOT).as_posix() not in assets):
            errors.append(f"Unexpected export: {path.relative_to(ROOT)}")
    checked = 0
    for path, page in pages.items():
        name = path.relative_to(ROOT).as_posix()
        errors.extend(f"{name}: {error}" for error in page.errors)
        expected_language = "zh-CN" if name.startswith("zh/") else "en"
        if page.language != expected_language or page.headings != 1:
            errors.append(f"{name}: incorrect language or H1 count")
        lang = "zh" if expected_language == "zh-CN" else "en"
        if name in {"index.html", "zh/index.html"}:
            source_page = ROOT / lang / "source-data.html"
            if source_page not in pages or not any(
                    not urlsplit(link).scheme and not urlsplit(link).netloc
                    and (path.parent / unquote(urlsplit(link).path)).resolve() == source_page
                    for link in page.links):
                errors.append(f"{name}: missing the local source-data download guide")
            if not {"tutorial", "original-space", "model", "walkthrough"} <= page.ids:
                errors.append(f"{name}: missing an embedded experience section")
            if len(page.iframes) != 1 or not page.iframes[0].get("title") or urlsplit(page.iframes[0].get("src", "")).hostname != "realsee.ai":
                errors.append(f"{name}: missing accessible Realsee iframe")
            if len(page.videos) != 1 or "controls" not in page.videos[0] or "playsinline" not in page.videos[0] or "autoplay" in page.videos[0]:
                errors.append(f"{name}: video must have inline controls without autoplay")
            if len(page.models) != 1 or not page.models[0].endswith("reconstruction_web.glb") or set(page.imports) != {"three", "three/addons/"}:
                errors.append(f"{name}: missing local Three.js model viewer")
        if page.redirect is not None:
            if name != "en/index.html" or page.redirect != "0; url=../index.html":
                errors.append(f"{name}: unexpected redirect")
        elif len(page.switches) != 1:
            errors.append(f"{name}: expected one language switch")
        else:
            other_path = (path.parent / page.switches[0]).resolve()
            other = pages.get(other_path)
            if not other or other.language == page.language or len(other.switches) != 1 or (other_path.parent / other.switches[0]).resolve() != path:
                errors.append(f"{name}: language switch does not link to its counterpart and back")
        for link in page.links:
            url = urlsplit(link)
            if url.hostname in {"www.realsee.com", "www.realsee.ai", "realsee.ai"}:
                query = parse_qs(url.query)
                if query.get("utm_source") != ["realsee-astra-blender"] or query.get("utm_medium") != ["referral"] or query.get("utm_campaign") != ["editable-space"] or not query.get("utm_content", [""])[0].startswith(lang + "-"):
                    errors.append(f"{name}: Realsee link missing language-specific UTM attribution")
                if url.hostname.startswith("www.") and url.hostname != ("www.realsee.com" if lang == "zh" else "www.realsee.ai"):
                    errors.append(f"{name}: official guide points to the wrong market")
            if url.scheme or url.netloc:
                continue
            if url.path.startswith("/"):
                errors.append(f"{name}: root-relative URL would escape the GitHub project path: {link}")
                continue
            target = (path.parent / unquote(url.path)).resolve() if url.path else path
            import_directory = link in page.imports.values() and link.endswith("/") and target.is_dir()
            if not target.is_relative_to(ROOT) or not (target.is_file() or import_directory):
                errors.append(f"{name}: broken local link: {link}")
            elif url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
                errors.append(f"{name}: missing fragment: {link}")
            checked += 1
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Site OK: {len(pages)} pages, {checked} local links, bilingual guides with UTM, embedded tour/video/model, and approved assets.")


if __name__ == "__main__":
    main()
