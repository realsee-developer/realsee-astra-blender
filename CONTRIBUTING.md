# 贡献指南

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
