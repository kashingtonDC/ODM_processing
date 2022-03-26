import os
import PIL
import sys
import shutil
import imageio
from PIL import Image
from PIL.ExifTags import TAGS


if len(sys.argv) == 1:
	print("Please supply image directory as argument, exiting")
	sys.exit(0)

target_dir = os.path.join(os.getcwd(),sys.argv[1])
	
files = [os.path.join(target_dir,x) for x in os.listdir(target_dir) if x.endswith("JPG")]

imtype_dict = {	"tir" : [],
				"vis" : []}

for fn in files[:]:
	image = Image.open(fn)
	if image.size == (640,480):
		imtype = 'tir'
	elif image.size == (4056,3040):
		imtype = 'vis'

	imtype_dict[imtype].append(fn)


for imtype, files in imtype_dict.items():
	imtype_outdir = target_dir[:-1] + "_" + imtype

	if not os.path.exists(imtype_outdir):
		os.mkdir(imtype_outdir)
		print("CREATED {}".format(imtype_outdir))

	for fn in files:

		im_dir = os.path.join(imtype_outdir,"images")
		if not os.path.exists(im_dir):
			os.mkdir(im_dir)
			print("CREATED {}".format(im_dir))

		im_id = os.path.split(fn)[1]
		outfn = os.path.join(im_dir,im_id)
		# print(fn,outfn)
		shutil.copy(fn, outfn)

	print("Moved files to {}".format(im_dir))

print("*****"  * 15)
print("COMPLETE")
print("*****"  * 15)
