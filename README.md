# rfp-intake

A Claude Code skill that turns a folder of RFP documents into a traceable, cited project packet for estimating: it extracts and indexes every page, builds requirement and scope registers linked to exact evidence, reconciles amendments, and reports what still blocks estimating.

Runs on Windows, macOS and Linux (tested on Windows and macOS). Requires Python 3.11 or newer. Everything stays local — no API key, no database, no uploads.

## Install (Claude Code)

In a Claude Code session, run these two commands:

```
/plugin marketplace add Gabriel-Omat/rfp-intake
/plugin install rfp-intake@target-tools
```

That's it — git is not required, and Claude Code picks the skill up immediately. Later versions arrive automatically; to pull one on demand, run `/plugin update rfp-intake@target-tools`.

Prefer the terminal? The same thing without opening a session:

```powershell
claude plugin marketplace add Gabriel-Omat/rfp-intake
claude plugin install rfp-intake@target-tools --scope user
```

## Requirements

Python 3.11 or newer on the machine. Check with `py --version` (Windows) or `python3 --version` (macOS/Linux). If it is missing, install it from python.org with **"Add python.exe to PATH"** ticked, or run `winget install Python.Python.3.12`.

The skill installs its own PDF and Excel libraries into a local folder the first time it runs, and asks before running anything.

Optional, for scanned pages only: Tesseract and Poppler on PATH. Without them, a scanned page is flagged rather than guessed at.

## Use

Ask for it by name and point it at the folder:

```
/rfp-intake Prepare the RFP package in C:\Projects\Fort Lewis Paving\RFP for estimating.
```

Claude sets up the Python environment on the first run, then copies and hashes every source file, extracts the text, and works through the package section by section. Claude asks permission before each command it runs.

Start at `START_HERE.md` in the packet folder. Estimating stays blocked until the checks pass and a named reviewer signs off on the four release attestations — the skill will not certify its own review.

When an addendum arrives, run it again against the complete current folder: unchanged files are reused, changes are reported, and the previous release is invalidated.

See [docs/INSTALL-WINDOWS.md](docs/INSTALL-WINDOWS.md) for the longer Windows walkthrough, including the manual install if you would rather not use the plugin system.

## What's in here

```
.claude-plugin/marketplace.json     the marketplace Claude Code reads
plugins/rfp-intake/                 the plugin
  skills/rfp-intake/SKILL.md        the skill instructions
  skills/rfp-intake/scripts/        the local processor and its tests
  skills/rfp-intake/references/     workflow, data contract, retrieval and estimator handoff
```

Run the processor's tests with `python -m unittest test_rfp_intake` from the `scripts` folder.

## License

Copyright (c) 2026 Gabriel Omat. All rights reserved. **Source-available, not open source.**

Clients authorized by Gabriel Omat may install and use this internally for their own bids. Redistribution, resale, and hosting it for others are not permitted. Anyone may read it and try it for 30 days to evaluate it. Provided as is, with no warranty: it organizes and cites RFP documents, it does not certify that anything has been found or correctly interpreted, and every bid decision stays with the user and their estimators. See [LICENSE](LICENSE) for the full terms, or email coachme@gabrielomat.com about licensing.
