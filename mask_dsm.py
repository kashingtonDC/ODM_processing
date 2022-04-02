import os
import sys
import imageio
import numpy as np
import rasterio as rio
import matplotlib.pyplot as plt

if len(sys.argv) == 1:
	print("Please supply image directory as argument, exiting")
	sys.exit(0)

target_dir = os.path.join(os.getcwd(),sys.argv[1])
dem_dir = os.path.join(target_dir,'odm_dem')
dtm_fn = os.path.abspath(os.path.join(dem_dir,"dtm.tif"))
dsm_fn = os.path.abspath(os.path.join(dem_dir,"dsm.tif"))

for fn in [dtm_fn, dsm_fn]:
	src = rio.open(fn)
	profile = src.profile
	arr = src.read(1)
	# Get mask set alpha channel
	alpha = arr!=src.nodata
	alpha = alpha.astype(np.uint8)
	alpha[alpha==1] = 255
	# mask nodata 
	arr[arr==src.nodata] = np.nan
	# scale vals bt 0-255
	arr = ((arr - np.nanmin(arr)) * (1/(np.nanmax(arr) - np.nanmin(arr)) * 255)).astype('uint8')

	arr[arr==np.nan] = 0

	# 4 channel stack (RGBA)
	rgb = np.dstack([arr,arr,arr, alpha])
	rgb = np.moveaxis(rgb, [0, 1, 2], [1, 2, 0])
	outfn = os.path.join(dem_dir,os.path.split(fn)[-1].replace(".","_masked."))
	
	# write out
	with rio.open(outfn, 'w',
		height=rgb.shape[1],
		width=rgb.shape[2],
		count=4,
		# dtype=profile['dtype'],
		dtype = np.uint8,
		nodata=0,
		transform = profile['transform'],
		crs = profile['crs'],
		compress='deflate') as dst:
			dst.write(rgb)
			
	print("Wrote {} =========================== ".format(outfn))