##########################
# Extract_Mask_Points.py #
##########################

import os
from arcpy import *
from arcpy import env
from arcpy.sa import *
import numpy as np
import pandas as pd
import rasterio
from rasterio.transform import from_origin
from rasterio.plot import show
import rioxarray as rio
from PIL import Image
import xarray as xr
import time


mask = "D:/Dothivamoitruong/CMAQ/Ca_Mau/Khung.shp"
output_dir = r'D:/Dothivamoitruong/CMAQ/Ca_Mau/Raster_Dataset/'
output_pnt = r'D:/Dothivamoitruong/CMAQ/Ca_Mau/Point_Dataset/'

### LISTING TIFF FILES AFTER CALIBRATE ###################################
path_tiff_files = r'D:/Dothivamoitruong/CMAQ/Ca_Mau/Tiff_after_Calibrate/'
raw_name = os.listdir(path_tiff_files)
outnames = []
for rname in raw_name:
    portion = os.path.splitext(rname)
    temp_name = portion[0] + '.TIFF'
    outnames.append(temp_name)

for outname in outnames:
    print(outname)

arcpy.env.overwriteOutput = True
arcpy.env.workspace = path_tiff_files
rasters_after_calibrate = arcpy.ListRasters("*", "All")
###########################################################################



### Extract by Mask Raster #####################################################
for raster in rasters_after_calibrate:
    outExtractByMask = ExtractByMask(raster, mask)
    outname = os.path.join(output_dir, os.path.splitext(raster)[0] + '.tif')
    outExtractByMask.save(outname)
    print(output_pnt + f"{raster[:7]}.shp")
    ### Changing Raster to Points #########################################################
    arcpy.RasterToPoint_conversion(outExtractByMask, output_pnt + f"{raster[:7]}.shp", "VALUE")
    #######################################################################################

################################################################################