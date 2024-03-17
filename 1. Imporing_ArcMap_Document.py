################################
# Importing_ArcMap_Document.py #
################################

import os
from arcpy import *
from arcpy import env
from arcpy.sa import *
import numpy as np

mxdDir = r"D:/Dothivamoitruong/CMAQ"
arcpy.env.overwriteOutput = True
arcpy.env.workspace = mxdDir

mxds = arcpy.ListFiles("*.mxd")
prj = arcpy.mp.ArcGISProject("CURRENT")

for map in mxds:
    print("Importing {} ".format(map))
    prj.importDocument(os.path.join(mxdDir, map))
    pMap = prj.listMaps("Layers")[0]
    pMap.name = map.split(".mxd")[0]

### NOTE: Run this code in Arcmap / ArcgisPro ###