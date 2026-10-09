# Debug 日志

根因类别只有五种：环境/依赖、数据、实现、评测、理解错误。

| 现象 | 根因类别 | 怎么发现 | 修法 | 怎么防止再犯 |
|---|---|---|---|---|
| acronym demo 解析模型回复时 IndexError，重试 3 次后脚本崩溃退出（有概率发生） | 环境/依赖 | 调试调用打印出 `reasoning_tokens: 1000`、`content: ''` | **已修**：加 `system_message` 引导模型直接输出；`max_tokens` 提到 8000 留余量 | 解析前判断标记是否存在 |
| `git push` 报 `ssh: connect to host github.com port 22: Connection refused` | 环境/依赖 | 分别测两个端口：22 失败、443 成功 | 建 `~/.ssh/config`，把 `github.com` 映射到 `ssh.github.com:443` | 新机器先配好 SSH 443 |
| GSM 跑 20 题，**输出文件只有 1 字节**（20 题全被静默丢弃） | 环境/依赖 | 跑完先数行数：只有 **3** 行；日志里 54 次 `IndexError` 全在 `feedback.py:44` | **已修**：`feedback.py` 的 `max_tokens` 600 → 8000 | **跑完先数行数**，不是先看准确率 |
| GSM feedback 解析崩：模型说"代码没问题"，回复里没有 `def solution():` | 实现 | 统计 54 次报错前的回复：约 15 次是 "no error — it is correct" 这类句子 | **已修**：`feedback.py` 补分支——缺标记时返回原解，让 `run.py` 的 "it is correct" 检查生效 | 解析前判断标记是否存在 |
| GSM 输出被**截断**：只有 8/20 题写出了 `def solution():` | 环境/依赖 | 打印 `solution_curr`，发现整个内容只有 "```python\ndef solution():" | **已修**：`task_init.py` 的 `max_tokens` 300 → 8000。**先试过换模型，只缓解（12/20 → 1/20），根治还是提 token** | 生成后校验输出完整性 |
| GSM 评测算出 **0/20**：模型用 markdown 围栏包代码，`exec()` 报语法错 | 环境/依赖 | 诊断脚本直接 exec → `SyntaxError`；统计 **18/20** 带围栏 | **已缓解**：换 glm（18/20 → 1/20）；**评测前用 `clean_solutions.py` 剥围栏** | 评测前先校验解能不能被 `exec` |
| GSM 跑 3 题 **0 秒跑完**、输出 1 字节、**0 报错** | 环境/依赖 | **绕过 `except: pass` 直接调 `iterative_gsm`** → `APIConnectionError: Network is unreachable` | **已修**：`wsl --shutdown` 重启 WSL 网络 | **跑之前先 `curl` 一下中转站** |
| GSM 偶发丢 1 题（每次掉的题都不同），**0 报错** | 环境/依赖 | 同上（绕过 `except: pass` 跑全部 20 题）→ `AttributeError: 'NoneType' object has no attribute 'strip'`，因为 API 的 `content` 返回了 **null** | **已修**：`task_init.py`/`feedback.py` 加 `if x is None: raise ValueError(...)`，让它变成可重试的错误 | 外部 API 的返回值都要判空 |
| GSM 偶发丢 1–2 题，**0 报错** | 环境/依赖 | 同上 → `InvalidRequestError: Upstream request failed: [unsupported_parameter]`（中转站上游偶发拒绝某个参数） | **已修**：prompt-lib 的重试列表加上 `InvalidRequestError`（换一个上游重试就成功） | 第三方接口的偶发 4xx 也要能重试 |

## 说明

这 9 条里面有 6 条来自 GSM，它们可以归成**三类**：

### A. 模型换代（2023 年的代码 vs 现代模型）

官方代码写于 2023 年，它假设模型会"按 few-shot 模式直接续写纯代码"。现代模型不保证：

| 假设（2023 年成立） | 现代模型的实际行为 | 后果 |
|---|---|---|
| 回复里一定有 `def solution():` | 认为代码没问题时就不写 | 解析越界崩溃 |
| 回复一定非空 | 推理吃光 token 时正文为空 | 同上 |
| 输出是纯代码 | 用 ```python 包起来 | 评测 `exec` 语法错 |
| 300/600 token 够用 | 光推理就要几千 token | 输出被截断 |

### B. 官方代码的静默失败（最难查的一类）

| 位置 | 后果 |
|---|---|
| `gsm/run.py:70-72` 的 `except: pass` | 失败的题**无声无息消失**（官方发布的结果里 1319 题只剩 1253 条） |
| 评测脚本的 `except: continue` | `exec` 失败的解被跳过，**算出 0% 也不报错** |

**排查这类问题的唯一办法**：绕过 `except`，直接调底层函数（本日志第 7–9 条都是这么定位的）。

### C. 环境与第三方接口的偶发问题

网络断开、`content` 返回 null、上游拒绝某个参数——**都不是代码逻辑错，但都会导致丢数据**。共同对策：**每个环节都加检查点**（数行数、判空、让异常可重试）。

**残余未解释**：`max_tokens=8000` 时 acronym 仍出现过 1 次空回复（`run2.log` 里 DEBUG 抓到的那次）。
