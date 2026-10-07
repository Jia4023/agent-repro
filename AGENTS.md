# 项目说明

这个仓库用于复现 Self-Refine 论文（Iterative Refinement with Self-Feedback）。
所有实验记录在 `experiments/` 下，适配改动在 `patches/` 下。

## 怎么装

1. **克隆官方代码**：`self-refine` 和它的依赖 `prompt-lib`（`prompt-lib` 放在 `self-refine/` 里面）
2. **打适配补丁**：见 `patches/README.md`（官方代码默认指向 OpenAI 的模型，要改成中转站支持的模型）
3. **建虚拟环境**：用 uv 装 **CPython 3.10**（3.12+ 装不了老版 wandb 依赖），然后 `uv venv .venv`
4. **装依赖**：`uv pip install prompt-lib/`，另外把 `httpx` 降到 `0.27.2`（新版与老版 anthropic SDK 冲突）
5. **配环境变量**：`OPENAI_API_KEY`、`OPENAI_API_BASE`（值不写进仓库）

## 怎么跑

```bash
cd ~/repos/self-refine
PYTHONPATH=.:prompt-lib .venv/bin/python -u src/acronym/run.py "Using language models of code for few-shot commonsense"
```

## 怎么测

跑通 acronym demo，看 5 轮迭代的分数变化（生成 → 自己打分 → 根据反馈改进）。

## 踩过的坑

- **必须带 `PYTHONPATH=.:prompt-lib`**。不带的话会导入 `site-packages` 里的原版 prompt-lib，`import` 阶段就报 `TypeError: Anthropic.__init__() takes 1 positional argument but 2 were given`。
- **GitHub 的 22 端口在这台机器不通**，SSH 要走 443（`~/.ssh/config` 已配 `ssh.github.com:443`）。
- **运行会在 `self-refine/` 根目录留下 `acronym_iterate_*.txt` 和 `temp_result.py`**，都是脚本自己写的，无害。
