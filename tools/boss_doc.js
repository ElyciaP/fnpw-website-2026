const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        AlignmentType, LevelFormat, HeadingLevel, BorderStyle, WidthType,
        ShadingType } = require('docx');

const border = { style: BorderStyle.SINGLE, size: 1, color: 'CCCCCC' };
const borders = { top: border, bottom: border, left: border, right: border };
const CW = 9026; // A4 content width, 1" margins

function cell(text, { w, bold = false, fill = null } = {}) {
  return new TableCell({
    borders, width: { size: w, type: WidthType.DXA },
    shading: fill ? { fill, type: ShadingType.CLEAR } : undefined,
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    children: [new Paragraph({ children: [new TextRun({ text, bold })] })],
  });
}
function row(cells, widths, opts = {}) {
  return new TableRow({ children: cells.map((t, i) => cell(t, { w: widths[i], ...opts })) });
}
function h1(t) { return new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(t)] }); }
function h2(t) { return new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(t)] }); }
function p(t, opts = {}) { return new Paragraph({ spacing: { after: 160 }, children: [new TextRun({ text: t, ...opts })] }); }
function bullet(t) {
  return new Paragraph({ numbering: { reference: 'bullets', level: 0 }, spacing: { after: 80 },
    children: [new TextRun(t)] });
}

const TW = [1900, 4526, 2600];
const timeline = new Table({
  width: { size: CW, type: WidthType.DXA }, columnWidths: TW,
  rows: [
    row(['Weeks', 'Phase', 'Outcome'], TW, { bold: true, fill: 'EAF4ED' }),
    row(['1-2  (6-19 Jul)', 'Foundations: access confirmations, security cleanup and plugin updates on the current site, staging copy created', 'Current site safer; safe build environment ready'], TW),
    row(['3-5  (20 Jul-9 Aug)', 'Design: eight AI design sessions against the brand guidelines, applied across all 121 built pages', 'Full site design approved'], TW),
    row(['6-9  (10 Aug-6 Sep)', 'WordPress build: new theme and content system built and tested on the staging copy; all 85 project pages driven by the CMS', 'Working site on staging'], TW),
    row(['10-11  (7-20 Sep)', 'Content: remaining copy brought across, projects categorised under the three pillars, forms and newsletter wired and tested', 'Content complete'], TW),
    row(['12-13  (21 Sep-4 Oct)', 'Quality: SEO redirects, accessibility, performance, cross-browser testing', 'Launch checklist green'], TW),
    row(['14  (5-11 Oct)', 'Launch: full backup, switch-over, one week of close monitoring. One-click rollback to the old theme is available throughout', 'New site live'], TW),
    row(['15-16 buffer', 'Contingency for slippage (content season, sign-off lead times)', 'Live by late October'], TW),
  ],
});

const CWD = [3200, 2000, 3826];
const costs = new Table({
  width: { size: CW, type: WidthType.DXA }, columnWidths: CWD,
  rows: [
    row(['Item', 'Cost (AUD)', 'Notes'], CWD, { bold: true, fill: 'EAF4ED' }),
    row(['Claude Max subscription (AI developer), Jul-Oct', '$150/month x 4 = $600', 'Higher-usage tier needed for daily development sessions; incl. GST'], CWD),
    row(['Contingency month (if launch slips within October)', '$150', 'Only if needed'], CWD),
    row(['Hosting (SiteGround)', '$0 additional', 'Existing plan; staging included'], CWD),
    row(['ACF Pro, Yoast, Redirection, backups', '$0 additional', 'Already installed and licensed'], CWD),
    row(['Design, development, content migration', '$0', 'Done in-house (Elycia + AI) within existing hours'], CWD),
    row(['Total project cost', '$600-750', 'After launch, drops to Claude Pro at ~$34/month for site maintenance'], CWD),
    row(['Comparator: agency rebuild', '$30,000-80,000', 'Typical range for a bespoke charity site of this scope, excluding ongoing retainers'], CWD),
  ],
});

const doc = new Document({
  styles: {
    default: { document: { run: { font: 'Arial', size: 22 } } },
    paragraphStyles: [
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 32, bold: true, font: 'Arial', color: '0F3132' },
        paragraph: { spacing: { before: 240, after: 200 }, outlineLevel: 0 } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 26, bold: true, font: 'Arial', color: '0F7768' },
        paragraph: { spacing: { before: 220, after: 140 }, outlineLevel: 1 } },
    ],
  },
  numbering: { config: [
    { reference: 'bullets', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•',
      alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
  ] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 },
      margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    children: [
      h1('FNPW Website Rebuild: Timeline & Cost'),
      p('Prepared by Elycia Paredes, Head of Content  |  July 2026', { italics: true }),
      h2('What we are doing'),
      p('We are rebuilding fnpw.org.au in-house, on our existing WordPress hosting, using AI (Claude) as the developer alongside my content role. The technical audit found the current site’s locked theme means every layout change, campaign page or new page type requires an agency invoice and a multi-week wait; campaign pages have been pushed onto external subdomains, costing us search visibility and brand consistency. The new site fixes this permanently: content, campaigns and pages become things we publish ourselves.'),
      p('The foundation is already built: a 121-page site including all 85 project pages organised under our three strategic pillars, aligned to the 2025 Brand Guidelines. Donations remain on Raisely throughout, so there is zero change and zero risk to payment processing at launch.'),
      h2('Timeline (approx. 6 hours/week alongside content work)'),
      timeline,
      p(''),
      p('Safety gate: if launch has not happened by 1 November, the finished site is held on staging through the peak giving season (Gift a Tree, 12 Days of Wildlife) and goes live in early February 2027 instead. Revenue-critical months are never used for a switch-over.'),
      h2('Cost'),
      costs,
      p(''),
      h2('Assumptions and risks'),
      bullet('My time: about 1.5 hours per day on this project, with content delivery continuing as normal.'),
      bullet('The build happens on a staging copy; the live site is untouched until launch, and rollback to the current theme is a one-click action.'),
      bullet('All existing page addresses are preserved (search rankings protected); the small number of retired pages get redirects.'),
      bullet('First Nations content (RAP, Kaurna, Firesticks) is carried across unchanged; any edits go through the existing cultural sign-off process.'),
      bullet('Main risk is schedule, not budget or site stability: if content season squeezes my hours, the launch moves to the February window rather than cutting testing.'),
    ],
  }],
});

Packer.toBuffer(doc).then(b => {
  fs.writeFileSync(process.argv[2] || 'FNPW-Website-Rebuild-Timeline-and-Cost.docx', b);
  console.log('written');
});
