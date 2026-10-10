# cjk-text-render

用 Python + Pillow 画中文图时，绕开**三个不会报错的坑**。

![demo](examples/demo.png)

AI 生图会把中文画糊，所以「画面里有大量中文」的场合（海报、数据卡片、营销主图、
before/after 对比图）只能靠代码画。而代码画中文，有三个坑会**静默**毁掉成品 ——
不抛异常、不留日志，图看上去"就是有点怪"。

这个库把三件事一次性封装好：**选对字面、校验缺字、按语义折行**。

## 坑一：TTC 字面顺序 —— index 0 不是「常规」

macOS 的 `/System/Library/Fonts/PingFang.ttc` 是字体集合（TrueType Collection），
它的 index 顺序是 **港繁 / 台繁 / 简体**，不是直觉上的「细 / 常规 / 粗」：

| index | 字面 | 说明 |
|---|---|---|
| **0** | PingFang **HK** Regular | ⚠️ 香港繁体 —— 最容易被误当"常规" |
| 1 | PingFang TC Regular | 台湾繁体 |
| **2** | PingFang **SC** Regular | ✅ 简体常规 |
| 3 / 4 / **5** | HK / TC / **SC** Medium | 5 是简体 |
| 6 / 7 / **8** | HK / TC / **SC** Semibold | 8 是简体，当粗体用 |
| 9 / 10 / 11 | HK / TC / SC Light | |

**踩了会怎样**：用 index 0 当常规字重 →

1. 全部中文用**港繁字形**渲染（写法不对，用户能看出怪但说不出哪里怪）；
2. **部分简体字直接缺失** —— 例如「稳」画出来是一片空白，**PIL 不报任何错**。

```python
# ❌ 常见错误写法
font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 40)     # index 默认 0 = 港繁

# ✅ 正确
font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 40, index=2)  # 简体常规
```

## 坑二：缺字是静默的，必须自己校验

PIL 渲染字体里没有的字符时不抛异常，直接画空白。**交付前必须自检。**

```python
from cjk_render import audit

audit(["本次要画的所有文字"])   # 有缺字 → 直接抛 RuntimeError
```

宁可让脚本炸掉，也不要交付一张少了字的图 —— 那是不会被发现的静默事故。

## 坑三：中文折行要按标点断，不能按像素断

中文没有空格，逐字累加到超宽就断行，会产生「知道你在打 / 杂」这种把词切开的断句。

```python
from cjk_render import wrap
lines = wrap(draw, "一段很长的中文正文……", font, max_w=900)
```

`wrap()` 的三条规则：

1. **标点优先**：在溢出点往前 12 字内找最近的标点（`，。、：；！？）」』】—…`），
   找到就断在那里；
2. **数字不拆**：`20` 和 `+` 不分到两行（`20` / `+ 项` 读起来像两个数）；
3. **标点不甩行首**：句号、逗号不会跑到下一行开头。

## 安装

无第三方依赖，只需要 Pillow：

```bash
pip install pillow
```

把 `cjk_render.py` 放进你的项目即可（单文件，无包结构）。

## 用法

```python
from PIL import Image, ImageDraw
from cjk_render import load_font, audit, wrap, draw_block

TITLE = "中文标题也会静默缺字"
BODY = "PingFang.ttc 的 index 0 是香港繁体，不是常规字重……"

audit([TITLE, BODY])                       # 交付前必跑

img = Image.new("RGB", (1080, 1080), "#0C1322")
draw = ImageDraw.Draw(img)

draw.text((80, 120), TITLE, font=load_font(72, bold=True), fill="#FF6B35")
draw_block(draw, BODY, load_font(40), (80, 300), max_w=920, fill="#F2F5FA")

img.save("out.png")
```

跑一遍示例（会生成 `examples/demo.png`）：

```bash
python3 examples/demo.py
```

## 平台字体查找顺序

`load_font()` 会自动按平台找可用的中文字体：

| 平台 | 首选 | 备选 |
|---|---|---|
| macOS | PingFang SC（index 2 / 8） | STHeiti Medium、Hiragino Sans GB |
| Windows | 微软雅黑 `msyh.ttc` | 黑体 `simhei.ttf`、宋体 `simsun.ttc` |
| Linux | Noto Sans CJK SC | 文泉驿正黑 / 微米黑 |

Linux 上装 Noto：

```bash
sudo apt-get install fonts-noto-cjk        # Debian / Ubuntu
sudo dnf install google-noto-sans-cjk-fonts # Fedora
```

## 几个工程细节（踩过才知道）

- **输出用 PNG，不用 JPG**：中文小字的笔画密集处，JPEG 压缩会产生彩色噪点。
  非要用 JPEG 的话 `quality` 别低于 95。
- **画布取平台推荐比例**：竖版信息流 `1242 × 1656`（3:4），方图 `1080 × 1080`。
- **标题要自适应缩放**：写逐档缩字号的 `fit_font()` 时，`min_size` 一定要
  小于最小调用处的起始字号 —— 否则 `while size > min_size` 首次即为假，
  循环被跳过，反而把小字反向放大到 `min_size`，直接撑出画布。
- **信息层级不超过 3 层**：小图（信息流缩略图）里能看懂才算合格。

## License

MIT
