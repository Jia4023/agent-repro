| 论文 | 核心模块（要搞懂到能画出来） | 脚手架（跑通就行） |
|---|---|---|
| Self-refine | 迭代循环：feedback反馈→refine精化→满⾜停⽌条件 | 数据加载、LLM API调用、prompt 模板 、评测指标|

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
代码位置：`self-refine/src/acronym/run.py:42-75`（已打开核对）
我做的验证：观察 run2.log 的 5 轮分数 —— 23 → 23 → 22 → 20 → 23，**没有单调上升**。说明这个实现不保证"越改越好"，它只是固定跑 5 轮并把每轮都记下来（`run.py:64` 的 `if total_score >= 0` 恒为真，`best_score_so_far` 本意是"记录最高分"，实际没起作用）
我还不懂：acronym/run.py 里一个 break 都没有。 所以它必然跑满 5 轮才停。而GSM 的 max_attempts 不是写死的。为什么前者固定五轮，后者不固定。（GSM的还没跑）