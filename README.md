# Participant Roster
- Mathieu Wauters — petitioner; primary narrator across all 20 messages.
- Rosey Alvero — respondent/opposing party; 21 Mar 2019 admissions email.
- Ryan Anderson — business partner who initiates 10 Oct 2022 counsel referral.
- Eric J. Proos — referring attorney connecting Mathieu to CFLS specialist.
- Brett A. Berman — Certified Family Law Specialist courted for trial representation.
- Robyn Macias — Berman Law Group paralegal coordinating the 30 Dec 2022 intake call.
- Joe Baldino — appraiser delivering the 25 Jul 2022 valuation for 3525 8th Ave., Los Angeles.
- California Mortgage Relief Program — confirms $49,262.84 mortgage assistance on 02 Nov 2022.
- Superhuman Reminder Bot — automation evidencing self-imposed follow-up discipline.

# Executive Summary
Twenty emails in `Mail/LEGAL-DIVORCE STUFF-EVIDENCE.mbox` (21 Mar 2019 – 30 Dec 2022) document the litigation pressure points for cases FDI-21-794666 (core dissolution with trial targeted for February 2023), FDV-24-817888 (credibility and conduct findings), and appellate placeholder A171270. The correspondence captures a mortgage relief infusion, a home appraisal for 3525 8th Ave., Los Angeles, and an attorney referral chain that culminates in a same-day paralegal outreach—each item anchoring valuation, support, or counsel-diligence arguments.

The repo includes a “Moneyball” scorecard visualization (`src/app/scorecards/page.tsx`) that weighs email touches, leverage scores, and response cadence for every participant. These metrics highlight Brett Berman’s sub-six-hour response median, Robyn Macias’s sub-ten-minute scheduling follow-through, and Mathieu’s 20-touch ownership of the evidentiary narrative.

# Background
- **Scope:** Parsed 20 messages from `LEGAL-DIVORCE STUFF-EVIDENCE.mbox` using ad-hoc Python scripts to normalize sender/recipient addresses, tally thread participation, and calculate response lag where reply chains existed.
- **Time frame:** Earliest entry 21 Mar 2019 (Rosey-Mathieu marital correspondence); latest entry 30 Dec 2022 (Berman Law Group scheduling).
- **Key artifacts extracted:**  
- 25 Jul 2022 appraisal delivery for 3525 8th Ave., Los Angeles.  
  - 02 Nov 2022 notice of $49,262.84 California Mortgage Relief payment (application MRP-0030504).  
  - October–December 2022 referral thread establishing diligence to retain trial counsel ahead of discovery deadlines (responses due 22 Dec 2022; trial referenced as early February 2023).
- **Visualization workflow:** Participant metrics serialized in `src/data/participants.ts`, exposed through Tailwind-styled cards at `/scorecards`.

# Legal Analysis
## 1. Mortgage Equity & Property Division (FDI-21-794666 · A171270)
- **Rule/Standard:** California Fam. Code §§ 2550–2552 (equal division; valuation at trial) and tracing doctrines for post-separation contributions.  
- **Supporting evidence:**  
  - Joe Baldino’s 25 Jul 2022 appraisal email establishes contemporaneous fair-market valuation for 3525 8th Ave.  
  - Mortgage Relief Program notice (02 Nov 2022) documents a $49,262.84 principal curtailment.  
- **Contrary considerations:** Relief funds may be characterized as community or separate property depending on application timing; need servicer records.  
- **Application:** Use appraisal as baseline, then adjust equity split by crediting Mathieu for the relief infusion if sourced from post-separation efforts; lock testimony from lender/appraiser to solidify the timeline for both trial and any A171270 appeal.

## 2. Credibility & Conduct Findings (FDV-24-817888 · FDI-21-794666)
- **Rule/Standard:** Impeachment under Cal. Evid. Code §§ 765, 780; DV findings influenced by credibility and admission evidence.  
- **Supporting evidence:**  
  - 21 Mar 2019 email from Rosey admits to depressive episodes, shoplifting “temporary high,” and emotional withdrawal—potential impeachment and mitigation of opposing DV allegations.  
  - Mathieu’s contemporaneous reply expresses willingness to reconcile, bolstering his good-faith posture.  
- **Contrary authorities:** Expect privacy/psychotherapy privilege objections; authenticity must be laid with metadata from Gmail export.  
- **Application:** Capture a declaration authenticating export metadata, prepare a motion in limine strategy addressing privilege waivers, and integrate admissions into DV credibility briefing.

## 3. Trial Readiness & Counsel Diligence (FDI-21-794666 · A171270)
- **Rule/Standard:** Grounds for continuance/substitution (Cal. Rules of Court 3.1332), ineffective assistance claims on appeal (rare but better preserved with diligence evidence).  
- **Supporting evidence:**  
  - Referral chain beginning 10 Oct 2022 (Ryan Anderson → Eric Proos → Brett Berman) shows proactive search for specialist counsel.  
  - Reminder bot (06 Nov 2022) and follow-up emails (8, 13, 16, 22, 30 Dec 2022) track persistent outreach before discovery response deadline (22 Dec) and trial (early Feb 2023).  
- **Contrary considerations:** Need to document why original counsel insufficient; ensure no gaps between outreach and response.  
- **Application:** Use scorecard metrics to demonstrate urgency and responsiveness; supports continuance motions or appellate arguments regarding reasonable diligence if substitution sought.

# Recommendations and Next Steps
1. **Authenticate digital evidence:** Export Gmail metadata (including X-GM-THRID) and prepare declaration for each highlighted email to pre-empt authenticity challenges.  
2. **Financial tracing package:** Combine appraisal PDF, mortgage relief confirmation, and current amortization schedule to quantify community equity adjustments before settlement talks.  
3. **Trial team decision:** Evaluate retaining Brett Berman; leverage response metrics to evidence readiness when moving for substitution or fee contributions.  
4. **Credibility brief:** Draft impeachment outline for Rosey’s 21 Mar 2019 email; coordinate with therapist records if privilege waiver feasible.  
5. **Further research:** Pull docket entries for FDI-21-794666, FDV-24-817888, and A171270 (San Francisco Superior Court & California Courts of Appeal) to map deadlines and confirm trial setting orders.

# Quality Control Checklist
- [x] Spellcheck and grammar review (US English).  
- [x] Verified participant metrics align with `participants.ts` dataset (touch counts, leverage scores).  
- [x] Confirmed date references match email headers (2019-03-21 to 2022-12-30).  
- [ ] External legal authorities requiring Shepardizing (Fam. Code §§ 2550–2552, Evid. Code §§ 765, 780) — pending confirmation via updated research tools.  
- [ ] Need servicer statement to corroborate $49,262.84 mortgage relief posting — follow-up required.

# Operating the Dashboard
- Install dependencies once: `npm install` (Node 18+ recommended).  
- Launch locally: `npm run dev` and open `http://localhost:3000/scorecards` for the Moneyball visualization.  
- Data source of truth: `Mail/LEGAL-DIVORCE STUFF-EVIDENCE.mbox`; metrics live in `src/data/participants.ts`.

## Specification-Driven Development

This project uses [GitHub Spec-Kit](https://github.com/github/spec-kit) for feature development:

1. **Constitution**: See `.specify/memory/constitution.md` for non-negotiable principles
2. **New Features**: Use `/speckit.specify` to create specs in `specs/` directory
3. **Quality Gates**: WCAG AAA, <3s loads, evidence-based claims, trauma-informed UX

### Available Slash Commands
- `/speckit.constitution` - Review/update governing principles
- `/speckit.specify` - Create new feature specification
- `/speckit.plan` - Generate technical implementation plan
- `/speckit.tasks` - Break down into atomic tasks
- `/speckit.implement` - Execute tasks with TDD

### JusticeOS™ Integration
Before merging into JusticeOS repo, all features must pass demo validation without breaking existing functionality. The constitution enforces empathy-first design, accessibility excellence, and trauma-informed UX patterns.

### Current Feature Specifications
- `specs/001-contact-extraction/` - Email parsing and contact extraction
- `specs/002-email-deduplication/` - CSV deduplication and data cleaning
