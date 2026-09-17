# Contract for the estimating agent

The intake skill supplies evidence and reviewed constraints. You own quantities, rates, labor/equipment choices, calculations, and estimate lines. Keep your assumptions distinct from government requirements.

`PY` is a Python 3.11+ interpreter with the rfp-intake requirements installed, and `SKILL` is the rfp-intake skill folder (see its SKILL.md). Examples use bash syntax; in Windows PowerShell, run `& $PY "$SKILL\scripts\rfp_intake.py" ...` with the same arguments.

1. Load `START_HERE.md` for orientation and call `packet --mode estimating` with a topic or record ID. This checks the gate live without dumping every blocker into context. If blocked, stop pricing; use `packet --mode research --view blockers` for paginated details. A saved gate file or context archive alone is insufficient. Research mode supports intake investigation only.
2. For each work package, call `packet --query "topic terms" --mode estimating`. It returns compact summary cards and locators, not full evidence. Follow continuation pages, then request `--view full --record-id ACTUAL-ID` for the necessary citations and details. See [retrieval guidance](retrieval.md). Common constraints and complete connected relationships are retained across pages; old/conflicting sources are not silently discarded. Read their status before using them. Summary cards alone do not justify pricing.
3. Load complete linked sections where interpretation crosses a page boundary or depends on a definition, condition, exception, table heading, drawing detail, or referenced attachment. Search returns relevant candidates, not a proof that every obligation was retrieved.
4. Check the requirements, exclusions, phase, contract layer, amendment decisions, units, bid-item mapping, and relevant drawings. Do not use IDIQ evaluation quantities as seed-project takeoff quantities. Do not infer quantities from unscaled photographs. Do not treat blank prices or cached formula zeros as priced work.
5. Keep supporting records, evidence IDs, source SHA-256, page/cell locators, assumptions, and calculation basis with each estimate line. A source quote supports a requirement; it does not establish an inferred takeoff or production rate.
6. Return estimate relationships to intake using `estimate_links` review-batch entries. Example: `{"estimate_line_id":"EST-104","record_id":"SC-014","estimate_file":"04_ESTIMATING/estimate.json"}`. A record can support many estimate lines and one line can reference many records.
7. Recheck the gate before finalizing. New source files, semantic changes, or decisions invalidate release. On an amendment, read `01_INTAKE/changes`, identify affected lines, reprice only after the revised intake is released, and retain old estimate versions.

Example CLI:

```sh
"$PY" "$SKILL/scripts/rfp_intake.py" packet --project /absolute/project-packet --query "hazardous materials sampling asbestos" --mode estimating --output /absolute/project-packet/04_ESTIMATING/hazmat-context.json
```

Exit status 2 means the estimate gate is blocked. Exit status 1 means a processing/validation error. Exit status 0 means the requested operation succeeded; `research` results may still explicitly prohibit estimating.
