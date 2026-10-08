# exp002 · GSM8K 上的 Self-Refine

目标：在 GSM8K 上复现"一次生成 vs 4 轮精化后"的 solve rate。
**实验计划和跑之前的预测见 `plan.md`。**

## 运行记录

| # | 时间 | 模型 | 结果 | 为什么 |
|---|---|---|---|---|
| 1 | 10-08 17:23 | deepseek-v4.1-flash | ❌ 输出文件 **1 字节** | `feedback.py` 的 `max_tokens=600` 被推理吃光 → 空回复 → 每题重试 3 次全失败 → 被 `except: pass` 静默丢弃。完整日志：`run_failed.log` |
| 2 | 10-08 23:00 | deepseek-v4.1-flash | ⚠️ 20 行、0 报错，但**评测 0/20** | 模型用 markdown 围栏（` ```python `）包代码，评测脚本 `exec()` 报语法错，而错误被 `except: continue` 吞掉。另外 `task_init` 的 `max_tokens=300` 导致 12/20 输出被截断 |
| 3 | 待做 | glm-5.3-flash | 待填 | 换模型解决上面两个未修的坑 |

## 文件

| 文件 | 是什么 |
|---|---|
| `plan.md` | 实验计划 + **跑之前的预测** |
| `gsm20.jsonl` | 20 道测试题（从 `data/tasks/gsm/gsm.jsonl` 取前 20） |
| `verify_fix_3q.log` | 修完两个 bug 后的 3 题验证（0 报错） |
| `run_failed.log` | 第一次跑的完整日志（输出 1 字节那次） |
| `run.log` | 第二次跑的完整日志 |
| `gsm20.fb_rich.temp_0.0.engine_*.jsonl` | 第二次跑的输出（20 行） |
| `official_check/` | 用**官方发布的结果**验证评测脚本的记录 |

## 结果

（待填 —— 等换模型重跑）

## 已知问题（跑之前就知道的）

1. **`src/gsm/run.py:70-72` 有 `except: pass`** → 失败的题会被静默丢弃 → **跑完必须先 `wc -l` 数行数**
2. **评测脚本的 `except: continue`** → `exec` 失败的解会被静默跳过 → **算出 0% 也不报错**（第 2 次跑就撞上了）
3. **评测脚本的分母写死 `num_gsm=1319`** → 20 题时必须自己按 `len(df)` 重算
4. **20 题的分辨率是 5%/题** → ±1 题以内的差异不能当结论
