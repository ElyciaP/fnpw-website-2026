const mt=document.getElementById('mt'),mn=document.getElementById('mn');
if(mt&&mn){mt.addEventListener('click',()=>{mn.classList.toggle('open');mt.setAttribute('aria-expanded',mn.classList.contains('open'))}); mn.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>mn.classList.remove('open')))}
const sh=document.getElementById('hdr');if(sh)window.addEventListener('scroll',()=>sh.classList.toggle('scrolled',window.scrollY>30),{passive:true});
const io=new IntersectionObserver(e=>{e.forEach(x=>{if(x.isIntersecting){x.target.classList.add('in');io.unobserve(x.target)}})},{threshold:.12,rootMargin:'0px 0px -50px 0px'});
document.querySelectorAll('.rv').forEach(el=>io.observe(el));
const ni=new IntersectionObserver(e=>{e.forEach(x=>{if(!x.isIntersecting)return;const el=x.target;const t=parseFloat(el.dataset.count);const d=parseInt(el.dataset.dec||'0');const s=el.dataset.suf||'';const p=el.dataset.pre||'';const dur=1500;const st=performance.now();function step(now){const pr=Math.min(1,(now-st)/dur);const ea=1-Math.pow(1-pr,3);const v=t*ea;el.textContent=p+v.toLocaleString('en-AU',{minimumFractionDigits:d,maximumFractionDigits:d})+s;if(pr<1)requestAnimationFrame(step);else el.textContent=p+t.toLocaleString('en-AU',{minimumFractionDigits:d,maximumFractionDigits:d})+s}requestAnimationFrame(step);ni.unobserve(x.target)})},{threshold:.4});
document.querySelectorAll('[data-count]').forEach(el=>ni.observe(el));
(function(){
  var ngs=document.querySelectorAll('.ng');
  ngs.forEach(function(ng){
    var btn=ng.querySelector('button');
    if(!btn)return;
    btn.setAttribute('aria-haspopup','true');
    btn.setAttribute('aria-expanded','false');
    btn.addEventListener('click',function(e){
      e.stopPropagation();
      var open=ng.classList.toggle('open');
      btn.setAttribute('aria-expanded',open?'true':'false');
      ngs.forEach(function(other){if(other!==ng)other.classList.remove('open')});
    });
  });
  document.addEventListener('click',function(){
    ngs.forEach(function(ng){
      ng.classList.remove('open');
      var b=ng.querySelector('button');if(b)b.setAttribute('aria-expanded','false');
    });
  });
  // Escape closes
  document.addEventListener('keydown',function(e){
    if(e.key==='Escape')ngs.forEach(function(ng){ng.classList.remove('open')});
  });
})();

(function(){
  var ngs=document.querySelectorAll('.ng');
  ngs.forEach(function(ng){
    var btn=ng.querySelector('button');
    if(!btn)return;
    btn.setAttribute('aria-haspopup','true');
    btn.setAttribute('aria-expanded','false');
    btn.addEventListener('click',function(e){
      e.stopPropagation();
      var open=ng.classList.toggle('open');
      btn.setAttribute('aria-expanded',open?'true':'false');
      ngs.forEach(function(other){if(other!==ng)other.classList.remove('open')});
    });
  });
  document.addEventListener('click',function(){
    ngs.forEach(function(ng){
      ng.classList.remove('open');
      var b=ng.querySelector('button');if(b)b.setAttribute('aria-expanded','false');
    });
  });
  // Escape closes
  document.addEventListener('keydown',function(e){
    if(e.key==='Escape')ngs.forEach(function(ng){ng.classList.remove('open')});
  });
})();
<!-- ng-click-toggle-installed -->
