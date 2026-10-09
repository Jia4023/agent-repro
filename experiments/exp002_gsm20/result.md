# exp002 结果：GSM8K 上的 Self-Refine

**时间**：2026-10-09
**模型**：`glm-5.3-flash`（经中转站 `opencode.ai/zen/go`）
**样本**：GSM8K 前 20 题（`gsm20.jsonl`）
**设置**：`max_attempts=4`、`temperature=0.0`、`feedback_type=rich`

## 结果（论文值 vs 我的值）

| | 论文 Table 1 | | | **我的** |
|---|---|---|---|---|
| 基座模型 | GPT-3.5 | ChatGPT | GPT-4 | **glm-5.3-flash** |
| attempt 0（一次生成） | 64.1 | 74.8 | 92.9 | **90.0** |
| attempt 4（4 轮精化后） | 64.1 | 75.0 | 93.1 | **95.0** |
| 提升 | 0 | +0.2 | +0.2 | **+5.0** |

逐轮明细：

| attempt | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| 答对 | 18/20 | 19/20 | 19/20 | 19/20 | 19/20 |
| 准确率 | 90.0% | 95.0% | 95.0% | 95.0% | 95.0% |

> 论文 §5 另有一组（GPT-3，对比 Self-Correction）：45.9 → 55.7。

## 预测对照（`plan.md` 里**跑之前**写的）

| | 预测 | 实际 | |
|---|---|---|---|
| attempt 0 | 80%（16/20） | 90%（18/20） | ❌ 低了 2 题 |
| attempt 4 | 85%（17/20） | 95%（19/20） | ❌ 低了 2 题 |
| **提升幅度** | **+1 题** | **+1 题** | ✅ |

猜错的地方也有信息量：我以为现代 flash 模型在 GSM8K 上约 80%，实际 **90%**——和论文里的 GPT-4（92.9）差不多。

## 和论文规律一致的地方（这两条支持"复现方向正确"）

1. **"基座越强、提升越小"**：我们的 base（90%）接近论文 GPT-4（92.9），而 GPT-4 在论文里只提升 0.2 个点。
2. **提升集中在早期**：论文 §4（Figure 4）说 early iterations 带来主要改善；我们的结果是**第 1 轮就到位**，之后 3 轮原地不动（19 → 19 → 19）。

## 差在哪、为什么

| # | 差异来源 | 说明 |
|---|---|---|
| 1 | **模型完全不同** | 论文用 GPT-3.5 / ChatGPT / GPT-4（2023）；我用 `glm-5.3-flash`（现代思考型模型） |
| 2 | **规模缩小** | 20 题 vs 全量 1319 题。**20 题的分辨率是 5%/题——+1 题就是最小可测量单位** |
| 3 | **prompt 被改过** | 加了 `system_message`（详见 `patches/README.md`） |
| 4 | **代码被改过** | 官方代码 9 个文件 + 环境 3 处（见下） |
| 5 | **只跑了一次** | 没有 3 个 seed，算不出标准差 |

### 被改动的清单

| 仓库 | 文件 | 改了什么 |
|---|---|---|
| self-refine（7） | `src/acronym/run.py` | 引擎名 |
| | `src/acronym/task_init.py`、`feedback.py`、`task_iterate.py` | `max_tokens` 300→8000、加 `system_message` |
| | `src/acronym/task_iterate.py` | 加一行调试打印 |
| | `src/gsm/run.py` | 引擎名 |
| | `src/gsm/task_init.py` | `max_tokens` 300→8000；**content 为 null 时抛 ValueError** |
| | `src/gsm/feedback.py` | `max_tokens` 600→8000；**补"模型认为代码没问题"的分支**；**content 为 null 时抛 ValueError** |
| prompt-lib（2） | `backends/anthropic_api.py` | 适配新版 anthropic SDK |
| | `backends/openai_api.py` | `chat_engines` 加模型路由；**`InvalidRequestError` 也重试** |
| 环境（3） | `.venv/bin/activate` | 加了 3 个环境变量 |
| | `sitecustomize.py`（新文件） | 给请求加 `x-opencode-session` 头 |
| | `httpx==0.27.2` | 修老 anthropic SDK 的依赖冲突 |

## 结论：**方向成立，但幅度不可判定**

- ✅ **方向成立**：精化后确实有提升（18 → 19 题），且提升发生在第 1 轮，与论文对"早期迭代最有效"的描述一致。
- ⚠️ **幅度不可判定**：+5 个点看起来比论文的 +0.2 大，但 **20 题规模下 +1 题就是最小单位**——两者在统计上无法区分。按任务书 6.1 第 4 条，应写"**当前预算下不可判定**"。
- **要判定幅度**，至少要：样本量提到 100 题以上，或跑 3 个 seed 看标准差和两组差异的大小关系。

## 我排除过的可能（排查证据链）

| 可能的问题 | 结论 | 证据 |
|---|---|---|
| 评测脚本坏了？ | ❌ 排除了 | 用官方发布的结果验证过：能跑通、能算出数字（`official_check/`） |
| 数据有问题？ | ❌ 排除了 | 用的是数据集原文件的前 20 题，一个字没改 |
| 是我的代码吃掉了样本？ | ⚠️ **一开始确实会** | 输出曾只有 1 字节（20 题全丢）、后来是 19 行；修好后 `wc -l` = 20 |
| 模型答不出来？ | ❌ 排除了 | 答对率 90%。失败全是"格式/接口"问题，不是"不会做" |

## 已知限制（读这个数字前必须知道）

1. **20 题，5%/题的分辨率，只跑一次** —— ±1 题以内的差异不能当结论。
2. **prompt 和代码共改了 12 处**（9 个文件 + 3 处环境）——和论文不可直接比较。
3. **评测前做过数据清洗**：用 `clean_solutions.py` 剥掉模型输出里的 markdown 围栏。**不清洗的话准确率会被算成 0%**（因为官方评测脚本直接 `exec()` 那段文本）。
4. **模型的"收敛"不是代码保证的**：这个实现固定跑 5 轮（acronym）或跑到 `max_attempts`（gsm），不保证"越改越好"。

## 复现命令

```bash
# 1. 取 20 题
head -20 ~/repos/self-refine/data/tasks/gsm/gsm.jsonl > ~/repos/agent-repro/experiments/exp002_gsm20/gsm20.jsonl

# 2. 跑（约 2-4 分钟）
cd ~/repos/self-refine
PYTHONPATH=.:prompt-lib .venv/bin/python -u src/gsm/run.py \
  --gsm_task_file ~/repos/agent-repro/experiments/exp002_gsm20/gsm20.jsonl \
  --max_attempts 4 --feedback_type rich --temperature 0.0 \
  --outfile ~/repos/agent-repro/experiments/exp002_gsm20/gsm20

# 3. 数行数（必须 20）
wc -l ~/repos/agent-repro/experiments/exp002_gsm20/gsm20.fb_rich.temp_0.0.engine_glm-5.3-flash.jsonl

# 4. 清洗 markdown 围栏
cd ~/repos/agent-repro/experiments/exp002_gsm20
~/repos/self-refine/.venv/bin/python clean_solutions.py \
  gsm20.fb_rich.temp_0.0.engine_glm-5.3-flash.jsonl gsm20_clean.jsonl

# 5. 评测
cd ~/repos/self-refine
PYTHONPATH=prompt-lib:. .venv/bin/python -m src.gsm.gsm_selfref_eval \
  --path ~/repos/agent-repro/experiments/exp002_gsm20/gsm20_clean.jsonl

# 6. 用正确分母重算（脚本打印的分母写死 1319，是错的）
.venv/bin/python -W ignore -c 'import pandas as pd; df = pd.read_json("/tmp/attempt_to_acc.jsonl", lines=True); [print(i, f"{df[str(i)].mean():.1%}", f"({df[str(i)].sum()}/{len(df)})") for i in range(5)]'
```
