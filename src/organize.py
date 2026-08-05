from pathlib import Path
from classify import classify
from datetime import datetime

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

def assign_projects(clusters, projects_source):
    projects = {}
    known = []

    root = Path(projects_source)
    if root.is_dir():
        for p in root.iterdir():
            if p.is_dir() and not p.name.startswith("."):                
                known.append(p.name)

    for date, files in clusters.items():
        print(f"\nOn {date} you had {len(files)} file(s): ")                              
        for file in files:
            print("  * " + file.name)

        if known:                                    
            print("Here's the list of project names: ")                           
            for i, name in enumerate(known, start=1):
                print(f"  {i}. {name}")
            answer = input("Type in the number, or a new project name: ")                  
        else:                                        
            answer = input("Type a new project name:")                 

        if answer.isdigit():
            name = known[int(answer) - 1]
        else:
            name = answer
            if name not in known:
                known.append(name)

        projects[date] = name
    return projects

def build_plan(clusters, projects, output_root):
    plan = []                                          # list of (source, destination) pairs
    for date, files in clusters.items():
        project = projects[date]                       # the project name for this date
        for file in files:
            sub = classify(file)                       # e.g. "references/videos"
            dest = Path(output_root) / project / date / sub / file.name   # stitch the 4 layers in order
            plan.append((file, dest))
    return plan



files = scan("/Users/rayyangbackup/Downloads")
clusters = cluster_by_date(files)
projects = assign_projects(clusters, "/Users/rayyangbackup/Desktop")
plan = build_plan(clusters, projects, "/Users/rayyangbackup/Desktop/Organized")
run_copy(plan)