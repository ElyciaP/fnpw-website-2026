/* Shared page script lifted unchanged from the static build by convert.py (3 pages, first: growing-national-parks.html). */
(function(){
  var grid=document.getElementById('pgrid');
  if(!grid)return;
  var meta=document.getElementById('fmeta');
  var chips=[].slice.call(document.querySelectorAll('#fps .fp'));
  var active='all';
  [].forEach.call(grid.querySelectorAll('.pc'),function(c){
    c.dataset.title=(c.querySelector('h3').textContent||'').trim();
  });
  function apply(){
    var c=0;
    [].forEach.call(grid.querySelectorAll('.pc'),function(x){
      var ok=(active==='all')||(x.dataset.state===active);
      x.style.display=ok?'':'none'; if(ok)c++;
    });
    meta.textContent='Showing '+c+' project'+(c===1?'':'s');
  }
  chips.forEach(function(b){b.addEventListener('click',function(){
    chips.forEach(function(p){p.classList.remove('on')});
    b.classList.add('on'); active=b.dataset.f; apply();
  })});
  var sel=document.getElementById('psort');
  if(sel)sel.addEventListener('change',function(e){
    var m=e.target.value;
    [].slice.call(grid.querySelectorAll('.pc')).sort(function(a,b){
      var r=a.dataset.title.localeCompare(b.dataset.title,'en',{numeric:true,sensitivity:'base'});
      return m==='za'?-r:r;
    }).forEach(function(c){grid.appendChild(c)});
  });
  apply();
})();
