# Debug 日志

根因类别只有五种：环境/依赖、数据、实现、评测、理解错误。

| 现象 | 根因类别 | 怎么发现 | 修法 | 怎么防止再犯 |
|---|---|---|---|---|
| acronym demo 解析模型回复时 IndexError，重试 3 次后脚本崩溃退出（有概率发生） | 环境/依赖 | ① 调试调用打印出 `reasoning_tokens: 1000`、`content: ''`；② 加调试打印抓到空回复 | **已修**：给三处调用加 `system_message` 引导模型直接输出；`max_tokens` 提到 8000 留余量 | 解析前判断标记是否存在 |
| `git push` 报 `ssh: connect to host github.com port 22: Connection refused` | 环境/依赖 | 分别测两个端口：`ssh -T git@github.com` 失败，`ssh -T -p 443 git@ssh.github.com` 成功 | 建 `~/.ssh/config`，把 `github.com` 映射到 `ssh.github.com:443` | 新机器先配好 SSH 443；写进 AGENTS.md |
| GSM 跑 20 题，**输出文件只有 1 字节**（20 题全被静默丢弃） | 环境/依赖 | 跑完先数行数：`wc -l` 只有 **3** 行；日志里 54 次 `IndexError` 全在 `feedback.py:44` | **已修**：`feedback.py` 的 `max_tokens` 600 → 8000（思考型模型把 600 个 token 全烧在推理上，正文为空） | **跑完先数行数**，不是先看准确率 |
| GSM feedback 解析崩：模型说"代码没问题"，回复里没有 `def solution():` | 实现 | 统计 54 次报错前模型回复的内容：约 15 次是 "no error — it is correct" 这类句子 | **已修**：在 `feedback.py` 加分支——缺标记时返回原解 + 原文当反馈，让 `run.py` 的 "it is correct" 检查生效 | 解析前判断标记是否存在（同第 1 条） |
| GSM 输出被**截断**：20 题里只有 8 题写出了 `def solution():` | 环境/依赖 | 打印 `solution_curr`，发现整个内容只有 "```python\ndef solution():"——就断在这 | **未修**（`task_init.py:33` 的 `max_tokens=300` 不够）→ 准备换模型解决 | 生成后校验输出完整性 |
| GSM 评测算出 **0/20**：模型用 markdown 围栏包代码，`exec()` 报语法错 | 环境/依赖 | 诊断脚本直接 exec 一行的解 → `SyntaxError: invalid syntax`；统计 **18/20** 带 ``` 围栏 | **未修**（模型输出格式问题）→ 准备换模型解决 | 评测前先校验解能不能被 `exec` |

## 说明

**这 4 条 GSM 的 bug 有同一个根源**：官方代码写于 2023 年，它假设模型会"按 few-shot 模式直接续写纯代码"。现代模型不保证这一点——它会思考（吃 token）、会用 markdown 格式、会在认为代码没问题时拒绝重写。

| 假设（2023 年成立） | 现代模型的实际行为 | 后果 |
|---|---|---|
| 回复里一定有 `def solution():` | 说"没问题"时就不写 | 解析越界崩溃 |
| 回复一定非空 | 推理吃光 token 时正文为空 | 同上 |
| 输出是纯代码 | 用 ```python 包起来 | 评测 `exec` 语法错 |
| 300/600 token 够用 | 推理就要几千 token | 输出被截断 |

**残余未解释**：`max_tokens=8000` 时 acronym 仍出现过 1 次空回复（`run2.log` 里 DEBUG 抓到的那次）。
