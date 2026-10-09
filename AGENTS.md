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

（GSM8K 的跑法见 `experiments/exp002_gsm20/result.md` 的「复现命令」。）

## 怎么测

跑通 acronym demo，看 5 轮迭代的分数变化（生成 → 自己打分 → 根据反馈改进）。

## 踩过的坑（都是实际踩到的）

### 跑之前

- **先确认网络通**：`curl -sS -o /dev/null -w '%{http_code}\n' https://opencode.ai/zen/go/v1/models`（看到 200 或 401 都算通）。
  WSL 的网络在电脑休眠/睡眠后会断，症状很吓人：**跑完 0 报错、0 秒结束、输出文件只有 1 字节**。
  修法：在 Windows 的 PowerShell 里执行 `wsl --shutdown`，然后重开 Ubuntu。
- **必须带 `PYTHONPATH=.:prompt-lib`**。不带的话会导入 `site-packages` 里的原版 prompt-lib，
  `import` 阶段就报 `TypeError: Anthropic.__init__() takes 1 positional argument but 2 were given`。
- **确认 API key 在环境里**：`echo ${#OPENAI_API_KEY}` 应该是 67。如果是 0，跑 `source ~/.bashrc`。

### 跑之后

- **第一件事是数行数**，不是看准确率：
  ```bash
  wc -l <输出文件>
  ```
  `src/gsm/run.py:70-72` 有 `except: pass`——**失败的题会无声无息消失**（官方发布的结果里 1319 题只剩 1253 条）。
  行数不对就说明有题被吞了，得去查为什么。
- **评测前要剥掉 markdown 围栏**：模型会把代码包在 ` ```python ` 里，而官方评测脚本直接 `exec()` 那段文本，
  不清洗的话准确率会被算成 0%（而它**不会报错**）。清洗脚本：`experiments/exp002_gsm20/clean_solutions.py`。

### 其他

- **GitHub 的 22 端口在这台机器不通**，SSH 要走 443（`~/.ssh/config` 已配 `ssh.github.com:443`）。
- **评测脚本的分母写死 `num_gsm=1319`**，跑子集时必须自己按 `len(df)` 重算。
- **运行会在 `self-refine/` 根目录留下 `acronym_iterate_*.txt` 和 `temp_result.py`**，都是脚本自己写的，无害。
