"""Three exemplar project pages with full content ported from the live site.

Run AFTER gen_projects.py (it skips these slugs). One long science-heavy page
(Warddeken), one medium partnership page (Southern Flinders), one short
completed-project page (Southern Highlands koalas).
"""
from site_lib import (write_page, hero_img, sec, two, cta_band, card,
                      RAISELY_DONATE, EXEMPLAR_SLUGS)
import json, os
from site_lib import ROOT

U = 'https://fnpw.org.au/wp-content/uploads/'

ACK_CSS = '''
.ackb{background:var(--euc-pale);border-left:5px solid var(--euc);border-radius:0 12px 12px 0;padding:1.4rem 1.6rem;margin:2rem 0}
.ackb .ey{margin-bottom:.4rem;display:block}
.upd{border:1px solid var(--rule);border-radius:14px;background:#fff;padding:1.6rem;margin-bottom:1.2rem}
.upd h3{color:var(--euc-deep);margin-bottom:.7rem}
.upd img{border-radius:8px;max-width:300px;height:auto;margin:.8rem .8rem 0 0}
.spl{columns:2;gap:2rem;font-size:.92rem}
@media(max-width:700px){.spl{columns:1}}
'''

def meta_panel(rows):
    items = ''.join(f'<div class="pmeta-i"><span>{k}</span><strong>{v}</strong></div>' for k, v in rows)
    return f'<div class="pmeta">{items}</div>'

def ack(text):
    return (f'<div class="ackb"><span class="ey">Acknowledgement of Country</span><p>{text}</p></div>')

def related(slug, pillar, label, cls):
    projects = json.load(open(os.path.join(ROOT, 'data/projects.json')))
    others = [p for p in projects if p['pillar'] == pillar and p['slug'] != slug][:3]
    cards = '\n'.join(card(p['slug'], p['title'], p['img'], label, cls, p['state'], '') for p in others)
    return sec(f'<span class="ey">More from this pillar</span>'
               f'<h2 style="margin:.8rem 0 1.6rem">Related projects</h2>'
               f'<div class="pg">{cards}</div>', 'paper')

CTA = cta_band('Help fund work like this.',
               'Every FNPW project is powered by donations, bequests and partnerships.',
               [('Donate', RAISELY_DONATE, 'btn-p'), ('Become a partner', 'partner.html', 'btn-o')])

def main():
    # ---------- 1. Remarkable Southern Flinders (Growing National Parks) ----------
    s = 'remarkable-southern-flinders'
    body = hero_img('Growing National Parks', 'Remarkable Southern Flinders',
        'Linking established parks, newly protected land and open reservoir country into one '
        'vast, connected park of national significance.', 'Remarkable Southern Flinders',
        U + '2021/02/square.jpg', 'Southern Flinders Ranges')
    body += sec(two(
        '<span class="ey">The project</span><h2 style="margin:.8rem 0 1.2rem">A new national park precinct for South Australia</h2>'
        '<p>Developing a Southern Flinders National Park precinct will create a new nature-based '
        'tourism destination for South Australia. It will connect the natural landscapes of the '
        'region and draw people into local communities. The project offers a rare opportunity to '
        'link well established national parks and conservation parks with land recently acquired '
        'for conservation and reservoir area opened for public use, to create a vast, connected '
        'park of national significance.</p>'
        '<h3 style="margin:1.6rem 0 .8rem">Project overview</h3>'
        '<p>The South Australian Government committed $5 million to establish the Southern '
        'Flinders Ranges National Park as part of the Parks 2025 strategy. Together, the community '
        'partners secured an additional $5 million from the Australian Government&rsquo;s Building '
        'Better Regions Fund.</p>'
        '<p>The establishment of the park closely involves the traditional owners of the land, the '
        'Nukunu Nation, who are also co-managers of the Telowie Gorge Conservation Park inside the '
        'greater precinct. Local communities have a key role in helping develop the park.</p>'
        '<p>Key projects within the precinct include:</p>'
        '<ul style="padding-left:1.2rem;display:grid;gap:.4rem;margin-top:.6rem">'
        '<li>upgrading visitor facilities</li>'
        '<li>upgrading and expanding campgrounds for a wider variety of camping experiences</li>'
        '<li>developing an international mountain biking destination at Mt Remarkable</li>'
        '<li>creating trails for hiking and cycling, including a new iconic multi-day trail</li></ul>',
        meta_panel([('Pillar', '<a href="growing-national-parks.html">Growing National Parks</a>'),
                    ('Year', '2020'), ('Where', 'South Australia'),
                    ('Status', 'Stage one complete'),
                    ('Partners', 'NPWS SA, Nukunu Nation, three councils, RDA Yorke &amp; Mid-North'),
                    ('Major sponsors', 'Building Better Regions Fund; SA Parks 2025 Strategy')])
        + ack('This project is undertaken on the traditional lands of the <strong>Nukunu nation</strong>. '
              'In the spirit of reconciliation we acknowledge the Traditional Owners of Country and '
              'recognise their continuing connection to land, waters and culture.')))
    body += sec(
        '<span class="ey">Latest news</span><h2 style="margin:.8rem 0 1.4rem">Progress on the ground</h2>'
        '<div class="upd"><h3>Stage one complete: 20km of new trails at Willowie</h3>'
        '<p>Twenty kilometres of new mountain bike trails have opened in Mount Remarkable National '
        'Park at Willowie. The new trails are family-friendly, catering for beginner through to '
        'intermediate riders, alongside new visitor facilities: a picnic area, accessible toilets '
        'and carpark improvements. At Wirrabarra, two new picnic shelters, a barbecue and upgraded '
        'facilities have been completed.</p></div>'
        '<div class="upd"><h3>The EPIC trail unveiled</h3>'
        '<p>Concept designs for the EPIC mountain biking trail have been unveiled, designed to the '
        'International Mountain Bike Association criteria for epic trail accreditation. The proposed '
        'route offers 37.5km of non-stop adventure, climbing to the summit of Mount Remarkable at '
        '950m above sea level before returning to Melrose, showcasing the unique ecology of the '
        'range with breathtaking views. It complements the trails at Willowie and grows the Melrose '
        'network to over 150km of singletrack.</p>'
        '<p><a class="btn-o" href="https://engagementhub.parks.sa.gov.au/southern-flinders-precinct">'
        'More at the SA parks engagement hub</a> '
        '<a class="btn-o" href="https://www.parks.sa.gov.au/parks/mount-remarkable-national-park#see-and-do">'
        'Visit Mount Remarkable National Park</a></p></div>')
    body += related(s, 'parks', 'Growing National Parks', 'pb-parks') + CTA
    write_page(f'project-{s}.html', 'Remarkable Southern Flinders',
        'The Remarkable Southern Flinders Project enhances visitor access, restores native habitat, '
        'and supports conservation in South Australia’s iconic ranges.', body, page_css=ACK_CSS)

    # ---------- 2. Southern Highlands Koala Conservation (Saving Species) ----------
    s = 'southern-highlands-koala-conservation'
    body = hero_img('Saving Species', 'Southern Highlands Koala Conservation',
        'Twenty koalas, GPS collars, and the map that now guides land-use decisions across the '
        'Wingecarribee Shire.', 'Southern Highlands Koala Conservation',
        U + '2021/02/Southern-Koala-05-scaled.jpg', 'Koala in the Southern Highlands')
    body += sec(two(
        '<span class="ey">The project</span><h2 style="margin:.8rem 0 1.2rem">Finding the Southern Highlands koalas</h2>'
        '<p>Twenty koalas were collared with GPS tracking devices in the Southern Highlands to learn '
        'more about where they live, their numbers, what trees they prefer to eat and shelter in, '
        'and their movements throughout the Southern Highlands shire corridors.</p>'
        '<h3 style="margin:1.6rem 0 .8rem">Project overview</h3>'
        '<p>The project provides a clear direction for the long-term conservation of koalas in the '
        'Southern Highlands, in three parts:</p>'
        '<ol style="padding-left:1.2rem;display:grid;gap:.6rem;margin-top:.6rem">'
        '<li>Locate koala populations and map key habitat and movement corridors throughout the '
        'Wingecarribee Shire, giving land managers the information they need to ensure sufficient '
        'habitat for koalas to live, breed and move about as they have done for millennia.</li>'
        '<li>Undertake site occupancy surveys and satellite collaring of 10-15 koalas in the local '
        'area, to tell us where koalas live and breed and how many there are.</li>'
        '<li>Map koala habitat and the corridors koalas use to move between colonies, to guide '
        'land-use planning and conservation investment so the Southern Highlands has a healthy, '
        'breeding koala population in 100 years.</li></ol>',
        meta_panel([('Pillar', '<a href="saving-species.html">Saving Species</a>'),
                    ('Year', '2015'), ('Where', 'New South Wales / Victoria'),
                    ('Status', 'Completed 2017'),
                    ('Lead partner', 'National Parks &amp; Wildlife Service NSW'),
                    ('Supported by', 'NSW Office of Environment &amp; Heritage'),
                    ('Funded by', 'FNPW supporters across Australia and beyond')])
        + ack('FNPW supports projects across Australia. In the spirit of reconciliation we '
              'acknowledge the Traditional Owners of Country and recognise their continuing '
              'connection to land, waters and culture.')))
    body += sec(
        '<span class="ey">Outcomes</span><h2 style="margin:.8rem 0 1.4rem">What the tracking showed</h2>'
        '<div class="upd"><h3>Project report</h3>'
        '<p>The twenty collared koalas were monitored for up to 8 months, with ground visits once '
        'to twice a week. The data allowed development of a list of key tree species used by koalas '
        'in the Southern Highlands, increasing the number of known koala-favoured trees in the '
        'region by 50%.</p>'
        '<p>This measure of success has been used by the OEH to inform submissions to the SEPP44 '
        'review by the Department of Planning and the statewide koala mapping project under the '
        'NSW Koala Strategy.</p>'
        f'<img src="{U}2021/02/Path-of-a-tracked-koala-300x169.jpg" alt="Path of a tracked koala" loading="lazy">'
        '<p style="font-size:.85rem;color:var(--stone)">Path of a tracked koala</p></div>')
    body += related(s, 'species', 'Saving Species', 'pb-species') + CTA
    write_page(f'project-{s}.html', 'Southern Highlands Koala Conservation',
        'The Southern Highlands Koala Conservation project protects local koala populations through '
        'habitat restoration, community action, and threat reduction.', body, page_css=ACK_CSS)

    # ---------- 3. Warddeken Mayh (long, Indigenous-led, Saving Species) ----------
    s = 'warddeken-mayh'
    SPECIES = [
        'Arnhem Rock-rat <em>(Zyzomys maini)</em> VU (NT), VU (National)',
        'Black Wallaroo <em>(Macropus bernardu)</em> Data deficient',
        'Black-footed Tree-rat <em>(Mesembriomys gouldii)</em> VU (NT), EN (National)',
        'Brush-tailed Rabbit-rat <em>(Conilurus penicillatus)</em> EN (NT), VU (National)',
        'Fawn Antechinus <em>(Antechinus bellus)</em> EN (NT), VU (National)',
        'Golden-backed Tree-rat <em>(Mesembriomys macrurus)</em> CR (NT), VU (National)',
        'Kakadu Dunnart <em>(Sminthopsis bindi)</em> Data deficient',
        'Nabarlek <em>(Petrogale concinna)</em> VU (NT), EN (National)',
        'Northern Brush-tailed Phascogale <em>(Phascogale pirata)</em> EN (NT), VU (National)',
        'Northern Hopping-mouse <em>(Notomys aquilo)</em> VU (NT), VU (National)',
        'Northern Quoll <em>(Dasyurus hallucatus)</em> CR (NT), EN (National)',
        'Pale Field-rat <em>(Rattus tunneyi)</em> VU (NT)',
        'Red-cheeked Dunnart <em>(Sminthopsis virginiae)</em> Data deficient',
    ]
    sp_list = ''.join(f'<li>{x}</li>' for x in SPECIES)
    body = hero_img('Saving Species', 'Warddeken Mayh Recovery Project',
        'Indigenous-led recovery of threatened mammals across 1.4 million hectares of the '
        'Warddeken Indigenous Protected Area.', 'Warddeken Mayh',
        U + '2021/01/Lorina-and-Tinnesha-in-EPBC-protected-sandstone-shrublands_photo-Donal-Sullivan5f911988b9c1d-scaled.jpg',
        'Rangers in EPBC protected sandstone shrublands, photo Donal Sullivan')
    body += sec(two(
        '<span class="ey">The project</span><h2 style="margin:.8rem 0 1.2rem">Recovering mayh on Country</h2>'
        '<p>In the face of catastrophic and ongoing mammal declines in northern Australia, the '
        'Warddeken Mayh Recovery Project seeks to improve the status of key mammal species in the '
        'Warddeken IPA through informed adaptive management of key threatening processes. Of the '
        'mammal species targeted by the monitoring activities, 30% are listed as threatened in the '
        'NT and nationally.</p>'
        '<h3 style="margin:1.6rem 0 .8rem">Project overview</h3>'
        '<p>At the centre of this project is the Mayh Monitoring Network, a long-term ecological '
        'monitoring program established in 2017: 120 monitoring sites strategically located across '
        'the IPA, sampled using remote sensing cameras. Warddeken rangers resampled 36 sites this '
        'field season and are processing the 900,000 images collected.</p>'
        '<p>Over 50% of the distribution of the nationally endangered Arnhem Plateau Sandstone '
        'Shrubland Complex occurs in the IPA. The causes of decline are landscape scale, often '
        'insidious, and involve the interplay of multiple threats: inappropriate fire regimes, '
        'feral herbivores, feral cats and Cane Toads, weeds and potentially disease.</p>'
        '<p>Managing 1.4 million hectares including close to 50% of the Arnhem Plateau, Warddeken '
        'Land Management Limited is uniquely placed to make substantial recovery and conservation '
        'gains. Baseline sampling has already revealed previously unrecorded populations of the '
        'nationally endangered Northern Quoll and Black-footed Tree-rat. Without a robust '
        'monitoring regime, WLML could not evaluate the effect of management actions and amplify '
        'their success.</p>'
        '<h3 style="margin:1.6rem 0 .8rem">Threatened mammals sampled by camera trap</h3>'
        f'<ul class="spl" style="padding-left:1.2rem">{sp_list}</ul>',
        meta_panel([('Pillar', '<a href="saving-species.html">Saving Species</a>'),
                    ('Year', '2020'), ('Where', 'Northern Territory'),
                    ('Status', 'Ongoing'),
                    ('Lead partner', '<a href="https://www.kkt.org.au">Karrkad Kanjdji Trust (KKT)</a>'),
                    ('Delivered by', 'Warddeken Land Management Limited'),
                    ('Funded by', 'FNPW supporters across Australia and beyond')])
        + ack('FNPW supports projects across Australia. In the spirit of reconciliation we '
              'acknowledge the Traditional Owners of Country and recognise their continuing '
              'connection to land, waters and culture.')))
    body += sec(
        '<span class="ey">Project updates</span><h2 style="margin:.8rem 0 1.4rem">News from the IPA</h2>'
        '<div class="upd"><h3>2022: tailored fire management for djabbo</h3>'
        '<p>The rangers have processed all photos from the grid at Barradj; sadly no quolls were '
        'captured. The site was hit by a very intense late dry season fire in 2020, though gorges '
        'radiating from the area mean quolls may remain in the region. Other threatened species '
        'were recorded, including the northern brown bandicoot, black-footed tree-rat and '
        'white-throated grasswren, so the plan is tailored fire management to bring the site back '
        'to suitable quoll habitat. This year 38 camera sites are planned in a single deployment.</p>'
        f'<img src="{U}2021/01/Mayh-Update-214x300.jpg" alt="Mayh monitoring poster summary" loading="lazy">'
        '<p style="font-size:.85rem;color:var(--stone)">Poster summary of the long-term Mayh '
        'Monitoring Program results</p></div>'
        '<div class="upd"><h3>2021: daluk rangers lead new research</h3>'
        '<p>FNPW support allowed Warddeken to begin investigating the extent of two Northern Quoll '
        '(djabbo) populations uncovered through the monitoring program, establishing a 70 camera '
        'station grid at each site to understand djabbo and feral cat populations.</p>'
        '<p>In exciting developments, senior daluk (female) rangers from the Manmoyi ranger base '
        'designed and began a second research project investigating a suspected decline of the '
        'Orange-footed Scrub-fowl (kurrkurlanj), a culturally important species. This project is a '
        'bininj (Indigenous) priority, with the daluk team leading all field work.</p></div>'
        '<div class="upd"><h3>2020: finding yok</h3>'
        '<p>The Northern Brown Bandicoot (yok) is the largest of Australia&rsquo;s bandicoots. '
        'Significant grass cover is a key requirement: when understory is severely burnt by large '
        'late-season fires, or denuded by buffalo and pig, yok are susceptible to predation. When '
        'those threats are mitigated, populations can rebound quickly.</p>'
        '<p>The Mayh Monitoring Project has located 20 populations of yok in the IPA, commonly in '
        'areas with gentle, patchy and early fire regimes and dense grass and midstorey. Yok are '
        'important to bininj: there are bandicoot-dreaming sites across the landscape, roles in '
        'ceremony, representations in rock art, and yok remain a prized food source. Senior people '
        'have observed a decline over the past 20 years, and Landowners have been heartened to see '
        'yok in the images coming from the Monitoring Project.</p>'
        f'<img src="{U}2021/01/yok2-300x225.jpg" alt="Yok, northern brown bandicoot" loading="lazy">'
        f'<img src="{U}2021/01/Yok-in-WIPA-300x212.jpg" alt="Yok in the Warddeken IPA" loading="lazy">'
        '<p style="font-size:.85rem;color:var(--stone)">Photos courtesy of Warddeken Land Management</p></div>')
    body += related(s, 'species', 'Saving Species', 'pb-species') + CTA
    write_page(f'project-{s}.html', 'Warddeken Mayh Recovery Project',
        'The Warddeken Mayh Recovery Project protects native species through Indigenous land '
        'management, cultural knowledge, and ecological conservation efforts.', body, page_css=ACK_CSS)

    print('exemplars written:', ', '.join(sorted(EXEMPLAR_SLUGS)))

if __name__ == '__main__':
    main()
