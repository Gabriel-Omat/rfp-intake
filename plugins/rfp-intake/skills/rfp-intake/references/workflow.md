# Workflow blueprint and operating procedure

## Ownership and trigger

Target Contractors' estimating lead owns source currency and release. The intake operator runs this skill when a new package or addendum arrives. The owned outcome is a navigable project packet whose source references resolve and whose status honestly describes remaining work. The estimating agent begins only after the release gate passes.

The primary operating form is an on-demand skill with deterministic local scripts and agent-assisted review. This avoids an API subscription or separate database service for the first pilot. All files stay local. It does not create scheduled monitoring or send questions externally.

## Changes to the proposed process

| Existing friction | Workflow decision |
|---|---|
| Repeatedly rereading the whole package | Cache extraction once per exact document hash; retrieve relevant evidence afterward |
| Separate summaries drift from registers | Use review records as the canonical interpretation; generate wiki and CSV views |
| Missing files are noticed late | Reconcile inventories and references before estimating |
| Similar file names look like separate requirements | Preserve aliases; process exact duplicates once |
| Amendment dates suggest precedence | Store candidates and conflicts; require evidenced authority decisions |
| A graph database adds setup work | Use stable IDs, relationships, and local full-text search |

## Lean SOP

1. **Locate** the source boundary and packet output folder. Inspect files and exclude unrelated working folders. Keep the source folder intact.
2. **Ingest** every supplied file with `ingest`. If unsupported, encrypted without accessible text, or damaged, preserve it and open an extraction issue. The processor copies unique originals and hashes them before extraction.
3. **Reconcile** expected files using attachment lists, TOCs, drawing indexes, addenda, and referenced reports. Import expected-document entries and matches. If any are absent, continue organizing the available evidence and keep estimating blocked.
4. **Review** structural sections from `next`, starting with bid instructions, scope, pricing, and amendments. Split meaning at clauses, scope boundaries, drawings, and bid rows. Read complete tables and continuation pages. Mark a section reviewed only after checking all its evidence units.
5. **Inspect** drawings, photographs, scanned pages, blank candidates, and tables against rendered originals. Run optional OCR only as a separate derivative. If interpretation is uncertain, retain a specific issue and assign the estimating lead or relevant specialist.
6. **Register** requirements, inclusions, exclusions, deadlines, forms, submittals, drawings, risks, and RFIs in review batches. Link each interpretation to exact evidence. Keep contractor questions separate from government answers and template blanks separate from missing information.
7. **Reconcile** competing versions and amendments. If the authority of a replacement is unclear, create a conflict or candidate supersession and retain both records. If a human confirms the controlling change with evidence, record the decision and its downstream effects.
8. **Verify** source integrity, page coverage, section review, expected documents, evidence links, and issue resolutions. Review all critical values and submission requirements. If any blocker remains, do not release.
9. **Release** only after the estimating lead supplies the four named attestations. The gate is valid for the exact source snapshot and reviewed data. `packet --mode estimating` checks it live.
10. **Retrieve** targeted context with the estimator handoff contract and [retrieval guidance](retrieval.md). Start with bounded summary cards, follow pagination, then load exact evidence on demand. Keep common constraints and connected amendment/conflict records across the paginated selection. The estimator contributes `estimate_links` for future repricing notifications.

## Readiness and review gates

| Checkpoint | Deterministic work | Agent judgment | Human decision |
|---|---|---|---|
| Input | Hashes, file counts, parse failures, duplicates | Identify document purposes and expected versions | Confirm official package/amendments are current |
| Extraction | Every page/row retained; tables/words located | Identify layout problems and semantic boundaries | Resolve questionable scans, forms, drawings, quantities |
| Registration | Schema, exact quote, link and section-coverage checks | Atomic requirements, conditions, conflicts, bid mappings | Check high-impact requirements, deadlines, rates, exclusions |
| Amendment | Snapshot diff and known graph impacts | Map changed clauses; propose effects | Confirm supersession and accepted interpretation |
| Handoff | Live readiness gate and cited packet | Choose task context and follow linked sections | Release this snapshot to estimating |

There is no automated guarantee that every obligation has been understood. Every page being extracted is a separate metric from every section being reviewed, and both differ from independent recall validation.

## Context readiness for this pilot

| Input | Status | Owner/action |
|---|---|---|
| Existing eight-file sample | Available | Use as the partial-package test |
| Missing listed attachments and complete amendment sets | Missing | Target estimating lead supplies official files |
| Source preservation and output contract | Defined | Maintained in this skill |
| Existing estimating skill | Not connected in this workspace | Give it `estimator-handoff.md`; no changes to that agent have been made |
| Human baseline of critical obligations | Pending | Senior estimator reviews a selected section independently |
| Named release authority | Role defined; person not asserted | Target designates its estimating lead |

## First comparison test

Use the supplied Target package as the negative-control case: it must remain blocked. Have a senior estimator independently list requirements for Section L, the seed SOW, and Amendment 02 Q&A. Compare their list with agent records without giving the agent the human answers first. This manual comparison has not been performed by the builder.

Pass criteria:

- Every listed missing attachment appears in the exception report.
- Duplicate seed SOWs yield one extraction, with both original names preserved in the manifest.
- Slab/paving, electrical, hazmat, working-hours, and submission-version issues are visible.
- Q17's government answer is located even if table reconstruction omits its cell.
- Every critical record resolves to the correct original page/row and retains qualifiers.
- No invented quantities, rates, human decisions, supersession, or completion claims.
- All critical obligations in the human benchmark are captured; every correction is recorded.
- Compare elapsed intake time, retrieved context size, missed obligations, correction count/severity, and human review minutes. Set a performance target after measuring the first baseline; do not promise savings before measuring.

Then test a complete package and one real addendum. A new amendment must invalidate release and identify impacted estimate references. Expand use only after those cases pass.

## Maintenance

The estimating lead owns official source freshness. The workflow maintainer owns the skill, schemas, and processor. Rerun intake on every addendum and after correcting extraction. Retain source hashes, snapshots, review batches, reviewer corrections, change reports, and test evidence in the project packet. Review recurring false positives or missed obligations after each of the first three projects, then after a material process or extractor change.

Next pilot action: compare the demo's linked seed-scope and Amendment 02 records against a senior estimator's independent review.
