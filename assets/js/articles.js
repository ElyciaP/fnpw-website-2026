/* Stories page: pillar filter, sort and paging, in one controller.
   There are now 160+ tiles, so the page shows a batch at a time. Filter and
   sort both reset the batch, and the count line says where you are. */
(function () {
  var grid = document.querySelector('.art-grid');
  if (!grid) return;

  var cards = [].slice.call(grid.querySelectorAll('.art'));
  var M = { jan: 0, feb: 1, mar: 2, apr: 3, may: 4, jun: 5, jul: 6, aug: 7, sep: 8, oct: 9, nov: 10, dec: 11 };

  cards.forEach(function (a) {
    var h = a.querySelector('h3');
    a.dataset.title = h ? h.textContent.trim() : '';
    var d = a.querySelector('.art-date');
    var p = d ? d.textContent.split('·')[0].trim().split(/\s+/) : [];
    var ts = 0, mo;
    if (p.length >= 3) {                       // 08 May 2026
      mo = M[(p[1] || '').slice(0, 3).toLowerCase()];
      ts = new Date(+p[2], mo || 0, +p[0]).getTime();
    } else if (p.length === 2) {               // May 2026
      mo = M[(p[0] || '').slice(0, 3).toLowerCase()];
      ts = new Date(+p[1], mo || 0, 1).getTime();
    }
    a.dataset.ts = isNaN(ts) ? 0 : ts;
    var c = a.querySelector('.cat');
    var t = (c ? c.textContent : '').toLowerCase();
    a.dataset.k = t.indexOf('park') > -1 ? 'parks'
      : t.indexOf('species') > -1 ? 'species'
        : (t.indexOf('heal') > -1 || t.indexOf('land') > -1) ? 'heal' : 'news';
  });

  var STEP = 24, shown = STEP, filter = 'all', order = 'recent';
  var btn = document.getElementById('moreart');
  var count = document.getElementById('artcount');

  function render() {
    var list = cards.filter(function (a) { return filter === 'all' || a.dataset.k === filter; });
    list.sort(function (a, b) {
      if (order === 'az') return a.dataset.title.localeCompare(b.dataset.title, 'en', { numeric: true, sensitivity: 'base' });
      if (order === 'oldest') return (+a.dataset.ts) - (+b.dataset.ts);
      return (+b.dataset.ts) - (+a.dataset.ts);
    });
    cards.forEach(function (a) { a.style.display = 'none'; });
    list.slice(0, shown).forEach(function (a) { a.style.display = ''; grid.appendChild(a); });
    if (count) count.textContent = Math.min(shown, list.length) + ' of ' + list.length + ' stories';
    if (btn) btn.style.display = shown >= list.length ? 'none' : '';
  }

  document.querySelectorAll('.fp').forEach(function (b) {
    b.addEventListener('click', function () {
      document.querySelectorAll('.fp').forEach(function (x) { x.classList.remove('on'); });
      b.classList.add('on');
      filter = b.dataset.f;
      shown = STEP;
      render();
    });
  });

  var sel = document.getElementById('asort');
  if (sel) sel.addEventListener('change', function (e) { order = e.target.value; render(); });
  if (btn) btn.addEventListener('click', function () { shown += STEP; render(); });

  render();
})();
