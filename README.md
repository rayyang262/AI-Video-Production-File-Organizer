# AI Video Production File Organizer

A Python tool — a **CLI and a visual (Streamlit) app** — that reconstructs order from the chaos of AI media generation. It scans messy download locations, classifies each file by **type, role, and true resolution**, groups files into projects and dates, uses image embeddings to **cluster similar clips and suggest project folders**, and — only after you confirm — copies everything into a clean, predictable folder tree. Non-destructive by design.

📖 **[How to run it → docs/RUNNING.md](docs/RUNNING.md)**

---

## The problem (why this exists)

I built this after an AI video production internship where I generated **hundreds** of video and image variants across tools — Google Omni/Flow, Kling, Seedance, Jimeng, Tapnow, Topaz upscaler, plus phone screen-recordings and screenshots. Every export landed in Desktop and Downloads with auto-generated names like `Camera_slow_motion_around_product_202607311700.mp4` or `video-1739482910.mp4`, all mixed together: reference clips next to raw trials next to near-final upscales.

Finding the right file meant scrubbing through dozens of near-identically named videos by hand. The manual process was: open a folder, guess from filenames, open files to check, drag things around, repeat. It was the bottleneck in an otherwise fast pipeline.

This tool automates the sorting so the human only makes the decisions a human actually has to make.

---

## What it does

```
scan → classify → cluster / assign projects (AI-assisted) → preview → confirm → copy
```

Two ways to use it:
- **CLI** (`src/organize.py`) — the original scriptable pipeline; assign projects, optionally run AI grouping, confirm, copy.
- **Visual app** (`src/app.py`, Streamlit) — see a thumbnail of every file, let the AI cluster them and suggest a project folder per group, adjust anything it got wrong, and organize with a click.

It produces a clean tree:

```
{ProjectName}/
  {YYYY-MM-DD}/
    references/
      screenshots/        macOS screenshots
      ai-generated/        AI images that aren't screenshots
      videos/              reference clips, screen recordings, phone footage
    videos/
      720p/  1080p/  4k/   generated videos, binned by TRUE resolution
        {scene}/           optional: same-scene trials grouped by the AI step
```

(The CLI builds this under a clean `Organized/` sandbox; the app can write it straight into your real Desktop project folders.) A separate `cuts` step lets you pick the final videos and their order and copies them out renamed `cut1`, `cut2`, `cut3`.

---

## Key engineering decisions

The interesting part of this project isn't that it moves files — it's *where I chose to automate, where I chose rules over AI, and where I kept a human in the loop.*

### Rules for the core, not an LLM
Every generator leaves a filename fingerprint (`kling_*`, `*_precision_starlight`, `video-{digits}`, `jimeng-*`, Omni's `..._{datetime}`), and every video's resolution is readable from the file itself. So the core classifier is **deterministic rules** — fast, free, 100% reproducible, and explainable. No LLM is needed to decide where a file goes, and adding a new generator is a one-line fingerprint. Reaching for AI on a problem the metadata already answers would be worse engineering, not better.

### Read the *true* pixel dimensions, never the filename
A file named `..._4k_precision_starlight.mp4` might actually be 1080p — the `4k` is just text someone typed, and **renamed files lie.** So resolution is determined by opening each video and reading its real pixel dimensions with OpenCV, then binning by the larger dimension (so landscape and vertical versions of the same tier land together). Trusting metadata over filenames is the single most important decision in the project.

### AI only where semantics live — and always as a suggestion
Filenames and dates *can't* tell you that eight differently-named clips are the same shot, or that a batch belongs to one project — only the visual content can. That's the one place rules fail and AI earns its place. The AI layer uses **CLIP image embeddings** (a 512-number vector per file, from the first frame of a video) two ways:
- **Cluster similar clips** by cosine similarity (`community_detection`) — group same-shot trials or a fresh batch.
- **Suggest a project folder** — average each existing folder's media into a "fingerprint," then nearest-neighbor-match a new group to the closest folder.

An honest finding: CLIP similarity scores bunch up in a narrow high band, so a fixed absolute threshold ("0.85 = same") is unreliable — the *relative* ranking carries the signal. So it uses relative clustering with a tunable threshold, and the AI only ever **proposes**. **You confirm, rename, or override any file** into a different (or brand-new) project. The model does the tedious 90%; the human catches the edge cases.

### Safe by default
The filesystem is only ever touched after an explicit confirmation, and files are **copied, never moved** — originals stay exactly where they are. Worst case, you delete the output and have lost nothing. Preview first, write second.

### The assumption that broke (and the fix)
The original design assumed "files from the same day belong to the same project." That turned out to be false — I often work on several projects in one day. The fix was to **decouple the two things I'd wrongly coupled**: *date* is a fact the file already knows (read automatically), while *project* is human intent (assigned per file). A project can now span many days, and a single day can hold many projects.

---

## Architecture

Two interfaces (CLI + app) over one shared core:

| File | Responsibility |
|------|----------------|
| `src/classify.py` | Deterministic classifier: file → (type, role, resolution) → destination subpath. Pure rules + OpenCV. |
| `src/organize.py` | The CLI application: scan, assign projects, build the plan, confirm, copy. `build_plan` is shared with the app. |
| `src/analyze.py` | The AI layer: CLIP embeddings, similarity, clustering, project fingerprints and matching. Loaded only when requested. |
| `src/cuts.py` | Manually pick final videos and their order; copy them out as `cut1`, `cut2`, … |
| `src/app.py` | Streamlit visual UI: thumbnails, AI grouping + folder suggestions, per-file overrides, one-click organize. |

The AI layer is **opt-in and lazy-loaded** — the heavy model only loads when you actually ask for grouping. The deterministic core never depends on it.

---

## Setup

Requires Python 3 and macOS (see limitations). Full run instructions: **[docs/RUNNING.md](docs/RUNNING.md)**.

```bash
git clone https://github.com/rayyang262/AI-Video-Production-File-Organizer.git
cd AI-Video-Production-File-Organizer
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

Dependencies: `opencv-python` (frames + dimensions), `sentence-transformers` (CLIP embeddings), `Pillow` (images), `numpy` (fingerprint averaging), `streamlit` (visual app).

---

## Usage

**Visual app:**
```bash
./.venv/bin/streamlit run src/app.py
```

**CLI:**
```bash
./.venv/bin/python src/organize.py "/path/to/messy/folder"
```

**Assemble final cuts:**
```bash
./.venv/bin/python src/cuts.py "/path/to/videos"
```

See **[docs/RUNNING.md](docs/RUNNING.md)** for the step-by-step for each.

---

## Limitations & future work

Honest about what's not done:

- **Drag-and-drop cluster editing (biggest next step).** The app lets you fix the AI's grouping with per-file dropdown overrides. True drag-a-thumbnail-between-clusters isn't possible in Streamlit — it's *drag OR thumbnails, not both* — so a polished version needs a dedicated web frontend (React + a drag library).
- **macOS only** — uses `st_birthtime` (file creation time) for dating, not available on all platforms.
- **CLI ergonomics** — you pass full paths; a shell alias or `argparse` would smooth this.
- **Thresholds are tunable knobs**, not magic — good defaults exist for scene and project similarity, but they vary by dataset.
- **No input validation yet** — an out-of-range selection or malformed command raises rather than reprompts.
- **Fingerprints aren't cached** — the app re-embeds reference folders on each grouping run.
- **The app copies on click** — unlike the CLI, there's no preview-then-confirm gate before writing.

---

## What I learned

- When *not* to use AI is as much a design decision as when to use it.
- Metadata beats filenames; verify at the source.
- Ship the reliable, deterministic core first; add AI as an assist with a human gate, not as the foundation.
- The AI's output should always be overridable by a human.
- Know your tool's ceiling — Streamlit is excellent for fast visual data apps but not for drag-and-drop; recognizing that tradeoff is part of choosing the right stack.
- A wrong assumption caught early (same-day ≠ same project) is cheaper to fix than a clever feature built on it.
