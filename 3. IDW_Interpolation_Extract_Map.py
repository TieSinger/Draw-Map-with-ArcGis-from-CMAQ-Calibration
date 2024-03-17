########################
# IDW_Interpolation.py #
########################

import os
import arcpy
from arcpy import env 
from arcpy import * 
from arcpy.sa import *

### IMPORTING SHAPE FILES AFTER CALIBRATE #################################
path_shape_files = r'D:/Dothivamoitruong/CMAQ/Ca_Mau/Point_Dataset/'

raw_name = os.listdir(path_shape_files)
outnames = []
for rname in raw_name:
    if (rname.endswith(".shp")):
        portion = os.path.splitext(rname)
        temp_name = portion[0]
        outnames.append(temp_name)
###########################################################################



### INTERPOLATION THE POINTS AND EXPORT TO TIF FILES ################################
path_shape_out_files = r"D:/Dothivamoitruong/CMAQ/Ca_Mau/Point_Dataset_3D/"
out_IDW = r"D:/Dothivamoitruong/CMAQ/Ca_Mau/IDW_Interpolation"
arcpy.env.outputZFlag = 'Enabled'
arcpy.CheckOutExtension("3D")
for outname in outnames:
    print(outname) # Watching the progress
    arcpy.ddd.FeatureTo3DByAttribute(path_shape_files + outname + ".shp", path_shape_out_files + outname + ".shp", 'GRID_CODE')
    outIDW = Idw(path_shape_out_files + outname + ".shp", "GRID_CODE", 7.25195312499999E-03, None, RadiusVariable(12, None))
    outname = os.path.join(out_IDW, os.path.splitext(outname)[0] + '.tif')
    outIDW.save(outname)
#####################################################################################