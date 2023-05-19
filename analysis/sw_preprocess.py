import os
import ee
import time
import datetime
import rioxarray
import dateutil.relativedelta

import numpy as np
import pandas as pd
import rasterio as rio
import geopandas as gp
import matplotlib.image as mpimg
import matplotlib.pyplot as plt

from PIL import Image
from osgeo import gdal
from tqdm import tqdm
from shapely.geometry import box

ee.Initialize()

def gdf_to_ee_poly(gdf, simplify = False):

	if simplify:
		gdf = gdf.geometry.simplify(0.01)

	lls = gdf.geometry.iloc[0]
	x,y = lls.exterior.coords.xy
	coords = [list(zip(x,y))]
	area = ee.Geometry.Polygon(coords)

	return area

def array_from_df(df, variable):    

	'''
	Convets a pandas df with lat, lon, variable to a numpy array 
	'''

	# get data from df as arrays
	lons = np.array(df.longitude)
	lats = np.array(df.latitude)
	data = np.array(df[variable]) # Set var here 

	# get the unique coordinates
	uniqueLats = np.unique(lats)
	uniqueLons = np.unique(lons)

	# get number of columns and rows from coordinates
	ncols = len(uniqueLons)    
	nrows = len(uniqueLats)

	# determine pixelsizes
	ys = uniqueLats[1] - uniqueLats[0] 
	xs = uniqueLons[1] - uniqueLons[0]

	# create an array with dimensions of image
	arr = np.zeros([nrows, ncols], np.float32)

	# fill the array with values
	counter =0
	for y in range(0,len(arr),1):
		for x in range(0,len(arr[0]),1):
			if lats[counter] == uniqueLats[y] and lons[counter] == uniqueLons[x] and counter < len(lats)-1:
				counter+=1
				arr[len(uniqueLats)-1-y,x] = data[counter] # we start from lower left corner

	return arr


def get_ims(ImageCollection, var_name, scale_factor, native_res, startdate, enddate, area):

	'''
	Returns gridded images for EE datasets 
	Params: 
	ImageCollection -> ee.ImageCollection objet e.g. ee.ImageCollection("USDA/NAIP/DOQQ")
	var_name -> name of the band
	scale_factor -> given with some datasets for compression 
	native_res -> spatial resolution 
	startdate -> MUST BE LIKE "YYYY-mm-dd"
	enddate -> Same^
	area -> ee.Geometry object 
	
	'''
	start = ee.Date(startdate)
	end = ee.Date(enddate)
	im = ee.ImageCollection(ImageCollection.filterBounds(area).filterDate(start, end).set('system:time_start', end.millis()).select(var_name).mean())
	result = im.getRegion(area,native_res,"epsg:4326").getInfo()
	header, data = result[0], result[1:]

	datecollection = ImageCollection.filterDate(start,end)
	date = ee.Date(datecollection.first().get('system:time_start'))
	date_dict = date.format('Y-M-d').getInfo()
	print(date_dict)

	df = pd.DataFrame(np.column_stack(data).T, columns = header)
	df.latitude = pd.to_numeric(df.latitude)
	df.longitude = pd.to_numeric(df.longitude)
	df[var_name] = pd.to_numeric(df[var_name])

	results = []
	images = []
	for idx,i in enumerate(df.id.unique()):

		t1 = df[df.id==i]
		arr = array_from_df(t1,var_name)
		arr[arr == 0] = np.nan
		images.append(arr*scale_factor)# This is the only good place to apply the scaling factor. 
	results.append(images) 
	results_out = [item for sublist in results for item in sublist]
	return results_out

def get_sentinel(geometry, im_ac_date):
	
	# advance the date +/- 1 week from drone acquisition time 
	# start = ee.Date(im_ac_date).advance(-1,'month')
	# end = ee.Date(im_ac_date).advance(1,'month')

	im_ac_dt = datetime.datetime.strptime(im_ac_date, "%Y-%m-%d")
	start = im_ac_dt - dateutil.relativedelta.relativedelta(days=3)
	end = im_ac_dt + dateutil.relativedelta.relativedelta(days=3)

	# print(start,end)

	# Get rgb bands For sentinel 

	r = get_ims(ee.ImageCollection("COPERNICUS/S2_HARMONIZED"), 'B2', 0.0001, 10, start, end, geometry)
	g = get_ims(ee.ImageCollection("COPERNICUS/S2_HARMONIZED"), 'B3', 0.0001, 10, start, end, geometry)
	b = get_ims(ee.ImageCollection("COPERNICUS/S2_HARMONIZED"), 'B4', 0.0001, 10, start, end, geometry)

	rn,gn,bn = normalize(r[0]), normalize(g[0]), normalize(b[0])
	rgb = np.dstack((rn,gn,bn))

	# return the date
	collection = ee.ImageCollection("COPERNICUS/S2_HARMONIZED").filterDate(start,end)
	date = ee.Date(collection.first().get('system:time_start'))
	date_dict = date.format('Y-M-d').getInfo()
	
	return rgb, date_dict

def get_naip(geometry, startdate ='2020-01-01', enddate = '2023-01-01'):

	r = get_ims(ee.ImageCollection("USDA/NAIP/DOQQ"), 'R', 1, 3, startdate, enddate, geometry)
	g = get_ims(ee.ImageCollection("USDA/NAIP/DOQQ"), 'G', 1, 3, startdate, enddate, geometry)
	b = get_ims(ee.ImageCollection("USDA/NAIP/DOQQ"), 'B', 1, 3, startdate, enddate, geometry)

	# Plot rgb 
	rn,gn,bn = normalize(r[0]), normalize(g[0]), normalize(b[0])
	rgb = np.dstack((rn,gn,bn))
	
	# return the date
	start = ee.Date(startdate)
	end = ee.Date(enddate)
	collection = ee.ImageCollection("USDA/NAIP/DOQQ").filterDate(start,end)
	date = ee.Date(collection.first().get('system:time_start'))
	date_dict = date.format('Y-M-d').getInfo()

	return rgb, date_dict

def normalize(array):
	"""Normalizes numpy arrays into scale 0.0 - 1.0"""
	array_min, array_max = np.nanmin(array), np.nanmax(array)
	return ((array - array_min)/(array_max - array_min))

def get_convex_hull(tiff_fn):
	
	print('determining convex hull')
	
	rds = rioxarray.open_rasterio(tiff_fn)
	rds.name = "data"
	df = rds.squeeze().to_dataframe().reset_index()

	geometry = gp.points_from_xy(df[df['band'] == 1].x, df[df['band'] == 1].y)
	gdf = gp.GeoDataFrame(df[df['band'] == 1], crs=rds.rio.crs, geometry=geometry)

	gdf[gdf['data'] == 0] = np.nan
	gdf.dropna(inplace = True)

	convex_hull = gdf[gdf.is_valid].unary_union.convex_hull 
	convex_hull = gp.GeoDataFrame(geometry=[convex_hull], crs=gdf.crs)
	
	return convex_hull

def main():
	# Make reprojection dir if not exist 
	if not os.path.exists("../composites/wgs84/"):
		os.mkdir("../composites/wgs84/")

	# Read orthomosaic filenames 
	im_fns = [os.path.join("../composites/", x) for x in os.listdir("../composites/") if x.endswith(".tif")]

	# Setup outfns    
	rpj_fns = [os.path.join("../composites/wgs84/", x) for x in [os.path.split(x)[1] for x in im_fns] ] 

	# Reproject if not exists 
	for im_fn, rpj_fn in zip(im_fns,rpj_fns):
		src_fn = os.path.abspath(im_fn)
		dst_fn = os.path.abspath(rpj_fn)
		cmd = '''gdalwarp -t_srs "EPSG:4326" {} {} '''.format(src_fn, dst_fn)
		if not os.path.exists(dst_fn):
			os.system(cmd)
			print(cmd)



	# For each reprojected file, get convex hull, write pngs of sentinel and naip 
	for rpj_fn in tqdm(rpj_fns[::-1]):
		print("=====" * 10 )
		print(rpj_fn)
		# read fn
		src = rio.open(rpj_fn)
		# plot rgb im
		im = mpimg.imread(rpj_fn)
		# plt.imshow(im); plt.axis("off"); plt.show()

		# Setup out dirs for bboxes 
		if not os.path.exists("bounds"):
			os.mkdir("bounds")

		shpfn = os.path.join('bounds',os.path.split(rpj_fn)[1].replace(".tif",".shp"))
		
		# Hull takes a long time to compute, so check if exists 
		if not os.path.exists(shpfn):
			# Get convex hull 
			gdf = get_convex_hull(rpj_fn)
			gdf.to_file(shpfn)
		else:
			gdf = gp.read_file(shpfn)

		# Define EE aoi
		aoi = gdf_to_ee_poly(gdf)

		# Lookup date based on name of fn 
		site_name = os.path.split(shpfn)[-1].split(".")[0]

		site_date_lookup = {"KanabDam_vis" : "2022-03-22",
							"KanabRiver_vis" : "2022-03-25",
							"KanabRiver_tir" : "2022-03-25",
							"OceanoDunes_vis": "2022-12-29",
							"OceanoDunes_tir": "2022-12-29",
							"OsoFlacoLake_vis": "2022-12-21",
							"OsoFlacoRiver_vis": "2022-12-21"}

		# print(site_name)
		# print(type(site_name))
		print(site_date_lookup[site_name])

		# Get naip and plot
		try:
			naip,naip_date = get_naip(aoi)
			alpha = np.ma.masked_invalid(naip[:,:,0]).data.astype(float)
			alpha[~np.isnan(alpha)] = 1
			naipim = Image.fromarray((np.dstack([naip, alpha]) * 255).astype(np.uint8))

			naiprgb = naipim.convert('RGBA') # color image
			naiprgb.save(rpj_fn.replace("wgs84",'pngs').replace('.tif','_naip.png'))
			print("WROTE NAIP for {}".format(naip_date))
		except:
			time.sleep(0.0)
			
		# Get sentinel and plot 
		s1, s1_date = get_sentinel(aoi, im_ac_date = site_date_lookup[site_name])
		alpha = np.ma.masked_invalid(s1[:,:,0]).data.astype(float)
		alpha[~np.isnan(alpha)] = 1
		s1im = Image.fromarray((np.dstack([s1,alpha]) * 255).astype(np.uint8))
		s1imrgb = s1im.convert('RGBA') # color image
		s1imrgb.save(rpj_fn.replace("wgs84",'pngs').replace('.tif','_s1.png'))
		print("WROTE S1 for {}".format(s1_date))

if __name__ == "__main__":
	main()
		