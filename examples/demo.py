"""生成一张示例图，验证 cjk-text-render 的三项能力。

运行：python3 examples/demo.py
产出：examples/demo.png
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw  # noqa: E402

from cjk_render import audit, draw_block, load_font  # noqa: E402

W, H = 1080, 1080

TITLE = "中文会静默缺字"
SUBTITLE = "PingFang.ttc 的 index 0 是香港繁体"
BODY = (
    "用它当常规字重渲染简体，部分字会直接变成空白，"
    "而且 PIL 不报任何错。这个库在交付前替你校验，"
    "宁可脚本炸掉，也不交出少字的图。"
)
FOOTER = "cjk-text-render · MIT"

# 交付前必跑：任一字缺字，这里就会抛错
audit([TITLE, SUBTITLE, BODY, FOOTER])

img = Image.new("RGB", (W, H), "#0C1322")
draw = ImageDraw.Draw(img)

draw.text((80, 110), TITLE, font=load_font(84, bold=True), fill="#FF6B35")
draw.text((80, 232), SUBTITLE, font=load_font(38), fill="#8FA3BF")

y = draw_block(draw, BODY, load_font(40), (80, 340), max_w=W - 160, fill="#F2F5FA")

draw.line((80, y + 40, W - 80, y + 40), fill="#24344D", width=2)
draw.text((80, y + 70), FOOTER, font=load_font(28), fill="#8FA3BF")

out = pathlib.Path(__file__).resolve().parent / "demo.png"
img.save(out)
print(f"已生成 {out}")
print(f"正文渲染了 {len(BODY)} 字，缺字校验通过")
