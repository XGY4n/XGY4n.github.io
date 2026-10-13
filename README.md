# XGY4n.github.io

TROCAR Works 静态站点，托管于 GitHub Pages，域名 `https://trocarworks.site/`。

用户主页仓库，内容直接发布在根路径 `https://xgy4n.github.io/`，无需子目录，Settings 里也不用手动开 Pages 。

纯静态：没有构建步骤、没有依赖，改动 push 到 `main` 即生效。

## 结构

```
index.html            工作室首页（品牌 / 作品列表）
Peeper/index.html     Peeper 游戏页
Peeper/favicon-*.png  Peeper 自己的标签页图标（用那只眼睛做的，无方底）
assets/               logo 派生素材（首屏锁定图、favicon、og 分享图）
assets/src/           logo 源图
fonts/                站点用的像素字体（Peeper 游戏字体的副本）
tools/logo-assets.py  从 assets/src/logo-src.jpg 重新生成 assets/ 里的素材
tools/eye-favicon.py  从 Peeper/eye.png 重新生成 Peeper 的标签页图标
```

首页与 Peeper 页共用同一套排版规矩：字号取 14 的整数倍，行高与字距取该档倍数的
整数倍，理由见 `Peeper/index.html` 顶部的注释。

## 本地预览

在仓库根目录起一个静态服务器：

```sh
python -m http.server 8000
```

直接双击打开 `index.html` 也看得到，但 `@font-face` 会被 `file://` 的跨域规则拦掉，
像素字体会退回系统字体，排版对不上，所以预览还是走 http。

## 换 logo

把新图覆盖到 `assets/src/logo-src.jpg`，然后：

```sh
python tools/logo-assets.py
```

脚本会把纸面抠成透明、笔画反白成品牌米白，并顺带重出 favicon 与 og 分享图。
源图换了尺寸或构图后，抠底参数（`ALPHA_LO/HI`、连通域分割阈值）可能需要重新调。