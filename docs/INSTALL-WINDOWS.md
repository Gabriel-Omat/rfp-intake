# Installing and running rfp-intake in Claude Code (Windows)

This skill runs inside **Claude Code**, the command-line version of Claude. It does not need Cowork.

## 1. One-time: install Python

The skill uses a local Python program to read the RFP files. Python 3.11 or newer must be on the PC.

Check in PowerShell:

```powershell
py --version
```

If that fails or shows an older version, install Python from python.org (tick **"Add python.exe to PATH"** during setup) or run `winget install Python.Python.3.12`, then close and reopen the terminal.

Nothing else is required. The skill installs the small PDF and Excel libraries it needs, into a folder next to your project, the first time you run it.

## 2. One-time: install the skill

Unzip `rfp-intake.zip` into your personal Claude skills folder so that the path ends up looking like this:

```
%USERPROFILE%\.claude\skills\rfp-intake\SKILL.md
%USERPROFILE%\.claude\skills\rfp-intake\scripts\
%USERPROFILE%\.claude\skills\rfp-intake\references\
```

Create the `.claude\skills` folders if they don't exist. In PowerShell:

```powershell
mkdir "$env:USERPROFILE\.claude\skills" -Force
Expand-Archive .\rfp-intake.zip -DestinationPath "$env:USERPROFILE\.claude\skills" -Force
dir "$env:USERPROFILE\.claude\skills\rfp-intake"
```

`SKILL.md` must sit directly inside the `rfp-intake` folder — not inside a second nested `rfp-intake` folder. If it ended up nested, move it up one level.

No restart is needed; Claude Code picks up the skill right away. Type `/` in Claude Code to see it in the list.

## 3. Running it

Start Claude Code in a terminal, then either type `/rfp-intake` or just ask for it in plain words. The useful version of the request names the folder:

```
/rfp-intake Prepare the RFP package in C:\Projects\Fort Lewis Paving\RFP for estimating.
```

or

```
Use the rfp-intake skill on the RFP folder at C:\Projects\Fort Lewis Paving\RFP.
Put the project packet in C:\Projects\Fort Lewis Paving\packet.
```

On the first run Claude sets up the Python environment itself — it checks the version, creates a local environment and installs the libraries. **Claude asks permission before each command it runs.** Read them and approve; they're all local (`python -m venv`, `pip install`, then the intake script). If Python is missing, Claude says so and asks before installing anything.

After that it copies and hashes every source file, extracts the text, and starts working through the package section by section. Expect the first pass on a large package to take a while and to involve a lot of reading.

## 4. What to expect

- Everything stays on the PC. No API key, no database, no uploads.
- The original RFP files are never modified. The packet is a separate folder.
- Start at `START_HERE.md` in the packet folder; it links to the registers and the readiness report.
- Estimating stays **blocked** until the checks pass and a named person signs off on the four release attestations. That is by design — the skill will not certify its own review.
- When an addendum arrives, run it again against the complete current folder. It reuses what hasn't changed, reports what did, and invalidates the previous release.

## Tips

- Keep the packet on a short local path, such as `C:\RFP\<project>-packet`. Very deep Windows paths can break at 260 characters.
- Don't build the packet inside a OneDrive or Dropbox synced folder; sync clients lock files mid-write.
- Close Excel or your PDF viewer if they have packet files open.
- Scanned pages: optional OCR needs Tesseract and Poppler installed and on PATH. Without them, the page is flagged rather than guessed at.

---

## Alternative: install from GitHub in one step

If the repo is published, skip steps 2 above entirely and run this inside Claude Code:

```
/plugin marketplace add Gabriel-Omat/rfp-intake
/plugin install rfp-intake@target-tools
```

Claude Code downloads it, keeps it updated, and lists it as `/rfp-intake`. Step 1 (Python) still applies.
