"""Build the bilingual site with embedded tours, media, and a Three.js viewer."""
from html import escape
import hashlib
import json
from pathlib import Path
import posixpath
import re
import shutil
from urllib.parse import quote, unquote, urlsplit, urlunsplit

import markdown
from markdown.extensions import Extension
from markdown.extensions.toc import slugify_unicode
from markdown.treeprocessors import Treeprocessor

ROOT = Path(__file__).resolve().parents[1]
STYLE_VERSION = hashlib.sha256((ROOT / "site/style.css").read_bytes()).hexdigest()[:12]
OUTPUT = ROOT / "output" / "site"
REPO = "https://github.com/realsee-developer/realsee-astra-blender"
TOUR = "https://realsee.ai/O3eeL2R3"
LANGUAGES = ("zh", "en")
# key, Chinese source, English source, Chinese label, English label
DOCUMENTS = (
    ("overview", "README.zh-CN.md", "README.md", "项目说明", "Project overview"),
    ("tutorial", "docs/tutorial.zh.md", "docs/tutorial.en.md", "图文教程", "Tutorial"),
    ("quickstart", "prompts/quickstart.zh.md", "prompts/quickstart.en.md", "快速提示词", "Quickstart prompt"),
    ("environment", "docs/environment.md", "docs/environment.en.md", "环境准备", "Environment"),
    ("code-map", "docs/code-map.md", "docs/code-map.en.md", "代码导读", "Code map"),
    ("scripts", "scripts/README.md", "scripts/README.en.md", "案例脚本", "Case scripts"),
    ("releases", "docs/releases.md", "docs/releases.en.md", "案例文件", "Case files"),
    ("licensing", "docs/data-and-license.md", "docs/data-and-license.en.md", "数据与许可", "Data & licensing"),
    ("contributing", "CONTRIBUTING.md", "CONTRIBUTING.en.md", "参与贡献", "Contributing"),
)
ROUTES = {doc[i + 1]: f"{lang}/{doc[0]}.html"
          for doc in DOCUMENTS for i, lang in enumerate(LANGUAGES)}
ASSETS = {f"docs/assets/{name}": f"assets/{name}" for name in
          ("overview.jpg", "plan.png", "source-comparison.jpg")}
MEDIA = {f"artifacts/{name}": f"assets/{name}" for name in
         ("reconstruction_web.glb", "reconstruction_roaming.mp4")}
THREE_FILES = (
    "LICENSE", "build/three.module.js", "build/three.core.js",
    "examples/jsm/controls/OrbitControls.js", "examples/jsm/loaders/GLTFLoader.js",
    "examples/jsm/loaders/DRACOLoader.js", "examples/jsm/utils/BufferGeometryUtils.js",
    "examples/jsm/utils/SkeletonUtils.js", "examples/jsm/environments/RoomEnvironment.js",
    "examples/jsm/libs/draco/README.md", "examples/jsm/libs/draco/gltf/draco_decoder.js",
    "examples/jsm/libs/draco/gltf/draco_wasm_wrapper.js", "examples/jsm/libs/draco/gltf/draco_decoder.wasm",
)


def relative(target, page):
    return posixpath.relpath(target, posixpath.dirname(page) or ".")


def home(lang):
    return "index.html" if lang == "en" else "zh/index.html"


class SiteLinks(Treeprocessor):
    def __init__(self, md, source, page):
        super().__init__(md)
        self.source = source
        self.page = page

    def run(self, root):
        for node in root.iter():
            attribute = "href" if node.tag == "a" else "src" if node.tag == "img" else None
            if attribute is None or not node.get(attribute):
                continue
            if node.tag == "a" and node.get(attribute).rstrip("/") == TOUR:
                lang = "zh" if self.page.startswith("zh/") else "en"
                node.set(attribute, relative(home(lang), self.page) + "#original-space")
                continue
            url = urlsplit(node.get(attribute))
            if url.scheme or url.netloc or not url.path:
                continue
            source_target = posixpath.normpath(posixpath.join(
                posixpath.dirname(self.source), unquote(url.path)))
            target = ROUTES.get(source_target) or ASSETS.get(source_target)
            if target:
                path = relative(target, self.page)
            else:
                source_path = (ROOT / source_target).resolve()
                if not source_path.is_relative_to(ROOT) or not source_path.exists():
                    raise ValueError(f"Unresolved source link: {self.source}: {url.path}")
                kind = "tree" if source_path.is_dir() else "blob"
                path = f"{REPO}/{kind}/main/{quote(source_target)}"
            node.set(attribute, urlunsplit(("", "", path, url.query, url.fragment)))
            if node.tag == "img":
                node.set("loading", "lazy")
                node.set("decoding", "async")


class LinksExtension(Extension):
    def __init__(self, source, page):
        self.source, self.page = source, page
        super().__init__()

    def extendMarkdown(self, md):
        md.treeprocessors.register(SiteLinks(md, self.source, self.page), "site_links", 1)


def frame(lang, page, title, body, counterpart, description, is_home=False):
    zh = lang == "zh"
    url = lambda target: escape(relative(target, page), quote=True)
    start = url(home(lang))
    scripts = ""
    if is_home:
        imports = json.dumps({"imports": {"three": "./" + relative("vendor/three/build/three.module.js", page),
                              "three/addons/": "./" + relative("vendor/three/examples/jsm", page) + "/"}})
        version = hashlib.sha256((ROOT / "site/scene-viewer.js").read_bytes()).hexdigest()[:12]
        scripts = f'<script type="importmap">{imports}</script>\n<script type="module" src="{url("assets/scene-viewer.js")}?v={version}"></script>'
    return f'''<!doctype html>
<html lang="{'zh-CN' if zh else 'en'}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)} · Realsee × Astra × Blender</title>
  <meta name="description" content="{escape(description, quote=True)}">
  <meta name="theme-color" content="#ffffff">
  <link rel="stylesheet" href="{url('assets/style.css')}?v={STYLE_VERSION}">
  <link rel="alternate" hreflang="{'en' if zh else 'zh-CN'}" href="{url(counterpart)}">
  {scripts}
</head>
<body class="{'home' if is_home else 'docs'}">
<a class="skip-link" href="#main">{'跳到正文' if zh else 'Skip to content'}</a>
<header class="site-header">
<div class="header-inner">
  <a class="brand" href="{url(home(lang))}">Realsee × Astra × Blender</a>
  <nav class="header-nav" aria-label="{'主导航' if zh else 'Main navigation'}">
    <a href="{start}#tutorial">{'教程' if zh else 'Tutorial'}</a>
    <a href="{start}#original-space">{'原始空间' if zh else 'Original space'}</a>
    <a href="{start}#model">{'三维模型' if zh else '3D model'}</a>
    <a href="{start}#walkthrough">{'漫游视频' if zh else 'Walkthrough'}</a>
    <a href="{REPO}">GitHub ↗</a>
    <a href="https://discord.gg/2BcZpmdZj">Discord ↗</a>
  </nav>
  <a class="language-switch" href="{url(counterpart)}" lang="{'en' if zh else 'zh-CN'}" hreflang="{'en' if zh else 'zh-CN'}">{'English' if zh else '简体中文'}</a>
</div>
</header>
{body}
<footer class="site-footer">
  <p>Realsee × GPT-6 Astra × Blender</p>
  <p><a href="{url(f'{lang}/licensing.html')}">{'代码与文档 MIT · 素材许可说明' if zh else 'Code & docs: MIT · Asset licensing'}</a> · <a href="{REPO}">GitHub ↗</a> · <a href="https://discord.gg/2BcZpmdZj">{'Discord 交流 ↗' if zh else 'Join Discord ↗'}</a></p>
</footer>
</body>
</html>
'''


def build_home(lang):
    zh = lang == "zh"
    page = home(lang)
    url = lambda target: escape(relative(target, page), quote=True)
    copy = {
        "title": "把真实空间，变成可以编辑的 Blender 模型。" if zh else "A real space. An editable Blender scene.",
        "lead": "下载 Realsee 的模型、点云和全景图，让 GPT-6 Astra 调用本地 Blender，从墙体、地面和门窗开始，一步步搭出你的空间。" if zh else "Start with Realsee models, point clouds, and panoramas. Let GPT-6 Astra work in local Blender to rebuild your space, from walls and floors to doors and windows.",
        "read": "开始阅读教程" if zh else "Read the tutorial",
        "tour": "查看原始空间" if zh else "Explore the original space",
        "caption": "本案例的 Blender 空间重建效果 · 原始扫描参考已隐藏" if zh else "The reconstructed Blender scene · Original scan reference hidden",
        "steps": "从一份空间资料开始" if zh else "Start with a space you have captured",
        "compare": "看一眼现场，再继续改。" if zh else "Compare with the real space. Then keep refining.",
        "compare_body": "打开 Realsee 官方在线实景，无需下载任何资料就能查看原来的空间。把它与 Blender 预览放在一起，看看房间连接、材质和灯光，再告诉 Astra 下一步想改什么。" if zh else "Open the official Realsee tour to see the original space without downloading the exports. Compare it with the Blender previews, check the room connections, materials, and lighting, then tell Astra what to adjust.",
        "compare_alt": "走廊现场照片与 Blender 渲染对比，每组左侧为现场、右侧为渲染" if zh else "Corridor comparison: source photographs on the left, Blender renders on the right in each pair",
        "resources": "带上这些，开始自己的项目" if zh else "Everything you need to get started",
        "availability": "代码、教程、模型和漫游视频均已公开，可以下载并在自己的项目中探索。" if zh else "Code, tutorials, models, and the walkthrough video are available to download and explore.",
    }
    guide, headings = render_markdown(f"docs/tutorial.{lang}.md", page, embedded=True)
    guide_nav = "".join(f'<a href="#{escape(item["id"])}">{escape(item["name"])}</a>' for item in headings)
    resources = (
        ("quickstart", "01 / PROMPT", "复制一段提示词", "清楚告诉 Astra 要搭什么空间、分几步完成。"),
        ("code-map", "02 / CODE", "看看建模代码", "从空间分析到 Blender 建模，找到可以借鉴的方法。"),
        ("releases", "03 / OUTPUT", "了解案例成果", "原生工程、漫游和 USDZ 的文件说明与发布进度。"),
    ) if zh else (
        ("quickstart", "01 / PROMPT", "Grab a starting prompt", "Tell Astra what to build and how to work through the space."),
        ("code-map", "02 / CODE", "Explore the modeling code", "Find useful methods, from spatial analysis to Blender modeling."),
        ("releases", "03 / OUTPUT", "See the case deliverables", "Details and availability for native scenes, the walkthrough, and USDZ."),
    )
    resource_html = "".join(f'<a class="resource" href="{url(f"{lang}/{key}.html")}"><span class="kicker">{kicker}</span><h3>{escape(title)} ↗</h3><p>{escape(text)}</p></a>'
                            for key, kicker, title, text in resources)
    body = f'''<main class="home-main" id="main">
<section class="hero">
  <div class="hero-copy">
    <p class="eyebrow">A SPACE, REBUILT WITH AI</p>
    <h1>{copy['title']}</h1><p class="lead">{copy['lead']}</p>
    <div class="actions"><a class="button" href="#tutorial">{copy['read']}</a><a class="button secondary" href="#original-space">{copy['tour']}</a><a class="button secondary" href="#walkthrough">{'播放漫游视频' if zh else 'Watch the walkthrough'}</a></div>
  </div>
</section>
<section class="section" id="tutorial">
  <div class="section-heading"><p class="eyebrow">THE TUTORIAL</p><h2>{copy['steps']}</h2></div>
  <div class="tutorial-layout"><aside class="guide-nav"><nav aria-label="{'教程目录' if zh else 'Tutorial contents'}">{guide_nav}</nav><a class="text-link" href="{url(f'{lang}/quickstart.html')}">{'复制快速提示词 →' if zh else 'Get the quickstart prompt →'}</a></aside><article class="prose tutorial-prose">{guide}</article></div>
</section>
<section class="section media-section" id="original-space">
  <div class="section-heading"><p class="eyebrow">THE ORIGINAL SPACE</p><h2>{'直接走进原来的空间' if zh else 'Step inside the original space'}</h2><p>{'在这里浏览 Realsee 官方实景，和重建模型对照着看。' if zh else 'Explore the official Realsee tour here and compare it with the reconstruction.'}</p></div>
  <iframe class="tour-embed" src="{TOUR}?utm_source=realsee-astra-blender&amp;utm_medium=referral&amp;utm_campaign=editable-space&amp;utm_content={lang}-original-space" title="{'Realsee 原始空间实景漫游' if zh else 'Original space — Realsee virtual tour'}" loading="lazy" allow="fullscreen; xr-spatial-tracking; gyroscope; accelerometer" allowfullscreen referrerpolicy="strict-origin-when-cross-origin"></iframe>
</section>
<section class="section media-section" id="model">
  <div class="section-heading"><p class="eyebrow">THE RECONSTRUCTION</p><h2>{'换个角度看看整个空间' if zh else 'Explore the reconstruction in 3D'}</h2><p>{'拖动旋转，滚轮或双指缩放。网页预览从公开的 USDZ 生成，隐藏顶面，便于查看房间与走廊。' if zh else 'Drag to orbit, scroll or pinch to zoom. This web preview is derived from the published USDZ, with ceilings hidden to reveal the rooms and corridors.'}</p></div>
  <div class="model-viewer" data-model-src="{url('assets/reconstruction_web.glb')}" data-language="{lang}">
    <div class="model-canvas" tabindex="0" role="region" aria-label="{'可旋转的空间模型' if zh else 'Interactive space model'}"></div>
    <div class="model-cover"><img src="{url('assets/plan.png')}" alt="{'空间模型俯视预览' if zh else 'Plan preview of the reconstructed space'}" loading="lazy"><button class="button load-model" type="button">{'加载三维模型' if zh else 'Load 3D model'}</button></div>
    <p class="model-status" role="status" aria-live="polite">{'点击加载交互预览' if zh else 'Load the preview to explore'}</p>
    <div class="model-tools" hidden><button type="button" class="button reset-model">{'重置视角' if zh else 'Reset view'}</button><button type="button" class="button plan-model">{'俯视图' if zh else 'Plan view'}</button><button type="button" class="button fullscreen-model">{'全屏' if zh else 'Full screen'}</button></div>
  </div>
  <p class="media-note">{'原始 USDZ（560 MB）及可编辑 Blender 工程见' if zh else 'Find the original USDZ (560 MB) and editable Blender scenes on the'} <a href="{url(f'{lang}/releases.html')}">{'案例下载页' if zh else 'case downloads page'}</a>{'。' if zh else '.'}</p>
</section>
<section class="section media-section" id="walkthrough">
  <div class="section-heading"><p class="eyebrow">THE WALKTHROUGH</p><h2>{'用 85 秒逛一遍重建空间' if zh else 'Walk through the rebuilt space in 85 seconds'}</h2><p>{'直接播放，可拖动进度条或全屏观看。视频没有音轨。' if zh else 'Play here, scrub through the route, or watch full screen. The video has no audio track.'}</p></div>
  <video class="walkthrough-video" controls playsinline preload="metadata" poster="{url('assets/overview.jpg')}" aria-label="{'Blender 空间漫游视频' if zh else 'Blender space walkthrough'}"><source src="{url('assets/reconstruction_roaming.mp4')}" type="video/mp4"></video>
</section>
<section class="section resources"><div class="section-heading"><p class="eyebrow">OPEN REFERENCE</p><h2>{copy['resources']}</h2><p>{copy['availability']}</p></div><div class="resource-grid">{resource_html}</div></section>
</main>'''
    return frame(lang, page, "可编辑空间建模" if zh else "Editable space modeling", body,
                 home("en" if zh else "zh"), copy["lead"], is_home=True)


def render_markdown(source, page, embedded):
    text = (ROOT / source).read_text(encoding="utf-8")
    # The site header switches to the equivalent page in the other language.
    text = re.sub(r"^(?:简体中文 \| \[English\].*|\[简体中文\].* \| English|English \| \[简体中文\].*)\n", "", text, flags=re.M)
    if embedded:
        text = re.sub(r"\A# .+\n", "", text, count=1)
    parser = markdown.Markdown(extensions=["fenced_code", "tables", "toc", LinksExtension(source, page)],
                               extension_configs={"toc": {"slugify": slugify_unicode, "baselevel": 2 if embedded else 1}})
    return parser.convert(text), parser.toc_tokens


def build_document(doc, lang):
    i = LANGUAGES.index(lang)
    key, source, label = doc[0], doc[i + 1], doc[i + 3]
    page = ROUTES[source]
    content, _ = render_markdown(source, page, embedded=False)
    navigation = "".join(
        f'<a href="{relative(f"{lang}/{item[0]}.html", page)}"' +
        (' aria-current="page"' if item[0] == key else '') + f'>{escape(item[i + 3])}</a>'
        for item in DOCUMENTS)
    body = f'<main class="doc-shell" id="main"><aside class="sidebar"><nav class="links" aria-label="{label}">{navigation}</nav></aside><article class="prose">{content}</article></main>'
    return frame(lang, page, label, body, ROUTES[doc[2 if i == 0 else 1]],
                 "使用 Realsee 资料与 GPT-6 Astra 在 Blender 中重建可编辑空间。" if lang == "zh" else
                 "Build an editable Blender space with Realsee exports and GPT-6 Astra.")


def main():
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    (OUTPUT / "assets").mkdir(parents=True)
    for source, target in ASSETS.items():
        shutil.copyfile(ROOT / source, OUTPUT / target)
    shutil.copyfile(ROOT / "site/style.css", OUTPUT / "assets/style.css")
    shutil.copyfile(ROOT / "site/scene-viewer.js", OUTPUT / "assets/scene-viewer.js")
    shutil.copyfile(ROOT / "site/DRACO_LICENSE.txt", OUTPUT / "assets/DRACO_LICENSE.txt")
    for source, target in MEDIA.items():
        with (ROOT / source).open("rb") as media:
            if media.read(64).startswith(b"version https://git-lfs.github.com/spec/v1"):
                raise ValueError(f"{source} is an LFS pointer. Fetch the web preview and video with git lfs pull before building.")
        shutil.copyfile(ROOT / source, OUTPUT / target)
    for name in THREE_FILES:
        target = OUTPUT / "vendor/three" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / "site/node_modules/three" / name, target)
    for lang in LANGUAGES:
        (OUTPUT / lang).mkdir(exist_ok=True)
        (OUTPUT / home(lang)).write_text(build_home(lang), encoding="utf-8")
        for doc in DOCUMENTS:
            source = doc[LANGUAGES.index(lang) + 1]
            (OUTPUT / ROUTES[source]).write_text(build_document(doc, lang), encoding="utf-8")
    # Keep the previously published English homepage URL working.
    (OUTPUT / "en/index.html").write_text('''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="refresh" content="0; url=../index.html">
  <link rel="canonical" href="../index.html">
  <title>Realsee × Astra × Blender</title>
</head>
<body><h1>Realsee × Astra × Blender</h1><p><a href="../index.html">Continue to the English homepage</a></p></body>
</html>
''', encoding="utf-8")
    print(f"Built {2 + 2 * len(DOCUMENTS)} content pages, 1 redirect, approved media, and the Three.js viewer in output/site/")


if __name__ == "__main__":
    main()
