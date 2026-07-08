const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, AlignmentType, LevelFormat,
        HeadingLevel, BorderStyle } = require('docx');

function h2(t) { return new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(t)] }); }
function p(t, opts = {}) { return new Paragraph({ spacing: { after: 120 }, children: [new TextRun({ text: t, size: 20, ...opts })] }); }
function b(t, boldLead) {
  const runs = boldLead
    ? [new TextRun({ text: boldLead + ' ', bold: true, size: 20 }), new TextRun({ text: t, size: 20 })]
    : [new TextRun({ text: t, size: 20 })];
  return new Paragraph({ numbering: { reference: 'bullets', level: 0 }, spacing: { after: 60 }, children: runs });
}
function n(t, boldLead) {
  const runs = [new TextRun({ text: boldLead + ' ', bold: true, size: 20 }), new TextRun({ text: t, size: 20 })];
  return new Paragraph({ numbering: { reference: 'nums', level: 0 }, spacing: { after: 60 }, children: runs });
}

const doc = new Document({
  styles: {
    default: { document: { run: { font: 'Arial', size: 20 } } },
    paragraphStyles: [
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal',
        run: { size: 30, bold: true, font: 'Arial', color: '0F3132' },
        paragraph: { spacing: { before: 0, after: 120 }, outlineLevel: 0 } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal',
        run: { size: 22, bold: true, font: 'Arial', color: '0F7768' },
        paragraph: { spacing: { before: 200, after: 80 }, outlineLevel: 1 } },
    ],
  },
  numbering: { config: [
    { reference: 'bullets', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•',
      alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 560, hanging: 280 } } } }] },
    { reference: 'nums', levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.',
      alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 560, hanging: 280 } } } }] },
  ] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 },
      margin: { top: 900, right: 1080, bottom: 900, left: 1080 } } },
    children: [
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun('Website Rebuild: Status Update')] }),
      p('Elycia Paredes  |  July 2026  |  Prepared for Suzana Majstorovic', { italics: true, size: 18 }),

      h2('Where it stands'),
      p('The new fnpw.org.au has been designed and built in-house using AI-assisted development, aligned to the 2025 Brand Guidelines. It is approximately 70% launch-ready: 121 pages including all 85 project pages organised under our three strategic pillars, a rebuilt About page with our real team and board, and a Reports library carrying all 21 publications from 2018 to 2025. Remaining work is a final messaging and imagery pass, then loading it into WordPress as a new theme on a staging copy. A clickable preview link is available.'),

      h2('Path to live: 4 to 6 weeks'),
      n('Final content pass: messaging and imagery refined across key pages.', 'Weeks 1-2.'),
      n('Site converted to a WordPress theme on SiteGround staging. The live site is untouched throughout.', 'Weeks 2-3.'),
      n('Content wired into the CMS: projects, pillars, forms, newsletter. I manage this and will train Mali on the standard WordPress backend.', 'Weeks 3-4.'),
      n('Quality assurance on staging: SEO redirects, accessibility, devices. Stakeholder review via a private staging link.', 'Week 5.'),
      n('Launch: full backup, switch to the new theme, monitored first week. Rollback to the current site is a one-click action at any time.', 'Week 6.'),

      h2('Cost'),
      b('a comparable bespoke rebuild from an agency typically runs $30,000-80,000 over 4-6 months. This build has cost $0 in external fees.', 'Build to date:'),
      b('Claude Max subscription at ~$150/month for approximately 4 months (~$600 total). This provides AI-assisted development for the WordPress conversion and any backend fixes that would otherwise require a contracted developer.', 'To finish:'),
      b('hosting unchanged, all required plugins already licensed. Post-launch there is no agency retainer: page changes, campaign pages and new sections are done in-house.', 'Ongoing:'),

      h2('What the rebuild unlocks'),
      b('every page rebuilt on one design system to the 2025 Brand Guidelines. One voice, sitewide.', 'Consistent messaging:'),
      b('modern, mobile-optimised, accessibility-conscious design with clear pathways to donate on every page.', 'User experience:'),
      b('Bring Back the Bush traffic currently exits to external Raisely domains and is lost to us afterwards. The new site hosts campaign landing pages on fnpw.org.au, so campaign visitors land with us, join our list and discover our projects. Raisely continues to process payments unchanged, so there is no payment risk.', 'Donor journey:'),
      b('the current locked theme made formal SEO impossible. The new build opens titles, metadata, schema and internal linking; all 85 project URLs are preserved so existing rankings carry over; and it positions FNPW to apply for Google Ad Grants (US$10,000/month in free search advertising for eligible charities).', 'SEO and Google authority:'),
      b('standard WordPress underneath. We can add, redesign and extend pages in hours rather than agency weeks, and scale the site as programs grow. Full documentation exists (build playbook, troubleshooting guide, launch checklist) so the site is not dependent on any one person.', 'Self-managed and scalable:'),

      h2('Risk controls'),
      p('Built and tested on staging with the live site untouched until switch-over; one-click rollback; donations remain on Raisely with zero change at launch; existing URLs preserved with a redirect map; launch scheduled outside peak giving season.'),

      h2('Approval requested'),
      b('to proceed with the 4-6 week path to launch above.', 'Go-ahead:'),
      b('Claude Max subscription for approximately 4 months (~$600 total), dropping to ~$34/month after launch.', 'Budget:'),
    ],
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(process.argv[2], buf);
  console.log('written');
});
