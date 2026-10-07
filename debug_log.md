# Debug 日志

根因类别只有五种：环境/依赖、数据、实现、评测、理解错误。

| 现象 | 根因类别 | 怎么发现 | 修法 | 怎么防止再犯 |
|---|---|---|---|---|
| acronym demo 解析模型回复时 IndexError，重试 3 次后脚本崩溃退出（有概率发生） | 环境/依赖 | ① 调试调用打印出 `reasoning_tokens: 1000`、`content: ''`；② 加调试打印抓到空回复 | **已修**：给三处调用加 `system_message` 引导模型直接输出（不再是"不校验就硬解析"）；`max_tokens` 提到 8000 留余量。官方重试机制仍兜住残余情况 | 解析前判断标记是否存在 |
| `git push` 报 `ssh: connect to host github.com port 22: Connection refused` | 环境/依赖 | 分别测两个端口：`ssh -T git@github.com` 失败，`ssh -T -p 443 git@ssh.github.com` 成功 | 建 `~/.ssh/config`，把 `github.com` 映射到 `ssh.github.com:443` | 新机器先配好 SSH 443；写进 AGENTS.md |

## 说明

第 1 条的根因是**换了思考型模型**：它面对"无指令的 few-shot 补全串"会把 token 全烧在推理上，正文返回空字符串。官方代码假设回复非空且含标记，所以解析时越界。代码不校验只是"崩得难看"，不是根因。

**残余未解释**：`max_tokens=8000` 时仍然出现过 1 次空回复（`run2.log` 里 DEBUG 抓到的那次），所以推理耗尽只解释了主要情况。
