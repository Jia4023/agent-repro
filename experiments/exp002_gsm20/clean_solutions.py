#!/usr/bin/env python3
"""把模型输出里的 markdown 代码围栏剥掉，生成一个可评测的文件。

为什么需要
----------
现代模型常把代码包在 ```python ... ``` 里，而官方评测脚本是**直接 exec() 这段文本**。
遇到围栏会报 SyntaxError，然后被评测脚本的 `except Exception: continue` **静默跳过**
——结果是准确率被算成 0（而不是报错）。详见 REPORT.md 的「归因」一节。

这个脚本把清洗步骤**显式化**：不动官方代码，而是在评测前对输出做一次转换。

用法
----
    python clean_solutions.py <原始输出.jsonl> <清洗后.jsonl>
"""
import json
import re
import sys

FENCE = re.compile(r"```(?:python)?\s*\n(.*?)```", re.DOTALL)


def clean_code(text):
    """剥掉 markdown 代码围栏和围栏外的说明文字。"""
    if not isinstance(text, str):
        return text
    m = FENCE.search(text)
    if m:
        return m.group(1).strip()
    t = text.strip()
    t = re.sub(r"^```[a-zA-Z]*\s*\n?", "", t)
    t = re.sub(r"\n?```\s*$", "", t)
    return t.strip()


def main(src, dst):
    with open(src, encoding="utf-8") as f:
        rows = [json.loads(l) for l in f]

    changed = 0
    for row in rows:
        for log in row.get("run_logs") or []:
            for key in ("solution_curr", "solution_fixed"):
                if isinstance(log.get(key), str) and "```" in log[key]:
                    log[key] = clean_code(log[key])
                    changed += 1
        for key in ("generated_answer_ours", "generated_answer_direct"):
            if isinstance(row.get(key), str) and "```" in row[key]:
                row[key] = clean_code(row[key])

    with open(dst, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print("题数:", len(rows))
    print("剥掉围栏的片段数:", changed)
    print("已写出:", dst)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
