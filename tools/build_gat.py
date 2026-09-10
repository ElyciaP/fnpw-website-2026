"""Build gift-a-tree.html, the Give a Tree page.

Follows Mali's EOY2026 wireframe: hero with the Raisely donate form embedded,
a certificate pitch, a succinct How it works band, a removable seasonal band,
a corporate block, an in-memory block and the FAQ.

The campaign is branded "Give a Tree"; the filename stays gift-a-tree.html so
existing links keep working.

Header and footer come from partials/, wrapped in the @header / @footer markers
that tools/sync.py looks for, so this page stays in step with every other page.

    python3 tools/build_gat.py
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
OUT = 'gift-a-tree.html'
NL = chr(10)

header = ('<!-- @header -->' + open('partials/header.html', encoding='utf-8').read().rstrip()
          + '<!-- /@header -->')
footer = ('<!-- @footer -->' + open('partials/footer.html', encoding='utf-8').read().rstrip()
          + '<!-- /@footer -->')

# The nav dropdowns are not in main.js, so every page carries this small block.
navjs = """(function(){
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
  document.addEventListener('keydown',function(e){
    if(e.key==='Escape')ngs.forEach(function(ng){ng.classList.remove('open')});
  });
})();"""

HEAD = '''<!DOCTYPE html>
<html lang="en-AU">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="referrer" content="no-referrer">
<title>Give a Tree | Foundation for National Parks &amp; Wildlife</title>
<meta name="description" content="Give a Tree and help bring back the bush. Every tree is a native species, planted in Australia&rsquo;s priority landscapes, and every gift comes with a personalised certificate.">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://gift-a-tree.raiselysite.com">
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800&family=Figtree:wght@300;400;500;600;700&family=Caveat:wght@400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/global.css">

<style>
/* ============================================================
   GIVE A TREE
   Every section uses var(--sec-y) top and bottom, so the vertical
   rhythm matches the rest of the site exactly.
   ============================================================ */

/* ---- Hero: photo behind, copy left, Raisely form right ---- */
.gt-hero{position:relative;overflow:hidden;background:var(--euc-deep);isolation:isolate}
.gt-hero-bg{position:absolute;inset:0;z-index:-2}
.gt-hero-bg img{width:100%;height:100%;object-fit:cover;object-position:center 42%}
.gt-hero-bg::after{content:"";position:absolute;inset:0;z-index:1;
  background:linear-gradient(100deg,rgba(15,49,50,.92) 0%,rgba(15,49,50,.78) 46%,rgba(15,49,50,.42) 100%)}
.gt-hero > .cw{position:relative;z-index:2;padding-top:var(--sec-y);padding-bottom:var(--sec-y)}
.gt-hero-g{display:grid;grid-template-columns:1fr minmax(330px,25rem);gap:3.5rem;align-items:center}
@media(max-width:1000px){.gt-hero-g{grid-template-columns:1fr;gap:2.4rem}}

.gt-crumb{display:flex;gap:.5em;font-size:.82rem;color:rgba(250,246,242,.72);margin-bottom:1.4rem;flex-wrap:wrap}
.gt-crumb a{color:var(--euc-soft)}
.gt-hero .ey{color:var(--wattle)}
.gt-hero .ey::before{background:var(--wattle)}
.gt-hero h1{color:var(--cream);font-size:clamp(2rem,4.2vw,3.3rem);font-weight:600;line-height:1.04;
  letter-spacing:-.028em;max-width:18ch;margin:1rem 0 0}
.gt-hero h1 em{font-style:normal;color:var(--euc-soft)}
.gt-hero .lede{color:rgba(250,246,242,.88);margin-top:1.3rem;max-width:46ch;font-size:1.05rem;line-height:1.6}
.gt-tiers{display:flex;flex-wrap:wrap;gap:.5rem;margin-top:1.6rem;padding:0;list-style:none}
.gt-tiers li{font-size:.82rem;font-weight:600;letter-spacing:.02em;color:var(--euc-deep);
  background:var(--euc-soft);padding:.5em .9em}
.gt-tiers li b{font-family:var(--ff-d);font-weight:800}
.gt-native{margin-top:1.3rem;font-size:.86rem;color:var(--euc-soft);font-weight:600;max-width:40ch;line-height:1.5}

/* ---- The embedded Raisely form ---- */
.gt-form{scroll-margin-top:96px;background:var(--white);border:1px solid var(--rule);box-shadow:0 30px 70px -34px rgba(15,49,50,.55)}
.gt-form-head{padding:1.5rem 1.6rem 1.1rem;border-bottom:1px solid var(--rule)}
.gt-form-head h2{font-size:1.25rem;color:var(--euc-deep);margin:0}
.gt-form-head p{margin:.5rem 0 0;font-size:.86rem;line-height:1.55;color:var(--stone)}
.gt-form-frame{display:block;width:100%;height:760px;border:0;background:var(--white)}
@media(max-width:600px){.gt-form-frame{height:880px}}
.gt-form-fb{margin:0;padding:.9rem 1.6rem 1.1rem;border-top:1px solid var(--rule);
  font-size:.8rem;color:var(--stone);line-height:1.5;background:var(--cream)}
.gt-form-fb a{color:var(--euc-deep);font-weight:700;border-bottom:1px solid currentColor}

/* ---- Proof band ---- */
.gt-stats{padding:var(--sec-y) 0;background:var(--euc-deep);color:var(--cream)}
.gt-stats-g{display:grid;grid-template-columns:repeat(4,1fr);gap:2.5rem;text-align:center}
@media(max-width:760px){.gt-stats-g{grid-template-columns:repeat(2,1fr);gap:2rem}}
.gt-stat .n{font-family:var(--ff-d);font-weight:800;font-size:clamp(2rem,4vw,3.1rem);line-height:1;
  color:var(--wattle);letter-spacing:-.03em;display:block;margin-bottom:.5rem}
.gt-stat .l{font-size:.82rem;color:rgba(250,246,242,.8);letter-spacing:.04em;line-height:1.4;
  max-width:22ch;margin:0 auto}

/* ---- Two-up text and picture rows ---- */
.gt-split{padding:var(--sec-y) 0}
.gt-split.white{background:var(--white)}
.gt-split-g{display:grid;grid-template-columns:1fr 1fr;gap:4rem;align-items:center}
@media(max-width:900px){.gt-split-g{grid-template-columns:1fr;gap:2.4rem}}
.gt-split-g.flip .gt-split-im{order:2}
@media(max-width:900px){.gt-split-g.flip .gt-split-im{order:0}}
.gt-split-im{aspect-ratio:4/3;overflow:hidden;background:var(--paper)}
.gt-split-im img{width:100%;height:100%;object-fit:cover}
.gt-split h2{font-size:clamp(1.6rem,2.5vw,2.2rem);margin:.9rem 0 1.1rem;max-width:20ch}
.gt-split p{font-size:1.02rem;line-height:1.68;margin:0 0 1.1rem;max-width:52ch}
.gt-split p:last-of-type{margin-bottom:0}
.gt-split .lead-out{font-weight:700;color:var(--euc-deep)}
.gt-cta{display:inline-flex;align-items:center;gap:.6em;margin-top:1.8rem;padding:1em 1.9em;
  background:var(--waratah);color:var(--cream);font-weight:700;font-size:.82rem;letter-spacing:.14em;
  text-transform:uppercase;border:1.5px solid var(--waratah);transition:.25s}
.gt-cta:hover{background:var(--waratah-dk);border-color:var(--waratah-dk);color:var(--cream);opacity:1;
  transform:translateY(-2px)}
.gt-cta.on-dark{background:var(--cream);border-color:var(--cream);color:var(--euc-deep)}
.gt-cta.on-dark:hover{background:var(--white);border-color:var(--white);color:var(--euc-deep)}
.gt-cta.solid{background:var(--euc-deep);border-color:var(--euc-deep)}
.gt-cta.solid:hover{background:var(--euc);border-color:var(--euc)}

/* ---- How it works ---- */
.gt-how{padding:var(--sec-y) 0;background:var(--euc);color:var(--cream)}
.gt-how .head{text-align:center;max-width:44ch;margin:0 auto 2.6rem}
.gt-how h2{color:var(--cream);font-size:clamp(1.7rem,2.6vw,2.3rem);margin:0}
.gt-how .ey{color:var(--cream)}
.gt-how .ey::before{background:var(--cream)}
.gt-how-g{display:grid;grid-template-columns:repeat(4,1fr);gap:2rem}
@media(max-width:900px){.gt-how-g{grid-template-columns:repeat(2,1fr);gap:2.2rem}}
@media(max-width:520px){.gt-how-g{grid-template-columns:1fr}}
.gt-step{text-align:center}
.gt-step .n{display:inline-flex;align-items:center;justify-content:center;width:44px;height:44px;
  border:1.5px solid var(--cream);color:var(--cream);font-family:var(--ff-d);font-weight:700;
  font-size:.95rem;margin-bottom:1.1rem}
.gt-step h3{color:var(--cream);font-size:1.06rem;margin:0 0 .55rem}
.gt-step p{color:rgba(250,246,242,.9);font-size:.92rem;line-height:1.6;margin:0;max-width:26ch;
  margin-left:auto;margin-right:auto}
.gt-how-note{margin:2.6rem auto 0;max-width:72ch;text-align:center;font-size:.88rem;line-height:1.65;
  color:rgba(250,246,242,.9);border-top:1px solid rgba(250,246,242,.28);padding-top:1.6rem}
.gt-how-note a{color:var(--cream);font-weight:700;border-bottom:1px solid currentColor}
.gt-how-note em{font-style:italic}

/* ---- Seasonal band (swap or delete the whole section) ---- */
.gt-season{padding:var(--sec-y) 0;background:var(--waratah);color:var(--cream)}
.gt-season h2{color:var(--cream);font-size:clamp(1.6rem,2.5vw,2.2rem);margin:.9rem 0 1.1rem;max-width:18ch}
.gt-season .ey{color:var(--cream)}
.gt-season .ey::before{background:var(--cream)}
.gt-season p{color:rgba(250,246,242,.94);font-size:1.02rem;line-height:1.68;margin:0 0 1.1rem;max-width:50ch}
.gt-season .lead-out{color:var(--cream);font-weight:700}
.gt-season-im{background:var(--euc);display:flex;align-items:flex-end;justify-content:center;aspect-ratio:4/3;overflow:hidden}
.gt-season-im img{width:auto;max-width:100%;height:100%;margin-inline:auto;object-fit:contain}

/* ---- In memory ---- */
.gt-memory{padding:var(--sec-y) 0;background:var(--euc-soft)}
.gt-memory h2,.gt-memory p,.gt-memory .ey{color:var(--euc-deep)}
.gt-memory .ey::before{background:var(--euc-deep)}
.gt-memory h2{font-size:clamp(1.6rem,2.5vw,2.2rem);margin:.9rem 0 1.1rem;max-width:18ch}
.gt-memory p{font-size:1.02rem;line-height:1.68;margin:0 0 1.1rem;max-width:50ch}

/* ---- Contact strip inside the corporate block ---- */
.gt-contact{display:flex;flex-wrap:wrap;gap:1rem;margin-top:1.8rem}
.gt-contact a{display:inline-flex;align-items:center;gap:.55em;padding:.85em 1.4em;
  border:1.5px solid var(--euc-deep);color:var(--euc-deep);font-weight:700;font-size:.86rem;transition:.25s}
.gt-contact a:hover{background:var(--euc-deep);color:var(--cream);opacity:1}

/* ---- FAQ ---- */
.gt-faq{padding:var(--sec-y) 0;background:var(--paper)}
.gt-faq .head{text-align:center;max-width:40ch;margin:0 auto 2.4rem}
.gt-faq h2{font-size:clamp(1.7rem,2.6vw,2.3rem);margin:.9rem 0 0}
.gt-faq-list{max-width:52rem;margin:0 auto;display:flex;flex-direction:column;gap:.85rem}
.gt-faq-i{background:var(--white);border:1px solid var(--rule);padding:1.3rem 1.5rem}
.gt-faq-i summary{font-family:var(--ff-d);font-weight:600;color:var(--euc-deep);font-size:1rem;
  cursor:pointer;list-style:none;display:flex;justify-content:space-between;align-items:center;gap:1rem}
.gt-faq-i summary::-webkit-details-marker{display:none}
.gt-faq-i summary::after{content:"+";font-size:1.4rem;line-height:1;color:var(--euc-deep);transition:.25s}
.gt-faq-i[open] summary::after{transform:rotate(45deg)}
.gt-faq-i p{margin:1rem 0 0;color:var(--char);font-size:.94rem;line-height:1.68}
.gt-faq-i p:last-child{margin-bottom:0}
</style>
</head>

<body>
'''

HERO = '''
<main>
<section class="gt-hero">
  <div class="gt-hero-bg"><img src="assets/img/give-a-tree-koala-COMP.jpg" alt="A koala resting in the fork of a eucalypt in open forest" fetchpriority="high" decoding="async"></div>
  <div class="cw rv">
    <div class="gt-hero-g">
      <div>
        <nav class="gt-crumb"><a href="index.html">Home</a><span style="opacity:.45">/</span><a href="ways-you-can-get-involved.html">Get Involved</a><span style="opacity:.45">/</span>Give a Tree</nav>
        <span class="ey">Give a Tree. Bring Back the Bush.</span>
        <h1>The best gifts don&rsquo;t sit under a tree. They <em>grow into one.</em></h1>
        <p class="lede">Give a tree and help bring back native bushland across Australia. Your gift funds on-ground restoration, creating habitat for wildlife and helping our landscapes become healthier and more resilient.</p>
        <ul class="gt-tiers">
          <li><b>$10</b> one tree</li>
          <li><b>$100</b> 10 trees</li>
          <li><b>$500</b> 50 trees</li>
          <li><b>$1,000</b> 100 trees</li>
        </ul>
        <p class="gt-native">100% of the trees are native species, planted in Australia&rsquo;s priority landscapes.</p>
      </div>

      <div class="gt-form" id="give">
        <div class="gt-form-head">
          <h2>Give a Tree</h2>
          <p>One native tree can be planted for every $10 you give. Minimum gift $10.</p>
        </div>
        <iframe id="raiselyFrame" class="gt-form-frame" src="https://gift-a-tree.raiselysite.com/embed/donate" title="Give a Tree donation form" allow="payment *" referrerpolicy="no-referrer-when-downgrade" loading="eager"></iframe>
        <p class="gt-form-fb">Form not loading? <a href="https://gift-a-tree.raiselysite.com/#donate" target="_blank" rel="noopener">Open the Give a Tree donation page</a> in a new tab.</p>
      </div>
    </div>
  </div>
</section>

<section class="gt-stats">
  <div class="cw">
    <div class="gt-stats-g">
      <div class="gt-stat rv"><span class="n" data-count="8" data-suf="M">0</span><span class="l">trees by 2030 pledge</span></div>
      <div class="gt-stat rv d1"><span class="n" data-count="1" data-suf="M+">0</span><span class="l">trees planted to date</span></div>
      <div class="gt-stat rv d2"><span class="n" data-count="30" data-suf="+">0</span><span class="l">community nurseries</span></div>
      <div class="gt-stat rv d3"><span class="n" data-count="100" data-suf="%">0</span><span class="l">native species, chosen for each site</span></div>
    </div>
  </div>
</section>
'''

MEANING = '''
<section class="gt-split white">
  <div class="cw">
    <div class="gt-split-g">
      <div class="gt-split-im rv"><img src="assets/img/nursery-volunteers.jpg" alt="A volunteer holding a tray of native seedlings at a community nursery" loading="lazy" decoding="async"></div>
      <div class="rv d1">
        <span class="ey">A gift that keeps growing</span>
        <h2>Looking for a gift that&rsquo;s more meaningful?</h2>
        <p>Give a Tree for a birthday, a thank you, or simply because you want to give something that does a little more good for Country.</p>
        <p>Each tree gift comes with a personalised certificate, giving them something special to receive while helping bring back the bush.</p>
        <a class="gt-cta" href="#give">Give a Tree today</a>
      </div>
    </div>
  </div>
</section>
'''

HOW = '''
<section class="gt-how">
  <div class="cw">
    <div class="head rv">
      <span class="ey">How it works</span>
      <h2 style="margin-top:1rem">Four steps, and the bush gets a little bigger.</h2>
    </div>
    <div class="gt-how-g">
      <div class="gt-step rv"><span class="n">1</span><h3>Choose your gift</h3><p>From $10 for a single tree, up to a legacy canopy, or enter your own amount.</p></div>
      <div class="gt-step rv d1"><span class="n">2</span><h3>Write a dedication</h3><p>In honour of, in memory of, or as a thank you. Your message, in your words.</p></div>
      <div class="gt-step rv d2"><span class="n">3</span><h3>Get the certificate</h3><p>Keep it, or send it straight to the person you are honouring.</p></div>
      <div class="gt-step rv d3"><span class="n">4</span><h3>We plant your trees</h3><p>Native species, planted by trained volunteers in Australia&rsquo;s priority landscapes.</p></div>
    </div>
    <p class="gt-how-note"><em>A little note from us:</em> to help reduce unnecessary printing, we recommend printed certificates for gifts of $100 or more. For gifts under $100 you are very welcome to print the certificate yourself at home or at work. Organising more than one certificate, or want your company logo on it? Email <a href="mailto:fnpw@fnpw.org.au">fnpw@fnpw.org.au</a> or call <a href="tel:1800898626">1800 898 626</a>.</p>
  </div>
</section>
'''

SEASON = '''
<!-- SEASONAL SLOT: swap this section for Valentine&rsquo;s Day, Father&rsquo;s Day or Mother&rsquo;s Day,
     or delete it entirely out of season. Nothing else on the page depends on it. -->
<section class="gt-season">
  <div class="cw">
    <div class="gt-split-g">
      <div class="rv">
        <span class="ey">This Christmas</span>
        <h2>Give a little more bush this Christmas.</h2>
        <p>This season, give a tree with our special Christmas certificate. A thoughtful way to celebrate friends, family, colleagues or clients while helping bring back the bush.</p>
        <p class="lead-out">Less stuff. More bush.</p>
        <a class="gt-cta on-dark" href="#give">Give a Tree for Christmas</a>
      </div>
      <!-- PLACEHOLDER: swap for Mali&rsquo;s seasonal creative (emu with a Christmas wreath) when it lands -->
      <div class="gt-season-im rv d1"><img src="assets/img/bbtb-emu.jpg" alt="The Bring Back the Bush emu" loading="lazy" decoding="async"></div>
    </div>
  </div>
</section>
'''

CORP = '''
<section class="gt-split white">
  <div class="cw">
    <div class="gt-split-g flip">
      <div class="gt-split-im rv"><img src="assets/img/get-involved-planting-day.jpg" alt="A corporate volunteering team planting native seedlings on a restoration site" loading="lazy" decoding="async"></div>
      <div class="rv d1">
        <span class="ey">For business</span>
        <h2>Recognise your team, clients or partners.</h2>
        <p>Give a Tree is a simple way for businesses to celebrate a milestone, say thank you, or share a little appreciation.</p>
        <p class="lead-out">A thoughtful gift for them. A positive impact for the bush.</p>
        <p>Giving to a group? We can arrange Give a Tree certificates in bulk, including your company logo. Get in touch and we will organise yours.</p>
        <div class="gt-contact">
          <a href="mailto:fnpw@fnpw.org.au">Email fnpw@fnpw.org.au</a>
          <a href="tel:1800898626">Call 1800 898 626</a>
        </div>
      </div>
    </div>
  </div>
</section>
'''

MEMORY = '''
<section class="gt-memory">
  <div class="cw">
    <div class="gt-split-g">
      <div class="rv">
        <span class="ey">In memory</span>
        <h2>Remember someone special.</h2>
        <p>Give a Tree in memory of someone you love and help create a lasting tribute while supporting the restoration of native bushland.</p>
        <p>It is a meaningful way to honour their life and share their memory with family and friends.</p>
        <p class="lead-out">A living tribute to someone who will always be remembered.</p>
        <a class="gt-cta solid" href="#give">Give a Tree in memory</a>
      </div>
      <div class="gt-split-im rv d1"><img src="assets/img/hero-golden.jpg" alt="Late afternoon light through open eucalypt woodland" loading="lazy" decoding="async"></div>
    </div>
  </div>
</section>
'''

FAQ_ITEMS = [
    ('When will I get my digital certificate?',
     'Your digital certificate is emailed to you the next business day after your gift is '
     'received. If you asked us to send it straight to the recipient, it goes to their inbox '
     'instead, on the date you nominated.'),
    ('I&rsquo;ve requested a physical certificate. When will it arrive?',
     'Printed certificates are posted within five business days and usually arrive within a '
     'week or two, depending on where you are in Australia. If you need one by a set date, '
     'let us know when you give and we will do our best to get it there in time.'),
    ('Can physical certificates be sent overseas?',
     'Yes. International post takes longer and delivery times vary by country, so we recommend '
     'sending the digital certificate as well, so your recipient has something to open on the day.'),
    ('I&rsquo;ve noticed an error on my certificate. What should I do?',
     'Email <a href="mailto:fnpw@fnpw.org.au">fnpw@fnpw.org.au</a> with your gift reference and '
     'the correction, and we will reissue it for you. There is no charge to have a certificate '
     'corrected and reissued.'),
    ('Where will my gifted tree be planted? Can I choose the site?',
     'Trees are planted in the priority landscapes where they will do the most good, which means '
     'we cannot allocate an individual tree to a site you choose. Our environmental team selects '
     'native species suited to the local ecology of each planting site, so the trees survive and '
     'rebuild functioning habitat rather than a monoculture.'),
    ('Will a plaque or dedication be placed on my tree?',
     'No. Restoration sites are working landscapes and often remote, so we do not place plaques '
     'or markers on individual trees. Your dedication lives on the certificate instead, which is '
     'yours to keep, frame or pass on.'),
    ('I&rsquo;m having trouble completing my donation. What should I do?',
     'Try refreshing the page first, and check that your browser is not blocking third-party '
     'content. If it still will not go through, call us on <a href="tel:1800898626">1800 898 626</a> '
     'or email <a href="mailto:fnpw@fnpw.org.au">fnpw@fnpw.org.au</a> and we will take your gift over the phone.'),
    ('Is my gift tax deductible?',
     'Yes. The Foundation for National Parks &amp; Wildlife is a registered Australian charity '
     '(ABN 51 248 905 949) with Deductible Gift Recipient status. Gifts of $2 or more are tax '
     'deductible in Australia, and your receipt is emailed with your certificate.'),
]


def faq():
    rows = []
    for n, (q, a) in enumerate(FAQ_ITEMS):
        d = ' d1' if n % 2 else ''
        rows.append('      <details class="gt-faq-i rv%s"><summary>%s</summary><p>%s</p></details>'
                    % (d, q, a))
    return ('''
<section class="gt-faq">
  <div class="cw">
    <div class="head rv">
      <span class="ey">Questions</span>
      <h2>Frequently asked</h2>
    </div>
    <div class="gt-faq-list">
%s
    </div>
  </div>
</section>
</main>
''' % NL.join(rows))


SCRIPT = '''
<script src="assets/js/main.js"></script>
<script>
/* The Raisely form is a cross-origin iframe, so it cannot be measured from here.
   It ships with a generous fixed height; if Raisely posts its own height back we
   use that instead, so the card never scrolls inside itself. */
(function () {
  var frame = document.getElementById('raiselyFrame');
  if (!frame) return;

  /* The home page tier tiles link here as gift-a-tree.html?amount=100#give.
     Pass that straight to Raisely so the tier is already chosen on arrival.
     If Raisely ignores the parameter the form simply opens on its default. */
  var amt = parseInt((location.search.match(/[?&]amount=(\d+)/) || [])[1], 10);
  if (amt > 0 && amt <= 1000000) {
    frame.src = frame.src.split('?')[0] + '?amount=' + amt;
  }
  window.addEventListener('message', function (e) {
    var host;
    try { host = new URL(e.origin).hostname; } catch (err) { return; }
    if (!/(^|\\.)raiselysite\\.com$|(^|\\.)raisely\\.com$/.test(host)) return;
    var d = e.data, h = null;
    if (typeof d === 'number') h = d;
    else if (d && typeof d === 'object') h = d.height || d.frameHeight || (d.payload && d.payload.height);
    h = parseInt(h, 10);
    if (h > 300 && h < 4000) frame.style.height = h + 'px';
  });
})();

%s
</script>
</body>
</html>
''' % navjs

page = (HEAD + header + NL + HERO + MEANING + HOW + SEASON + CORP + MEMORY + faq()
        + NL + footer + NL + SCRIPT)

open(OUT, 'w', encoding='utf-8').write(page)
print('wrote %s, %d lines, %d bytes' % (OUT, page.count(NL) + 1, len(page)))

# ---- checks ----
bad = [w for w in ('—', ' and Wildlife', 'Kaurna Yerta') if w in page]
print('house-rule breaches:', bad or 'none')
for t in ('section', 'div', 'main', 'details', 'ul', 'li', 'nav', 'p'):
    o = len(re.findall(r'<%s[\s>]' % t, page))
    c = len(re.findall(r'</%s>' % t, page))
    if o != c and t != 'p':
        print('  UNBALANCED %s: %d open, %d close' % (t, o, c))
print('script blocks:', page.count('<script>'), 'closes:', page.count('</script>'))
print('nav IIFEs:', page.count('var ngs=document.querySelectorAll'))
print('orphan ids referenced:', [i for i in ('raiselyFrame',) if 'id="%s"' % i not in page])
