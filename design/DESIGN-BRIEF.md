# FNPW design brief: paste this with every Claude Design session

You are restyling one template page from the Foundation for National Parks & Wildlife website.
The page is self-contained HTML with all CSS inlined in a `<style>` block.

## Hard rules
1. **Do not rename, add or remove CSS classes, IDs, or restructure the HTML** unless the change
   is essential to the design. Every class maps to 121 generated pages; structural changes are
   expensive to port back. Prefer changing CSS only.
2. All colour changes go through the CSS custom properties in `:root`, and only use the
   Brand Guidelines v1.0 palette (section 5.2): eight families of four tones.
   Greens (Eucalyptus) `#0F7768` `#0F3132` `#51B593` `#C6EBCA`
   Reds (Waratah) `#C23747` `#8C1422` `#ED4E61` `#FFADB7`
   Golds (Wattle) `#C4A927` `#9F8506` `#E1CD4A` `#F8EEA9`
   Earth `#AB7341` `#85735E` `#EEE8E1` `#FAF6F2`
   Blues `#2C4B89` `#202F54` `#5D7BC1` `#A8C4F3`
   Terracotta `#B64629` `#8E3821` `#E26539` `#FFAA8A`
   Purples `#703985` `#47243A` `#B790DE` `#DBD1EC`
   Deep browns `#371F1D` `#241914` `#956F6F` `#CBABAB`
   Each swatch's AA badge sets the approved text colour on that background. Pair within a
   family; mix families only with care. Donate and Send enquiry buttons are exempt from the
   pairing rules so they stay bright, but must still pass contrast.
3. Typography: **Sora** for display, **Figtree** for body, Caveat only as a rare accent.
4. Australian spelling. **No em dashes anywhere.** Always "&" in "Foundation for National
   Parks & Wildlife". Always "Kaurna Yarta", never "Kaurna Yerta".
5. Keep the dashed yellow `.port-note` boxes visible; they mark unfinished content, not design.
6. Donate buttons keep their existing hrefs (Raisely). Never invent donation amounts or stats.
7. WCAG AA: wattle `#C4A927` fails contrast on white for body text; use it for large display
   text or decoration only.

## What good looks like
Warm, grounded, editorial. A conservation charity with 55 years of history, not a tech startup.
Photography-forward, generous whitespace, confident type scale. The campaign components
(`cmp-*`) can be bolder and louder than the rest of the site.

## Output
Return the complete modified HTML file. Keep the `<!-- DESIGN PACK ... -->` comment at the top.
List at the end, in a comment, every selector you changed, so the changes can be merged into
the shared stylesheet mechanically.
