# patches

官方代码默认指向 OpenAI 的模型（已下线 / 无权限），这里的文件是为了让它能在这台机器上跑起来。

| 文件 | 改了什么 |
|---|---|
| `self-refine-deepseek.patch` | **6 个文件**：4 个 acronym + 2 个 gsm（换引擎名、调 `max_tokens`、加 `system_message`、加一行调试打印、**修 `gsm/feedback.py` 的解析分支**） |
| `prompt-lib-deepseek.patch` | 2 个文件：修 anthropic SDK 调用、给 deepseek 加路由 |
| `sitecustomize.py` | 给发往 opencode.ai 的请求自动加 `x-opencode-session` 头 |

## 怎么套用

在**干净的官方代码**上执行：

```bash
cd ~/repos/self-refine
git apply ~/repos/agent-repro/patches/self-refine-deepseek.patch
git -C prompt-lib apply ~/repos/agent-repro/patches/prompt-lib-deepseek.patch
cp ~/repos/agent-repro/patches/sitecustomize.py ~/repos/self-refine/.venv/lib/python3.10/site-packages/
```

## patch 之外还缺什么（缺了跑不起来）

| 缺什么 | 为什么需要 | 怎么补 |
|---|---|---|
| `httpx==0.27.2` | 新版 httpx 与老版 anthropic SDK 冲突，`import anthropic` 会崩 | `.venv/bin/pip install httpx==0.27.2` |
| Python **3.10** | 官方依赖里的老版 wandb / pathtools 在 3.12+ 上装不了 | 用 uv 装 CPython 3.10 再建 venv |
| 3 个环境变量 | 没有 key 和地址，一行都跑不了 | 见根目录 README |

## 注意：改动分三类，读数字前必须知道

| 类别 | 具体 | 说明 |
|---|---|---|
| **必须**（不换模型就跑不起来） | 引擎名、`chat_engines` 路由、anthropic SDK 调用 | 换模型的必然代价，不影响可比性 |
| **修官方 bug** | `gsm/feedback.py` 补"模型认为代码没问题"的分支 | 原代码和 `run.py` 的 "it is correct" 检查**自相矛盾**——`run.py` 允许模型说"没问题"，但解析器要求回复里必须有 `def solution():`。不修就必然崩 |
| **模型适配**（⚠️ 会改变实验条件） | `max_tokens` 调大、加 `system_message` | 思考型模型的推理会吃掉 token 预算，不加就跑不出结果。**但这两处改变了 prompt 和生成长度上限，所以结果与论文不可直接比较** |
