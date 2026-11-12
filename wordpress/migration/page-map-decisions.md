# Page map decisions

The decision ids used in `page-map.csv`. Each row already carries the recommendation, so a yes means nothing changes. Once you decide, I update `build_page_map.py` and regenerate the csv.

## Live pages with no match in the build

| Live URL | What it is | Recommendation |
|---|---|---|
| /upload-your-blog-post/ | Front-end blog upload form (AccessPress Anonymous Post Pro) | Retire, redirect to /contact-us/ |
| /test-form/ | Test page | Retire, redirect to the homepage |
| /project/form-test/ | Not a test: the contractor expression of interest page, with a Formidable form | Retire and redirect to /projects/ if the call for contractors has closed; keep it if it's still open |
| /tech4forests/ | 2022 corporate fundraising landing page (COP15) | Redirect to /corporate-partnerships/ |
| /project-partnerships/ | Government partnerships copy | Redirect to the new /government-partnerships/ |
| /tax-deductible-charity-donation/ | Tax FAQs | Redirect to /faqs/, where those FAQs now sit |
| /annual-reports-financials/our-2024-impact-and-vision/ | 2024 Impact Report and Strategic Plan page | Redirect to /annual-reports-financials/, which carries the 2024 report |
| /grant/wildlife-heroes-grants/ | Wildlife Heroes grants page | Redirect to /project/wildlife-heroes/ |
| /welcome-to-fnpw/ (D4) | Supporter landing page | Redirect to the homepage once Reef confirms it isn't a Google Ads final URL |
| /thank-you-volunteer-for-impact/ (D4) | A Volunteer for Impact landing page, despite the slug | Redirect to /corporate-volunteering/ once Reef confirms the same |

Five pages the handover listed as unmatched do have a home: /paws-magazine/, /mitigating-effects-environmental-change/ and /fundraising-with-fnpw/ have pages in the build, and /koala-facts/ and /biodiversity-month/ were ported as articles (D6).

## Other decisions

- **D1. Keep the live URLs.** Pages the build replaces keep their live address, so about.html becomes /about-us/ and bequests.html becomes /bequest/. That avoids redirects and keeps Google Ads, EDM links, backlinks and form redirects working. The alternative is tidier URLs (/about/, /bequests/) with 301s. Recommended: keep.
- **D2. Blog post bodies.** The 164 static articles carry the same words as the live posts (15 checked, all within 2%), so this is about markup and design rather than copy. Option A keeps the live bodies and adds the build's standfirst, pillar, related stories and hero alt text as fields the new post template reads. Option B swaps each body for the build's block version, which matches your article design exactly, with the old body saved on the post for rollback. Recommended: B. The launch scope says the posts stay unchanged, so this one is yours.
- **D5. New page URLs.** Proposed from the file names: /growing-national-parks/, /saving-species/, /healing-the-land/, /government-partnerships/, /partner-invest/, /our-impact/, /in-the-news/, /bequests-professional-advisers/.
- **D6.** /koala-facts/ and /biodiversity-month/ stay pages at their current URLs, shown in the article layout.
- **D7.** /thank-you/ takes the build's general thank-you copy. On live it confirms a blog upload, which goes once /upload-your-blog-post/ retires. Task 8 shows which forms send people there.
- **D8. Donation pages.** The handover sends every donation page to bush.fnpw.org.au, while CLAUDE.md sends monthly giving to habitat-heroes.fnpw.org.au. Proposed: the monthly gift page goes to Habitat Heroes, the plant-a-tree page to Give a Tree and the rest to Bring Back the Bush.
- **D9. Project taxonomy archives** (38 URLs) stay, through one archive template, as recommended in the handover's open decisions.

## Decided by Ely, 10 November

- **D1.** Keep the live URLs.
- **D2.** Option B: the build's block version replaces each post body, with the old body saved for rollback.
- **D5.** New page URLs as proposed, except /partner-with-us/ (partner-invest.html) and /bequest/professional-advisers/ (bequests-professional-advisers.html). New projects follow /project/{slug}/.
- **D8.** Monthly giving goes to habitat-heroes.fnpw.org.au, Donate to bush.fnpw.org.au and Give a Tree to giveatree.fnpw.org.au.
- **Old wp/ folder.** Build fresh in wordpress/ and borrow what fits; wp/ stays untouched until after launch.

- **Contractor call.** Closed: /project/form-test/ and /test-form/ retire, redirecting to /projects/ and the homepage.

Still open: Reef's answer on /welcome-to-fnpw/ and /thank-you-volunteer-for-impact/ (D4).
