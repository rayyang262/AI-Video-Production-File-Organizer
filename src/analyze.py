# v2 — AI content analysis: group same-scene trials via image embeddings
import cv2
from sentence_transformers import SentenceTransformer
from PIL import Image
from sentence_transformers import util
from sentence_transformers import util
from classify import classify_type     
from pathlib import Path

model = SentenceTransformer("clip-ViT-B-32")

def embed(image_path):
    image = Image.open(image_path)      # open the image file into memory (PIL)
    return model.encode(image)            # turn the image into its vector

def first_frame(video_path, out_path):
    cap = cv2.VideoCapture(video_path)
    success, frame = cap.read()      # read the first frame -> returns (success, frame)
    cap.release()
    if success:
        cv2.imwrite(out_path, frame)    # save the frame array to an image file
        return True
    return False

def similarity(image_a, image_b):
    va = embed(image_a)                    # vector for image A
    vb = embed(image_b)                    # vector for image B
    return util.cos_sim(va, vb).item()     # how close they are, as a plain number

def to_image(path):
    if classify_type(path) == "video":
        cap = cv2.VideoCapture(path)
        success, frame = cap.read()
        cap.release()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return Image.fromarray(frame_rgb)
    else:
        return Image.open(path)

def group_scenes(image_paths, threshold=0.8):
    images = [to_image(p) for p in image_paths]     # open every image
    embeddings = model.encode(images)                 # embed them all -> matrix
    clusters = util.community_detection(
        embeddings, threshold=threshold, min_community_size=1
    )
    groups = []
    for cluster in clusters:                          # each cluster = list of indices
        groups.append([image_paths[i] for i in cluster])   # indices -> paths
    return groups

def name_groups(groups):
    scene_of = {}                                  # file -> scene name
    for group in groups:
        print("\nProposed group:")
        for f in group:
            print("  *", Path(f).name)
        name = input("Scene name (blank = leave untagged): ").strip()
        if name:                                    # only tag if they typed something
            for f in group:
                scene_of[f] = name
    return scene_of

imgs = [
  "/Users/rayyangbackup/Downloads/拉布布/Replace_coke_bottle_with_screenshot_202607311710.mp4",
  "/Users/rayyangbackup/Downloads/拉布布/Camera_slow_motion_around_product_202607311558.mp4",
  "/Users/rayyangbackup/Downloads/拉布布/Camera_slow_motion_around_product_202607311700.mp4",
]


for i, group in enumerate(group_scenes(imgs, threshold=0.8), start=1):
    groups = group_scenes(imgs, threshold=0.8)   # AI proposes groups
    scene_map = name_groups(groups)              # YOU name them (this is the input step)
    print(scene_map)                             # the file -> scene result