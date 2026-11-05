document.documentElement.classList.add('js');
/* FNPW base script: mobile drawer, header shadow, scroll reveal, counters, dropdown/accordion nav.
   Loaded by every page. The WordPress theme (wp/themes/fnpw-2026/assets/js/main.js) mirrors this file. */
(function(){
  var doc=document,root=doc.documentElement;
  var reduce=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var mobile=window.matchMedia?window.matchMedia('(max-width:980px)'):{matches:false};
  var FOCUSABLE='a[href],button:not([disabled]),input:not([disabled]),select:not([disabled]),textarea:not([disabled]),[tabindex]:not([tabindex="-1"])';
  function visible(el){return !!(el.offsetWidth||el.offsetHeight||el.getClientRects().length)&&getComputedStyle(el).visibility!=='hidden'}

  /* ---- Mobile drawer (.nav under 980px, toggled by #mt) ---- */
  var mt=doc.getElementById('mt'),mn=doc.getElementById('mn'),bd=doc.getElementById('nav-bd');
  var drawerOpen=false;
  function firstLink(){var a=mn.querySelector('a[href],button');return a}
  function openDrawer(){
    if(drawerOpen)return;drawerOpen=true;
    mn.classList.add('open');mt.classList.add('open');mt.setAttribute('aria-expanded','true');
    doc.body.classList.add('nav-lock');if(bd)bd.hidden=false;
    var f=firstLink();if(f)requestAnimationFrame(function(){f.focus()});
  }
  function closeDrawer(returnFocus){
    if(!drawerOpen)return;drawerOpen=false;
    mn.classList.remove('open');mt.classList.remove('open');mt.setAttribute('aria-expanded','false');
    doc.body.classList.remove('nav-lock');if(bd)bd.hidden=true;
    if(returnFocus)mt.focus();
  }
  if(mt&&mn){
    mt.setAttribute('aria-expanded','false');
    mt.addEventListener('click',function(){drawerOpen?closeDrawer(true):openDrawer()});
    if(bd)bd.addEventListener('click',function(){closeDrawer(true)});
    mn.querySelectorAll('a').forEach(function(a){a.addEventListener('click',function(){closeDrawer(false)})});
    /* Tab stays inside the open drawer; the cycle is the close button (#mt) followed by the drawer's links. */
    doc.addEventListener('keydown',function(e){
      if(e.key!=='Tab'||!drawerOpen)return;
      var items=[mt].concat(Array.prototype.filter.call(mn.querySelectorAll(FOCUSABLE),visible));
      var first=items[0],last=items[items.length-1],cur=doc.activeElement,inside=items.indexOf(cur)>-1;
      if(e.shiftKey&&(cur===first||!inside)){e.preventDefault();last.focus()}
      else if(!e.shiftKey&&(cur===last||!inside)){e.preventDefault();first.focus()}
    });
    var onChange=function(){if(!mobile.matches)closeDrawer(false)};
    if(mobile.addEventListener)mobile.addEventListener('change',onChange);else if(mobile.addListener)mobile.addListener(onChange);
  }

  /* ---- Header shadow once scrolled ---- */
  var sh=doc.getElementById('hdr');
  if(sh)window.addEventListener('scroll',function(){sh.classList.toggle('scrolled',window.scrollY>30)},{passive:true});

  /* ---- Scroll reveal (.rv). CSS only hides .rv when html.js is present, so content shows without scripts. ---- */
  var rvs=doc.querySelectorAll('.rv');
  if(reduce||!('IntersectionObserver' in window)){rvs.forEach(function(el){el.classList.add('in')})}
  else{
    var io=new IntersectionObserver(function(es){es.forEach(function(x){if(x.isIntersecting){x.target.classList.add('in');io.unobserve(x.target)}})},{threshold:0.01,rootMargin:'0px 0px -40px 0px'});
    rvs.forEach(function(el){io.observe(el)});
  }

  /* ---- Counters ([data-count]). The HTML already holds the final formatted value (tools/fix_counters.py);
     the animation starts from 0 only when it runs, and is skipped under reduced motion. ---- */
  function fmt(el,v){
    var d=parseInt(el.dataset.dec||'0',10);
    return (el.dataset.pre||'')+v.toLocaleString('en-AU',{minimumFractionDigits:d,maximumFractionDigits:d})+(el.dataset.suf||'');
  }
  var counters=doc.querySelectorAll('[data-count]');
  if(counters.length&&!reduce&&'IntersectionObserver' in window){
    var ni=new IntersectionObserver(function(es){es.forEach(function(x){
      if(!x.isIntersecting)return;
      var el=x.target,t=parseFloat(el.dataset.count),dur=1500,st=performance.now();
      ni.unobserve(el);
      if(isNaN(t)){return}
      /* Hold the counter at its finished width while it rolls. Without this the
         number grows from "0", so anything beside or below it reflows on every
         frame (the Healing Our Land graphic on our-impact.html jumped as the
         row wrapped and unwrapped). The hold is released when the roll ends. */
      var inl=getComputedStyle(el).display==='inline',w=el.getBoundingClientRect().width;
      if(inl)el.style.display='inline-block';
      el.style.boxSizing='border-box';el.style.width=w+'px';el.style.whiteSpace='nowrap';
      el.textContent=fmt(el,0);
      (function step(now){
        var pr=Math.min(1,(now-st)/dur),ea=1-Math.pow(1-pr,3);
        el.textContent=fmt(el,pr<1?t*ea:t);
        if(pr<1)requestAnimationFrame(step);
        else{el.style.width='';el.style.whiteSpace='';el.style.boxSizing='';if(inl)el.style.display='';}
      })(st);
    })},{threshold:.4});
    counters.forEach(function(el){ni.observe(el)});
  }else{
    counters.forEach(function(el){var t=parseFloat(el.dataset.count);if(!isNaN(t))el.textContent=fmt(el,t)});
  }

  /* ---- Dropdowns (desktop: hover, focus-within and click; mobile drawer: accordions) ---- */
  var ngs=Array.prototype.slice.call(doc.querySelectorAll('.ng'));
  function setOpen(ng,open){
    ng.classList.toggle('open',open);
    var b=ng.querySelector(':scope > button');if(b)b.setAttribute('aria-expanded',open?'true':'false');
  }
  function closeAll(except){ngs.forEach(function(ng){if(ng!==except)setOpen(ng,false)})}
  ngs.forEach(function(ng){
    var btn=ng.querySelector(':scope > button'),dd=ng.querySelector('.dd');
    if(!btn||!dd)return;
    if(!btn.hasAttribute('aria-expanded'))btn.setAttribute('aria-expanded','false');
    if(dd.id&&!btn.hasAttribute('aria-controls'))btn.setAttribute('aria-controls',dd.id);
    btn.addEventListener('click',function(e){
      e.stopPropagation();
      ng.classList.remove('esc');
      var open=!ng.classList.contains('open');
      setOpen(ng,open);
      if(!mobile.matches)closeAll(ng);
    });
    btn.addEventListener('keydown',function(e){
      if(e.key==='ArrowDown'){
        e.preventDefault();ng.classList.remove('esc');setOpen(ng,true);if(!mobile.matches)closeAll(ng);
        var a=dd.querySelector('a');if(a)requestAnimationFrame(function(){a.focus()});
      }
    });
    ng.addEventListener('keydown',function(e){
      if(e.key!=='Escape'||mobile.matches)return;  /* in the drawer, Escape closes the drawer instead */
      e.stopPropagation();
      setOpen(ng,false);
      ng.classList.add('esc');  /* keeps :focus-within from re-opening the panel while the button holds focus */
      btn.focus();
    });
    ng.addEventListener('focusout',function(e){
      if(!ng.contains(e.relatedTarget))ng.classList.remove('esc');
    });
  });
  doc.addEventListener('click',function(){if(!mobile.matches)closeAll(null)});
  doc.addEventListener('keydown',function(e){
    if(e.key!=='Escape')return;
    if(drawerOpen){closeDrawer(true);return}
    closeAll(null);
  });
})();
