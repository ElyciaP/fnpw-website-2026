/* Article reading bar. Lifted unchanged from the inline script at the foot of every
   static article-*.html page; one copy here instead of one per post. */
(function(){
  var art=document.querySelector('.ed'); if(!art)return;
  var bar=document.createElement('div'); bar.className='ed-prog'; document.body.appendChild(bar);
  var tick=function(){
    var r=art.getBoundingClientRect(), h=window.innerHeight;
    var total=r.height-h, done=Math.min(Math.max(-r.top,0),Math.max(total,1));
    bar.style.width=(total<=0?0:(done/total)*100)+'%';
  };
  tick(); addEventListener('scroll',tick,{passive:true}); addEventListener('resize',tick);
})();
