## 论文核心模块vs脚手架

| 论文 | 核心模块（要搞懂到能画出来） | 脚手架（跑通就行） |
|---|---|---|
| Self-refine | 迭代循环：feedback反馈→refine精化→满⾜停⽌条件 | 数据加载、LLM API调用、prompt 模板 、评测指标|

## 论文的 7 个任务和它们的评测方式

论文在 7 个任务上评测（Table 1），但**只有 3 个能自动算分**（§3.2）：

| 评测方式 | 任务 | 怎么算 |
|---|---|---|
| **自动指标** | Math Reasoning (GSM8K) | % solve rate |
| | Code Optimization (PIE) | % programs optimized |
| | Constrained Generation (Commongen) | coverage % |
| **人工盲评 A/B** | Dialogue Response / Code Readability / Sentiment Reversal / Acronym Generation | 各 150 个样本，作者当裁判（Appendix C） |
| **GPT-4 当代理裁判** | 上述 4 个人工任务 | 与人工一致性：情感反转 82%、缩写 68%、对话 71% |

**为什么这个区分重要**：没有自动指标的任务，一周内做不出可信的复现数字——要么要真人打分，要么要 GPT-4 当裁判（而裁判本身也是模型，有噪声）。

另外注意 Table 6 里 acronym 的人工盲评结果：Self-Refine 44.59% / 基线 12.16% / **打平 43.24%**——近一半样本人工分不出高下。

## 模块：迭代循环

论文原句：Given an input sequence, SELF-REFINE generates an initial output, provides feedback on the output,and refines the output according to the feedback. SELF-REFINE iterates between feedback and refinement until a desired condition is met.（§2） 
我的翻译：给它一个输入，模型先自己写一版初稿，再对自己的初稿给出反馈，然后按反馈改一版；"给反馈—改一版"这两步反复交替，直到满足某个停止条件。
输入 / 输出：in = 输入 x + 三个 prompt（p_gen、p_fb、p_refine）+ 模型 M；out = 最后一轮的改进结果 y_t（§2 末句：we use the last refinement y_t as the output）
伪代码（我自己写的）：
  1. y = M(p_gen ∥ x)                          # 初始生成（Eqn 1）
  2. history = []
  3. while 未满足停止条件:
  4.     fb = M(p_fb ∥ x ∥ y)                  # 同一个模型给自己的输出写反馈（Eqn 2）
  5.     if stop(fb, t): break                 # 停止条件，每个任务自己定
  6.     y_new = M(p_refine ∥ x ∥ history ∥ y ∥ fb)   # 带着历史改进（Eqn 4）
  7.     history.append((y, fb)) #每一轮迭代，history 里都会存：- 当前的输出 y 和 当前的反馈 fb
  8.     y = y_new
  9. return y                                  # 只返回最后一次改进的结果 
代码位置：`src/acronym/run.py:42-75`（无停止条件，固定跑 5 轮）；
          `src/gsm/run.py:34-51`（有停止条件，`break` 在 :45）
我做的验证：
  ① acronym：观察 run2.log 的 5 轮分数 —— 23 → 23 → 22 → 20 → 23，**没有单调上升**。
     说明这个实现不保证「越改越好」，它只是固定跑 5 轮并把每轮都记下来
     （`run.py:64` 的 `if total_score >= 0` 恒为真，`best_score_so_far` 本意是「记录最高分」，实际没起作用）。
  ② GSM（20 题，glm-5.3-flash）：attempt 0 = **90.0%**（18/20），attempt 4 = **95.0%**（19/20），**+1 题**。
     提升**集中在第 1 轮**，之后 3 轮原地不动（19 → 19 → 19）——
     这和论文 §4（Figure 4）「early iterations 带来主要改善」一致。
     完整分析见 `experiments/exp002_gsm20/result.md`。

我还不懂：acronym/run.py 里一个 break 都没有，必然跑满 5 轮才停；而 GSM 的循环里有
break（反馈出现 "it is correct" 就停），max_attempts 还是命令行参数、不是写死的。
为什么两者不一样？
我现在的答案：取决于这个任务**有没有客观的对错信号**（论文 §2 原话：
"the condition is determined per-task"）。
  - GSM 有唯一正确答案 → 反馈里能出现"答对了"这种明确信号 → 可以提前 break
  - acronym 是首字母缩写词生成，只能打 0~25 分，没有"对/错" → 设不了可靠的
    停止条件 → 只能固定跑 5 轮
同一个原因还决定了另一件事：GSM 能自动算准确率，acronym 只能靠人工盲评或
GPT-4 当裁判（§3.2 + Appendix C）——所以 acronym 适合跑通流程，GSM 适合复现数字。

