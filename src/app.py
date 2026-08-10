import streamlit as st
from pathlib import Path
from classify import classify
from organize import build_plan
import shutil

MEDIA_EXTS = (".mp4", ".mov", ".png", ".jpg", ".jpeg", ".tiff", ".heic")

st.title("Media Organizer")

if "extra_projects" not in st.session_state:      # runs once
    st.session_state.extra_projects = []          # projects you type in

folder = st.text_input("Paste a folder path to preview:")

if folder:
    desktop = Path.home() / "Desktop"
    organized = desktop / "Organized"
    existing = sorted(p.name for p in desktop.iterdir() if p.is_dir() and not p.name.startswith("."))
    files = [f for f in Path(folder).iterdir() if f.suffix.lower() in MEDIA_EXTS]
    st.write(f"{len(files)} media files found")

    if st.button("Group similar files (AI)"):
        from analyze import group_scenes, project_fingerprints, suggest_project
        st.session_state.groups = group_scenes(files, threshold=0.7)
        fps = project_fingerprints(desktop)                                   # fingerprint desktop folders
        st.session_state.suggestions = [suggest_project(g[0], fps) for g in st.session_state.groups]

    groups = st.session_state.get("groups", [])
    suggestions = st.session_state.get("suggestions", [])
    NEW = "➕ Type a new project…"

    assignments = {}
    if groups:
        st.write(f"### AI found {len(groups)} group(s)")
        for g_idx, group in enumerate(groups):
            st.write(f"**Group {g_idx + 1}** — {len(group)} files")
            gcols = st.columns(4)
            for j, f in enumerate(group):
                c = gcols[j % 4]
                if f.suffix.lower() in (".mp4", ".mov"):
                    c.video(str(f))
                else:
                    c.image(str(f))

            options = existing + [NEW]
            suggestion = suggestions[g_idx] if g_idx < len(suggestions) else None
            default_idx = options.index(suggestion) if suggestion in existing else len(options) - 1
            choice = st.selectbox(f"Project for group {g_idx + 1}:", options,
                                  index=default_idx, key=f"gsel_{g_idx}")     # dropdown, AI-defaulted
            name = choice
            if choice == NEW:
                name = st.text_input(f"New project name for group {g_idx + 1}:", key=f"gnew_{g_idx}")

            if name and name != NEW:
                for f in group:
                    assignments[f] = name

    st.write(f"### {len(assignments)} of {len(files)} files assigned")
    if st.button("Organize files"):
        plan = build_plan(assignments, desktop, {})          
        for source, dest in plan:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
        st.success(f"Copied {len(plan)} files into your Desktop project folders")