/* Project map (fnpw/project-map).
   The pin popup is the inline map script from the static projects.html, unchanged apart
   from two things: the project link and thumbnail come from the pin data (IMAP, printed
   by render.php) instead of being built from the static file name, and the state picker
   under the map (phones) is handled here so the block works on its own.

   The state picker filters a project list when one is on the page (#pgrid .pc tiles with
   data-state, as on the static projects page) and always announces the choice with a
   "fnpw:project-state" event on document, for the project grid block to listen to. */
(function(){
  var IMAP=window.IMAP||[];
  var pop=document.getElementById('imPop');if(!pop)return;
  var box=pop.parentNode;
  var current=null;
  var reduce=window.matchMedia('(prefers-reduced-motion:reduce)');
  function show(i,pin){
    var p=IMAP[i];if(!p)return;
    document.getElementById('imChip').textContent=p.pl;
    document.getElementById('imChip').className='im-chip '+p.pc.replace('pb-','pc-');
    document.getElementById('imTitle').textContent=p.t;
    document.getElementById('imState').textContent=p.st;
    document.getElementById('imGo').href=p.l;
    var th=document.getElementById('imThumb');
    var src=p.img||'';
    if(!src){
      /* same fallback as the static page: borrow the image from the project's tile */
      var links=document.querySelectorAll('.pc-link');
      for(var k=0;k<links.length;k++){
        if(links[k].href===p.l||links[k].getAttribute('href')===p.l){
          var im=links[k].querySelector('img');if(im)src=im.currentSrc||im.getAttribute('src')||'';
          break;
        }
      }
    }
    if(src){th.src=src;th.alt=p.t;th.hidden=false;}
    else{th.removeAttribute('src');th.alt='';th.hidden=true;}
    pop.hidden=false;
    place(pin);
    document.querySelectorAll('.im-pin.on').forEach(function(q){q.classList.remove('on')});
    pin.classList.add('on');
    pin.setAttribute('aria-expanded','true');
    current=pin;
    /* a proper dialog: focus moves to its heading; Close / Escape send it back to the pin */
    document.getElementById('imTitle').focus({preventScroll:true});
    if(window.innerWidth<700){pop.scrollIntoView({behavior:reduce.matches?'auto':'smooth',block:'nearest'});}
  }
  function hide(returnFocus){
    if(pop.hidden)return;
    pop.hidden=true;
    var pin=current;current=null;
    document.querySelectorAll('.im-pin.on').forEach(function(q){q.classList.remove('on');q.removeAttribute('aria-expanded')});
    if(returnFocus&&pin)pin.focus();
  }
  /* keep the card inside the map: flip sides near the right edge, sit it
     off the bottom edge rather than over the legend, and shrink the image
     if the map is shorter than the card (small screens) */
  function place(pin){
    var wrap=pop.parentNode,pad=10;
    var cw=wrap.clientWidth,ch=wrap.clientHeight;
    var px=parseFloat(pin.style.left)/100*cw,py=parseFloat(pin.style.top)/100*ch;
    var th=document.getElementById('imThumb');
    th.style.height='';
    var pw=pop.offsetWidth,phh=pop.offsetHeight;
    if(!th.hidden&&phh>ch-pad*2){
      th.style.height=Math.max(60,th.offsetHeight-(phh-(ch-pad*2)))+'px';
      phh=pop.offsetHeight;
    }
    var left=px+16;
    if(left+pw>cw-pad)left=px-pw-16;
    if(left<pad)left=Math.max(pad,(cw-pw)/2);
    var top=py-24;
    if(top+phh>ch-pad)top=ch-phh-pad;
    if(top<pad)top=pad;
    pop.style.left=left+'px';
    pop.style.top=top+'px';
  }
  document.querySelectorAll('.im-pin').forEach(function(b){
    b.setAttribute('aria-haspopup','dialog');
    b.setAttribute('aria-controls','imPop');
    b.addEventListener('click',function(e){e.stopPropagation();show(parseInt(b.dataset.i,10),b)});
  });
  document.getElementById('imX').addEventListener('click',function(){hide(true)});
  document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!pop.hidden){e.preventDefault();hide(true)}});
  document.addEventListener('click',function(e){if(!box.contains(e.target))hide(false)});
  window.addEventListener('resize',function(){if(current&&!pop.hidden)place(current)});

  /* ---- state picker (phones) ---- */
  var states=document.getElementById('imStates');
  if(!states)return;
  var meta=document.getElementById('imStMeta');
  var STATE_NAME={NSW:'New South Wales',VIC:'Victoria',QLD:'Queensland',SA:'South Australia',WA:'Western Australia',TAS:'Tasmania',NT:'the Northern Territory',ACT:'the ACT',Australia:'Australia-wide programs'};
  var state='all';
  function setState(st){
    state=st;
    states.querySelectorAll('.im-st').forEach(function(b){
      var on=b.dataset.st===st;b.classList.toggle('on',on);b.setAttribute('aria-pressed',on?'true':'false');
    });
    var c=0;
    IMAP.forEach(function(p){if(st==='all'||p.st===st)c++});
    /* If the page's own project-list script (static projects page markup) is running it
       owns the tiles and the count line; it listens to the same buttons. */
    var ownsList=!!document.getElementById('fmeta');
    if(!ownsList){
      var tiles=document.querySelectorAll('#pgrid .pc[data-state]');
      if(tiles.length){
        c=0;
        tiles.forEach(function(x){var ok=st==='all'||x.dataset.state===st;x.style.display=ok?'':'none';if(ok)c++});
      }
      if(meta){
        meta.textContent='';
        if(st!=='all'){
          meta.appendChild(document.createTextNode(c+' project'+(c===1?'':'s')+' in '+(STATE_NAME[st]||st)+'. '));
          var list=document.getElementById('projectsGrid')||document.getElementById('pgrid');
          if(list&&list.id){var a=document.createElement('a');a.href='#'+list.id;a.textContent='Jump to the list';meta.appendChild(a)}
        }
      }
    }
    document.dispatchEvent(new CustomEvent('fnpw:project-state',{detail:{state:st,count:c}}));
  }
  states.querySelectorAll('.im-st').forEach(function(b){b.addEventListener('click',function(){setState(b.dataset.st)})});
  /* the picker is only shown under 700px; past that, drop the state filter so no hidden control stays applied */
  var mq=window.matchMedia('(min-width:700px)');
  var onMq=function(e){if(e.matches&&state!=='all')setState('all')};
  if(mq.addEventListener)mq.addEventListener('change',onMq);else if(mq.addListener)mq.addListener(onMq);
})();
