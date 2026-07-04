# FNPW design brief — paste this with every Claude design session

You are restyling one template page from the Foundation for National Parks & Wildlife website.
The page is self-contained HTML with all CSS inlined in a `<style>` block.

## Hard rules
1. **Do not rename, add or remove CSS classes, IDs, or restructure the HTML** unless the change
   is essential to the design. Every class maps to 121 generated pages; structural changes are
   expensive to port back. Prefer changing CSS only.
2. All colour changes go through the CSS custom properties in `:root`. Brand palette (fixed):
   Eucalyptus `#0F7768`, Deep Eucalyptus `#0F3132`, Wattle `#C4A927`, Waratah `#C23747`,
   Reef `#2C4B89`. You may adjust tints/shades and usage, not the core hues.
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
