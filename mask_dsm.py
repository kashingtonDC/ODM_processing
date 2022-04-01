import os
import sys
import imageio
import numpy as np
import rasterio as rio

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
	arr[arr==src.nodata] = np.nan

	outfn = os.path.join(dem_dir,os.path.split(fn)[-1].replace(".","_masked."))

	with rio.open(outfn, 'w', **profile) as dst:
		dst.write(arr, 1)
		
	print("Wrote {} =========================== ".format(outfn))