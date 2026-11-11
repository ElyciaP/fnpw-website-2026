/* Shared page script lifted unchanged from the static build by convert.py (5 pages, first: corporate-volunteering-nsw.html). */
(function () {
  var pins = [].slice.call(document.querySelectorAll('.vm-pin'));
  var list = document.querySelector('.vs-list');
  var cards = [].slice.call(document.querySelectorAll('.vs-card'));
  if (!pins.length || !list) return;

  function mark(i, on) {
    pins.forEach(function (p) { if (+p.dataset.i === i) p.classList.toggle('on', on); });
    cards.forEach(function (c) { if (+c.dataset.i === i) c.classList.toggle('on', on); });
  }
  function wire(el) {
    var i = +el.dataset.i;
    el.addEventListener('mouseenter', function () { mark(i, true); });
    el.addEventListener('mouseleave', function () { mark(i, false); });
    el.addEventListener('focus', function () { mark(i, true); });
    el.addEventListener('blur', function () { mark(i, false); });
  }
  pins.forEach(wire);
  cards.forEach(wire);

  // Tapping a pin brings its entry into view. That is the point of the map on a
  // phone, where the two are stacked rather than side by side.
  pins.forEach(function (p) {
    p.addEventListener('click', function () {
      var c = cards.filter(function (x) { return x.dataset.i === p.dataset.i; })[0];
      if (c) { c.scrollIntoView({ behavior: 'smooth', block: 'center' }); c.focus({ preventScroll: true }); }
    });
    p.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); p.click(); }
    });
  });

  // On a phone the map sits above the list, and a scrolling box inside a
  // scrolling page is horrible to use, so there the list shows four and expands.
  // On desktop it is a scroll panel matched to the map, and the fade at the
  // bottom edge switches off once you reach the end.
  var wrap = document.querySelector('.vs-listwrap');
  var more = document.getElementById('vsMore');
  var STEP = 4, expanded = false;
  var touchLayout = window.matchMedia('(max-width: 1000px)');

  // The map scales with the column, so the list is measured against it rather
  // than given a fixed height. Both columns then finish on the same line.
  var mapcol = document.querySelector('.vs-mapcol');
  function matchHeight() {
    if (!mapcol || touchLayout.matches) { list.style.maxHeight = ''; return; }
    var h = mapcol.getBoundingClientRect().bottom - list.getBoundingClientRect().top;
    list.style.maxHeight = Math.max(620, Math.round(h)) + 'px';   // never fewer than about four cards
  }

  function fade() {
    if (!wrap) return;
    var atEnd = list.scrollTop + list.clientHeight >= list.scrollHeight - 4;
    wrap.classList.toggle('at-end', atEnd || list.scrollHeight <= list.clientHeight + 4);
  }
  list.addEventListener('scroll', fade, { passive: true });
  window.addEventListener('resize', function () { matchHeight(); render(); });
  if (window.ResizeObserver && mapcol) new ResizeObserver(function () {
    matchHeight(); fade();
  }).observe(mapcol);

  var btns = [].slice.call(document.querySelectorAll('.vs-filter button'));
  var count = document.getElementById('vsCount');
  var sort = document.getElementById('vsSort');
  var empty = document.getElementById('vsEmpty');
  var filter = 'all';

  function render() {
    var shown = 0;
    cards.forEach(function (c) {
      var hit = (filter === 'all' || c.dataset.type === filter);
      c.hidden = !hit;
      if (hit) shown++;
      pins.forEach(function (p) {
        if (p.dataset.i === c.dataset.i) p.style.opacity = hit ? '' : '.15';
      });
    });
    var mode = sort ? sort.value : 'distance';
    cards.slice().sort(function (a, b) {
      if (mode === 'name') return a.dataset.name.localeCompare(b.dataset.name);
      if (mode === 'type') return a.dataset.type.localeCompare(b.dataset.type)
        || (+a.dataset.km) - (+b.dataset.km);
      return (+a.dataset.km) - (+b.dataset.km);
    }).forEach(function (c) { list.appendChild(c); });
    if (count) count.textContent = shown + (shown === 1 ? ' site' : ' sites');
    if (empty) empty.hidden = shown > 0;

    var capped = touchLayout.matches && !expanded && shown > STEP;
    var n = 0;
    cards.forEach(function (c) {
      if (c.hidden) return;
      n++;
      if (capped && n > STEP) c.hidden = true;
    });
    if (more) {
      more.classList.toggle('on', touchLayout.matches && shown > STEP);
      more.hidden = !(touchLayout.matches && shown > STEP);
      more.textContent = expanded ? 'Show fewer sites'
        : 'Show all ' + shown + (shown === 1 ? ' site' : ' sites');
    }
    matchHeight();
    fade();
  }

  if (more) more.addEventListener('click', function () { expanded = !expanded; render(); });

  btns.forEach(function (b) {
    b.addEventListener('click', function () {
      btns.forEach(function (x) { x.classList.remove('on'); });
      b.classList.add('on');
      filter = b.dataset.f;
      render();
    });
  });
  if (sort) sort.addEventListener('change', render);
  render();
})();
