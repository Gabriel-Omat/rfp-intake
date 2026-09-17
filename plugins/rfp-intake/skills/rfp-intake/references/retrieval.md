# Efficient, evidence-backed retrieval

The default `packet` response is a compact orientation, not a substitute for source review. Read the relevant pages and exceptions before making substantive claims. All existing estimating gates still apply.

`PY` and `SKILL` are the Python interpreter and skill folder set up in SKILL.md. Examples use bash syntax; in Windows PowerShell, run `& $PY "$SKILL\scripts\rfp_intake.py" ...` with the same arguments.

## Start small

```sh
"$PY" "$SKILL/scripts/rfp_intake.py" packet --project /absolute/project-packet --query "slab removal paving"
```

This returns summary cards, relationships, source locators, related blockers, and counts of all blockers. It omits verbatim quotes, detailed record fields, and full source text. Essential common records and the entire connected relationship set remain in the paginated selection. Conflicts are listed first; common/conflicting records are prioritized, but may still span pages.

`--max-chars` defaults to 24000 and accepts 4000–100000. It caps the whole serialized response, including metadata, not just evidence text. `usage` reports exact response characters and UTF-8 bytes plus a rough token estimate based on bytes divided by four. This is not an exact tokenizer count, a billing measurement, or a cap on the agent's total reasoning/context use. Printing compact JSON also avoids indentation overhead.

## Follow continuation pages

If `pagination.has_more` is true, repeat the same request with `--cursor` set to `pagination.next_cursor`. Preserve the query, ID filters, mode, view, limit, and character budget. Cursors reject changed source/review/gate context. Do not treat the first page as the entire result. If a query is too broad, narrow it and restart; never imply that the narrower selection is complete coverage of the RFP.

Oversized individual items appear in `fragments`, with an item ID, collection, part number, total parts, and `json_fragment`. Collect all parts, concatenate their strings in order, then parse JSON before interpreting that item. No text is silently clipped. Use local scripts to assemble large results; do not repeatedly paste the entire assembled file into context.

## Load only the details needed

```sh
"$PY" "$SKILL/scripts/rfp_intake.py" packet --project /absolute/project-packet --record-id SC-001 --view full
"$PY" "$SKILL/scripts/rfp_intake.py" packet --project /absolute/project-packet --evidence-id EV-EXAMPLE --view full
"$PY" "$SKILL/scripts/rfp_intake.py" packet --project /absolute/project-packet --view blockers
```

Replace example IDs with actual returned IDs. Repeat `--record-id` or `--evidence-id` for several targets. Explicit IDs replace keyword seeding, but still include common constraints and connected records; they are not a way to suppress a conflicting source. Full view includes original record details, citations, and evidence text, still paginated. Blocker view gives every live gate blocker without dumping them into each topic summary.

The `full_context_file` points to a hash-addressed local archive of all selected full records, relationships, evidence, and all gate blockers. It costs no model-context tokens just to save this file. Prefer the bounded commands over reading this archive. The archive is not authority to estimate and does not replace a live gate check.

`--limit` controls initial full-text search hits, not total selected records or token use. Keyword matches, common constraints, and linked records can expand selection substantially. Every selected item remains available across the pages and in the archive; retrieval never claims to discover every relevant obligation.

## Avoid repeated work

Do not reread source text already available in the current conversation unless checking an ambiguity or change. Use record/evidence IDs in follow-up requests. Do not load the whole state, all registers, or script source for ordinary lookups. Run the scripts instead. Document extraction caching saves processing time; it is not provider-side prompt caching.

Complete initial semantic review still requires reading every section, including relevant tables and drawings. This optimization primarily reduces repeated question-answering context, not the obligation to perform the initial review. No automatic model switching or background execution is added.
