#!/usr/bin/env python3
"""把失败那次的 prompt 原样重放，看模型到底回了什么。

用法: python replay.py <prompt文件> [每组次数]
"""
import os
import sys

sys.path.insert(0, os.path.expanduser("~/repos/self-refine/prompt-lib"))
from prompt_lib.backends import openai_api  # noqa: E402

path = sys.argv[1]
n = int(sys.argv[2]) if len(sys.argv) > 2 else 6
prompt = open(path).read()

# 和官方代码里一模一样的参数
SYSTEM = (
    "Continue the few-shot examples for iteratively improving acronyms. "
    "Given the latest acronym and its scores, respond with an improved version: "
    "a line 'Title: <improved title>' followed by a line 'Acronym: <improved acronym>', and nothing else."
)
STOP = "\n\n###\n\n"


def one_call(use_stop):
    out = openai_api.OpenaiAPIWrapper.call(
        prompt=prompt,
        engine="deepseek-v4.1-flash",
        max_tokens=8000,
        stop_token=STOP if use_stop else None,
        temperature=0.7,
        system_message=SYSTEM,
    )
    return openai_api.OpenaiAPIWrapper.get_first_response(out)


def run(label, use_stop):
    print(f"\n===== {label} =====")
    bad = 0
    for i in range(n):
        r = one_call(use_stop)
        ok = "Acronym:" in r
        if not ok:
            bad += 1
        head = r[:70].replace("\n", "\\n")
        print(f"第{i + 1}次 长度={len(r):5d} {'正常' if ok else '❌ 会崩'} | {head!r}")
    print(f"-> {n} 次里坏了 {bad} 次")


run("A 组：和官方代码一样，带 stop_token", True)
run("B 组：去掉 stop_token，看模型本来想输出什么", False)
