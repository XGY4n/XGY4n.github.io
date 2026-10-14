# -*- coding: utf-8 -*-
"""从 assets/peeper/eye.png 派生 Peeper 页的浏览器标签页图标。

eye.png 是一张不透明方图，整张都是画（深色纹理一直铺到四边，没有可抠的
"背景"），所以直接拿来当图标就是一块深色方砖。这里把页面那套径向羽化
**烘进 alpha 通道**，再垫一层暗红辉光：

  * 羽化在离画框还有几像素的地方就归零 —— 方底的断崖感来自"残留 alpha 到
    边突然中断"，归零之后方形轮廓就不存在了；
  * 辉光是给小尺寸用的：16px 下瞳孔细节全糊，只剩这团红光能认出是那只眼睛。

FADE 的数值必须和 assets/css/peeper.css 里 .eye 的 mask-image 保持一致，
两处一起改。

    python tools/eye-favicon.py
"""

import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EYE = os.path.join(ROOT, "assets", "peeper", "eye.png")
OUT_DIR = os.path.join(ROOT, "assets", "icons")
BG = (11, 11, 13)          # 站点 --bg，苹果图标铺底用

N = 237                    # eye.png 边长
# 羽化比页面上那套（rx60/ry54，零点 78%）再收紧一档：遮罩是按盒子尺寸按比例
# 算的，页面那只眼睛有 237px、死区 7px 够用，缩到图标的 30px 只剩不到 1px，
# 边上就会浮出十几级 alpha，等于方底又回来了。
FADE = dict(rx=56, ry=50, cx=0.5, cy=0.5,
            stops=((46, 1.0), (64, 0.35), (72, 0.0)))
ZOOM = 1.18                # 从中心裁掉 1/1.18 再放大：16px 下眼睛更大一点
GLOW = 0.28
GLOW_RGB = (150, 20, 26)


def fade_alpha(size=N, **kw):
    """复刻 CSS radial-gradient(ellipse rx% ry% at cx cy% ...) 的 alpha。"""
    rx, ry, cx, cy = kw["rx"], kw["ry"], kw["cx"], kw["cy"]
    y, x = np.mgrid[0:size, 0:size]
    d = np.sqrt(((x + 0.5 - cx * size) / (rx / 100 * size)) ** 2 +
                ((y + 0.5 - cy * size) / (ry / 100 * size)) ** 2) * 100
    stops = kw["stops"]
    return np.interp(d, [s[0] for s in stops], [s[1] for s in stops],
                     left=stops[0][1], right=0.0) * 255


def eyed_layer(size):
    """裁掉外圈再放大到目标尺寸，**然后**在目标尺寸上羽化。

    顺序很要紧：先羽化再缩图的话，LANCZOS 的核会把内圈的亮部卷进边缘像素，
    画框边上又会浮出一圈残余 alpha（实测 32px 下能到 17/255），方底就回来了。
    CSS 那套遮罩本来就是按盒子尺寸算的，这样也跟页面完全同构。
    """
    src = Image.open(EYE).convert("RGB")
    keep = int(N / ZOOM)
    off = (N - keep) // 2
    src = src.crop((off, off, off + keep, off + keep)).resize((size, size), Image.LANCZOS)
    return Image.fromarray(
        np.dstack([np.asarray(src).astype(float), fade_alpha(size, **FADE)]).astype(np.uint8), "RGBA")


def render(size, opaque_bg=None, box=0.94, glow_r=0.40, glow_blur=0.028):
    inner = round(size * box)
    canvas = Image.new("RGBA", (size, size),
                       (0, 0, 0, 0) if opaque_bg is None else opaque_bg + (255,))
    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow)
    # 辉光半径收在 0.40×边长以内，模糊后也够不着画框，否则它自己会被方框裁出边
    for i in range(40, 0, -1):
        t = i / 40
        r = size * glow_r * t
        draw.ellipse([size / 2 - r, size / 2 - r, size / 2 + r, size / 2 + r],
                     fill=GLOW_RGB + (int(255 * GLOW * (1 - t) ** 2.2),))
    canvas.alpha_composite(glow.filter(ImageFilter.GaussianBlur(size * glow_blur)))
    canvas.alpha_composite(eyed_layer(inner), ((size - inner) // 2, (size - inner) // 2))
    return canvas


def main():
    for size in (32, 64):
        render(size).save(os.path.join(OUT_DIR, "peeper-favicon-%d.png" % size), optimize=True)
    # 苹果图标不透明（iOS 会把透明处填黑），铺站点底色，跟首屏一个观感
    render(180, opaque_bg=BG, box=0.86).save(
        os.path.join(OUT_DIR, "peeper-apple-touch-icon.png"), optimize=True)

    # 自检：外圈 3px 的 alpha 要接近 0 —— 几十就说明方底又回来了
    for size in (32, 64):
        a = np.asarray(render(size))
        ring = np.concatenate([a[:3].reshape(-1, 4), a[-3:].reshape(-1, 4),
                               a[:, :3].reshape(-1, 4), a[:, -3:].reshape(-1, 4)])
        assert ring[:, 3].max() <= 8, "favicon 外圈 alpha 残留 %d，方底可能又出来了" % ring[:, 3].max()
        print("  %dpx 外圈 alpha 峰值 %d/255" % (size, ring[:, 3].max()))
    print("assets/icons/peeper-favicon-32/64.png + peeper-apple-touch-icon.png 已更新")


if __name__ == "__main__":
    main()