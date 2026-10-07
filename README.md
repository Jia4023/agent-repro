# Self-Refine 复现

复现论文 **Self-Refine: Iterative Refinement with Self-Feedback**（NeurIPS 2023）。
官方代码：https://github.com/madaan/self-refine

## 我复现的是哪个数字

GSM8K（论文里叫 Math Reasoning）上，**一次生成（attempt 0） vs 4 轮自我精化后（attempt 4）的 solve rate**。

| 基座模型 | Base | +Self-Refine |
|---|---|---|
| GPT-3.5（论文 Table 1） | 64.1 | 64.1 |
| ChatGPT（论文 Table 1） | 74.8 | 75.0 |
| GPT-4（论文 Table 1） | 92.9 | 93.1 |
| **deepseek-v4.1-flash（我的）** | **待填** | **待填** |

> 论文 §5 另有一组（用 GPT-3，对比 Self-Correction）：45.9 → 55.7。

**结果见** `experiments/exp002_gsm20/`。

## 怎么装

### 1. 克隆官方代码

```bash
mkdir -p ~/repos && cd ~/repos
git clone https://github.com/madaan/self-refine.git
cd self-refine
git clone https://github.com/reasoning-machines/prompt-lib.git    # 放在 self-refine/ 里面
```

### 2. 打适配补丁

官方代码默认指向 OpenAI 的模型（已下线 / 本机的中转站不支持），要先打补丁：
**见 `patches/README.md`**（里面还列了 patch 之外必须补的几样东西）。

### 3. 建虚拟环境

必须用 **Python 3.10**（3.12+ 装不了老版 wandb 依赖）：

```bash
uv venv .venv --python 3.10
source .venv/bin/activate
uv pip install prompt-lib/
pip install httpx==0.27.2        # 新版 httpx 与老版 anthropic SDK 冲突
```

### 4. 配环境变量

```bash
export OPENAI_API_KEY="你的 key"
export OPENAI_API_BASE="中转地址（本机用的是 https://opencode.ai/zen/go/v1）"
```

> ⚠️ 值不要写进仓库。本机这两个变量写在 `.venv/bin/activate` 末尾。

## 怎么跑

```bash
cd ~/repos/self-refine
PYTHONPATH=.:prompt-lib .venv/bin/python -u src/acronym/run.py "Using language models of code for few-shot commonsense"
```

> **必须带 `PYTHONPATH=.:prompt-lib`**。不带的话会导入 `site-packages` 里的原版 prompt-lib，
> `import` 阶段就报 `TypeError: Anthropic.__init__() takes 1 positional argument but 2 were given`。

## 目录

| 路径 | 内容 |
|---|---|
| `docs/paper_notes.md` | 论文精读笔记（核心模块 vs 脚手架、算法逻辑） |
| `experiments/` | 每次实验的命令、日志、结果 |
| `patches/` | 让官方代码能跑起来的适配改动 + 依赖说明 |
| `debug_log.md` | bug 根因记录（每个 bug 一行） |
| `agent_log.md` | Agent 出错记录（底线 2 要求） |
| `AGENTS.md` | 这个项目怎么装 / 怎么跑 / 怎么测 |

## 已知限制（为什么我的数字和论文不能直接比）

1. **模型不同**：论文用 GPT-3.5 / ChatGPT / GPT-4；我只能用中转站提供的 `deepseek-v4.1-flash`，而且它是**思考型模型**（回答前先推理，行为与原论文模型差别很大）。
2. **prompt 被改过**：为了让思考型模型正常工作，加了一条 `system_message`（详见 `patches/README.md`）。这改变了实验条件。
3. **规模缩小**：只跑 20 题（论文是全量 1319 题）；20 题的分辨率是 5%/题，一题之差就是 5 个点。
4. **官方代码本身有坑**：`src/gsm/run.py` 有 `except: pass` 会静默吞掉失败的题（官方发布的结果里 1319 题只剩 1253 条），所以跑完必须数行数。

## API 花费

（待填）
