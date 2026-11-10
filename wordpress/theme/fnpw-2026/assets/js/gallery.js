/* Photo gallery: pages of six, advancing a page at a time.

   Built on a native scroll-snap track so touch swipe and trackpad drag work
   without a library. It advances on its own and stops the moment someone takes
   over, whether by pointer, keyboard or focus. */
(function () {
  var track = document.getElementById('galTrack');
  if (!track) return;

  var pages = [].slice.call(track.querySelectorAll('.vg-page'));
  var dotsBox = document.getElementById('galDots');
  var count = document.getElementById('galCount');
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var DELAY = 5200;
  var timer = null, paused = false, index = 0;

  if (pages.length < 2) {
    var nav = document.querySelector('.vg-nav');
    if (nav) nav.hidden = true;
    return;
  }

  pages.forEach(function (p, i) {
    var d = document.createElement('button');
    d.type = 'button';
    d.className = 'vg-d';
    d.setAttribute('aria-label', 'Photographs, set ' + (i + 1) + ' of ' + pages.length);
    d.addEventListener('click', function () { stop(); go(i); });
    dotsBox.appendChild(d);
  });
  var dots = [].slice.call(dotsBox.children);

  function go(i) {
    index = (i + pages.length) % pages.length;
    track.scrollTo({ left: pages[index].offsetLeft - track.offsetLeft,
                     behavior: reduced ? 'auto' : 'smooth' });
    paint();
  }

  function nearest() {
    var best = 0, bd = Infinity;
    pages.forEach(function (p, i) {
      var d = Math.abs(p.offsetLeft - track.offsetLeft - track.scrollLeft);
      if (d < bd) { bd = d; best = i; }
    });
    return best;
  }

  function paint() {
    dots.forEach(function (d, i) {
      d.setAttribute('aria-current', i === index ? 'true' : 'false');
    });
    pages.forEach(function (p, i) { p.setAttribute('aria-hidden', i === index ? 'false' : 'true'); });
    if (count) count.textContent = (index + 1) + ' / ' + pages.length;
  }

  function tick() { if (!paused) go(index + 1); }
  function start() { if (!reduced && !timer) timer = setInterval(tick, DELAY); }
  function stop() { clearInterval(timer); timer = null; }

  var settle;
  track.addEventListener('scroll', function () {
    clearTimeout(settle);
    settle = setTimeout(function () { index = nearest(); paint(); }, 90);
  }, { passive: true });

  ['pointerdown', 'touchstart', 'wheel'].forEach(function (e) {
    track.addEventListener(e, stop, { passive: true });
  });
  var box = track.parentElement;
  box.addEventListener('mouseenter', function () { paused = true; });
  box.addEventListener('mouseleave', function () { paused = false; });
  box.addEventListener('focusin', stop);
  document.addEventListener('visibilitychange', function () { paused = document.hidden; });

  [].slice.call(document.querySelectorAll('.vg-b')).forEach(function (b) {
    b.addEventListener('click', function () { stop(); go(index + (+b.dataset.dir)); });
  });

  track.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowRight') { stop(); go(index + 1); e.preventDefault(); }
    if (e.key === 'ArrowLeft') { stop(); go(index - 1); e.preventDefault(); }
  });

  paint();
  start();
})();
