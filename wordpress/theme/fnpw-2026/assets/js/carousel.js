/* Photo carousel: native scroll-snap track, so touch swipe and trackpad drag
   work without a library. Auto-advances, and stops as soon as a person takes
   over (pointer, focus, keyboard) or the tab goes to the background. */
(function () {
  var track = document.getElementById('volTrack');
  if (!track) return;

  var slides = [].slice.call(track.querySelectorAll('.v-car-s'));
  var dotsBox = document.getElementById('volDots');
  var count = document.getElementById('volCount');
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var DELAY = 4500;
  var timer = null, paused = false, index = 0;

  slides.forEach(function (s, i) {
    var d = document.createElement('button');
    d.type = 'button';
    d.className = 'v-car-d';
    d.setAttribute('aria-label', 'Photograph ' + (i + 1) + ' of ' + slides.length);
    d.addEventListener('click', function () { stop(); go(i); });
    dotsBox.appendChild(d);
  });
  var dots = [].slice.call(dotsBox.children);

  function go(i) {
    index = (i + slides.length) % slides.length;
    var s = slides[index];
    track.scrollTo({ left: s.offsetLeft - (track.clientWidth - s.clientWidth) / 2,
                     behavior: reduced ? 'auto' : 'smooth' });
    paint();
  }

  function nearest() {
    var mid = track.scrollLeft + track.clientWidth / 2, best = 0, bd = Infinity;
    slides.forEach(function (s, i) {
      var d = Math.abs(s.offsetLeft + s.clientWidth / 2 - mid);
      if (d < bd) { bd = d; best = i; }
    });
    return best;
  }

  function paint() {
    dots.forEach(function (d, i) { d.setAttribute('aria-current', i === index ? 'true' : 'false'); });
    slides.forEach(function (s, i) { s.setAttribute('aria-hidden', i === index ? 'false' : 'true'); });
    if (count) count.textContent = (index + 1) + ' / ' + slides.length;
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

  [].slice.call(document.querySelectorAll('.v-car-b')).forEach(function (b) {
    b.addEventListener('click', function () { stop(); go(index + (+b.dataset.dir)); });
  });

  track.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowRight') { stop(); go(index + 1); e.preventDefault(); }
    if (e.key === 'ArrowLeft') { stop(); go(index - 1); e.preventDefault(); }
  });

  paint();
  start();
})();
