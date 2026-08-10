from pathlib import Path
import cv2
import re


def classify_type(path):
    suffix = Path(path).suffix        
    suffix = suffix.lower()           

    video_exts = {".mp4", ".mov", ".m4v"}          
    image_exts = {".jpg", ".jpeg", ".png"}

    if suffix in video_exts:      
        return "video"
    elif suffix in image_exts:
        return "image"
    else:
        return "other"


def read_dimensions(path):
    cap = cv2.VideoCapture(path)     # block 1 — opens the file (given to you)

    width  = cap.get(cv2.CAP_PROP_FRAME_WIDTH)        # block 2 — read the WIDTH property
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    cap.release()                          # block 3 — close the file

    return width, height                 # hand back both numbers, comma-separated

def resolution_tier(width, height):
    long_side = max(width, height)

    if long_side >= 3700:        # your 4k cutoff
        return "4k"
    elif long_side >= 1800:      # your 1080p cutoff
        return "1080p"
    else:
        return "720p"

def is_screenshot(path):
    p = Path(path).name
    return p.startswith(("Screenshot", "屏幕快照"))



def is_generated_video(path):
    name = Path(path).name.lower()       # lowercase it or not? your case decision

    if Path(path).suffix.lower() != ".mp4":   # not an mp4 → can't be generated
        return False

    name = Path(path).name.lower()
    if name.startswith("kling"):
            return True

    # Jimeng: filename contains a known marker anywhere
    if name.startswith("jimeng-"):
        return True
    
    # Topaz: filename contains a known marker anywhere
    if "_precision_starlight" in name:
        return True

    # Tapnow: filename contains a known marker anywhere
    if re.search(r"video-", name):
        return True

    # Omni: an underscore, then a long run of digits (datetime stamp)
    if re.search(r"_\d{8,}", name):
        return True
    
    # ... your four pattern checks stay exactly as they are ...
    return False


def classify(path):
    file_type = classify_type(path)

    if file_type == "image":
        if is_screenshot(path):
            return "references/screenshots"      # macOS screenshot → references
        else:
            return "references/ai-generated"     # any other image → ai-generated

    elif file_type == "video":
        if is_generated_video(path):
            width, height = read_dimensions(path)
            tier = resolution_tier(width, height)
            return f"videos/{tier}"              # e.g. "videos/1080p"
        else:
            return "references/videos"

    else:
        return "other"

if __name__ == "__main__":
    print(classify("/Users/rayyangbackup/Desktop/MentorMatching_1.mp4"))                        # expect references/videos      (.mp4, no generator name → reference)
    print(classify("/Users/rayyangbackup/Desktop/Session_1.mp4"))                               # expect references/videos      (.mp4, no generator name → reference)
    print(classify("/Users/rayyangbackup/Desktop/Screen Recording 2026-07-31 at 6.26.20 PM.mov"))  # expect references/videos  (.mov → guard → reference)
    print(classify("/Users/rayyangbackup/Desktop/Screenshot 2026-07-21 at 5.00.31 PM.png"))     # expect references/screenshots

