# XGY4n.github.io

TROCAR Works 静态站点，托管于 GitHub Pages，域名 `https://trocarworks.site/`。

用户主页仓库，内容直接发布在根路径 `https://xgy4n.github.io/`，无需子目录，Settings 里也不用手动开 Pages 。

纯静态：没有构建步骤、没有依赖，改动 push 到 `main` 即生效。

## 结构

```
index.html            入口：按浏览器语言跳 /zh/ 或 /en/（跳转壳，noindex）
sitemap.xml           四个内容页 + hreflang 交叉声明（与页内 <head> 一致）
robots.txt            全放行 + 指向 sitemap
zh/
├── index.html        工作室首页 · 中文
└── peeper/index.html Peeper 游戏页 · 中文
Peeper/
└── index.html        旧地址兼容壳：/Peeper/ 曾长期对外分发，只做语言检测
                      跳 /zh/peeper/ 或 /en/peeper/，不放内容（目录保留大写
                      正是为了匹配旧链接）
en/
├── index.html        工作室首页 · English
└── peeper/index.html Peeper 游戏页 · English
assets/
├── css/              base.css（像素字体/重置/body/语言切换，两页共用）
│                     root.css、peeper.css（各页专属；页面按 base+自己 两个 link 引）
├── js/               eye-tracking.js（瞳孔跟随，zh/en peeper 共用）
│                     lang-switch.js（切换时写 localStorage，四页共用）
├── fonts/            像素字体 Uranus_Pixel_11Px（整站唯一一份）
├── icons/            标签页图标：首页用 favicon-*.png，Peeper 用 peeper- 前缀
├── brand/            首页品牌素材（logo 锁定图、og 分享图、src/ 为 logo 源图）
└── peeper/           Peeper 页素材：眼睛美术、游戏 gif、场景 png、背景纹理
tools/
├── logo-assets.py    从 assets/brand/src/logo-src.jpg 重生成 brand + icons 里首页那组
└── eye-favicon.py    从 assets/peeper/eye.png 重生成 icons 里 peeper- 前缀那组
```

约定：**目录里只放 html，二进制素材一律进 `assets/` 按用途分组**；文件名全小写
（GitHub Pages 的 URL 大小写敏感）——唯一例外是兼容壳 `Peeper/`，大写沿用旧链接。

## 多语言

每种语言一个目录、目录内 `index.html`：`/zh/peeper/`、`/en/peeper/` 这类
干净 URL 直接拿去分发。根 `index.html` 是跳转壳：优先读
`localStorage("trocar-lang")`（值 zh|en，各页右上角切换时写入），没有记录
就看浏览器语言（`zh*` → `/zh/`，其余 → `/en/`）；禁用 JS 时 `meta refresh`
1 秒落 `/en/`，并有 noscript 手动链接。壳页带 `noindex`，语言页互挂
canonical / hreflang（x-default：根指向壳，Peeper 指向英文版）。

加第三种语言 = 新建目录（如 `ja/`）复制一套页面，再补各页的 hreflang。

语言页的 **html 只含文案**，样式与行为全在 `assets/css`、`assets/js`：
版式改动改一处即两语言生效；文案与 canonical / og / hreflang 里的语言路径
仍需两页各自同步。CSS 里的 `url()` 按 css 文件自身位置解析，页面深度变化
不影响素材寻址。根 `index.html` 壳里的检测脚本是整站唯一保留的内联 JS
（必须在样式加载前跑，且只有一处用）。

首页与 Peeper 页共用同一套排版规矩：字号取 14 的整数倍，行高与字距取该档
倍数的整数倍，理由见 `assets/css/base.css` 顶部的注释。

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