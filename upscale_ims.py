
import os
import PIL
import sys
from PIL import Image
from tqdm import tqdm


if len(sys.argv) == 1:
	print("Please supply image directory as argument, exiting")
	sys.exit(0)

target_dir = os.path.join(os.getcwd(),sys.argv[1])
img_dir = os.path.join(target_dir,"images")
	
files = [os.path.join(img_dir,x) for x in os.listdir(img_dir) if x.endswith("JPG")]

print("RESIZING IMAGES")

for fn in tqdm(files[:]):
	image = Image.open(fn)
	width, height = image.size
	new_img = image.resize((int(width/2),int(height/2)))
	new_img.save(fn, "JPEG", optimize=True)

print("*****"  * 15)
print("COMPLETE")
print("*****"  * 15)
