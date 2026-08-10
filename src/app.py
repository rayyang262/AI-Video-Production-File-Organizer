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
    existing = sorted(p.name for p in desktop.iterdir()
                      if p.is_dir() and not p.name.startswith("."))   # existing folders = buckets

    new = st.text_input("Add a new project bucket:")
    if new and new not in existing and new not in st.session_state.extra_projects:
        st.session_state.extra_projects.append(new)                  # remember it across reruns

    projects = existing + st.session_state.extra_projects            # all buckets

    files = [f for f in Path(folder).iterdir() if f.suffix.lower() in MEDIA_EXTS]
    st.write(f"{len(files)} media files found")

    assignments = {}
    cols = st.columns(3)
    for i, f in enumerate(files):
        col = cols[i % 3]
        if f.suffix.lower() in (".mp4", ".mov"):
            col.video(str(f))
        else:
            col.image(str(f))
        col.caption(f.name)

        choice = col.selectbox("Project", ["—"] + projects, key=f"sel_{i}")   # pick a bucket
        if choice != "—":
            assignments[f] = choice

    st.write(f"### {len(assignments)} of {len(files)} files assigned")

    if st.button("Organize files"):
        plan = build_plan(assignments, desktop / "Organized", {})
        for source, dest in plan:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
        st.success(f"Copied {len(plan)} files into {desktop / 'Organized'}")