/* Shared page script lifted unchanged from the static build by convert.py (6 pages, first: volunteer.html). */
/* Corporate Volunteering enquiry form, HubSpot portal 441704788, region ap1.
   The state pages set window.FNPW_VOL_STATE before this runs, so the person
   arrives with their state already chosen. This form stays on the legacy v2
   embed because it renders the fields in this document, which is what lets the
   callback below pre-select the state and pair the fields up; the v3 embed
   renders in a cross-origin iframe and cannot. v2.js is deferred, so the set-up
   waits for DOMContentLoaded, when deferred scripts have run. Everything here is
   guarded in case the field is renamed or the script is blocked. */
document.addEventListener('DOMContentLoaded', function () {
  var slot = document.getElementById('hsform');
  if (!slot || typeof hbspt === 'undefined') { showFallback(); return; }
  var liveForm = null;

  function showFallback() {
    var f = document.getElementById('hsFallback');
    if (f) f.hidden = false;
  }

  /* Preferred Location is a combobox backed by a hidden input named "0-1/state",
     whose options are exactly our state codes. Writing to that hidden input is
     what actually posts. It has to go through the native value setter, because
     the form is React-rendered and a plain assignment is ignored. The visible
     control stays blank, which is why the field is left optional: anyone can
     still pick it themselves. */
  function applyState(form) {
    var code = window.FNPW_VOL_STATE;
    if (!form || !code) return;
    try {
      var doc = form.ownerDocument, win = doc.defaultView;
      var el = form.querySelector('input[name$="/state"], input[name="state"]');
      if (!el) return;
      var setter = Object.getOwnPropertyDescriptor(win.HTMLInputElement.prototype, 'value').set;
      setter.call(el, code);
      el.dispatchEvent(new win.Event('input', { bubbles: true }));
      el.dispatchEvent(new win.Event('change', { bubbles: true }));
    } catch (e) { /* HubSpot changed the form; the person picks the state themselves */ }
  }

  // lets the state tabs on this page update a form that has already rendered
  window.fnpwSetVolState = function (code, name) {
    window.FNPW_VOL_STATE = code;
    window.FNPW_VOL_STATE_NAME = name;
    applyState(liveForm);
  };


  /* HubSpot stacks every field, which made a ten field form a very long strip.
     The form renders into a same-origin iframe, so we can lay it out in two
     columns from here. Class names inside that iframe are HubSpot's and change
     without notice, so nothing below depends on them: we find the element that
     actually contains the field rows by walking up from the fields themselves,
     and anything we cannot read is left exactly as HubSpot rendered it. */
  function pairUpFields(form) {
    if (!form) return;
    try {
      var doc = form.ownerDocument;

      if (!doc.getElementById('fnpwFormGrid')) {
        var s = doc.createElement('style');
        s.id = 'fnpwFormGrid';
        s.textContent =
          '[data-fnpw-grid]{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));' +
          'column-gap:1.1rem;align-items:start}' +
          '[data-fnpw-grid] > [data-fnpw-wide]{grid-column:1/-1}' +
          '@media(max-width:620px){[data-fnpw-grid]{grid-template-columns:1fr}}' +
          'input[type=submit],button[type=submit],.hs-button{background:#C23747!important;' +
          'border:0!important;border-radius:0!important;color:#FAF6F2!important;' +
          'box-shadow:none!important;text-transform:none!important;letter-spacing:0!important}' +
          'input[type=submit]:hover,button[type=submit]:hover,.hs-button:hover{background:#8C1422!important}';
        (doc.head || doc.body).appendChild(s);
      }

      var ctrls = [].slice.call(form.querySelectorAll('input,select,textarea'))
        .filter(function (el) {
          return el.type !== 'hidden' && el.type !== 'submit' && el.type !== 'button' &&
                 el.offsetParent !== null;
        });
      if (ctrls.length < 4) return;   // too few to be worth pairing

      // the deepest element that contains every field: its children are the rows
      function chain(el) {
        var a = [];
        for (var n = el.parentElement; n; n = n.parentElement) {
          a.push(n);
          if (n === form) break;
        }
        return a;
      }
      var lists = ctrls.map(chain), box = null, first = lists[0];
      for (var i = 0; i < first.length; i++) {
        var cand = first[i];
        var all = lists.every(function (l) { return l.indexOf(cand) > -1; });
        if (all) { box = cand; break; }
      }
      if (!box || box.children.length < 4) return;

      [].slice.call(box.children).forEach(function (row) {
        // a row goes full width if it holds a textarea, the submit, the captcha,
        // or no field at all (consent text, error summaries, headings)
        var wide = !!row.querySelector('textarea,iframe,[type=submit],button') ||
                   !row.querySelector('input,select,textarea');
        if (wide) row.setAttribute('data-fnpw-wide', '');
        else row.removeAttribute('data-fnpw-wide');
      });
      box.setAttribute('data-fnpw-grid', '');

      // the embed sizes its own iframe, so tell it the height just changed
      try { (doc.defaultView || window).dispatchEvent(new Event('resize')); } catch (e) {}
    } catch (e) { /* HubSpot changed the form: leave it as rendered */ }
  }

  hbspt.forms.create({
    region: 'ap1',
    portalId: '441704788',
    formId: '5275a663-85fc-43d4-8400-b17d34ece7fa',
    target: '#hsform',
    onFormReady: function (form) {
      liveForm = (form && form.querySelector) ? form : (form && form[0]);
      applyState(liveForm);
      pairUpFields(liveForm);
      // the form re-renders on validation and on step changes, so re-apply
      [250, 900, 2500].forEach(function (ms) {
        setTimeout(function () { pairUpFields(liveForm); }, ms);
      });
      try {
        var mo = new MutationObserver(function () { pairUpFields(liveForm); });
        mo.observe(liveForm, { childList: true, subtree: true });
        setTimeout(function () { mo.disconnect(); }, 20000);
      } catch (e) {}
    }
  });

  setTimeout(function () {
    if (!slot.querySelector('iframe, form')) showFallback();
  }, 8000);
});
