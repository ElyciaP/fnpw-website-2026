/* FNPW import: runs a dry run, an import or a restore-all in batches over admin-ajax. */
(function () {
  var cfg = window.FNPW_MIGRATE;
  if (!cfg) return;
  var $ = function (id) { return document.getElementById(id); };
  var busy = false;

  function post(data) {
    var body = new URLSearchParams();
    body.append('action', 'fnpw_migrate_batch');
    body.append('nonce', cfg.nonce);
    Object.keys(data).forEach(function (k) { body.append(k, data[k]); });
    return fetch(cfg.ajax, { method: 'POST', credentials: 'same-origin', body: body })
      .then(function (r) { return r.text().then(function (t) {
        try { return JSON.parse(t); } catch (e) { throw new Error('The server answered with something that is not JSON (HTTP ' + r.status + '): ' + t.slice(0, 200)); }
      }); });
  }

  function ensureTable() {
    var t = $('fnpw-results');
    if (t) return t;
    var wrap = $('fnpw-migrate');
    var d = document.createElement('div');
    d.innerHTML = '<div id="fnpw-progress"><progress id="fnpw-bar" max="100" value="0" style="width:100%;max-width:640px;height:1.4em"></progress><p id="fnpw-status" aria-live="polite"></p></div><div id="fnpw-summary"></div><table class="widefat striped" id="fnpw-results"><thead><tr><th>Item</th><th>Action</th><th>Post</th><th>Detail</th></tr></thead><tbody></tbody></table>';
    wrap.appendChild(d);
    return $('fnpw-results');
  }

  function addRows(rows) {
    var tb = ensureTable().querySelector('tbody');
    rows.forEach(function (r) {
      var tr = document.createElement('tr');
      tr.dataset.action = r.action;
      [r.key, r.action, r.post_id ? String(r.post_id) : '', r.message].forEach(function (v, i) {
        var td = document.createElement('td');
        if (i === 2 && r.post_id && r.action.indexOf('media') !== 0) {
          var a = document.createElement('a'); a.href = cfg.edit + r.post_id; a.textContent = v; td.appendChild(a);
        } else { td.textContent = v; }
        if (i === 0) td.style.wordBreak = 'break-all';
        tr.appendChild(td);
      });
      tb.appendChild(tr);
    });
  }

  function run(mode, startPhase) {
    if (busy) return;
    busy = true;
    var counts = {};
    var table = ensureTable();
    table.hidden = false;
    table.querySelector('tbody').innerHTML = '';
    $('fnpw-progress').hidden = false;
    if ($('fnpw-filter')) $('fnpw-filter').hidden = false;
    $('fnpw-summary').innerHTML = '';
    ['fnpw-dry', 'fnpw-apply', 'fnpw-restore-all'].forEach(function (id) { if ($(id)) $(id).disabled = true; });
    var fetchBase = $('fnpw-fetch') ? $('fnpw-fetch').value.trim() : '';
    var reading = $('fnpw-reading') && $('fnpw-reading').checked ? '1' : '0';
    var label = mode === 'apply' ? 'Importing' : (mode === 'restore' ? 'Restoring' : 'Dry run');

    function step(phase, offset, runId) {
      return post({ mode: mode === 'restore' ? 'apply' : mode, phase: phase, offset: offset, run: runId, fetch_base: fetchBase, set_reading: reading })
        .then(function (res) {
          if (!res || !res.success) throw new Error(res && res.data && res.data.message ? res.data.message : 'The request failed.');
          var d = res.data;
          addRows(d.rows || []);
          (d.rows || []).forEach(function (r) { counts[r.action] = (counts[r.action] || 0) + 1; });
          if (d.total) {
            var at = d.at || d.offset || 0;
            $('fnpw-bar').value = Math.round(100 * at / d.total);
            $('fnpw-status').textContent = label + ': ' + (d.label || phase) + ' ' + at + ' of ' + d.total;
          }
          if (d.done) return d;
          return step(d.phase, d.offset, d.run);
        });
    }

    step(startPhase, 0, '').then(function (d) {
      $('fnpw-bar').value = 100;
      $('fnpw-status').textContent = label + ' finished. Run ' + d.run + '.';
      var parts = Object.keys(counts).sort().map(function (k) { return k + ': ' + counts[k]; });
      var p = document.createElement('p');
      p.id = 'fnpw-totals';
      p.dataset.counts = JSON.stringify(counts);
      p.dataset.mode = mode;
      p.innerHTML = '<strong>' + (mode === 'dry' ? 'Dry run, nothing was changed. ' : '') + '</strong>';
      p.appendChild(document.createTextNode(parts.join(' · ')));
      $('fnpw-summary').appendChild(p);
    }).catch(function (e) {
      var p = document.createElement('div');
      p.className = 'notice notice-error';
      p.id = 'fnpw-error';
      p.innerHTML = '<p></p>';
      p.firstChild.textContent = 'Stopped: ' + e.message + ' Rows above this point were processed; running again continues safely (finished items are skipped).';
      $('fnpw-summary').appendChild(p);
    }).then(function () {
      busy = false;
      ['fnpw-dry', 'fnpw-apply', 'fnpw-restore-all'].forEach(function (id) { if ($(id)) $(id).disabled = false; });
    });
  }

  if ($('fnpw-dry')) $('fnpw-dry').addEventListener('click', function () { run('dry', 'media'); });
  if ($('fnpw-apply')) $('fnpw-apply').addEventListener('click', function () {
    var msg = 'Apply the import to this site now?';
    if ($('fnpw-reading') && $('fnpw-reading').checked) msg += '\n\nThe front page and posts page in Settings > Reading will also be set.';
    if (window.confirm(msg)) run('apply', 'media');
  });
  if ($('fnpw-restore-all')) $('fnpw-restore-all').addEventListener('click', function () {
    if (window.confirm('Put the pre-import content back on every post that has a saved copy?')) run('restore', 'restore');
  });
  if ($('fnpw-hide-skip')) $('fnpw-hide-skip').addEventListener('change', function (e) {
    var t = $('fnpw-results'); if (!t) return;
    t.querySelectorAll('tr[data-action="skip"], tr[data-action="media-leave"]').forEach(function (tr) { tr.hidden = e.target.checked; });
  });
})();
