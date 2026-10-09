# exp002 · GSM8K 上的 Self-Refine

目标：在 GSM8K 上复现"一次生成 vs 4 轮精化后"的 solve rate。
**实验计划和跑之前的预测见 `plan.md`；最终结果见 `result.md`。**

## 运行记录（20 题）

| # | 模型 | 结果 | 根因 | 修了什么 |
|---|---|---|---|---|
| 1 | deepseek-v4.1-flash | ❌ 输出 **1 字节** | `feedback.py` 的 `max_tokens=600` 被推理吃光 → 空回复 → 每题重试 3 次全失败 → 被 `except: pass` 丢光（日志：`run_failed.log`） | `feedback.py` max_tokens 600→8000 |
| 2 | deepseek-v4.1-flash | ⚠️ 20 行，但**评测 0/20** | 模型用 markdown 围栏包代码 → `exec` 语法错 → 被 `except: continue` 跳过；另 `task_init` 300 token 导致 12/20 截断（日志：`run_deepseek.log`） | 换模型（见 #3） |
| 3 | glm-5.3-flash | ❌ **19 行** | `task_init.py:33` 的 `max_tokens=300` → 推理吃光 → API 返回 `content: null` → `None.strip()` 抛 AttributeError（不在重试列表）→ 静默丢题 | `task_init.py` max_tokens 300→8000 |
| 4 | glm-5.3-flash | ❌ **19 行**（掉的题和第 3 次不同） | `content` **偶发**为 null（中转站问题，不是题目问题） | `task_init.py`/`feedback.py` 加 `if x is None: raise ValueError(...)` → 变成可重试 |
| 5 | glm-5.3-flash | ❌ **19 行**（又换了一题） | `InvalidRequestError: [unsupported_parameter]`：中转站**上游偶发拒绝某个参数**，而这个异常不在任何重试列表里 | prompt-lib 的重试列表加 `InvalidRequestError` |
| 6 | glm-5.3-flash | ✅ **20 行** | —— | —— |

> 中间还做过两次 3 题验证（3 题、0 报错），用来确认每次修复有效。有一次 3 题验证曾**0 秒跑完、输出 1 字节**——那不是代码问题，是 **WSL 网络断了**（详见 `debug_log.md`）。

## 结果

| attempt | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| 答对 | 18/20 | 19/20 | 19/20 | 19/20 | 19/20 |
| 准确率 | **90.0%** | 95.0% | 95.0% | 95.0% | **95.0%** |

**详细分析（论文值 vs 我的值、差在哪、为什么）见 `result.md`。**

## 文件

| 文件 | 是什么 |
|---|---|
| `plan.md` | 实验计划 + **跑之前的预测** |
| `result.md` | **最终结果与分析**（论文值 vs 我的值） |
| `gsm20.jsonl` | 20 道测试题（从 `data/tasks/gsm/gsm.jsonl` 取前 20） |
| `clean_solutions.py` | 评测前剥掉模型输出里的 markdown 围栏 |
| `gsm20.fb_rich...engine_deepseek-v4.1-flash.jsonl` | deepseek 那次跑的输出（20 行，评测会算 0%——用来对照） |
| `gsm20.fb_rich...engine_glm-5.3-flash.jsonl` | ✅ **成功那次的原始输出**（20 行） |
| `gsm20_clean.jsonl` | 清洗后的文件（**评测用的是它**） |
| `gsm20_clean.jsonl.reports.txt` | 评测脚本的报告（哪道题从错变对） |
| `run_failed.log` | 第 1 次（输出 1 字节）的完整日志 |
| `run_deepseek.log` | 第 2 次的完整日志 |
| `run.log` | ✅ **成功那次**的完整日志 |
| `verify_fix_3q.log` | 3 题验证（确认修复有效） |

## 已知问题（跑之前就知道的）

1. **`src/gsm/run.py:70-72` 有 `except: pass`** → 失败的题会被静默丢弃 → **跑完必须先 `wc -l` 数行数**
2. **评测脚本的 `except: continue`** → `exec` 失败的解会被静默跳过 → **算出 0% 也不报错**（第 2 次跑就撞上了）
3. **评测脚本的分母写死 `num_gsm=1319`** → 20 题时必须自己按 `len(df)` 重算
4. **20 题的分辨率是 5%/题** → ±1 题以内的差异不能当结论
5. **模型输出可能带 markdown 围栏** → 评测前必须用 `clean_solutions.py` 清洗
