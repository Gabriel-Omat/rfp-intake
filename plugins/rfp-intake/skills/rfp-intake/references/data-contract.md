# Data contract

The canonical stores are copied source files, extraction sidecars, immutable review batches, and `01_INTAKE/state.json`. CSV, Markdown, and SQLite are generated views. Edit interpretations by importing a new record and relationship; never edit generated CSVs or source text to correct a fact. Keep raw and normalized values separate. CSV cells beginning with formula characters are escaped; exact values and formulas remain in JSON.

## Identifiers and evidence

`DOC-...` is a content-hash identifier. A new byte stream has a new document ID; two filenames with identical contents have one extraction and two manifest entries. Original user files remain untouched. The packet stores one verified byte-identical copy per unique document. A copy is a source of record for navigation; it is not a new government-issued version.

`EV-...` identifies one PDF page or populated workbook row. Evidence includes source SHA-256, PDF page (1 based), observed printed label and numbering scheme, section, heading, worksheet, and exact cell/range. PDF word sidecars preserve bounding boxes in PDF points (top-left convention used by pdfplumber). Table sidecars retain bounding boxes and every reconstructed cell, including nulls. Source formula text, cached values, types, number formats, comments, hyperlinks, hidden dimensions, and merged ranges are retained for workbooks. Cached values are not recalculation results. The processor does not execute workbook macros, external links, or formulas.

`SEC-...` identifies a structural review unit. Specification footers and top-level bookmarks propose boundaries; a worksheet is one unit. A page is still fully retained if headings are absent. The agent must inspect TOCs and boundaries, and can use multiple records for clauses on the same page. Never assume bookmarks alone prove semantic completeness.

Each register record uses a type prefix (`SC`, `REQ`, `DATE`, `BID`, `FORM`, `AMD`, `RISK`, `RFI`, `DRAW`, `SUB`, `DEL`) and stable suffix. Human-friendly sequential suffixes are allowed within a project. Do not recycle IDs or use a row number as a cross-version identity. Track unchanged logical entities across versions using relationships, without overwriting historical evidence.

## Review batch

`batch.schema.json` is the machine-readable input contract. The CLI validates its types, required fields, enum values, and identifiers, then validates quotes, targets, and coverage. It supports exactly the JSON Schema subset used by this file; adding new schema keywords requires updating the validator.

Required top-level fields: `batch_id`, `snapshot`. The current snapshot comes from `status`. Optional arrays: `records`, `relationships`, `expected_documents`, `issues`, `resolutions`, `section_reviews`, `attestations`, `estimate_links`.

Every record requires:

| Field | Meaning |
|---|---|
| `record_id`, `type`, `title` | Stable identity and register |
| `interpretation` | AI-written meaning; never labeled authoritative |
| `contract_layer` | `idiq`, `seed_task_order`, `task_order`, `project`, or `unknown` |
| `applicability` | Conditions, phase, location, exclusions, and triggers |
| `tags` | Retrieval topics, such as `electrical`, `hazmat`, `submission` |
| `critical` | Needs explicit checking during critical-record review |
| `always_include` | Included in every topic selection, possibly on continuation pages; reserve for essential common constraints |
| `authority_status` | `unverified`, `conflicted`, `candidate_current`, `historical`; human authority decisions live in separate review entries |
| `review_status` | `ai_draft` or `ai_reviewed`; neither is human approval |
| `evidence_ids`, `citations` | Each ID has a matching source quote |
| `details` | Type-specific typed data below |

Quote validation permits only Unicode compatibility normalization and whitespace differences. It does not validate the interpretation's meaning. A valid quote can still support a wrong conclusion; semantic review is necessary. Do not label OCR as native or human-verified based on this check.

Use these `details` fields where supported; preserve unknown values as null, not zero:

| Record type | Details |
|---|---|
| Scope | action, asset, location, inclusion_or_exclusion, quantity_raw, quantity, unit, quantity_basis |
| Requirement | responsible_party, obligation, condition, phase, acceptance_criteria |
| Bid item | item_code_raw, item_code_normalized, period, clin, row_kind, description, quantity, unit, quantity_basis, unit_price_input_cell, source_formula, cached_total, cost_inclusions, cost_exclusions, credit_sign_review |
| Date | raw_date_text, event, date, time, timezone_raw, normalized_timestamp, normalization_status, relative_trigger, offset, calendar_or_working_days |
| Form | form_number, phase, submission_slot, required_fields, signature_required, original_attachment_number, format, destination |
| Amendment | amendment_number, issue_date_raw, effect, affected_ids, authority_evidence, prior_version_known |
| Drawing | sheet_number, title, revision, discipline, scale_raw, visual_review_status, referenced_details, quantity_takeoff_status |
| Submittal/deliverable | designation, approval_code, recipient, copies_or_format, due_trigger, required_before_work, related_spec_section |
| Risk/RFI | question_or_conflict, impact, severity, proposed_action, owner_role, resolution |

`relationships` connect record IDs. Use `candidate_supersedes` for a suspected change, `conflicts_with` for incompatible requirements, and `clarifies` for supporting explanation. For `supersedes`, `from_id` is the new record and `to_id` is the old one. Explicit `human_approved`, `reviewer`, `decision_note`, and evidence are required. The graph is data, not a declaration that a newer filename is authoritative.

`expected_documents` requires an evidence-backed title, optional matched document IDs, and `version_verified`. An empty match is missing. A nonempty match with false verification remains unresolved. Distinguish attachment numbers in the source inventory from numbered submission slots (this package uses both). Only an actual resolved review can set version verification true.

`section_reviews` must enumerate every evidence ID in the section, name the reviewer (agent name is allowed for `ai_reviewed`), and explain coverage. This attests to work actually done. Presence of a review row cannot independently prove recall; compare against a human baseline.

`resolutions` address specific issue IDs with evidence and an actual named human decision. Blockers are not waived by deleting rows. Original issue and decision history remain in review batches. Missing files must be supplied or the expected-document record must be corrected with documented authority; this first version does not offer a generic override switch.

Four human attestations are required: `package_complete`, `authority_reconciled`, `critical_records_reviewed`, and `release_to_estimating`. Their validity is bound to the source snapshot and the current review-data hash. Adding records, resolutions, relationships, or documents invalidates prior release. The CLI records declarations; it does not authenticate the identity of the named reviewer. A production multi-user service would need identity and access controls.

## Incremental behavior

Rerun against the complete current input folder. Extraction is cached per source hash. A removed file remains in historical storage; removal is not authority to retire its requirements. Same-path changes produce text diffs and candidate replacement links. New amendment candidates conservatively flag all prior records for impact review; graph links propagate known impacts to registered estimate lines. Different filenames are not automatically paired as versions. Human/AI analysis maps the actual changed clauses.

All section reviews and human attestations become stale when the package snapshot changes. The agent may revalidate an unaffected section after comparing changes and dependencies, but may not silently copy its old approval. Immutable review batches make this decision auditable.

## Current implementation limits

Packet format version 2 defaults to summary cards, with full details and blockers available in separate paginated views. The packet's `format_version` is independent of the canonical store schema. Consumers must handle `pagination`, `fragments`, and `usage`; do not assume `records` and `evidence` are complete on the first response or that summary evidence contains `text`. The old evidence-text-only `approximate_characters` field remains in the on-disk full context archive for compatibility, not in the compact response. See [retrieval guidance](retrieval.md) for the contract and CLI options. Canonical records and source evidence have not been truncated or migrated.

Native PDFs and `.xlsx` are supported. Other files are preserved and flagged, including CAD, legacy Excel, images, archives, and signed/dynamic form formats requiring specialist handling. Optional page OCR requires Poppler and Tesseract. Drawing takeoff, legal precedence decisions, and unrestricted semantic extraction are performed by the agent/human workflow, not by the parser. The SQLite index is lexical full-text search, with relationship expansion; no embedding service is installed. This is a local single-operator workflow, not a hosted application. It runs on Windows, macOS, and Linux with Python 3.11+; stored relative paths always use forward slashes, and a packet lock prevents two intake commands from writing the same packet at once.
