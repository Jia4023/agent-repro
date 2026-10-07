# patches

官方代码默认指向 OpenAI 的模型（已下线 / 无权限），这里的文件是为了让它能在这台机器上跑起来。

| 文件 | 改了什么 |
|---|---|
| `self-refine-deepseek.patch` | 5 个文件：4 个 acronym + 1 个 gsm（换引擎名、调 `max_tokens`、加 `system_message`、加一行调试打印） |
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

## 注意

其中 `system_message` 和 `max_tokens` 是**必要的适配**（思考型模型必须先引导它直接输出，而且推理过程会吃掉 token 预算），**但它们确实改变了 prompt**，所以结果与论文不可直接比较。
