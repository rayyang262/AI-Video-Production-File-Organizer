# Running the File Organizer

Three ways to use the tool: a **visual app** (Streamlit), a **CLI**, and a separate **cuts** step.

## 1. One-time setup (per machine)

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

Optional but recommended before a demo — pre-download the CLIP model so nothing
downloads while you're presenting:

```bash
./.venv/bin/python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('clip-ViT-B-32')"
```

## 2. Visual app (Streamlit)

```bash
./.venv/bin/streamlit run src/app.py
```

- Opens a browser tab at `http://localhost:8501`.
- Paste a **real folder path** into the box (e.g. `/Users/you/Desktop/demo_sample`).
- Click **Group similar files (AI)** — clusters by content and suggests a folder per group.
- Confirm or rename each group's project, then click **Organize files**.
- Copies into your Desktop project folders (non-destructive — originals stay put).

> ⚠️ Must be launched with `streamlit run` — **not** `python src/app.py`. Plain
> `python` prints "missing ScriptRunContext" warnings and never starts the app.

## 3. CLI

```bash
./.venv/bin/python src/organize.py "/path/to/folder"
```

- Pass a **real folder path** as the argument (not the literal `/path/to/folder`).
- Assign each file to a project when prompted, then type `y` to confirm the copy.
- Writes into `~/Desktop/Organized/`.

## 4. Assemble final cuts

```bash
./.venv/bin/python src/cuts.py "/path/to/folder"
```

Lists the videos; type the finals in edit order (e.g. `3,1,5`); it copies them
into a `cuts/` folder renamed `cut1`, `cut2`, …

## Syncing to another computer

```bash
git pull origin main
./.venv/bin/python -m pip install -r requirements.txt   # picks up any new dependencies
```

Never copy the `.venv` folder between machines — recreate it from
`requirements.txt` instead.

## Notes

- **Non-destructive:** everything is a copy; source files are never moved or deleted.
- **First AI run** downloads the CLIP model (~hundreds of MB); it's cached after that.
- `python` runs the CLI/scripts; `streamlit run` runs the app — different launchers.
