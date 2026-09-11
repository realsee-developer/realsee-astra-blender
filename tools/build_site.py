"""Build the bilingual Pages site from reviewed Markdown and three previews."""
from html import escape
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
OUTPUT = ROOT / "output" / "site"
REPO = "https://github.com/realsee-developer/realsee-astra-blender"
TOUR = "https://realsee.ai/O3eeL2R3"
LANGUAGES = ("zh", "en")
# key, Chinese source, English source, Chinese label, English label
DOCUMENTS = (
    ("overview", "README.md", "README.en.md", "项目说明", "Project overview"),
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


def relative(target, page):
    return posixpath.relpath(target, posixpath.dirname(page) or ".")


def home(lang):
    return "index.html" if lang == "zh" else "en/index.html"


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
    tutorial = url(f"{lang}/tutorial.html")
    quickstart = url(f"{lang}/quickstart.html")
    return f'''<!doctype html>
<html lang="{'zh-CN' if zh else 'en'}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)} · Realsee × Astra × Blender</title>
  <meta name="description" content="{escape(description, quote=True)}">
  <meta name="theme-color" content="#faf8f3">
  <link rel="stylesheet" href="{url('assets/style.css')}">
  <link rel="alternate" hreflang="{'en' if zh else 'zh-CN'}" href="{url(counterpart)}">
</head>
<body class="{'home' if is_home else 'docs'}">
<a class="skip-link" href="#main">{'跳到正文' if zh else 'Skip to content'}</a>
<header class="site-header">
  <a class="brand" href="{url(home(lang))}">Realsee × Astra × Blender</a>
  <nav class="header-nav" aria-label="{'主导航' if zh else 'Main navigation'}">
    <a href="{tutorial}">{'图文教程' if zh else 'Tutorial'}</a>
    <a href="{quickstart}">{'快速提示词' if zh else 'Quickstart'}</a>
    <a href="{REPO}">GitHub ↗</a>
  </nav>
  <a class="language-switch" href="{url(counterpart)}" lang="{'en' if zh else 'zh-CN'}" hreflang="{'en' if zh else 'zh-CN'}">{'English' if zh else '简体中文'}</a>
</header>
{body}
<footer class="site-footer">
  <p>Realsee × GPT-6 Astra × Blender</p>
  <p><a href="{url(f'{lang}/licensing.html')}">{'代码与文档 MIT · 素材许可说明' if zh else 'Code & docs: MIT · Asset licensing'}</a> · <a href="{REPO}">GitHub ↗</a></p>
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
        "tour": "在线逛逛原始空间 ↗" if zh else "Explore the original space ↗",
        "caption": "本案例的 Blender 空间重建效果 · 原始扫描参考已隐藏" if zh else "The reconstructed Blender scene · Original scan reference hidden",
        "steps": "从一份空间资料开始" if zh else "Start with a space you have captured",
        "compare": "看一眼现场，再继续改。" if zh else "Compare with the real space. Then keep refining.",
        "compare_body": "打开 Realsee 官方在线实景，无需下载任何资料就能查看原来的空间。把它与 Blender 预览放在一起，看看房间连接、材质和灯光，再告诉 Astra 下一步想改什么。" if zh else "Open the official Realsee tour to see the original space without downloading the exports. Compare it with the Blender previews, check the room connections, materials, and lighting, then tell Astra what to adjust.",
        "compare_alt": "走廊现场照片与 Blender 渲染对比，每组左侧为现场、右侧为渲染" if zh else "Corridor comparison: source photographs on the left, Blender renders on the right in each pair",
        "resources": "带上这些，开始自己的项目" if zh else "Everything you need to get started",
        "availability": "代码、教程和预览图已公开；模型与漫游视频稍后提供。" if zh else "Code, tutorials, and previews are available now. Models and the walkthrough video will follow.",
    }
    steps = (
        ("整理 Realsee 资料", "将下载的模型与贴图、点云、全景图或 CAD 放进 data/，保留原来的文件夹结构。"),
        ("让 Astra 调用 Blender", "打开项目，发出建模提示词。先还原空间布局，再完善材质与灯光。"),
        ("看预览，继续修改", "对照现场检查效果，打开工程单独编辑墙体、门窗和地面，也可以尝试新的布局。"),
    ) if zh else (
        ("Gather your Realsee exports", "Place models and textures, point clouds, panoramas, or CAD in data/, keeping their original folder structure."),
        ("Let Astra work in Blender", "Open the project and send the modeling prompt. Build the spatial layout first, then refine materials and lighting."),
        ("Review, edit, and explore", "Compare previews with the source. Edit walls, windows, and floors independently, or try a new layout."),
    )
    resources = (
        ("quickstart", "01 / PROMPT", "复制一段提示词", "清楚告诉 Astra 要搭什么空间、分几步完成。"),
        ("code-map", "02 / CODE", "看看建模代码", "从空间分析到 Blender 建模，找到可以借鉴的方法。"),
        ("releases", "03 / OUTPUT", "了解案例成果", "原生工程、漫游和 USDZ 的文件说明与发布进度。"),
    ) if zh else (
        ("quickstart", "01 / PROMPT", "Grab a starting prompt", "Tell Astra what to build and how to work through the space."),
        ("code-map", "02 / CODE", "Explore the modeling code", "Find useful methods, from spatial analysis to Blender modeling."),
        ("releases", "03 / OUTPUT", "See the case deliverables", "Details and availability for native scenes, the walkthrough, and USDZ."),
    )
    step_html = "".join(f'<article class="step"><span class="step-number">0{i}</span><h3>{escape(title)}</h3><p>{escape(text)}</p></article>'
                        for i, (title, text) in enumerate(steps, 1))
    resource_html = "".join(f'<a class="resource" href="{url(f"{lang}/{key}.html")}"><span class="kicker">{kicker}</span><h3>{escape(title)} ↗</h3><p>{escape(text)}</p></a>'
                            for key, kicker, title, text in resources)
    body = f'''<main class="home-main" id="main">
<section class="hero">
  <div class="hero-copy">
    <p class="eyebrow">A SPACE, REBUILT WITH AI</p>
    <h1>{copy['title']}</h1><p class="lead">{copy['lead']}</p>
    <div class="actions"><a class="button" href="{url(f'{lang}/tutorial.html')}">{copy['read']}</a><a class="button secondary" href="{TOUR}">{copy['tour']}</a></div>
  </div>
  <figure class="hero-visual"><img src="{url('assets/overview.jpg')}" alt="{copy['caption']}" fetchpriority="high"><figcaption>{copy['caption']}</figcaption></figure>
</section>
<section class="section"><div class="section-heading"><p class="eyebrow">THE WORKFLOW</p><h2>{copy['steps']}</h2></div><div class="steps">{step_html}</div></section>
<section class="preview"><img src="{url('assets/source-comparison.jpg')}" alt="{copy['compare_alt']}" loading="lazy"><div><p class="eyebrow">REAL SPACE / BLENDER</p><h2>{copy['compare']}</h2><p>{copy['compare_body']}</p><div class="actions"><a class="button secondary" href="{TOUR}">{copy['tour']}</a></div></div></section>
<section class="section resources"><div class="section-heading"><p class="eyebrow">OPEN REFERENCE</p><h2>{copy['resources']}</h2><p>{copy['availability']}</p></div><div class="resource-grid">{resource_html}</div></section>
</main>'''
    return frame(lang, page, "可编辑空间建模" if zh else "Editable space modeling", body,
                 home("en" if zh else "zh"), copy["lead"], is_home=True)


def build_document(doc, lang):
    i = LANGUAGES.index(lang)
    key, source, label = doc[0], doc[i + 1], doc[i + 3]
    page = ROUTES[source]
    text = (ROOT / source).read_text(encoding="utf-8")
    # The site header switches to the equivalent page in the other language.
    text = re.sub(r"^(?:简体中文 \| \[English\].*|\[简体中文\].* \| English)\n", "", text, flags=re.M)
    content = markdown.markdown(text, extensions=["fenced_code", "tables", "toc", LinksExtension(source, page)],
                                extension_configs={"toc": {"slugify": slugify_unicode}})
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
    for lang in LANGUAGES:
        (OUTPUT / lang).mkdir(exist_ok=True)
        (OUTPUT / home(lang)).write_text(build_home(lang), encoding="utf-8")
        for doc in DOCUMENTS:
            source = doc[LANGUAGES.index(lang) + 1]
            (OUTPUT / ROUTES[source]).write_text(build_document(doc, lang), encoding="utf-8")
    print(f"Built {2 + 2 * len(DOCUMENTS)} HTML pages and 4 assets in output/site/")


if __name__ == "__main__":
    main()
