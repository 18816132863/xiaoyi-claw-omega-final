#!/usr/bin/env python3
"""Generate a PDF with various math formulas for manual verification."""
import json
import os
import sys

_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, _root)
sys.path.insert(0, os.path.join(_root, "scripts"))

from render_body import build


def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))

    tokens = {
        "accent": "#3366CC",
        "accent_lt": "#E8F0FE",
        "muted": "#888888",
        "dark": "#222222",
        "body_text": "#333333",
        "font_display_rl": "HarmonyHeiTi-Bold",
        "font_body_rl": "HarmonyHeiTi",
        "font_body_b_rl": "HarmonyHeiTi-Bold",
        "size_h1": 24,
        "size_h2": 18,
        "size_h3": 14,
        "size_body": 10.5,
        "size_caption": 9,
        "size_meta": 8.5,
        "line_gap": 16,
        "para_gap": 10,
        "section_gap": 22,
        "margin_left": 72,
        "margin_right": 72,
        "margin_top": 72,
        "margin_bottom": 72,
        "title": "Math Formula Rendering Test",
        "date": "2026-04-14",
        "author": "xiaoyi-pdf",
    }

    content = [
        {"type": "h1", "text": "数学公式渲染测试报告"},
        {"type": "body", "text": "本页用于人工核对各类数学公式在修复后的渲染效果。"},
        {"type": "divider"},

        {"type": "h2", "text": "1. 基础公式（不带 $）"},
        {"type": "math", "text": r"E = mc^2", "caption": "质能方程 (no $ wrapper)"},
        {"type": "math", "text": r"\frac{-b \pm \sqrt{b^2 - 4ac}}{2a}", "caption": "一元二次方程求根公式"},

        {"type": "h2", "text": "2. 用户习惯写法（带 $）"},
        {"type": "math", "text": r"$E = mc^2$", "caption": "带 $ 的质能方程"},
        {"type": "math", "text": r"$\sum_{i=1}^{n} x_i = x_1 + x_2 + \dots + x_n$", "caption": "带 $ 的求和公式"},
        {"type": "math", "text": r"$\int_{a}^{b} f(x)\,dx = F(b) - F(a)$", "caption": "带 $ 的定积分"},

        {"type": "h2", "text": "3. 复杂/长公式"},
        {"type": "math", "text": r"\sum_{i=1}^{n} \left( \frac{a_i + b_i}{c_i} \right) = \int_{0}^{1} \frac{x^2 + 1}{\sqrt{x^4 + 1}} \, dx", "caption": "长公式测试"},
        {"type": "math", "text": r"\int_0^\infty e^{-x^2}\,dx = \frac{\sqrt{\pi}}{2}", "label": "(1)", "caption": "高斯积分（带 label）"},

        {"type": "h2", "text": "4. 含中文 CJK 公式"},
        {"type": "math", "text": r"x = 某个值", "caption": "裸 CJK 公式"},
        {"type": "math", "text": r"\text{面积} = \pi r^2", "caption": "已带 \\text{} 的 CJK 公式"},
        {"type": "math", "text": r"$\text{标准差} = \sqrt{\frac{1}{N}\sum_{i=1}^N (x_i - \mu)^2}$", "caption": "带 $ 且含 CJK 的公式"},

        {"type": "h2", "text": "5. 段落上下文中的公式渲染检查"},
        {"type": "body", "text": "以上公式应清晰显示，无空白、无截断、无过度压缩。中文标签和公式说明文字也应正常显示。"},
    ]

    # Save inputs for reference
    with open(os.path.join(out_dir, "tokens.json"), "w", encoding="utf-8") as f:
        json.dump(tokens, f, indent=2, ensure_ascii=False)
    with open(os.path.join(out_dir, "content.json"), "w", encoding="utf-8") as f:
        json.dump(content, f, indent=2, ensure_ascii=False)

    out_pdf = os.path.join(out_dir, "math_formula_test.pdf")
    result = build(tokens, content, out_pdf)
    print(json.dumps(result, indent=2))
    print(f"\nFiles kept in: {out_dir}")
    for f in os.listdir(out_dir):
        print(f"  - {f}")


if __name__ == "__main__":
    main()
