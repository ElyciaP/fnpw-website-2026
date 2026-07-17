const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, AlignmentType, LevelFormat,
        HeadingLevel } = require('docx');

function h2(t) { return new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(t)] }); }
function p(t, opts = {}) { return new Paragraph({ spacing: { after: 120 }, children: [new TextRun({ text: t, size: 20, ...opts })] }); }
function b(t, boldLead) {
  const runs = boldLead
    ? [new TextRun({ text: boldLead + ' ', bold: true, size: 20 }), new TextRun({ text: t, size: 20 })]
    : [new TextRun({ text: t, size: 20 })];
  return new Paragraph({ numbering: { reference: 'bullets', level: 0 }, spacing: { after: 70 }, children: runs });
}
function n(t, boldLead) {
  return new Paragraph({ numbering: { reference: 'nums', level: 0 }, spacing: { after: 70 },
    children: [new TextRun({ text: boldLead + ' ', bold: true, size: 20 }), new TextRun({ text: t, size: 20 })] });
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
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun('Website Rebuild: Kick-off Plan')] }),
      p('Elycia Paredes  |  July 2026  |  Kick-off: 1 August 2026', { italics: true, size: 18 }),

      h2('Where it stands'),
      p('Approved and scheduled. The new fnpw.org.au has been designed and built in-house, aligned to the 2025 Brand and Messaging Guidelines. It is approximately 70% launch-ready: 121 pages including all 85 project pages organised under our three strategic pillars, a rebuilt About page with our real team and board, an interactive national project map, and a Reports library carrying all 21 publications from 2018 to 2025. A clickable preview link is available.'),
      p('Remaining work: copywriting and imagery across key pages, loading the site into WordPress as a new theme on a staging copy, then testing and launch. Hosting access is being arranged with Lucian (WordPress admin plus file access, with a staging copy to be created); the preview-image quirk resolves with that access and disappears entirely at launch.'),

      h2('Path to live: ten weeks from 1 August'),
      n('Copy and design (with breathing room). Copywriting across key pages with content support from Jess and Cat; final design refinements; an intro session with Reef to capture the current site’s history and integrations.', 'Weeks 1-3 (1-22 Aug).'),
      n('WordPress build. The site converted to a new theme and content system on the SiteGround staging copy. The live site is untouched throughout.', 'Weeks 4-5 (24 Aug - 5 Sep).'),
      n('Content into the CMS: projects, pillars, forms, newsletter. I manage this and will train Mali on the standard WordPress backend.', 'Weeks 6-7 (7-18 Sep).'),
      n('Quality assurance on staging: accessibility, devices, performance. Reef independently reviews the redirect map and runs a technical SEO check of the staging site. Stakeholder review via a private link.', 'Week 8 (21-25 Sep).'),
      n('Launch in the first half of October: full backup, switch to the new theme, monitored first week. Rollback to the current site is a one-click action at any time. Safety gate: if launch has not happened by 1 November, the finished site holds on staging and goes live in early February, keeping peak giving season untouched.', 'Weeks 9-10 (28 Sep - 9 Oct).'),

      h2('Cost'),
      b('a comparable bespoke rebuild from an agency typically runs over $100,000 over 4-6 months. This build has cost $0 in external fees.', 'Build to date:'),
      b('Claude Max subscription at $399/month for approximately 3 months (~$1,200 total). This provides assisted coding for the WordPress conversion and any backend fixes that would otherwise require a contracted developer.', 'To finish:'),
      b('three defined touchpoints on a time-and-materials basis (site-history session, redirect-map review, pre-launch technical SEO check), quoted separately by Reef. This targets their expertise at the genuine risk areas without agency rates on build work we do in-house.', 'Reef advisory:'),
      b('hosting unchanged, all required plugins already licensed. Post-launch there is no agency retainer: page changes, campaign pages and new sections are done in-house, and the subscription drops to a lower tier.', 'Ongoing:'),

      h2('What the rebuild unlocks'),
      b('every page rebuilt on one design system to the 2025 Brand and Messaging Guidelines. One voice, sitewide.', 'Consistent messaging:'),
      b('modern, mobile-optimised, accessibility-conscious design with clear pathways to donate on every page. The current site scores 27/100 on mobile performance in Reef’s review; the rebuild is engineered to fix this.', 'User experience:'),
      b('Bring Back the Bush traffic currently exits to external Raisely domains and is lost to us afterwards. The new site hosts campaign landing pages on fnpw.org.au, so campaign visitors land with us, join our list and discover our projects. Raisely continues to process payments unchanged, and we can explore embedding donations on-site in a later phase.', 'Donor journey:'),
      b('the current locked theme made formal SEO impossible. The new build opens titles, metadata, schema and internal linking; all 85 project URLs are preserved so existing rankings carry over; and it positions FNPW to apply for Google Ad Grants (US$10,000/month in free search advertising for eligible charities).', 'SEO and Google authority:'),
      b('we currently run ads with limited visible return. Two causes the rebuild fixes: donation conversions are lost when visitors jump to Raisely domains, so Google cannot see or optimise for what works; and slow, generic landing pages raise our cost per click. The new site keeps the journey on our domain with proper tracking and matched landing pages per campaign.', 'Google Ads performance:'),
      b('standard WordPress underneath. We can add, redesign and extend pages in hours rather than agency weeks. Full documentation exists (build playbook, troubleshooting guide, launch checklist) so the site is not dependent on any one person.', 'Self-managed and scalable:'),

      h2('After launch: Backyard Buddies'),
      p('Reef’s Phase 2 review recommends consolidating Backyard Buddies (535,000 yearly visitors, $0 in donations today) into fnpw.org.au with its brand identity preserved. The rebuild is the platform that makes this possible: the new design system supports a distinct Backyard Buddies look, and consolidation should land on the new theme rather than the current site, avoiding migrating 244 pages twice. Sequencing: main site live first (October), Backyard Buddies consolidation scoped as the next phase, with Reef reviewing the redirect strategy. Reef sizes the opportunity at roughly $18,000 per month if Backyard Buddies visitors converted at Gift a Tree rates (illustrative).'),

      h2('Dependencies and risk controls'),
      b('staging copy created in SiteGround, plus either launch-day actions run at Lucian’s end or collaborator access (requested).', 'Lucian:'),
      b('three advisory touchpoints scheduled across August-September.', 'Reef:'),
      b('content days with Jess (and Cat where needed) confirmed for the copy phase.', 'Content support:'),
      p('Risk controls: built and tested on staging with the live site untouched until switch-over; one-click rollback; donations remain on Raisely with zero change at launch; existing URLs preserved with a redirect map; launch scheduled outside peak giving season, with the February fallback if the gate is missed.'),

      h2('Next steps'),
      b('re-dated build plan (this document) shared for the final risks and dependencies check.', 'This week:'),
      b('access items confirmed with Lucian; intro chat with Jess; Reef session booked for early August.', 'Before kick-off:'),
      b('copy and design phase begins.', '1 August:'),
    ],
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(process.argv[2], buf);
  console.log('written');
});
