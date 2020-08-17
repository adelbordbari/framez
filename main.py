from natsort import natsorted
from ffprobe import FFProbe
from time import sleep
from tqdm import tqdm
from PIL import Image
import cv2
import os

# get and format file path
print("All modules loaded, press enter to proceed...")
path = input("\nEnter file path to the file(w/ filename, w/out the last backslash):\n")
if not os.path.exists(path):
    print("Path is incorrect, quitting")
    exit(0)
if path[0] == "~":
    os.path.expanduser(path)  # replace ~ with literal home address

meta = FFProbe(path)
# get metadata
video_duration = meta.metadata["Duration"][:-3]
rate = meta.video[0].framerate
height = int(meta.video[0].width)
# one shot per 5 seconds
freq = int(rate) * 5

# info for the process bar
hours = int(video_duration[1]) * 3600
minutes = int(video_duration[3:5]) * 60
seconds = int(video_duration[-2:])
duration_seconds = hours + minutes + seconds
frames = rate * duration_seconds
output_images = frames // freq  # number of extracted images

(directory, video_name) = os.path.split(path)

dst_path = directory + "/images/"
os.system("mkdir " + dst_path)
os.system("mkdir " + dst_path + "resized")
print("Destination folder created.\n")

print("Extracting frames...")
cap = cv2.VideoCapture(path)
i = 1  # current captured frame, how many 24's has already been iterated
with tqdm(total=frames) as pbar:
    while cap.isOpened():
        frame_id = cap.get(1)  # first frame in the current stream
        ret, frame = cap.read()
        if ret != True:  # if run out of frames, video finished
            break
        if frame_id % freq == 0:  # if frame# is a multiplicand of freq=24
            filename = dst_path + str(i) + ".jpg"
            i += 1
            cv2.imwrite(filename, frame)  # create the image
        pbar.update(1)
print(str(output_images) + " images extracted successfully.")
cap.release()
del pbar

src_path = directory + "/images/"
dst_path = src_path + "resized/"

images = natsorted(os.listdir(src_path))

os.system("clear")
i = 1
max_counter = len(images) - 1  # all images count
with tqdm(total=output_images) as pbar:
    for image in images:
        if i <= max_counter:  # process until all images are done
            read_path = src_path + image
            img = cv2.imread(read_path, cv2.IMREAD_UNCHANGED)
            w = 2  # convert to 2px
            h = img.shape[1]  # unchanged
            dim = (w, h)
            resized = cv2.resize(img, dim)
            filename = dst_path + str(i) + "_re.jpg"
            cv2.imwrite(filename, resized)  # create the image
            if i == 1:  # do only once
                print(str(img.shape) + " convert to " + str(dim))
            i += 1
            pbar.update(1)
        else:
            print("Finished " + str(len(images) - 1) + " pictures.")

images_list = natsorted(os.listdir(dst_path))

images_list = [Image.open(dst_path + x) for x in images_list]

# we have the height, user input #3
width = len(images_list) * 2  # number of small pictures, each 2px
out = Image.new("RGB", (width, height))  # create an empty image

x_offset = 0
for im in images_list:
    out.paste(im, (x_offset, 0))
    x_offset += im.size[0]

out.save(directory + "/" + video_name[:-4] + ".jpg")
print("Cleaning Up...")
os.system("rm -rf " + src_path)

print("All set, finishing now.")
