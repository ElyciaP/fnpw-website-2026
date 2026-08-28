"""Generate data/projects.json, three pillar pages and all project detail pages.

Data source: fnpw.org.au project sitemap (July 2026). Pillar and state values
are PROVISIONAL guesses; correct them in data/projects.json and re-run.
Excluded: form-test (junk) and the three grants projects (FNPW no longer runs grants).
"""
import json, os, re
from site_lib import (ROOT, write_page, hero, hero_img, sec, two, port, cta_band,
                      stats, card, RAISELY_DONATE, PLACEHOLDER_IMG)

U = 'https://fnpw.org.au/wp-content/uploads/'

# slug | image path (under wp-content/uploads/) | pillar | state
DATA = """
garners-beach-cassowary-rehabilitation-centre-project|2020/12/Cassowary-Rehabilitation-Centre-Project-lge.jpg|species|QLD
tangaroa-blue|2021/01/Dugong-fish-CYMK.jpg|healing|QLD
genetic-code-of-koalas|2021/02/Koala-mum-bub-scaled.jpg|species|Australia
bushfire-recovery-habitat-restoration|2022/04/Kosciuszko-National-Park-Harrington-New-South-Wales-Australia-by-benkrut-from-Getty-Images.png|healing|NSW
bilby-fire-project|2022/03/11057207814_38a4518a3f_b.jpg|species|Australia
brush-tailed-rock-wallaby-school-education|2021/02/Brush-tailed-Rock-wallaby-school-education-KVPS-puppet-show-18-scaled.jpg|species|NSW
caught-on-camera|2021/02/Caught-on-Camera-Superb-Lyrebird.jpg|species|Australia
christmas-island-reptiles|2021/02/Christmas-Island-Reptile-Captive-Breeding-lge.jpg|species|Christmas Island
eastern-bristlebird|2021/02/Eastern-Bristlebird.jpg|species|NSW
endangered-pomaderris-plants|2021/02/Pomaderris-intermedia-lge.jpg|species|NSW
feather-leaved-banksia-of-wa|2021/02/FeatherLeavedBanksia-lge.jpg|species|WA
gogerlys-point-heritage-precinct|2021/02/Gogerlys-Cottage.jpg|parks|NSW
granite-island-little-penguins|2021/01/LittlePenguins.jpg|species|SA
green-parrot-breeding-project|2021/02/Phillip-Island-Green-Parrot-lge.jpg|species|Norfolk Island
habitats-for-koalas-in-the-otways|2022/04/Koala-Habitat.png|healing|VIC
jungurra|2021/02/GOPR0158_1641337130395-scaled-e1658287534120.jpg|healing|WA
kangaroo-islands-bandicoots|2021/01/Bandicoot-2.png|species|SA
kangaroo-islands-enigma-moth|2021/02/EnigmaMoth-lge.jpg|species|SA
koala-tree-planting|2021/02/Koala-Alyson-Boyer-1-scaled.jpg|healing|NSW
kosciuszko-national-park-2020-fire-recovery|2021/02/KNP-recovery-1-scaled.jpg|healing|NSW
kukundi-nature-playspace|2021/02/Discovery-rangers-biodiversity-education-WilderQuest.jpg|parks|NSW
lane-cove-bushcare-program-2018|2021/02/Lane-Cove-Bushcare-Program-2018-scaled.jpg|healing|NSW
malleefowl-conservation|2021/01/2113-malleefowl-Jill-Lochman.jpg|species|Australia
manly-little-penguins|2021/01/Featured-projects-Penguins-lge.jpg|species|NSW
movement-of-koalas-back-into-severely-burnt-forest|2022/04/Koala-Movement.png|species|NSW
mt-schank-walking-trail|2021/02/Mount-Schank-walking-track.jpg|parks|SA
petaurus-connections|2021/01/K2W-GER-Aerial.jpg|healing|NSW
quolls|2020/12/Quoll-lge.jpg|species|Australia
red-tailed-phascogale|2021/02/red-tailed-phascogale.jpg|species|WA
redlands-koala-planting|2021/02/CurrumbinKoala-Erik-Veland.jpg|healing|QLD
remarkable-southern-flinders|2021/02/square.jpg|parks|SA
restoring-the-glideways-of-k2w|2021/01/K2W-glideways-1920x600-1.jpg|healing|NSW
seagrass-collaboration|2021/01/Seagrass-Small.jpg|healing|Australia
southern-highlands-koala-conservation|2021/02/Southern-Koala-05-scaled.jpg|species|NSW
tassie-devil-roadkill|2021/02/TassieDevilRoadkill_PhotoBurrardLucas.jpg|species|TAS
the-great-koala-count|2022/04/Koala-tree.png|species|Australia
trails-for-tails|2021/01/Alberts-Lyrebird-Peter-Owen-Birdlife-2016.jpg|parks|QLD
wa-bird-watering-stations|2021/02/WA-Bird-Watering-Stations-Jirdarup-bushland-precinct-Three-cockies.jpeg|species|WA
warddeken-mayh|2021/01/Lorina-and-Tinnesha-in-EPBC-protected-sandstone-shrublands_photo-Donal-Sullivan5f911988b9c1d-scaled.jpg|healing|NT
was-woylie-survival|2021/02/Woylie.jpg|species|WA
western-swamp-tortoise|2021/02/Western-Swamp-Tortoise-scaled.jpg|species|WA
woomargama-national-park|2021/02/Ascent-37-Woomargama-2000px-Copy.jpg|parks|NSW
yarning-online-oncountry-kurrupurra-pila-weaving|2022/03/pexels-kelly-l-3794747-scaled.jpg|healing|SA
yarrahapinni-wetlands-restoration-stage-1|2021/02/NSW-NPWS-Yarrahapinni-Wetlands-National-Park-1.jpg|healing|NSW
youth-wildlife-ambassadors|2021/02/Phillip-Island-Ambassadors.jpg|species|VIC
nectarlovers|2021/01/Black-chinned-honeyeater-PETER-SAWYER-CYMK.jpg|species|NSW
enhancing-biodiversity-protecting-cultural-heritage-at-torrens-island-conservation|2022/02/torrens-Island-bird.jpg|parks|SA
fnpw-koala-projects|2023/08/koala-fun-facts.png|species|Australia
nilpena-nationalpark|2021/01/nilpena03.png|parks|SA
aussie-ark-quolls|2021/01/Aussie-Ark-Quoll-enclosure.jpg|species|NSW
lion-island-little-penguin|2021/01/LittlePenguins.jpg|species|NSW
impact-of-bushfires-on-koalas|2021/02/Southern-Koala-05-scaled.jpg|species|NSW
alpine-frogs-a-calling|2022/03/pexels-pixabay-67290-scaled.jpg|species|NSW
ngurrawaana-ranger-habitat-conservation|2021/02/WArangers-lge.jpg|healing|WA
heritage-estates|2021/02/heritage-Estates-05-lg.jpg|parks|NSW
1-million-turtles|2021/02/1-million-turtles.png|species|Australia
native-plant-nurseries|2024/03/Native-Nursery-Australia.png|healing|Australia
cultivating-koala-habitat|2023/12/Feature-Images-for-website.png|healing|Australia
mountain-pygmy-possum|2022/02/mpp_dept_environment_and_primaryIndustries2_VIC_edited-scaled-e1683699811709.jpg|species|VIC
wild-heart||healing|Australia
bushfire-recovery-program|2022/03/2jGU-mXU.png|healing|Australia
fire-wise|2024/01/Carpobrotus-rossii.png|healing|Australia
sturt-national-park|2021/02/sturt-national-park-08_Amanda-Cutlack-DPIE.jpg|parks|NSW
wildlife-heroes|2021/01/feeding.jpg|species|Australia
black-cockatoo-corridor|2021/01/Black-Cockatoo-Too_big_nestling_240420-rotated-e1746404683346.jpg|healing|WA
memorial-trees||healing|Australia
bandicoot-superhighway-project|2021/01/Southern-Brown-Bandicoot.jpg|species|VIC
students-dig-in-for-conservation|2021/02/King-Island-Students-Field-Days-scaled.jpg|healing|TAS
devil-ark|2021/02/TasmanianDevil-MelanieWagner.jpg|species|NSW
bushfire-recovery-seedbanks|2021/01/51965515327_82f49da53c_k.jpg|healing|Australia
mary-valley-rail-trail-habitat-link|2021/12/koala_gympie.gif|healing|QLD
save-the-orange-bellied-parrot|2022/02/Orange-belliedParrot_DPIPWE-scaled.jpg|species|TAS
recovering-blue-butterflies-in-victoria|2022/03/46018344_10157140736212125_311600624649109504_n.jpg|species|VIC
restoring-campbells-wetland-walkway|2022/03/Griffith-Swamp-Land.jpg|healing|NSW
nest-boxes-in-plenty-gorge-park|2021/02/Koala-projects.png|species|VIC
backyard-buddies|2021/01/children-Biodiversity-discovery-native-flora-banksia-seed-cones.jpg|species|Australia
white-throated-grasswren|2021/02/White-throated-gresswrenMale-Female-Luke-Paterson-NTBS.jpg|species|NT
mount-field-national-park|2021/02/Mount-Field-NP-East-Planking-PAWS.jpg|parks|TAS
booningyah-junior-rangers-program|2021/12/PXL_20211024_001509888.PORTRAIT-scaled.jpg|healing|Australia
dalki-garringa-botanic-park|2022/03/Wail-Nursery.jpg|parks|VIC
gift-a-tree-for-nature-conservation|2024/03/Plant-a-Tree-Australia.png|healing|Australia
curb-wombat-mange-program||species|Australia
supporting-community-led-treatment-to-protect-bare-nosed-wombats||species|Australia
""".strip()

TITLE_OVERRIDES = {
    'was-woylie-survival': "WA's Woylie Survival",
    'wa-bird-watering-stations': 'WA Bird Watering Stations',
    'nilpena-nationalpark': 'Nilpena National Park',
    'fnpw-koala-projects': 'FNPW Koala Projects',
    'restoring-the-glideways-of-k2w': 'Restoring the Glideways of K2W',
    'kangaroo-islands-bandicoots': "Kangaroo Island's Bandicoots",
    'kangaroo-islands-enigma-moth': "Kangaroo Island's Enigma Moth",
    'yarning-online-oncountry-kurrupurra-pila-weaving': 'Yarning Online, On Country: Kurrupurra Pila Weaving',
    'enhancing-biodiversity-protecting-cultural-heritage-at-torrens-island-conservation':
        'Enhancing Biodiversity &amp; Protecting Cultural Heritage at Torrens Island',
    '1-million-turtles': '1 Million Turtles',
    'mt-schank-walking-trail': 'Mt Schank Walking Trail',
    'alpine-frogs-a-calling': 'Alpine Frogs: A Calling',
    'lane-cove-bushcare-program-2018': 'Lane Cove Bushcare Program',
    'tassie-devil-roadkill': 'Tassie Devil Roadkill',
}
SMALL = {'of', 'the', 'in', 'for', 'a', 'at', 'on', 'to', 'with', 'and', 'back', 'into'}

def title_of(slug):
    if slug in TITLE_OVERRIDES:
        return TITLE_OVERRIDES[slug]
    words = slug.split('-')
    out = []
    for i, w in enumerate(words):
        out.append(w if (w in SMALL and i > 0) else w.capitalize())
    return ' '.join(out)

PILLARS = {
    'parks':   dict(label='Growing National Parks', page='growing-national-parks.html', cls='pb-parks',
                    ey='Pillar one',
                    lede='We buy high-conservation-value land and hand it back, adding it to '
                         "Australia's national parks and protected areas so it is safe forever.",
                    desc='FNPW projects growing national parks and protected areas across Australia.'),
    'species': dict(label='Saving Species', page='saving-species.html', cls='pb-species',
                    ey='Pillar two',
                    lede='From koalas to enigma moths, we fund the recovery work that keeps '
                         "Australia's threatened plants and animals in the world.",
                    desc='FNPW projects protecting and recovering threatened Australian species.'),
    'healing': dict(label='Healing the Land', page='healing-the-land.html', cls='pb-healing',
                    ey='Pillar three',
                    lede='We restore what has been damaged: replanting habitat, healing waterways '
                         'and supporting cultural fire and land management.',
                    desc='FNPW projects restoring habitat and healing damaged Australian landscapes.'),
}


U_ART = 'https://fnpw.org.au/wp-content/uploads/'
RELATED = {
    'parks': ('Stories from the parks we\u2019re growing', 'parks', 'Growing Parks', [
        (U_ART + '2022/02/torrens-Island-bird.jpg', '08 May 2026 &middot; Story',
         'Mundoo Island: a once-in-a-generation conservation victory',
         'From the Murray Mouth, 1,900 hectares of Ramsar wetlands have been secured for '
         'Coorong National Park, with the Ngarrindjeri at the heart of decision-making.'),
        (U_ART + '2021/02/Lane-Cove-Bushcare-Program-2018-scaled.jpg', 'Jul 2026 &middot; Story',
         'A wildlife corridor is only as wide as its narrowest point',
         'Development keeps narrowing the routes wildlife depend on, and it is the tightest '
         'pinch point that decides whether a corridor works at all.'),
        (U_ART + '2021/02/KNP-recovery-1-scaled.jpg', 'Jun 2026 &middot; Story',
         'Years of restoration, written in layers',
         'Hindmarsh Valley has gone from cleared paddock to returning forest, and the layers '
         'of that recovery are now readable on the ground.')]),
    'species': ('Stories from the species we\u2019re saving', 'species', 'Saving Species', [
        (U_ART + '2021/02/NSW-NPWS-Yarrahapinni-Wetlands-National-Park-1.jpg',
         '02 May 2026 &middot; Update', '18,582 wombat mange treatments delivered',
         'An update from the Curb Wombat Mange Program, which exceeded its 2025 targets and '
         'grew volunteer capacity by 92%.'),
        (U_ART + '2021/02/KNP-recovery-1-scaled.jpg', '18 Apr 2026 &middot; Story',
         'Mountain Pygmy Possums: a year on',
         'Tracking the recovery of one of Australia\u2019s most threatened mammals after the '
         'alpine breeding centre\u2019s first full year of operations.'),
        (U_ART + '2021/02/Southern-Koala-05-scaled.jpg', '11 Apr 2026 &middot; Story',
         'Restoring the Growling Grass Frog',
         'How Winton Wetlands is becoming a stronghold for one of south-eastern '
         'Australia\u2019s most endangered amphibians.')]),
    'healing': ('Stories from the land we\u2019re healing', 'heal', 'Healing Land', [
        (U_ART + '2021/02/KNP-recovery-1-scaled.jpg', '28 Mar 2026 &middot; Update',
         'Fire Wise: 110,000 plants and counting',
         'Inside the community network propagating fire-resilient natives across NSW, '
         'Victoria and South Australia.'),
        (U_ART + '2021/02/Southern-Koala-05-scaled.jpg', '14 Mar 2026 &middot; Update',
         'Healing Hindmarsh Island',
         'Multi-year wetland restoration on Ngarrindjeri Country reaches a new milestone.'),
        (U_ART + '2021/02/Lane-Cove-Bushcare-Program-2018-scaled.jpg', 'Aug 2026 &middot; Story',
         'What does healthy bushland actually look like?',
         'It looks messier than you would expect, and the science behind bringing back the '
         'bush at Mulligans Flat explains why.')]),
}

FILTER_JS = """<script>
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
</script>
"""


def related_section(key):
    heading, catcls, catlabel, items = RELATED[key]
    cards = []
    for i, (img, date, title, para) in enumerate(items):
        d = '' if i == 0 else ' d%d' % i
        cards.append(
            f'      <a href="#" class="art rv{d}">\n'
            f'        <div class="art-im"><img src="{img}" alt="{title}" loading="lazy">'
            f'<span class="cat {catcls}">{catlabel}</span></div>\n'
            f'        <div class="art-bd">\n'
            f'          <div class="art-date">{date}</div>\n'
            f'          <h3>{title}</h3>\n'
            f'          <p>{para}</p>\n'
            f'          <span class="art-link">Read more</span>\n'
            f'        </div>\n'
            f'      </a>')
    return f'''<!-- Related articles -->
<section class="ra ra-{ "parks" if key=="parks" else ("species" if key=="species" else "healing") }">
  <div class="ra-block">
    <div class="cw rv">
      <div class="ra-head">
        <div><span class="ey">Related reading</span><h2>{heading}</h2></div>
        <a href="articles.html" class="btn-g">All articles</a>
      </div>
    </div>
  </div>
  <div class="cw ra-cards">
    <div class="art-grid">
{chr(10).join(cards)}
    </div>
  </div>
</section>'''


# Fields that are curated by hand or by another tool and must survive a re-run.
# gen_map.py reads lat/lon/on_map from data/projects.json; regenerating the file
# without carrying them across silently empties the projects map.
CURATED_FIELDS = ('lat', 'lon', 'on_map', 'pillar_confirmed', 'year')


def _preserve_curated(projects, path):
    """Copy curated per-project fields from the existing projects.json."""
    try:
        with open(path) as f:
            existing = {p['slug']: p for p in json.load(f)}
    except (IOError, ValueError):
        return
    for p in projects:
        old = existing.get(p['slug'])
        if not old:
            continue
        for k in CURATED_FIELDS:
            if k in old:
                p[k] = old[k]


def main():
    projects = []
    for line in DATA.splitlines():
        slug, img, pillar, state = line.split('|')
        projects.append(dict(
            slug=slug, title=title_of(slug),
            img=(U + img) if img else PLACEHOLDER_IMG,
            pillar=pillar, state=state,
            pillar_confirmed=False,
            live_url=f'https://fnpw.org.au/project/{slug}/',
        ))
    os.makedirs(os.path.join(ROOT, 'data'), exist_ok=True)
    _preserve_curated(projects, os.path.join(ROOT, 'data/projects.json'))
    with open(os.path.join(ROOT, 'data/projects.json'), 'w') as f:
        json.dump(projects, f, indent=1)

    # ---- project detail pages (exemplars are owned by gen_exemplars.py) ----
    from site_lib import EXEMPLAR_SLUGS
    for p in projects:
        if p['slug'] in EXEMPLAR_SLUGS:
            continue
        pil = PILLARS[p['pillar']]
        others = [q for q in projects if q['pillar'] == p['pillar'] and q['slug'] != p['slug']][:3]
        related = '\n'.join(card(q['slug'], q['title'], q['img'], pil['label'], pil['cls'],
                                 q['state'], '') for q in others)
        body = f'''{hero_img(pil['label'], p['title'],
                   'An FNPW conservation project.', p['title'], p['img'], p['title'])}
{sec(two(
  f"""<span class="ey">The project</span>
  <h2 style="margin:.8rem 0 1.2rem">About this project</h2>
  {port(f"body copy, stats and gallery from <a href='{p['live_url']}'>{p['live_url']}</a>")}
  <p>Project story goes here. What the threat is, what we and our partners are doing about it, and what has changed because supporters funded it.</p>""",
  f"""<div class="pmeta">
    <div class="pmeta-i"><span>Pillar</span><strong><a href="{pil['page']}">{pil['label']}</a></strong></div>
    <div class="pmeta-i"><span>Where</span><strong>{p['state']}</strong></div>
    <div class="pmeta-i"><span>Status</span><strong>To confirm</strong></div>
  </div>"""))}
{sec(f'<span class="ey">More from this pillar</span><h2 style="margin:.8rem 0 1.6rem">Related projects</h2><div class="pg">{related}</div>', 'paper')}
{cta_band('Help fund work like this.',
          'Every FNPW project is powered by donations, bequests and partnerships.',
          [('Donate', RAISELY_DONATE, 'btn-p'), ('Become a partner', 'partner.html', 'btn-o')])}'''
        write_page(f"project-{p['slug']}.html", p['title'],
                   f"{p['title']}: a Foundation for National Parks & Wildlife project. {pil['label']}.",
                   body)

    # ---- pillar pages ----
    NARRATIVE = {
        'parks': (
            '<p>National parks are the strongest protection Australian law can give a landscape. '
            'When land with high conservation value comes up, we help buy it and hand it back, '
            'adding it to the protected estate so it is safe from clearing and development forever.</p>'
            '<p>It started with our founding gift in 1970 and it has never stopped: from wetlands '
            'at the Murray Mouth to outback stations beside Boodjamulla, these projects are how '
            'the map of protected Australia grows.</p>',
            ['We identify land of high conservation value, often adjoining existing parks',
             'We fund or co-fund the purchase with partners and supporters',
             'The land is transferred to the national parks estate, protected forever']),
        'species': (
            '<p>Australia is home to plants and animals found nowhere else on Earth, and one of '
            'the worst extinction records anywhere. These projects fund the unglamorous, essential '
            'work of recovery: breeding programs, monitoring, nest boxes, disease treatment and '
            'the science that underpins all of it.</p>'
            '<p>From koalas and quolls to enigma moths and endangered wattles, if it is on the '
            'brink, this is the pillar fighting for it.</p>',
            ['We fund recovery programs run with researchers, carers and land managers',
             'We back both flagship species and the overlooked ones',
             'Every project reports real outcomes: populations, hectares, hollows, seedlings']),
        'healing': (
            '<p>Much of Australia is damaged rather than destroyed, and damaged land can heal. '
            'These projects replant habitat, restore wetlands and waterways, recover country after '
            'bushfire and support First Nations cultural land management.</p>'
            '<p>Healing the land is slow, patient work measured in seasons and seedlings. It is '
            'also the work that turns a map of loss back into habitat.</p>',
            ['We fund revegetation, restoration and bushfire recovery at scale',
             'We support cultural fire and caring-for-Country programs led by First Nations communities',
             'We stay for the follow-up: watering, weeding, monitoring, replanting']),
    }
    # bespoke content per pillar: hero image, headline stat (Impact Report), featured project
    EXTRA = {
        'parks': dict(
            tint='parks',
            hero_img=U + '2021/02/sturt-national-park-08_Amanda-Cutlack-DPIE.jpg',
            hero_alt='Sturt National Park at dusk',
            stat=('29,479', 'hectares', 'of land added to National Park status'),
            stat_label='Hectares protected',
            stat_desc='Land bought and transferred into the national parks estate. '
                      '<a href="reports.html">FNPW Impact Report</a>.',
            projects_desc='Land purchases and park expansions funded with partners, '
                          'supporters and government.',
            states_desc='From the Flinders Ranges to the New South Wales coast.',
            feat2='It is the largest single project in the pillar and the clearest picture of '
                  'what growing a national park actually takes: patient negotiation, co-funding, '
                  'and Traditional Owners at the centre of how the land is managed afterwards.',
            feat=('remarkable-southern-flinders', 'Remarkable Southern Flinders',
                  U + '2021/02/square.jpg',
                  'Linking established parks, newly protected land and open reservoir country into '
                  'one vast, connected park precinct for South Australia, co-managed with the Nukunu Nation.')),
        'species': dict(
            tint='species',
            hero_img=U + '2021/02/Woylie.jpg',
            hero_alt='Woylie, the brush-tailed bettong',
            stat=('18,582', 'treatments', 'delivered to wombats with mange'),
            stat_label='Treatments delivered',
            stat_desc='Wombats treated for mange through the Curb Wombat Mange Program. '
                      '<a href="reports.html">FNPW Impact Report</a>.',
            projects_desc='Recovery programs run with researchers, carers, Traditional Owners '
                          'and land managers.',
            states_desc='From Christmas Island to the Tasmanian midlands, including two '
                        'external territories.',
            feat2='It is the largest single landscape in the pillar and the clearest '
                  'demonstration of what the pillar funds: local knowledge, long timeframes, '
                  'measured outcomes.',
            feat=('warddeken-mayh', 'Warddeken Mayh Recovery Project',
                  U + '2021/01/Lorina-and-Tinnesha-in-EPBC-protected-sandstone-shrublands_photo-Donal-Sullivan5f911988b9c1d-scaled.jpg',
                  'Indigenous rangers monitor 120 camera sites across 1.4 million hectares of the '
                  'Warddeken Indigenous Protected Area, recovering threatened mammals through '
                  'right-way fire and feral animal management.')),
        'healing': dict(
            tint='healing',
            hero_img='assets/img/bongil.jpg',
            hero_alt='Forest in Bongil Bongil National Park',
            stat=('1.2M', 'plantings', 'trees, shrubs and seedlings in key areas'),
            stat_label='Plants in the ground',
            stat_desc='Trees, shrubs and seedlings planted across priority restoration sites. '
                      '<a href="reports.html">FNPW Impact Report</a>.',
            projects_desc='Revegetation, wetland repair, bushfire recovery and cultural land '
                          'management.',
            states_desc='Across the eastern seaboard, the Top End and the west.',
            feat2='It shows what healing at scale looks like when you undo the original '
                  'damage rather than work around it, and then stay long enough to watch the '
                  'system come back on its own terms.',
            feat=('yarrahapinni-wetlands-restoration-stage-1', 'Yarrahapinni Wetlands',
                  U + '2021/02/NSW-NPWS-Yarrahapinni-Wetlands-National-Park-1.jpg',
                  'Floodgates and levee walls removed, tidal flows returned: a wetland on the Macleay '
                  'coming back to life after decades of damage.')),
    }
    others_of = {'parks': ['species', 'healing'], 'species': ['parks', 'healing'],
                 'healing': ['parks', 'species']}
    for key, pil in PILLARS.items():
        mine = [p for p in projects if p['pillar'] == key]
        x = EXTRA[key]
        mine = sorted(mine, key=lambda q: q['title'].lower())
        cards = '\n'.join(card(p['slug'], p['title'], p['img'], pil['label'], pil['cls'],
                               p['state'], '', data_state=p['state']) for p in mine)

        # ---- state filter chips, most-used first ----
        from collections import Counter as _C
        st_counts = _C(q['state'] for q in mine)
        chip_order = sorted(st_counts.items(), key=lambda kv: (-kv[1], kv[0]))
        chips = [f'<button class="fp on" data-f="all">All projects ({len(mine)})</button>']
        for st, n in chip_order:
            label = 'Australia-wide' if st == 'Australia' else st
            chips.append(f'<button class="fp" data-f="{st}">{label} ({n})</button>')
        filter_bar = f"""<div class="fb fb-paper fb-{x['tint']}">
  <div class="cw"><div class="fb-r">
    <div class="fps" id="fps">{''.join(chips)}</div>
    <div class="fb-right">
      <label class="sortwrap">Sort by
        <select class="psel" id="psort">
          <option value="az">A to Z</option>
          <option value="za">Z to A</option>
        </select>
      </label>
      <div id="fmeta">Showing all {len(mine)} projects</div>
    </div>
  </div></div>
</div>"""
        para, hows = NARRATIVE[key]
        how_list = ''.join(f'<li>{h}</li>' for h in hows)

        hero_html = f'''<section class="ch chi pil-hero chi-{x['tint']}" style="--chi:url('{x['hero_img']}')">
  <div class="cw rv">
    <nav style="display:flex;gap:.5em;font-size:.82rem;color:rgba(255,255,255,.75);margin-bottom:1.5rem"><a href="index.html" style="color:var(--euc-soft)">Home</a><span style="opacity:.4">/</span><a href="projects.html" style="color:var(--euc-soft)">Projects</a><span style="opacity:.4">/</span>{pil['label']}</nav>
    <span class="ey" style="color:var(--euc-soft)">{pil['ey']} &#183; {len(mine)} projects</span>
    <h1 style="margin:1rem 0 1.2rem;max-width:16ch;color:#fff">{pil['label']}</h1>
    <p class="lede" style="color:rgba(255,255,255,.88);max-width:52ch">{pil['lede']}</p>
  </div>
</section>'''

        # ---- stats band, directly under the hero ----
        n_states = len({q['state'] for q in mine if q['state'] != 'Australia'})
        stats_html = f'''<section class="pil-stats ps-{x['tint']}">
  <div class="cw rv">
    <div class="psg">
      <div class="pst"><span class="pst-n">{x['stat'][0]}</span><span class="pst-l">{x['stat_label']}</span><p class="pst-d">{x['stat_desc']}</p></div>
      <div class="pst"><span class="pst-n">{len(mine)}</span><span class="pst-l">Projects funded</span><p class="pst-d">{x['projects_desc']}</p></div>
      <div class="pst"><span class="pst-n">{n_states}</span><span class="pst-l">States and territories</span><p class="pst-d">{x['states_desc']}</p></div>
    </div>
  </div>
</section>'''

        intro = two(
            f'<span class="ey">Why it matters</span><h2 style="margin:.8rem 0 1.2rem">What this pillar does</h2>{para}',
            f'<div class="pmeta"><h3 style="margin-bottom:.8rem">How we do it</h3>'
            f'<ul style="padding-left:1.1rem;display:grid;gap:.6rem">{how_list}</ul></div>')

        related_html = related_section(key)
        fslug, ftitle, fimg, fdesc = x['feat']
        fdesc2 = x['feat2']
        featured = sec(
            f'''<div class="two" style="align-items:center">
<div class="rv"><a href="project-{fslug}.html"><img src="{fimg}" alt="{ftitle}" loading="lazy" style="display:block;width:100%;aspect-ratio:4/3;object-fit:cover;box-shadow:12px 12px 0 var(--euc-pale)"></a></div>
<div class="rv d1"><span class="ey">Featured project</span><h2 style="margin:.8rem 0 1rem">{ftitle}</h2>
<p>{fdesc}</p>
<p>{fdesc2}</p>
<a class="hx-cta" href="project-{fslug}.html">Read the full story<span class="hx-cta-line" aria-hidden="true"></span></a></div>
</div>''', 'dark')

        cross = '\n'.join(
            f'<a class="lc rv" href="{PILLARS[o]["page"]}"><h3>{PILLARS[o]["label"]}</h3>'
            f'<p>{PILLARS[o]["lede"][:90]}...</p><span class="lc-go">&rsaquo;</span></a>'
            for o in others_of[key])

        body = f'''{hero_html}
{stats_html}
{sec(intro)}
{featured}
<section class="sec paper" style="padding-bottom:1.5rem">
  <div class="cw rv"><span class="ey">All {len(mine)} projects</span><h2 style="margin:.8rem 0 0">Projects under this pillar</h2></div>
</section>
{filter_bar}
<section class="sec paper" style="padding-top:2.2rem">
  <div class="cw"><div class="pg" id="pgrid">{cards}</div></div>
</section>
{related_html}
{sec(f"<span class='ey'>Keep exploring</span><h2 style='margin:.8rem 0 1.4rem'>The other pillars</h2><div class='lcg'>{cross}</div>")}
{cta_band(f"Support {pil['label']}.",
          'Donate to this pillar directly, or explore the other ways to get involved.',
          [('Donate', RAISELY_DONATE, 'btn-p'), ('Ways to get involved', 'ways-you-can-get-involved.html', 'btn-o')])}'''
        write_page(pil['page'], pil['label'], pil['desc'], body,
                   page_css='''
.pil-hero{padding:10rem 0 5rem}
.fb.fb-paper{background:rgba(244,238,230,.95)}
''',
                   extra_js=FILTER_JS)

    print(f"projects: {len(projects)} pages, 3 pillar pages, data/projects.json written")
    from collections import Counter
    print('pillar split:', Counter(p['pillar'] for p in projects))

if __name__ == '__main__':
    main()
