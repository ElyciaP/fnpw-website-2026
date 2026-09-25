SOURCE: https://habitat-heroes.raiselysite.com/

Fetched 2026-09-25 via WebFetch.

## Access notes
- https://habitat-heroes.raiselysite.com/ returns a 302 redirect to https://habitat-heroes.fnpw.org.au/ (canonical).
- https://habitat-heroes.fnpw.org.au/ needs JavaScript. The only visible body text is "You need to enable JavaScript to run this app."
- https://habitat-heroes.fnpw.org.au/donate returns 404. (The raiselysite /donate URL wasn't fetched separately; the root redirects to the fnpw.org.au host.)
- The public Raisely campaign config was readable at https://api.raisely.com/v3/campaigns/habitat-heroes?private=false. The page-content endpoints (/pages) returned 403 or 404, so the landing-page body copy (hero text, impact descriptions per amount, benefits) could NOT be retrieved.

## Meta tags (verbatim)
- Title: Habitat Heroes | Australia's Wildlife Needs You
- Meta description: Every year, more native species are pushed closer to extinction - but every dollar and small action can drive powerful change. Become a Habitat Hero today!
- og:title: Habitat Heroes | Australia's Wildlife Needs You
- og:description: Become a Habitat Hero Today
- og:image: https://raisely-images.imgix.net/habitat-heroes/uploads/54420729444-bbb-8004953-o-jpg-b1c472.jpg
- Canonical: https://habitat-heroes.fnpw.org.au/

## Campaign config (from Raisely API, values verbatim)
- Campaign name: "Habitat Heroes"; mode: LIVE; theme: special-conversionGivingDay
- theme.headlineText: "Habitat Heroes"
- theme.homeText: "<h3>Make a donation today to support Habitat Heroes</h3>"
- theme.footerText: "Copyright 2019 Habitat Heroes"
- theme.donationsText: "A tax receipt will be emailed to you once the donation has processed."
- social.facebookDescription: "Become a Habitat Hero Today"
- social.twitterTweet: "Habitat Heroes : Make a donation today to support Habitat Heroes"
- social.emailSubject: "Help me support [campaign]"

### Suggested amounts (stored in cents, currency AUD)
- One-off (ONCE): $30, $60, $80, $100
- Monthly (1 MONTH): $15, $25, $35, $45
- Other interval slots in the config (1 WEEK, 2 WEEK, 4 WEEK, 3 MONTH, 1 YEAR) have no preset amounts. Enabled intervals reported: ONCE, WEEK, MONTH, YEAR. Which of these the live form shows can't be confirmed without rendering the page.
- No per-amount impact descriptions were found in the campaign config. If any exist, they are in page blocks that couldn't be retrieved.
- Minimum/maximum donation, default amount/interval and processing-fee settings: not present in the readable config.
- Currency selection: enabled. Gift Aid: disabled.

### Upsell to monthly (verbatim)
- Step title: "Become a regular supporter"
- Step description: "Our regular supporters make all of our work possible! By making a monthly monthly donation, you give us the certainty we need to dream big." (the doubled "monthly monthly" is in the source)
- Nudge message: "Giving monthly has a greater impact"

### Thank-you screen (verbatim)
- Title: "Thank you for donating [donation.amount]!"
- Message: "Thank you so much [donation.firstName] for supporting FNPW."
- Confetti enabled.

### Stated benefits
- Tax receipt: "A tax receipt will be emailed to you once the donation has processed."
- Nothing was found about how often donors are charged, updates or newsletters, or how to cancel or change a gift.

## Related copy elsewhere on fnpw.org.au (verbatim, from /thank-you-volunteer-for-impact/)
"Become a Habitat Hero – Join Habitat Heroes to aid long-term conservation work. Your monthly contribution ensures a steady stream of support for restoring habitats, aiding recovery from natural disasters, and securing a brighter future for Australia's unique biodiversity."
