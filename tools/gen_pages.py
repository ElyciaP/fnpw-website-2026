"""Generate the static pages matching live fnpw.org.au URLs we are keeping.

Copy marked with port() must be brought across from the live site before launch.
Grants pages are intentionally absent (FNPW no longer runs grants).
"""
import os, re, glob
from site_lib import (ROOT, write_page, hero, sec, two, port, cta_band, faq,
                      RAISELY_DONATE, RAISELY_HERO)

GAT = 'https://gift-a-tree.fnpw.org.au'
P = []  # (fname, title) collected for the search index

def add(fname, title, desc, body, **kw):
    write_page(fname, title, desc, body, **kw)
    P.append((fname, title))

def linkcards(items):
    tiles = ''.join(
        f'<a class="lc rv" href="{href}"><h3>{t}</h3><p>{d}</p><span class="lc-go">&rsaquo;</span></a>'
        for t, d, href in items)
    return f'<div class="lcg">{tiles}</div>'

def rows(items):
    """Editorial index list (shared .hx-row components from global.css)."""
    pal = ['var(--wattle-soft)', 'var(--euc-pale)', 'var(--waratah-pale)', 'var(--reef-pale)']
    out = ['<div class="hx-help-list">']
    for i, (t_, d, href) in enumerate(items):
        out.append(
            f'<a class="hx-row rv" href="{href}" style="--rowc:{pal[i % 4]}">'
            f'<span class="hx-row-i">{i+1:02d}</span>'
            f'<span><h3>{t_}</h3><p>{d}</p></span>'
            f'<span class="hx-row-a">&#8594;</span></a>')
    out.append('</div>')
    return ''.join(out)

DONATE_CTA = cta_band('Ready to make a difference?',
    'Your donation grows national parks, saves species and heals the land.',
    [('Donate now', RAISELY_DONATE, 'btn-p'), ('Become a Habitat Hero', RAISELY_HERO, 'btn-o')])

def main():
    # ---- Get Involved hub ----
    add('ways-you-can-get-involved.html', 'Ways to Get Involved',
        'Donate, volunteer, partner, fundraise or leave a gift in your Will. Every way to support FNPW.',
        hero('Get involved', 'Every way to stand with natural Australia.',
             'However you want to help, there is a way that fits. Choose yours.', 'Get Involved')
        + sec(rows([
            ('Donate', 'A one-off gift, put to work where it is needed most.', 'donate.html'),
            ('Become a Habitat Hero', 'Monthly giving that funds long-term recovery.', RAISELY_HERO),
            ('Gift a Tree', 'A tree planted for someone you love.', 'gift-a-tree.html'),
            ('Corporate volunteering', 'Bring your team out for a planting day.', 'volunteer.html'),
            ('Become a partner', 'Corporate and philanthropic partnerships.', 'partner.html'),
            ('Workplace giving', 'Small regular gifts from your pay, often matched by employers.', 'workplace-giving.html'),
            ('Fundraise for us', 'Run, bake, climb or host in support of FNPW.', 'fundraising-with-fnpw.html'),
            ('Leave a gift in your Will', 'A bequest that protects what you love, forever.', 'bequests.html'),
            ('Donate land', 'Give land a permanent future in the protected estate.', 'donate-land.html'),
        ])) + DONATE_CTA)

    # ---- partnership + giving pages ----
    add('project-partnerships.html', 'Government &amp; Project Partnerships',
        'FNPW partners with government agencies and land managers to deliver conservation outcomes.',
        hero('Partnerships', 'Conservation is a team sport.',
             'We work alongside national parks services, government agencies and land managers '
             'across Australia to deliver projects none of us could do alone.', 'Project Partnerships')
        + sec(two('<h2>How our project partnerships work</h2>'
                  '<p>We fund and coordinate; our partners bring land management expertise and boots '
                  'on the ground. Together we have added land to the protected estate, recovered '
                  'threatened species and restored damaged country for over 55 years.</p>'
                  + port('partnership process copy from fnpw.org.au/project-partnerships/'),
                  '<h3>Talk to us about a project</h3>'
                  '<p>If your agency or organisation has a conservation project that needs a partner, '
                  'we would love to hear about it.</p>'
                  '<p><a class="btn-p" href="contact.html">Contact us</a></p>'))
        + DONATE_CTA)

    add('workplace-giving.html', 'Workplace Giving',
        'Support FNPW with a small regular donation from your pre-tax pay.',
        hero('Get involved', 'Workplace giving.',
             'A small amount from each pay, before tax, often matched by your employer. '
             'Set and forget, and it adds up to habitat.', 'Workplace Giving')
        + sec(two('<h2>How it works</h2>'
                  '<p>Ask your payroll team to add the Foundation for National Parks &amp; Wildlife '
                  'as a workplace giving recipient. Donations come out of pre-tax pay, so there is '
                  'nothing to claim at tax time, and many employers match staff giving dollar for dollar.</p>',
                  '<h3>Details payroll will need</h3>'
                  '<p>Foundation for National Parks &amp; Wildlife<br>ABN 90 107 744 771<br>'
                  'Registered charity with the ACNC, endorsed as a Deductible Gift Recipient (DGR).</p>'
                  + port('any existing workplace giving platform links (Good2Give, Benevity etc.)')))
        + DONATE_CTA)

    add('fundraising-with-fnpw.html', 'Fundraising with FNPW',
        'Run, bake, climb or host an event in support of FNPW.',
        hero('Get involved', 'Fundraise for the bush.',
             'Birthdays, fun runs, morning teas, mountain climbs. Turn your thing into '
             'habitat for wildlife.', 'Fundraising')
        + sec(two('<h2>Start a fundraiser</h2>'
                  '<p>Create a fundraising page, set a goal and share it. Every dollar you raise '
                  'goes to growing national parks, saving species and healing the land.</p>'
                  f'<p><a class="btn-p" href="{RAISELY_DONATE}">Start fundraising</a></p>',
                  '<h3>We will help</h3>'
                  '<p>We can supply logos, photos, impact stats and ideas. '
                  '<a href="contact.html">Get in touch</a> and tell us what you are planning.</p>'))
        + DONATE_CTA)

    add('donate-land.html', 'Donate Land',
        'Give land a permanent future in Australia\'s protected estate.',
        hero('Get involved', 'Donate land.',
             'Some gifts are measured in hectares. Land with conservation value can become '
             'part of the protected estate, safe forever.', 'Donate Land')
        + sec(two('<h2>How land donation works</h2>'
                  '<p>We assess the conservation value of the land, then work with you and the '
                  'relevant parks service on the pathway: addition to a national park, a covenant, '
                  'or sale with proceeds funding conservation. Every situation is different, and we '
                  'treat every offer with care.</p>' + port('process detail from fnpw.org.au/donate-land/'),
                  '<h3>Start the conversation</h3>'
                  '<p>Contact us for a confidential discussion about your land.</p>'
                  '<p><a class="btn-p" href="contact.html">Contact us</a></p>'))
        + DONATE_CTA)

    # ---- donation SEO pages ----
    add('how-your-contributions-help.html', 'How Your Contributions Help',
        'Where FNPW donations go and what they achieve.',
        hero('Donate', 'Where your money goes.',
             'Every donation is put to work across our three pillars. Here is what that looks like.',
             'How Your Contributions Help')
        + sec(linkcards([
            ('Growing National Parks', 'Buying high-value land and adding it to the protected estate.', 'growing-national-parks.html'),
            ('Saving Species', 'Funding recovery programs for threatened plants and animals.', 'saving-species.html'),
            ('Healing the Land', 'Restoring habitat, waterways and cultural land management.', 'healing-the-land.html'),
        ]) + port('impact stats and examples from fnpw.org.au/how-your-contributions-help/'))
        + DONATE_CTA)

    add('why-your-support-is-needed.html', 'Why Your Support Is Needed',
        'Australia has one of the worst extinction records on Earth. Your support changes that.',
        hero('Donate', 'Why your support matters.',
             'Australia is home to species found nowhere else, and one of the worst extinction '
             'records on Earth. Support is not optional; it is the whole mechanism.', 'Why Your Support Is Needed')
        + sec('<h2>The case for giving</h2>'
              + port('statistics and narrative from fnpw.org.au/why-your-support-is-needed/')
              + '<p>When you give, you are not funding awareness. You are funding hectares, '
              'seedlings, nest boxes, rangers and science.</p>')
        + DONATE_CTA)

    # ---- about / governance ----
    add('corporate-governance.html', 'Corporate Governance',
        'FNPW board, constitution, policies and financial accountability.',
        hero('About us', 'Corporate governance.',
             'We are accountable to our supporters, our partners and the ACNC. '
             'Here is how the organisation is run.', 'Corporate Governance')
        + sec(two('<h2>Our board and policies</h2>'
                  + port('board structure, constitution, policies from fnpw.org.au/corporate-governance/'),
                  '<h3>Reports and financials</h3>'
                  '<p>Our annual reports and audited financials are available on the '
                  '<a href="reports.html">Reports</a> page. FNPW is registered with the ACNC and '
                  'endorsed as a Deductible Gift Recipient. ABN 90 107 744 771.</p>')))

    # RAP: content ported verbatim from fnpw.org.au/reconciliation-action-plan/ (Apr 2025 version).
    # Any wording changes beyond layout require cultural sign-off.
    RAP_PDF = 'https://fnpw.org.au/wp-content/uploads/2025/04/FNWP-Reconciliation-Action-Plan-February-25-February-27.pdf'
    add('reconciliation-action-plan.html', 'Innovate Reconciliation Action Plan',
        'For a deeper look into our initiatives, goals, and commitments, download the full '
        'FNPW Innovate Reconciliation Action Plan 2025-2027.',
        hero('About us', 'Innovate Reconciliation Action Plan.',
             'Advancing reconciliation with First Nations Peoples.', 'Reconciliation Action Plan')
        + sec(two(
            '<h2 style="margin-bottom:1.2rem">Our commitment</h2>'
            '<p>At FNPW, we&rsquo;re committed to fostering reconciliation by building meaningful '
            'partnerships with Aboriginal and Torres Strait Islander communities. Our '
            '<strong>Innovate Reconciliation Action Plan</strong> for 2025-2027 formalises this '
            'commitment, guiding our efforts to support cultural recognition, environmental '
            'stewardship, and sustainable conservation efforts led by First Nations peoples.</p>'
            '<h3 style="margin:1.6rem 0 .8rem">Our vision for reconciliation</h3>'
            '<p>FNPW recognises that Aboriginal and Torres Strait Islander peoples are the '
            '<strong>Traditional Custodians</strong> of Australia&rsquo;s lands, waters, and '
            'biodiversity. Our vision is to honour First Nations knowledge, cultures, and '
            'contributions by embedding respect, recognition, and collaboration into our '
            'conservation initiatives. Through our RAP, we aim to:</p>'
            '<ul style="padding-left:1.2rem;display:grid;gap:.5rem;margin-top:.8rem">'
            '<li>Strengthen relationships with First Nations communities</li>'
            '<li>Enhance cultural understanding within our organisation</li>'
            '<li>Recognise and integrate the scientific and cultural knowledge of Aboriginal and '
            'Torres Strait Islander communities to support their leadership in conservation efforts</li>'
            '<li>Support community-led environmental programs</li></ul>',
            '<div class="pmeta"><h3 style="margin-bottom:.8rem">Key initiatives in our RAP</h3>'
            '<ul style="padding-left:1.1rem;display:grid;gap:.7rem">'
            '<li><strong>Community partnerships:</strong> working with First Nations communities to '
            'grow national parks, save native species, and restore degraded lands.</li>'
            '<li><strong>Cultural recognition:</strong> promoting cultural learning, participating in '
            'National Reconciliation Week and NAIDOC Week, and embedding Aboriginal and Torres Strait '
            'Islander cultural protocols.</li>'
            '<li><strong>Employment &amp; procurement:</strong> increasing opportunities for Aboriginal '
            'and Torres Strait Islander employment, professional development, and business engagement.</li>'
            '<li><strong>Governance &amp; accountability:</strong> establishing a strong framework to '
            'measure our progress and impact.</li></ul></div>'))
        + sec('<div style="text-align:center"><span class="ey">The full plan</span>'
              '<h2 style="margin:.8rem 0 1rem">FNPW Innovate Reconciliation Action Plan 2025-2027</h2>'
              '<p class="lede" style="margin:0 auto 1.8rem;max-width:50ch">For a deeper look into our '
              'initiatives, goals, and commitments, read the full plan.</p>'
              '<div style="display:flex;gap:1rem;justify-content:center;flex-wrap:wrap">'
              '<a class="btn-p" href="https://heyzine.com/flip-book/52077716c5.html">Read online</a>'
              f'<a class="btn-o" href="{RAP_PDF}">Open PDF</a></div></div>', 'paper'))

    add('faqs.html', 'FAQs', 'Frequently asked questions about donating to and working with FNPW.',
        hero('Help', 'Frequently asked questions.',
             'Quick answers about donations, receipts, volunteering and more.', 'FAQs')
        + sec(''.join([
            faq('Is my donation tax deductible?',
                'Yes. FNPW is endorsed as a Deductible Gift Recipient, so donations of $2 or more '
                'are tax deductible. We email receipts automatically.'),
            faq('Where does my money go?',
                'Across our three pillars: growing national parks, saving species and healing the land. '
                'See <a href="how-your-contributions-help.html">how your contributions help</a>.'),
            faq('Can my company volunteer with you?',
                'Yes, we run corporate planting and restoration days in most capital cities. '
                'See <a href="volunteer.html">corporate volunteering</a>.'),
            faq('How do I leave a gift in my Will?',
                'Our <a href="bequests.html">bequests page</a> explains the process and the wording '
                'your solicitor needs. You can also call us for a confidential chat on 1800 898 626.'),
            faq('How do I gift a tree?',
                f'Through our <a href="{GAT}">Gift a Tree</a> program. We plant a native tree and '
                'send a certificate to your recipient.'),
            faq('How do I contact FNPW?',
                'Email us via the <a href="contact.html">contact page</a> or call 1800 898 626. '
                'Post: GPO Box 2666, Sydney NSW 2001.'),
        ])))

    add('media-enquiry.html', 'Media Enquiries', 'Media contact for FNPW.',
        hero('News', 'Media enquiries.',
             'Talking wildlife, national parks or a specific FNPW project? We can help with '
             'interviews, imagery and background.', 'Media Enquiries')
        + sec(two('<h2>Get in touch</h2>'
                  '<p>Email <a href="mailto:fnpw@fnpw.org.au">fnpw@fnpw.org.au</a> with '
                  '"Media enquiry" in the subject line, or call 1800 898 626. '
                  'We respond fastest to email.</p>',
                  port('media enquiry form (Formidable) from fnpw.org.au/media-enquiry/'))))

    # ---- newsletter, thanks, legal, utility ----
    add('newsletters-sign-up.html', 'Newsletter Sign-up',
        'Get epaws, the FNPW email newsletter.',
        hero('Stay close', 'Get epaws in your inbox.',
             'Project updates, species spotlights and ways to help, straight from the bush.', 'Newsletter')
        + sec('<div class="hs-form-frame">' + port('HubSpot form embed code from the live site') + '</div>'))

    add('thank-you.html', 'Thank You', 'Thank you for supporting FNPW.',
        hero('Thank you', 'You are officially one of the good ones.',
             'Your support grows national parks, saves species and heals the land. '
             'We will be in touch soon.', 'Thank You')
        + sec('<p style="text-align:center"><a class="btn-p" href="projects.html">See what you are supporting</a></p>'))

    add('privacy-policy.html', 'Privacy Policy', 'How FNPW collects, uses and protects personal information.',
        hero('Legal', 'Privacy policy.', 'How we collect, use and protect your information.', 'Privacy Policy')
        + sec(port('full policy text from fnpw.org.au/privacy-policy/ (legal content, port verbatim)')))

    add('terms-and-conditions.html', 'Terms &amp; Conditions', 'FNPW website terms and conditions.',
        hero('Legal', 'Terms &amp; conditions.', 'The terms that govern use of this website.', 'Terms &amp; Conditions')
        + sec(port('full terms text from fnpw.org.au/terms-and-conditions/ (legal content, port verbatim)')))

    # ---- corporate volunteering city pages ----
    cities = {
        'sydney': ('Sydney', 'NSW'), 'melbourne': ('Melbourne', 'VIC'),
        'brisbane': ('Brisbane', 'QLD'), 'adelaide': ('Adelaide', 'SA'),
        'perth': ('Perth', 'WA'),
    }
    for slug, (city, state) in cities.items():
        add(f'corporate-volunteering-{slug}.html', f'Corporate Volunteering {city}',
            f'Corporate volunteering days with FNPW in {city}.',
            hero('Corporate volunteering', f'Volunteering days in {city}.',
                 f'Bring your team out of the office and into the bush. Planting and restoration '
                 f'days near {city}, run with our project partners.', f'Corporate Volunteering / {city}')
            + sec(two(f'<h2>A day in the field, {state}</h2>'
                      '<p>Your team plants natives, clears weeds or builds habitat alongside our '
                      'project partners, with all tools, guidance and safety covered. Most groups '
                      'tell us it is the best team day they have done.</p>'
                      + port(f'site details, photos and dates from fnpw.org.au/corporate-volunteering/{slug}/'),
                      '<h3>Book a day</h3>'
                      '<p>Days fill early, especially in planting season. '
                      '<a href="contact.html">Contact us</a> to check dates near ' + city + '.</p>'
                      '<p><a class="btn-p" href="contact.html">Enquire now</a></p>'))
            + DONATE_CTA)

    # ---- campaign template (bush.fnpw.org.au style, reusable) ----
    add('campaign.html', 'Campaign Template', 'Reusable campaign landing page template.',
        '''<section class="cmp-hero"><div class="cmp-hero-grain"></div>
  <div class="cw cmp-hero-g rv">
    <div>
      <span class="cmp-ey"><span class="cmp-ey-dot"></span>Campaign template</span>
      <h1 class="cmp-h1">Big campaign headline goes here.</h1>
      <p class="cmp-lede">One sentence that makes the stakes obvious and the ask simple.</p>
      <div class="cmp-btns"><a class="cmp-btn-p" href="''' + RAISELY_DONATE + '''">Donate now</a>
      <a class="cmp-btn-g" href="#story">Read the story</a></div>
      <div class="prog-wrap"><div class="prog"><i style="width:62%"></i></div>
      <p class="prog-lbl"><strong>$62,000</strong> raised of $100,000 goal</p></div>
    </div>
    <div class="cmp-hero-im"><img src="https://raisely-images.imgix.net/bring-back-the-bush/uploads/emu-blue-sky-v-2-png-5d1b82.png" alt=""></div>
  </div>
</section>
''' + sec('<span class="ey" id="story">The story</span><h2 style="margin:.8rem 0 1.2rem">Why this campaign exists</h2>'
          '<p>Campaign narrative goes here. Swap this template\'s copy, imagery and progress '
          'figures per campaign; the layout and components stay the same. This is the page type '
          'that used to require a Raisely subdomain.</p>', 'paper')
        + cta_band('The final word.', 'End with the ask, once more, plainly.',
                   [('Donate now', RAISELY_DONATE, 'btn-p')]))

    # ---- search page with generated index ----
    all_pages = sorted(glob.glob(os.path.join(ROOT, '*.html')))
    index = []
    for f in all_pages:
        base = os.path.basename(f)
        if base in ('404.html', 'search.html'):
            continue
        content = open(f).read()
        if '<!-- removed -->' in content or len(content) < 200:
            continue
        m = re.search(r'<title>(.*?)</title>', content, re.S)
        t = re.sub(r'\s*\|.*', '', m.group(1)).strip() if m else base
        index.append([base, t.replace('&amp;', '&')])
    import json as _json
    idx_js = _json.dumps(index)
    add('search.html', 'Search', 'Search the FNPW website.',
        hero('Search', 'Find what you are after.', 'Search pages and projects across the site.', 'Search')
        + sec('<input id="q" class="srch" type="search" placeholder="Try: koala, volunteering, bequests" autofocus>'
              '<ul id="res" class="srch-res"></ul>'),
        extra_js='''<script>
const IDX = ''' + idx_js + ''';
const q = document.getElementById('q'), res = document.getElementById('res');
q.addEventListener('input', () => {
  const v = q.value.trim().toLowerCase();
  res.innerHTML = !v ? '' : IDX.filter(([f, t]) => t.toLowerCase().includes(v) || f.includes(v))
    .slice(0, 30).map(([f, t]) => `<li><a href="${f}">${t}</a></li>`).join('') || '<li>No results. Try another word?</li>';
});
</script>''')

    print(f'static pages generated: {len(P)}')

if __name__ == '__main__':
    main()
