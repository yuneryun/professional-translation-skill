---
name: professional-translation
description: >-
  Professional translation workflow for long-form documents (books, contracts, medical/technical materials).
  Use when translating documents where accuracy, terminology consistency, and traceability matter, or when the user requests
  translation with review, glossary management, terminology unification, date/number normalization, docx text replacement
  preserving formatting, multi-round proofreading, or project postmortem and lessons-learned. Covers pre-translation prep
  (task boundary, glossary, style guide), translation (meaning units, modality, facts), post-translation review (4 rounds),
  and project management rules (master-file-first, version log). Works with scanned PDFs via text-layer extraction and
  python-docx formatting-preserving edits.
---

# Professional Translation

Translate documents with publication-grade rigor: **不猜测、不擅改、有依据、可复核** (no guessing, no unauthorized changes, evidence-based, verifiable).

## Quick Start

1. **Define task boundary** — text type, audience, language variant, delivery specs, client term preferences
2. **Build glossary + style guide** — extract terms, verify against authoritative sources, lock translations
3. **Translate by meaning units** — preserve logic/modality/facts; never add unverified content
4. **Review in 4 rounds** — bilingual check → terminology/facts → monolingual read → format check
5. **Keep evidence** — record every change (time/location/reason/source page)

## Core Rules (from real project lessons)

1. **Master file is the single source of truth** — edit only the master document; regenerate format variants from it
2. **Every edit must be checked against the original** — editor/AI suggestions are proposals, not facts
3. **Glossary is a living document** — updating a term in text requires updating the glossary
4. **Normalization scripts target the master file** — verify immediately after running
5. **Version list + change log** — every file = what it is + status; every change = time/location/reason/page
6. **Text replacement must preserve run formatting** — check run count before rebuilding paragraphs
7. **When requirements conflict, ask priority first** — don't over-engineer unverifiable metrics
8. **Don't fake precision on unverifiable metrics** — say "cannot verify precisely" instead
9. **Proactively review each phase** — don't wait to be asked

## Workflow

### Phase 0: Source extraction (scanned PDFs)
- Check for text layer with pypdf; if none, OCR pipeline: de-watermark → page render → chunk OCR → merge text layer
- Keep the text-layer PDF as the comparison baseline for all later checks
- See [references/source-extraction.md](references/source-extraction.md)

### Phase 1: Pre-translation
- Confirm task boundary (see [references/task-boundary.md](references/task-boundary.md))
- Build glossary.json (medical terms / people / institutions) — see [assets/glossary_template.json](assets/glossary_template.json)
- Create style guide (dates, numbers, units, abbreviations, citation style)
- Extract source per chapter with footnote markers and paragraph numbers preserved

### Phase 2: Translation
- Translate by meaning units + logical relations, not word-by-word
- **Zero tolerance on modality**: must/shall/should/may/likely/typically — 可能≠确定, 建议≠要求
- **Zero error on facts**: numbers, units, dates, clause numbers, proper names — immutable
- Keep viewpoint attribution (按雷德菲尔德的说法…)
- When source is ambiguous: verify first; if unresolvable, conservative handling + question list
- Don't "fix" source errors silently — flag via translator notes

### Phase 3: Post-translation (4 review rounds)
1. **Bilingual check** — omissions, errors, additions, logic shifts, term inconsistency, modality changes
2. **Terminology & facts audit** — numbers, units, dates, proper names, abbreviations, cross-references
3. **Monolingual read** — naturalness, clarity, ambiguity, professional writing norms
4. **Format & delivery** — layout, punctuation, full/half-width, heading levels, version number

For high-risk texts (legal/medical/financial/regulatory): add domain second reviewer or overnight review.

### Phase 4: Project management
- Maintain version README: every file = what + status
- Maintain change log: time/location/reason/source page
- Back up to markdown after each master-file change
- Run scripts targeting the master file only (see [scripts/](scripts/))

## Bundled Resources

### Scripts
- `scripts/docx_replace_text.py` — replace paragraph text in docx preserving run formatting (use run-level replacement; check run count first)
- `scripts/normalize_dates.py` — normalize Chinese numeral dates to Arabic (year/month/day), Arabic centuries to Chinese; excludes duration expressions (一年/十年) and proper nouns (《失落的二月》)
- `scripts/make_version_readme.py` — generate version list + change log template for a project directory

### References
- `references/source-extraction.md` — scanned PDF → text layer pipeline (de-watermark, OCR, chunking, footnote recovery)
- `references/task-boundary.md` — pre-translation checklist (type, audience, variant, delivery specs)
- `references/review-checklists.md` — the 4 review rounds with concrete check items
- `references/project-lessons.md` — real failure cases and the rules derived from them

### Assets
- `assets/glossary_template.json` — glossary schema (medical_terms/people/institutions) with context & source fields
- `assets/style_guide_template.md` — style guide skeleton (dates, numbers, terms, citation)
