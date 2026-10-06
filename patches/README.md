# patches

官方代码默认指向 OpenAI 的模型（已下线 / 无权限），这两个 patch 是为了让它能用 DeepSeek 跑起来。

| patch | 改了什么 |
|---|---|
| `self-refine-deepseek.patch` | 5 个文件：4 个 acronym + 1 个 gsm（换引擎名、调 max_tokens、加 system_message、加一行调试打印） |
| `prompt-lib-deepseek.patch` | 2 个文件：修 anthropic SDK 调用、给 deepseek 加路由 |

## 怎么套用

在**干净的官方代码**上执行：

```bash
cd ~/repos/self-refine
git apply ~/repos/agent-repro/patches/self-refine-deepseek.patch
git -C prompt-lib apply ~/repos/agent-repro/patches/prompt-lib-deepseek.patch
```

## 注意

改动里有 2 处**可疑**（`max_tokens` 300→8000、`system_message`）——它们改变了实验结果和论文的可比性，**需要做对照实验才能决定去留（选做：replay里修改这两处参数做对照实验）**。
