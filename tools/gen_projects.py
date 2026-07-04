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
    for key, pil in PILLARS.items():
        mine = [p for p in projects if p['pillar'] == key]
        cards = '\n'.join(card(p['slug'], p['title'], p['img'], pil['label'], pil['cls'],
                               p['state'], '') for p in mine)
        para, hows = NARRATIVE[key]
        how_list = ''.join(f'<li>{h}</li>' for h in hows)
        intro = two(
            f'<span class="ey">Why it matters</span><h2 style="margin:.8rem 0 1.2rem">What this pillar does</h2>{para}',
            f'<div class="pmeta"><h3 style="margin-bottom:.8rem">How we do it</h3>'
            f'<ul style="padding-left:1.1rem;display:grid;gap:.6rem">{how_list}</ul></div>')
        body = f'''{hero(pil['ey'], pil['label'], pil['lede'], pil['label'])}
{sec(intro)}
{sec(f"<span class='ey'>{len(mine)} projects</span><h2 style='margin:.8rem 0 1.6rem'>Projects under this pillar</h2><div class='pg'>{cards}</div>", 'paper')}
{cta_band(f"Support {pil['label']}.",
          'Donate to this pillar directly, or explore the other ways to get involved.',
          [('Donate', RAISELY_DONATE, 'btn-p'), ('Ways to get involved', 'ways-you-can-get-involved.html', 'btn-o')])}'''
        write_page(pil['page'], pil['label'], pil['desc'], body)

    print(f"projects: {len(projects)} pages, 3 pillar pages, data/projects.json written")
    from collections import Counter
    print('pillar split:', Counter(p['pillar'] for p in projects))

if __name__ == '__main__':
    main()
