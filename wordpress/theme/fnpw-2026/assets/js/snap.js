/*
 * Section snap (Oct 2026)
 * A gentle, one-direction settle onto the next section edge once scrolling has fully stopped.
 * - Waits for scroll (and trackpad momentum) to end, so it never fights the reader.
 * - Only moves in the direction the reader was already scrolling. Never pulls back.
 * - Only acts when a section edge is within the top 30% of the screen, so long sections can be read mid-way.
 * - Any wheel, touch, click or key press cancels the glide. Anchor links are left alone.
 * - Desktop with a pointer only; off for prefers-reduced-motion.
 * Opt in per page by loading this script. Snap points are the top edges of main > section.
 */
(function () {
  var mq = window.matchMedia('(min-width:1024px) and (hover:hover) and (prefers-reduced-motion:no-preference)');
  var ZONE = 0.3;
  var lastY = window.scrollY, dir = 0, anim = null, skip = false, timer = null;
  var hasScrollEnd = 'onscrollend' in window;

  function headerH() {
    var h = document.querySelector('header.hdr');
    return h ? h.getBoundingClientRect().height : 0;
  }
  function points() {
    var off = window.scrollY - headerH();
    return Array.prototype.map.call(document.querySelectorAll('main > section'), function (s) {
      return Math.round(s.getBoundingClientRect().top + off);
    });
  }
  function ease(x) { return 1 - Math.pow(1 - x, 3); }
  function cancel() { if (anim) { cancelAnimationFrame(anim); anim = null; } }

  function glide(to) {
    var from = window.scrollY, dist = to - from;
    if (Math.abs(dist) < 2) return;
    var dur = Math.min(650, Math.max(320, Math.abs(dist) * 1.6)), start = performance.now();
    function step(now) {
      var p = Math.min(1, (now - start) / dur);
      window.scrollTo({ top: from + dist * ease(p), behavior: 'instant' });
      if (p < 1) { anim = requestAnimationFrame(step); } else { anim = null; skip = true; }
    }
    anim = requestAnimationFrame(step);
  }

  function settle() {
    if (!mq.matches || anim) return;
    if (skip) { skip = false; return; }
    var y = window.scrollY, vh = window.innerHeight - headerH(), pts = points(), target = null, i;
    if (dir > 0) {
      for (i = 0; i < pts.length; i++) { if (pts[i] > y + 1 && pts[i] - y <= vh * ZONE) { target = pts[i]; break; } }
    } else if (dir < 0) {
      for (i = pts.length - 1; i >= 0; i--) { if (pts[i] < y - 1 && y - pts[i] <= vh * ZONE) { target = pts[i]; break; } }
    }
    if (target !== null) glide(target);
  }

  window.addEventListener('scroll', function () {
    var y = window.scrollY;
    if (!anim && y !== lastY) dir = y > lastY ? 1 : -1;
    lastY = y;
    if (!hasScrollEnd) { clearTimeout(timer); timer = setTimeout(settle, 140); }
  }, { passive: true });
  if (hasScrollEnd) window.addEventListener('scrollend', settle);
  ['wheel', 'touchstart', 'keydown', 'mousedown'].forEach(function (ev) {
    window.addEventListener(ev, cancel, { passive: true });
  });
  document.addEventListener('click', function (e) {
    if (e.target.closest && e.target.closest('a[href*="#"]')) skip = true;
  }, true);
})();
