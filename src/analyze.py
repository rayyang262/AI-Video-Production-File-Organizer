# v2 — AI content analysis: group same-scene trials via image embeddings
import cv2
from sentence_transformers import SentenceTransformer
from PIL import Image
from sentence_transformers import util
from sentence_transformers import util


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

def group_scenes(image_paths, threshold=0.8):
    images = [Image.open(p) for p in image_paths]     # open every image
    embeddings = model.encode(images)                 # embed them all -> matrix
    clusters = util.community_detection(
        embeddings, threshold=threshold, min_community_size=1
    )
    groups = []
    for cluster in clusters:                          # each cluster = list of indices
        groups.append([image_paths[i] for i in cluster])   # indices -> paths
    return groups

trees1 = "/Users/rayyangbackup/Downloads/Trees_flowers_grass_sunlight_202607171539.jpeg"
trees2 = "/Users/rayyangbackup/Downloads/Trees_flowers_grass_dawn_scene_202607171539.jpeg"
ui     = "/Users/rayyangbackup/Downloads/Add_button_to_navigation_bar_202607171542.jpeg"

imgs = [trees1, trees2, ui]
for i, group in enumerate(group_scenes(imgs, threshold=0.8), start=1):
    print(f"Group {i}:", [p.split('/')[-1] for p in group])