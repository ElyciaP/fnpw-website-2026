SOURCE: https://fnpw.org.au/mitigating-effects-environmental-change/
COMPLETE: yes. Body copy is taken verbatim from the raw HTML of the WP REST page content (/wp-json/wp/v2/pages?slug=mitigating-effects-environmental-change) and cross-checked against 3 fetches of the live page. The form markup is quoted from the raw HTML.
Discrepancy: the REST content ends with a paragraph "Ready to make an impact? Contact FNPW to learn how your organisation can play a crucial role in protecting the environment and promoting sustainability." The live page fetch explicitly reported that this sentence is NOT shown. It is kept at the end, marked as hidden. In the other direction, the live page shows consent text under the form that does not appear in the REST form markup.

PAGE META: WP page id (not captured), template views/template-flexible.blade.php, published 2023-04-20, modified 2023-06-07.

## FORM PLATFORM FINDING
**NOT HubSpot.** The form is **Formidable Forms (Pro)**, a WordPress plugin. It has none of the HubSpot markers: no hbspt / hsforms script, no portalId, no formId GUID, and no 441704788.
- `<form ... class="frm-show-form frm_pro_form" id="form_ebooksubmission">`
- Formidable form_id = 17, form_key = "ebooksubmission", legend "Ebook submission"
- Hidden fields: frm_action=create, form_id=17, form_key=ebooksubmission, frm_submit_entry_17 (nonce), frm_state, item_key
- Fields:
  1. **Name*** (required, combo field id 239, layout first_last): sub-inputs `item_meta[239][first]` (autocomplete given-name, description "First") and `item_meta[239][last]` (autocomplete family-name, description "Last"). Error text: "Name cannot be blank." / "Name is invalid"
  2. **Email*** (required, field 241, type=email, `item_meta[241]`). Error text: "Email cannot be blank." / "Email is invalid"
  3. Honeypot (field 274, `item_meta[274]`, class frm_verify): label "If you are human, leave this field blank." It is hidden and must not be shown to people.
- Submit button: "Submit"
- Consent text shown on the live page (not in the REST form markup): "By submitting the form, you agree to receive email updates about FNPW's work from time to time."
- Success message / eBook delivery: not visible in the page. It is presumably a Formidable confirmation action or email.

## eBOOK
- Title: Mitigating the effects of environmental change on Australia's fragile ecosystem
- Cover image (displayed size): https://fnpw.org.au/wp-content/uploads/2023/05/FNP1009_e-book_thumbnail_shadow-300x219.jpg
- Cover image (full size, media id 31824): https://fnpw.org.au/wp-content/uploads/2023/05/FNP1009_e-book_thumbnail_shadow.jpg
- Cover alt: "Ebook cover Mitigating the effects of environmental change on Australia's fragile ecosystem"
- eBook PDF URL: NOT visible on the page or in the page HTML. The media library has no match for "FNP1009" or "ebook" other than the cover. It is presumably delivered after the form is submitted.
- og/hero image reported: https://fnpw.org.au/wp-content/uploads/2023/03/FNPW-growing-parks-and-saving-species.png (this is the site-wide default og:image)

---

# Mitigating the effects of environmental change on Australia's fragile ecosystem

## How to make proactive contributions to reduce the impacts of environmental change beyond 2023

Despite its remarkable resilience, the Australian ecosystem is being pushed to its limits by the persistent impact of human-induced environmental change. Every year, the country is struck by catastrophic natural disasters, including devastating floods, damaging cyclones, record-breaking droughts, and raging bushfires , wreaking havoc on its precious landscape.

Although we are approaching the point of no return to halt the detrimental effects of environmental change, there is still hope. We can make a difference if we take swift action.

Discover how to save Australia's precious ecosystem from environmental catastrophe in the Foundation for National Parks & Wildlife's (FNPW) latest eBook, Mitigating the effects of environmental change on Australia's fragile ecosystem, that outlines collaborative strategies to combat environmental change, including:

- Prioritising a whole of system approach
- Coordinating funding and resourcing for projects, and
- Establishing short term and long-term goals.

Take action today to create a brighter future: Download the eBook and learn how you can make a meaningful and proactive contribution in 2023 and beyond.

![Ebook cover Mitigating the effects of environmental change on Australia's fragile ecosystem](https://fnpw.org.au/wp-content/uploads/2023/05/FNP1009_e-book_thumbnail_shadow-300x219.jpg)

<!-- Layout: on the live page the list/CTA copy and the cover image sit side by side (2-column table layout), followed by the form. -->

**[FORM: Ebook submission]**
Name* — First / Last
Email*
[Submit]

By submitting the form, you agree to receive email updates about FNPW's work from time to time.

<!-- In REST content only, NOT displayed on live page: -->
<!-- Ready to make an impact? Contact FNPW to learn how your organisation can play a crucial role in protecting the environment and promoting sustainability. -->

(The raw REST HTML has a space before the comma in "raging bushfires , wreaking". One live-page fetch rendered it as "bushfires, wreaking".)
