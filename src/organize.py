from pathlib import Path
from classify import classify
from datetime import datetime
import sys


import shutil     # add at the TOP of the file with your other imports

def run_copy(plan):
    # 1. show the plan
    for source, dest in plan:
        print(f"{source.name}  ->  {dest}")

    # 2. confirm before writing anything
    answer = input("\nProceed with copy? (y/n) ")
    if answer != "y":
        print("Cancelled — nothing was copied.")
        return

    # 3. create folders and copy
    for source, dest in plan:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
    print("Done — files copied.")



def scan(folder):
    results = []              
    for item in Path(folder).iterdir():
        if item.is_file() and not item.name.startswith((".", "~$")):
            results.append(item)
    return results

def preview(folder):
    files = scan(folder)

    groups = {}                              # blank 1: an empty dictionary
    for file in files:
        destination = classify(file)
        if destination not in groups:         # first time seeing this destination?
            groups[destination] = []         # blank 2: start it with an empty list
        groups[destination].append(file.name)       # blank 3: add the file's NAME

    for destination, names in groups.items():  # .items() gives key, value pairs
        print(destination)                     # the folder header
        for name in names:
            print("   " + name)                # indent the file under its header

def file_date(path):
    timestamp = Path(path).stat().st_birthtime
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d")


def cluster_by_date(files):
    clusters = {}    
    for file in files:
        date = file_date(file)             
        if date not in clusters:
            clusters[date] = []
        clusters[date].append(file)        
    return clusters

def parse_command(text):
    project_part, numbers_part = text.split(":")        # "portfolio: 1,3,5" -> ["portfolio", " 1,3,5"]
    project = project_part.strip()                      # clean spaces -> "portfolio"
    numbers = [int(n) for n in numbers_part.split(",")] # " 1,3,5" -> [1, 3, 5]
    return project, numbers


def assign_files_to_projects(files, projects_source):
    assignments = {}                      # file -> project name (the result)
    known = []                            # existing project names, for reuse

    # seed known projects from existing folders (same seeding as before)
    root = Path(projects_source)
    if root.is_dir():
        for p in root.iterdir():
            if p.is_dir() and not p.name.startswith("."):
                known.append(p.name)

    # keep looping until EVERY file has been assigned a project
    while len(assignments) < len(files):
        print("\nFiles still needing a project:")
        for i, file in enumerate(files, start=1):
            if file not in assignments:                 # only show unassigned ones
                print(f"  {i}. {file.name}   ({file_date(file)})")

        if known:
            print("Known projects:", ", ".join(known))

        command = input("Assign  (e.g.  portfolio: 1,3,5 ) : ")
        project, numbers = parse_command(command)       # your parser from before

        if project not in known:
            known.append(project)

        for n in numbers:
            file = files[n - 1]                          # 1-based menu -> 0-based list
            assignments[file] = project

    return assignments
def build_plan(assignments, output_root):
    plan = []
    for file, project in assignments.items():   # each file already knows its project
        date = file_date(file)                  # ← date derived per file, automatically
        sub = classify(file)
        dest = Path(output_root) / project / date / sub / file.name
        plan.append((file, dest))
    return plan



input_folder = sys.argv[1]         
desktop = Path.home() / "Desktop" 
files = scan(input_folder)
assignments = assign_files_to_projects(files, desktop)
plan = build_plan(assignments, desktop / "Organized")
run_copy(plan)