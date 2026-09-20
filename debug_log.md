# Debug 日志

根因类别只有五种：环境/依赖、数据、实现、评测、理解错误。

| 现象 | 根因类别 | 怎么发现 | 修法 | 怎么防止再犯 |
|---|---|---|---|---|
| acronym demo 解析模型回复时 IndexError，重试 3 次后脚本崩溃退出（有概率发生） | 实现 | 加调试打印，抓到模型回复是空字符串 | 目前未改代码，靠官方重试兜住 | 解析前判断标记是否存在 |
| `git push` 报 `ssh: connect to host github.com port 22: Connection refused` | 环境/依赖 | 分别测两个端口：`ssh -T git@github.com` 失败，`ssh -T -p 443 git@ssh.github.com` 成功 | 建 `~/.ssh/config`，把 `github.com` 映射到 `ssh.github.com:443` | 新机器先配好 SSH 443；写进 AGENTS.md |
