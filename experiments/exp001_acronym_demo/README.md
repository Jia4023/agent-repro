# exp001 · acronym demo

跑通官方 acronym demo，观察 Self-Refine 的迭代循环（生成 → 打分 → 改进，共 5 轮）。

**前置条件**：见仓库根目录 README（API 环境变量、patch、PYTHONPATH）。

## 运行命令

```bash
cd ~/repos/self-refine
PYTHONPATH=.:prompt-lib .venv/bin/python -u src/acronym/run.py "Using language models of code for few-shot commonsense" 2>&1 | tee run.log
```

约 1 分钟。

## 文件

| 文件 | 是什么 |
|---|---|
| `run1.log` | 第一次运行，最后崩溃 |
| `run2.log` | 第二次运行，跑通 |
| `repro_prompt.txt` | 失败那次的 prompt 快照 |
| `replay.py` | 重放脚本，未使用（可选：用于验证"空回复"的根因） |

## 结果

跑通，输出 5 个缩写：

| 缩写 | 分数 |
|---|---|
| CICERO | 23/25 |
| CLOVER | 20/25 |
| CLEAR | 24/25 |
| FOCUS | 24/25 |
| CLICK | 23/25 |

三个问题：

1. 分数没有单调上升（23 → 23 → 22 → 20 → 23）
2. 模型偶尔返回空字符串 → 解析失败 → 靠官方重试机制兜住。
   **原因**：这个模型是思考型，推理过程会吃光 token 预算，正文返回空（详见根目录 `debug_log.md`）
3. 重试 3 次全失败时脚本崩溃（`run1.log` 就是这样）

详见 `run1.log` 和仓库根目录 `debug_log.md`。
