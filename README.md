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
| **glm-5.3-flash（我的）** | **90.0** | **95.0** |

> 论文 §5 另有一组（用 GPT-3，对比 Self-Correction）：45.9 → 55.7。

**结果见** `experiments/exp002_gsm20/`。

**为什么选 GSM8K**：论文在 7 个任务上评测，但只有 3 个有自动指标（GSM8K、代码优化、受限生成）。其中 GSM8K 的数据集（1319 题）和评测脚本仓库里都现成，能自动算准确率，所以选它。

**为什么另外跑了 acronym**：它是官方 README 里的入门 demo，用来跑通流程（生成 → 打分 → 改进）并观察迭代行为。但它的指标是人工盲评，一周内做不出可信数字，所以**不作为复现目标**。

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

1. **模型不同**：论文用 GPT-3.5 / ChatGPT / GPT-4；我只能用中转站提供的模型（最终用 `glm-5.3-flash`，之前试过 `deepseek-v4.1-flash`）。它们都是**思考型模型**（回答前先推理），行为与原论文模型差别很大。
2. **prompt 被改过**：为了让思考型模型正常工作，加了一条 `system_message`（详见 `patches/README.md`）。这改变了实验条件。
3. **规模缩小**：只跑 20 题（论文是全量 1319 题）；20 题的分辨率是 5%/题，一题之差就是 5 个点。
4. **官方代码本身有坑**：`src/gsm/run.py` 有 `except: pass` 会静默吞掉失败的题（官方发布的结果里 1319 题只剩 1253 条），所以跑完必须数行数。
5. **评测前做过数据清洗**：模型会把代码包在 markdown 围栏里，而官方评测脚本是直接 `exec()` 那段文本——**不清洗的话准确率会被算成 0%**。清洗脚本见 `experiments/exp002_gsm20/clean_solutions.py`。

## API 花费

中转站（opencode.ai）按量计费，本机看不到账单。本次全部实验（acronym demo + GSM 20 题跑了 6 次 + 两次 3 题验证）的日志合计约 **1.7 MB** 文本，按 4 字符/token 粗估在 **10 万～40 万 token** 量级（日志里含报错堆栈，所以这是上界）。

**无法给出准确金额**——这也是我「仍然不知道」的一件事（见 `REPORT.md`）。
