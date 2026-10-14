# XGY4n.github.io

TROCAR Works 静态站点，托管于 GitHub Pages，域名 `https://trocarworks.site/`。

用户主页仓库，内容直接发布在根路径 `https://xgy4n.github.io/`，无需子目录，Settings 里也不用手动开 Pages 。

纯静态：没有构建步骤、没有依赖，改动 push 到 `main` 即生效。

## 结构

```
index.html            首页入口（语言跳转壳，见下）
index-cn.html         工作室首页 · 中文
index-en.html         工作室首页 · English
Peeper/index.html     Peeper 页入口（语言跳转壳）
Peeper/index-cn.html  Peeper 游戏页 · 中文
Peeper/index-en.html  Peeper 游戏页 · English
assets/
├── fonts/            像素字体 Uranus_Pixel_11Px（整站唯一一份，两个页面共用）
├── icons/            标签页图标：首页用 favicon-*.png，Peeper 用 peeper- 前缀
├── brand/            首页品牌素材（logo 锁定图、og 分享图、src/ 为 logo 源图）
└── peeper/           Peeper 页的全部素材：眼睛美术、游戏 gif、场景 png、背景纹理
tools/
├── logo-assets.py    从 assets/brand/src/logo-src.jpg 重生成 brand + icons 里首页那组
└── eye-favicon.py    从 assets/peeper/eye.png 重生成 icons 里 peeper- 前缀那组
```

约定：**目录里只放 html，二进制素材一律进 `assets/` 按用途分组**；文件名全小写
（GitHub Pages 的 URL 大小写敏感）。

## 多语言

每个页面拆成 `index-cn.html` / `index-en.html` 两份**完全独立**的文件，
`index.html` 是跳转壳：优先读 `localStorage("trocar-lang")`（右上角切换时写入），
没有记录就看浏览器语言（`zh*` → 中文，其余 → 英文），兜底英文；禁用 JS 时
`meta refresh` 1 秒后落英文页并给出手动链接。

**分发就用语言后缀的固定链接**（如 `trocarworks.site/Peeper/index-en.html`），
`/` 与 `/Peeper/` 短链自动分流。两份文件互不引用、无共享脚本，
**改任何一份文案/版式记得同步另一份**（含 canonical / og / hreflang 里的语言后缀）。

首页与 Peeper 页共用同一套排版规矩：字号取 14 的整数倍，行高与字距取该档倍数的
整数倍，理由见 `Peeper/index-cn.html` 顶部的注释。

## 本地预览

在仓库根目录起一个静态服务器：

```sh
python -m http.server 8000
```

直接双击打开 `index.html` 也看得到，但 `@font-face` 会被 `file://` 的跨域规则拦掉，
像素字体会退回系统字体，排版对不上，所以预览还是走 http。

## 换 logo

把新图覆盖到 `assets/brand/src/logo-src.jpg`，然后：

```sh
python tools/logo-assets.py
```

脚本会把纸面抠成透明、笔画反白成品牌米白，并顺带重出 favicon 与 og 分享图。
源图换了尺寸或构图后，抠底参数（`ALPHA_LO/HI`、连通域分割阈值）可能需要重新调。