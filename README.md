# AI Video Production File Organizer

A Python CLI that reconstructs order from the chaos of AI media generation. It scans messy download locations, classifies each file by **type, role, and true resolution**, groups files into projects and dates, optionally clusters same-scene trials with an image-embedding model, and — only after you confirm — copies everything into a clean, predictable folder tree. Non-destructive by design.

---

## The problem (why this exists)

I built this after an AI video production internship where I generated **hundreds** of video and image variants across tools — Google Omni/Flow, Kling, Seedance, Topaz upscaler, phone screen-recordings, screenshots. Every export landed in Desktop and Downloads with auto-generated names like `Camera_slow_motion_around_product_202607311700.mp4` or `video-1739482910.mp4`, all mixed together: reference clips next to raw trials next to near-final upscales.

Finding the right file meant scrubbing through dozens of near-identically named videos by hand. The manual process was: open a folder, guess from filenames, open files to check, drag things around, repeat. It was the bottleneck in an otherwise fast pipeline.

This tool automates the sorting so the human only makes the decisions a human actually has to make.

---

## What it does

```
scan  →  classify  →  assign projects  →  [AI scene grouping]  →  preview  →  confirm  →  copy
```

Point it at a folder and it produces a clean tree:

```
Organized/
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

A separate `cuts` step lets you pick the final videos and their order and copies them out renamed `cut1`, `cut2`, `cut3`.

---

## Key engineering decisions

The interesting part of this project isn't that it moves files — it's *where I chose to automate, where I chose rules over AI, and where I kept a human in the loop.*

### Rules for the core, not an LLM
Every generator leaves a filename fingerprint (`kling_*`, `*_precision_starlight`, `video-{digits}`, Omni's `..._{datetime}`), and every video's resolution is readable from the file itself. So the core classifier is **deterministic rules** — fast, free, 100% reproducible, and explainable. No LLM is needed to decide where a file goes. Reaching for AI on a problem the metadata already answers would be worse engineering, not better.

### Read the *true* pixel dimensions, never the filename
A file named `..._4k_precision_starlight.mp4` might actually be 1080p — the `4k` is just text someone typed, and **renamed files lie.** So resolution is determined by opening each video and reading its real pixel dimensions with OpenCV, then binning by the larger dimension (so landscape and vertical versions of the same tier land together). Trusting metadata over filenames is the single most important decision in the project.

### AI only where semantics live
Filenames and dates *can't* tell you that eight differently-named videos are all trials of the same shot — only the visual content can. That's the one place rules fail and AI earns its place. The optional scene-grouping step turns each file's first frame into a **CLIP embedding** (a 512-number vector capturing content) and clusters them by cosine similarity.

An honest finding from building this: CLIP similarity scores bunch up in a narrow high band, so a fixed absolute threshold ("0.85 = same scene") is unreliable — the *relative* ranking is what carries the signal. So grouping uses relative clustering with a tunable threshold, and — critically — the AI only *proposes* groups. **You confirm and name them.** The model does the tedious 90%; the human catches the edge cases.

### Safe by default
The filesystem is only ever touched after an explicit confirmation, and files are **copied, never moved** — originals stay exactly where they are. Worst case, you delete the output folder and have lost nothing. Preview first, write second.

### The assumption that broke (and the fix)
The original design assumed "files from the same day belong to the same project." That turned out to be false — I often work on several projects in one day. The fix was to **decouple the two things I'd wrongly coupled**: *date* is a fact the file already knows (read automatically), while *project* is human intent (assigned per file). A project can now span many days, and a single day can hold many projects.

---

## Architecture

Four modules, each with one job:

| File | Responsibility |
|------|----------------|
| `src/classify.py` | Deterministic classifier: file → (type, role, resolution) → destination subpath. Pure rules + OpenCV. |
| `src/organize.py` | The application: scan folders, cluster by date, assign projects, build the plan, confirm, copy. |
| `src/analyze.py` | The AI layer: CLIP embeddings, similarity, and same-scene clustering. Loaded only when requested. |
| `src/cuts.py` | Stage 7: manually pick final videos and their order; copy them out as `cut1`, `cut2`, … |

The AI layer is **opt-in** — the CLI asks before running it, and the heavy model only loads if you say yes. The deterministic core never depends on it.

---

## Setup

Requires Python 3 and macOS (see limitations).

```bash
git clone https://github.com/rayyang262/AI-Video-Production-File-Organizer.git
cd AI-Video-Production-File-Organizer
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

Dependencies: `opencv-python` (video frames + dimensions), `sentence-transformers` (CLIP embeddings), `Pillow` (image handling).

---

## Usage

**Organize a folder:**
```bash
./.venv/bin/python src/organize.py "/path/to/messy/folder"
```
You'll assign each file to a project, optionally run AI scene grouping, and confirm before anything is copied.

**Assemble final cuts** (separate manual step):
```bash
./.venv/bin/python src/cuts.py "/path/to/videos"
```
Lists the videos; you type the finals in edit order (e.g. `3,1,5`); it writes `cuts/cut1…` in that order.

---

## Limitations & future work

Honest about what's not done:

- **macOS only** — uses `st_birthtime` (file creation time) for dating, which isn't available on all platforms.
- **CLI ergonomics** — you pass full paths; a shell alias or `argparse` would smooth this.
- **Scene-grouping threshold** needs tuning per dataset; a good default exists but it's a knob, not magic.
- **No input validation yet** — an out-of-range selection number or a malformed command will raise rather than reprompt.
- **Planned v3: a web UI** — for media, filenames aren't enough; a thumbnail-based interface would let you *see* what you're sorting instead of reading names. This is the highest-impact next step.

---

## What I learned

- When *not* to use AI is as much a design decision as when to use it.
- Metadata beats filenames; verify at the source.
- Ship the reliable, deterministic core first; add AI as an assist with a human gate, not as the foundation.
- A wrong assumption caught early (same-day ≠ same project) is cheaper to fix than a clever feature built on it.
