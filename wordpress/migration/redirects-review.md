# Redirect map review

Written by `build_redirects.py`. `redirects.csv` is the full set for launch: 319 redirects, from 311 on live plus 17 the new site needs.

Because Redirection adds imported rows without replacing old ones, the launch step is: export a backup, delete the existing redirects, then import `redirects.csv`.

| Change | Count |
|---|---|
| Broken on live, repaired (page was renamed, please review the match) | 8 |
| Broken on live, repaired (same page found at its current address) | 9 |
| Broken on live, sent to the closest page (please review) | 6 |
| Chain shortened | 16 |
| Dropped (disabled on live) | 3 |
| Dropped (placeholder or test row) | 2 |
| Old giving site retired | 7 |
| Retargeted for the new site | 4 |
| Target is outside the page map but works on live | 1 |

## Broken on live, repaired (page was renamed, please review the match)

| Source | Target | Note |
|---|---|---|
| /news-and-events/bandicoot-super-highway-shifts-into-next-gear/ | /project/bandicoot-superhighway-project/ | was /project/bandicoot-super-highway/ |
| /news-and-events/building-bungalows-for-bandicoots/ | /project/bandicoot-superhighway-project/ | was /project/bandicoot-super-highway/ |
| /news-and-events/fnpw-to-support-the-creation-of-a-new-national-park-in-sa/ | /project/nilpena-nationalpark/ | was /project/nilpena-station/ |
| /news-and-events/nsw-private-land-conservation-grants-300k-funding-available/ | /project/private-land-conservation-grants/ | was /project/private-land-conservation-grants-2017/ |
| /news-and-events/one-of-australia-s-most-iconic-animals-is-threatened-with-numbers-already-dropping-by-80/ | /project/redlands-koala-planting/ | was /project/patfm-redlands-koala-planting/ |
| /news-and-events/celebrating-women-in-indigenous-ranger-programs-on-international-womens-day/ | /news/latest-news/first-nations-women-in-ranger-programs/ | was /news/latest-news/celebrating-women-in-indigenous-ranger-programs-on-international-womens-day/ |
| /news/uncategorized/september-is-biodiversity-month/ | /biodiversity-month/ | was /news/latest-blogs/september-is-biodiversity-month/ |
| /news/media/fnpw-new-chair-new-directors/ | /news/media/fnpw-new-chair-and-new-directors/ | was /news/latest-news/fnpw-new-chair-new-directors/ |

## Broken on live, repaired (same page found at its current address)

| Source | Target | Note |
|---|---|---|
| /latest-news-title-3/ | /news/latest-news/wildlife-heroes-large-durable-asset-grants-recipients-announced/ | was /wildlife-heroes-large-durable-asset-grants-recipients-announced/ |
| /latest-news-title/ | /news/latest-news/fnpw-announces-bushfire-emergency-appeal/ | was /fnpw-announces-bushfire-emergency-appeal/ |
| /latest-news-title-5/ | /news/latest-news/emergency-grants-provide-relief-for-nsw-wildlife-volunteers/ | was /emergency-grants-provide-relief-for-nsw-wildlife-volunteers/ |
| /latest-news-title-4/ | /news/latest-news/giving-australian-wildlife-volunteers-the-help-they-need/ | was /giving-australian-wildlife-volunteers-the-help-they-need/ |
| /latest-news-title-2/ | /news/latest-news/wildlife-heroes-wildlife-rescue-handbook-to-keep-animals-and-rescuers-safe-this-summer/ | was /wildlife-heroes-wildlife-rescue-handbook-to-keep-animals-and-rescuers-safe-this-summer/ |
| /victor-harbor-times-2/ | /news/media/byron-shire-news/ | was /byron-shire-news/ |
| /grants/conservation-project-grants/ | /project/community-conservation-grants/ | was /grant/community-conservation-grants/ |
| /news-and-events/ | /news/category/latest-news/ | was /category/latest-news/ |
| /news-and-events/healing-our-land-bushfire-recovery-grants-awarded/ | /news/latest-news/healing-our-land-emergency-bushfire-recovery-grants-awarded/ | was /healing-our-land-emergency-bushfire-recovery-grants-awarded/ |

## Broken on live, sent to the closest page (please review)

| Source | Target | Note |
|---|---|---|
| /donations-thankyou-page/ | /thank-you/ | was /donation-thank-you-plant-a-tree/, which returns 404 |
| /donation-thank-you-gift-a-tree-2/ | /thank-you/ | was /donation-thank-you-habitat-hero-monthly-gift/, which returns 404 |
| /donation-thank-you-gift-a-tree/ | /thank-you/ | was /donation-thank-you-plant-a-tree/, which returns 404 |
| /project-updates/plant-a-tree-for-me/ | /projects/ | was /project/plant-a-tree-for-me/, which returns 404 |
| /news/uncategorized/wombat-mange/ | /news/ | was /news/media/wombat-mange/, which returns 404 |
| /fnpw/fnpw/fundraising/donate-pages/appeals.aspx | / | was /unknown, which returns 404 |

## Chain shortened

| Source | Target | Note |
|---|---|---|
| /donations-listing/ | https://bush.fnpw.org.au | was /donations/ |
| /donations-thankyou-page/ | /donation-thank-you-plant-a-tree/ | was /donation-thank-you-gift-a-tree/ |
| /support/corporate-supporters/ | /corporate-partnerships/ | was /corporate-partners/ |
| /how-we-work/our-partners/ | /government-partnerships/ | was /project-partnerships/ |
| /appeals/ | https://bush.fnpw.org.au | was /donations/ |
| /wildlifeheroes/ | /project/wildlife-heroes/ | was /grant/wildlife-heroes-grants/ |
| /appeals/protect-our-native-animals/ | https://bush.fnpw.org.au | was /donations/ |
| /latest-updates/reconnecting-nectar-lovers/ | /project/nectar-sippers/ | was /project/nectarlovers/ |
| /appeals/grow-our-national-parks/ | https://bush.fnpw.org.au | was /donations/ |
| /appeals/current-appeal/ | https://bush.fnpw.org.au | was /donations/ |
| /donate-monthly/ | https://bush.fnpw.org.au | was /donations/ |
| /donation/gift-a-tree/ | https://giveatree.fnpw.org.au/ | was /donation/plant-a-tree/ |
| /test-post/ | /contact-us/ | was /test-post-upload/ |
| /test-post-upload/ | /contact-us/ | was /upload-your-blog-post/ |
| /volunteer-for-impact/ | /corporate-volunteering/ | was /thank-you-volunteer-for-impact/ |
| /corporate-volunteering/corporate-volunteering-nsw/ | /corporate-volunteering/sydney/ | was /corporate-volunteering/nsw/ |

## Dropped (disabled on live)

| Source | Target | Note |
|---|---|---|
| /news/uncategorized/frog-disease/ | /news/latest-blogs/frog-disease/ |  |
| /news/latest-blogs/frog-disease/ | /news/uncategorized/frog-disease/ |  |
| /news/latest-news/the-secret-lives-of-australian-freshwater-turtles/ | /news/latest-blogs/the-secret-lives-of-australian-freshwater-turtles/ |  |

## Dropped (placeholder or test row)

| Source | Target | Note |
|---|---|---|
| /source URL | target URL |  |
| /news/latest-news/test/ | /news/postie/test/ |  |

## Old giving site retired

| Source | Target | Note |
|---|---|---|
| /donation/healing-our-land/ | https://bush.fnpw.org.au | was https://support.fnpw.org.au/FNPW/Fundraising/FNPW-Gift-Items/Healing-Our-Land.aspx |
| /donation/growing-parks-and-saving-species/ | https://bush.fnpw.org.au | was https://support.fnpw.org.au/FNPW/Fundraising/FNPW-Gift-Items/Growing-parks-and-Saving-Species.aspx |
| /donation/healing-our-land/?giftid= | https://bush.fnpw.org.au | was https://support.fnpw.org.au/FNPW/Fundraising/FNPW-Gift-Items/Healing-Our-Land.aspx |
| /donation/become-a-habitat-hero-with-a-monthly-gift/?giftid= | https://habitat-heroes.fnpw.org.au | was https://support.fnpw.org.au/FNPW/Fundraising/FNPW-Gift-Items/Become-a-Habitat-Hero.aspx |
| /donation/plant-a-tree/?giftid= | https://giveatree.fnpw.org.au/ | was https://support.fnpw.org.au/FNPW/Fundraising/FNPW-Gift-Items/Plant-a-Tree.aspx |
| /donation/growing-parks-and-saving-species/?giftid= | https://bush.fnpw.org.au | was https://support.fnpw.org.au/FNPW/Fundraising/FNPW-Gift-Items/Growing-parks-and-Saving-Species.aspx |
| /donation/leave-a-legacy-for-the-future/ | https://bush.fnpw.org.au | was https://support.fnpw.org.au/FNPW/Fundraising/FNPW-Gift-Items/Healing-our-land.aspx |

## Retargeted for the new site

| Source | Target | Note |
|---|---|---|
| /donation/ | https://bush.fnpw.org.au | was /donations/ |
| /donation/become-a-habitat-hero-with-a-monthly-gift/ | https://habitat-heroes.fnpw.org.au | was https://support.fnpw.org.au/FNPW/Fundraising/FNPW-Gift-Items/Become-a-Habitat-Hero.aspx |
| /donation/healing-our-land-2/ | https://bush.fnpw.org.au | was https://support.fnpw.org.au/FNPW/Fundraising/FNPW-Gift-Items/Healing-our-land.aspx |
| /donation/plant-a-tree/ | https://giveatree.fnpw.org.au/ | was https://support.fnpw.org.au/FNPW/Fundraising/FNPW-Gift-Items/Plant-a-Tree.aspx |

## Target is outside the page map but works on live

| Source | Target | Note |
|---|---|---|
| /news/uncategorized/30765/ | /news/latest-news/30765/ | check on staging |
