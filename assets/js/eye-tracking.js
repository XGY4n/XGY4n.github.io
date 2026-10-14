/* Peeper 页眼睛瞳孔跟随鼠标。
   被 zh/peeper 与 en/peeper 两页共用，用 <script src ... defer> 引入，
   依赖页面上的 .eye / .eye-pupil 两层图（同 237×237、共用像素网格）。 */
/* 瞳孔跟随鼠标 */
    (function () {
        var eye = document.querySelector('.eye');
        var pupil = document.querySelector('.eye-pupil');
        if (!eye || !pupil || !window.requestAnimationFrame) return;

        var ART = 237;
        var MAX_X = 13;
        var MAX_UP = 4;
        var MAX_DOWN = 7;
        var REACH = 240;
        var EASE = 0.18;

        var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        var tx = 0, ty = 0, mx = 0, my = 0;
        var px = 0, py = 0, scale = 1, raf = 0, tracking = false;

        function frame() {
            raf = 0;
            var k = reduce ? 1 : EASE;
            tx += (mx - tx) * k;
            ty += (my - ty) * k;
            if (Math.abs(mx - tx) < 0.01 && Math.abs(my - ty) < 0.01) { tx = mx; ty = my; }
            pupil.style.transform =
                'translate(' + Math.round(tx * scale) + 'px,' + Math.round(ty * scale) + 'px)';
            if (tx !== mx || ty !== my) raf = requestAnimationFrame(frame);
        }

        function kick() { if (!raf) raf = requestAnimationFrame(frame); }

        function aim() {
            if (!tracking) return;
            var r = eye.getBoundingClientRect();
            if (!r.width) return;
            scale = r.width / ART;
            var ax = (px - (r.left + r.width / 2)) / REACH;
            var ay = (py - (r.top + r.height / 2)) / REACH;
            ax = ax < -1 ? -1 : ax > 1 ? 1 : ax;
            ay = ay < -1 ? -1 : ay > 1 ? 1 : ay;
            mx = ax * MAX_X;
            my = ay * (ay < 0 ? MAX_UP : MAX_DOWN);
            kick();
        }

        function onMove(e) {
            px = e.clientX;
            py = e.clientY;
            tracking = true;
            aim();
        }

        function recenter() {
            tracking = false;
            mx = 0;
            my = 0;
            kick();
        }

        window.addEventListener('pointermove', onMove, { passive: true });
        window.addEventListener('pointerdown', onMove, { passive: true });
        window.addEventListener('pointerup', function (e) {
            if (e.pointerType !== 'mouse') recenter();
        }, { passive: true });
        window.addEventListener('scroll', aim, { passive: true });
        window.addEventListener('resize', aim);
        document.addEventListener('mouseleave', recenter);
        window.addEventListener('blur', recenter);
    })();
