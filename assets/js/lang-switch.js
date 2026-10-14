/* 右上角语言切换：点击时把目标语言（<a data-lang="zh|en">）写进
   localStorage，供根目录的跳转壳下次读用。href 本身已完成跳转，
   这里只负责记住选择，不做任何重定向。 */
(function () {
    var links = document.querySelectorAll('.lang-switch a[data-lang]');
    for (var i = 0; i < links.length; i++) {
        links[i].addEventListener('click', function () {
            try { localStorage.setItem('trocar-lang', this.getAttribute('data-lang')); } catch (e) { }
        });
    }
})();
