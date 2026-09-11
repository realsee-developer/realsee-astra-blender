# 贡献指南

简体中文 | [English](CONTRIBUTING.en.md)

欢迎改进上手文档、提示词、准备工具与空间建模方法。请在说明中写清改了什么、使用了哪些输入、怎样检查结果。

- 新的通用准备功能放进 `tools/`，测试放进 `tests/`。
- `scripts/` 是案例代码，按其说明提供场景数据后再运行。不要把它的 `test_*.py` 历史检查当作自动单元测试集。
- 代码用项目相对路径；通过 PATH 或显式参数发现 Blender，不写个人机器目录。
- 不提交自己的 `data/`、输出模型、逐帧渲染、虚拟环境或访问凭据。预览图放 `docs/assets/`；经审查的公开成果放 `artifacts/`，同时更新 `.gitignore` 的文件清单，并使用 Git LFS。
- 本仓库对 `scripts/` 采用公开清单。新增案例脚本时，同时更新 `.gitignore` 与 `scripts/README.md`。

提交前运行：

```sh
python3 -m unittest discover -s tests -v
python3 tools/check_public_tree.py
```

如果改动涉及 Blender 执行，再运行 `python3 tools/project.py smoke`。请说明你实际运行的检查，避免把未执行的场景验证写成已通过。

## 维护中英文网站

文档的中文、英文版本放在一起；修改内容时同步更新对应译文。GitHub Pages 直接使用这些 Markdown 文件，页面映射和首页文案在 [tools/build_site.py](tools/build_site.py)，样式在 [site/style.css](site/style.css)。

在仓库根目录构建并预览（macOS/Linux）：

```sh
python3 -m venv .venv-site
.venv-site/bin/python -m pip install -r requirements-site.txt
.venv-site/bin/python tools/build_site.py
python3 tools/check_site.py
python3 -m http.server 8000 --bind 127.0.0.1 --directory output/site
```

然后打开 `http://127.0.0.1:8000/`。Windows 下将 `.venv-site/bin/python` 换成 `.venv-site/Scripts/python.exe`。

生成内容在 `output/site/`，每次构建会重新生成这个目录。构建器只复制三张公开预览图与样式文件。站点检查覆盖本地链接、页内锚点和中英文切换；原始资料和大型模型不进入网站包。

Pull request 会运行检查与网站构建；推送到 `main` 后，检查通过才会部署 GitHub Pages。部署使用 GitHub Actions，Pages 设置的构建来源应为 **GitHub Actions**。
