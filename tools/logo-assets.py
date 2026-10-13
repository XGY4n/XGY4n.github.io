# -*- coding: utf-8 -*-
"""从 assets/src/logo-src.jpg 派生站点用的 logo 素材。

源图是一张 1024×1024 的 JPEG：深墨色的套管针 + 烘焙在右下角的
trocarworks 字标，铺在米白纸面上。网页是深色底，直接用会带一块
亮方块，所以这里把纸面抠成透明、笔画改成米白（品牌反白）。

产出（全部写回 assets/）：
    logo-lockup.png     首屏品牌锁定图，透明底 + 米白笔画
    favicon-32/64.png   奶油底 + 墨色管身（浏览器标签栏深浅色都看得清）
    apple-touch-icon.png 同上，180px 不预圆角（iOS 自己会裁）
    og-image.png        1200×630 分享图，深底 + 米白锁定图 + 像素字标语

抠底原理：纸面与笔画的亮度差很大（实测 240 vs 35），用亮度当 alpha
反算，再用 smoothstep 掐掉纸面噪点和 JPEG 块状纹理；字标与器械在源图
里不连通，按连通域分开即可单独取器械。换 logo 时重跑本脚本。

    python tools/logo-assets.py
"""

import os
from collections import deque

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets", "src", "logo-src.jpg")
OUT = os.path.join(ROOT, "assets")
FONT = os.path.join(ROOT, "Peeper", "fonts", "Uranus_Pixel_11Px.ttf")

CREAM = (239, 233, 219)      # 品牌纸面米白
INK = (43, 53, 54)           # 品牌笔画墨色
BG = (11, 11, 13)            # 站点底色（与 CSS 的 --bg 一致）

ALPHA_LO, ALPHA_HI = 0.20, 0.70   # alpha 映射的死区/饱和点，压掉纸面噪点


def luminance(img):
    return np.asarray(img).astype(np.float32) @ np.array([0.299, 0.587, 0.114], dtype=np.float32)


def key_out(path):
    """把纸面抠成透明，返回 (alpha, 原始 RGB 数组)。"""
    rgb = Image.open(path).convert("RGB")
    lum = luminance(rgb)
    # 轻微模糊压掉 JPEG 块噪；针体最细处约 6px，不受影响
    lum = np.asarray(Image.fromarray(lum.astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.7)),
                     dtype=np.float32)

    l_bg = float(np.median(lum[lum > 200]))
    l_ink = float(np.percentile(lum[lum < 128], 5))
    t = np.clip((l_bg - lum) / (l_bg - l_ink), 0.0, 1.0)
    s = np.clip((t - ALPHA_LO) / (ALPHA_HI - ALPHA_LO), 0.0, 1.0)
    return (s * s * (3.0 - 2.0 * s) * 255.0).astype(np.uint8), np.asarray(rgb)


def components(alpha, thr=60):
    """8 连通标注，返回 [(掩码, 最小 y)]，用来把字标从器械上摘掉。"""
    solid = alpha > thr
    h, w = solid.shape
    seen = np.zeros((h, w), dtype=bool)
    out = []
    for sy in range(h):
        for sx in range(w):
            if solid[sy, sx] and not seen[sy, sx]:
                seen[sy, sx] = True
                q = deque([(sy, sx)])
                pix = []
                y0 = sy
                while q:
                    y, x = q.popleft()
                    pix.append((y, x))
                    y0 = min(y0, y)
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            ny, nx = y + dy, x + dx
                            if 0 <= ny < h and 0 <= nx < w and solid[ny, nx] and not seen[ny, nx]:
                                seen[ny, nx] = True
                                q.append((ny, nx))
                m = np.zeros((h, w), dtype=bool)
                ys, xs = zip(*pix)
                m[list(ys), list(xs)] = True
                out.append((m, y0))
    return out


def rgba(alpha, color):
    h, w = alpha.shape
    out = np.zeros((h, w, 4), dtype=np.uint8)
    out[..., 0], out[..., 1], out[..., 2], out[..., 3] = color[0], color[1], color[2], alpha
    return Image.fromarray(out, "RGBA")


def trim(img, pad_ratio=0.02):
    ys, xs = np.nonzero(np.asarray(img)[..., 3] > 60)
    px = int(round((xs.max() - xs.min()) * pad_ratio))
    py = int(round((ys.max() - ys.min()) * pad_ratio))
    w, h = img.size
    return img.crop((max(0, xs.min() - px), max(0, ys.min() - py),
                     min(w, xs.max() + 1 + px), min(h, ys.max() + 1 + py)))


def opening(mask_alpha, radius=5, thr=100):
    """腐蚀再膨胀：细针（约 6~8px 宽）断开，管身原样回来。"""
    y, x = np.mgrid[-radius:radius + 1, -radius:radius + 1]
    disk = ((x * x + y * y) <= radius * radius).astype(np.uint8)

    def dilate(m):
        acc = np.zeros_like(m)
        ys, xs = np.nonzero(disk)
        for dy, dx in zip(ys - radius, xs - radius):
            acc |= np.roll(np.roll(m, dy, 0), dx, 1)
        return acc

    m = (mask_alpha > thr).astype(np.uint8)
    return dilate(1 - dilate(1 - m))


def tint(img, color):
    t = Image.new("RGBA", img.size, color + (255,))
    t.putalpha(img.split()[3])
    return t


def fit(img, bw, bh):
    s = min(bw / img.width, bh / img.height)
    return img.resize((max(1, round(img.width * s)), max(1, round(img.height * s))), Image.LANCZOS)


def tile(mark, size, bg, fg, ratio, radius_pct):
    pad = int(size * (1 - ratio) / 2)
    inner = size - 2 * pad
    m = fit(tint(mark, fg), inner, inner)
    base = Image.new("RGBA", (size, size), bg + (255,))
    if radius_pct:
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, size - 1, size - 1],
                                               radius=int(size * radius_pct), fill=255)
        base.putalpha(mask)
    base.alpha_composite(m, (pad + (inner - m.width) // 2, pad + (inner - m.height) // 2))
    return base


def main():
    alpha, _ = key_out(SRC)

    # 字标字母全部起于 y>=574（裁剪后坐标），器械两段最早起于 y=214，
    # 按连通域顶端一分为二即可。阈值取 500，两边都留足余量。
    comps = components(alpha)
    icon_mask = np.zeros_like(alpha, dtype=bool)
    for m, y0 in comps:
        if y0 < 500:
            icon_mask |= m
    assert len(comps) > 3, "连通域太少，抠底参数可能失效了"

    lockup = trim(rgba(alpha, CREAM))
    icon_img = rgba(np.where(icon_mask, alpha, 0).astype(np.uint8), CREAM)
    ys, xs = np.nonzero(np.asarray(icon_img)[..., 3] > 60)
    icon_img = icon_img.crop((xs.min() - 10, ys.min() - 10, xs.max() + 11, ys.max() + 11))

    body_alpha = np.where(opening(np.asarray(icon_img)[..., 3]), np.asarray(icon_img)[..., 3], 0)
    body = rgba(body_alpha.astype(np.uint8), CREAM)
    ys, xs = np.nonzero(body_alpha > 40)
    body = body.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))

    lockup.save(os.path.join(OUT, "logo-lockup.png"), optimize=True)
    tile(body, 32, CREAM, INK, 0.92, 0.22).save(os.path.join(OUT, "favicon-32.png"), optimize=True)
    tile(body, 64, CREAM, INK, 0.90, 0.22).save(os.path.join(OUT, "favicon-64.png"), optimize=True)
    tile(body, 180, CREAM, INK, 0.74, 0.0).save(os.path.join(OUT, "apple-touch-icon.png"), optimize=True)

    # og 分享图：逻辑稿 400×210 排完再 3x 整数放大，
    # 像素字才不会像 PIL 直接渲染大字那样被抗锯齿糊掉。
    W, H, S = 1200, 630, 3
    w, h = W // S, H // S
    og = Image.new("RGB", (w, h), BG)
    lg = fit(lockup, 150, 150)
    og.paste(lg, ((w - lg.width) // 2, 16), lg)
    font = ImageFont.truetype(FONT, 14)
    text, spacing = "独立游戏工作室", 2
    widths = [font.getbbox(c)[2] - font.getbbox(c)[0] for c in text]
    x = (w - (sum(widths) + spacing * (len(text) - 1))) // 2
    draw = ImageDraw.Draw(og)
    for c, cw in zip(text, widths):
        draw.text((x, 182), c, font=font, fill=CREAM)
        x += cw + spacing
    og.resize((W, H), Image.NEAREST).save(os.path.join(OUT, "og-image.png"), optimize=True)

    print("logo-lockup.png %s" % (lockup.size,))
    print("favicon / apple-touch-icon / og-image 已更新")


if __name__ == "__main__":
    main()