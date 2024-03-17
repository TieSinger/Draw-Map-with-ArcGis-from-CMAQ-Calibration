#############################
# Read_Extract_Calculate.py #
#############################

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

### READING EXCEL FILES USING PANDAS ############################################
    ### Reading multiplier ###
df = pd.read_excel(r"D:\Dothivamoitruong\CMAQ\Calibration_CaMau_Multiplier.xlsx")
print(df)
    ### Reading longitude and lattitude ###
df_lon = pd.read_excel(r"D:\Dothivamoitruong\CMAQ\COORLON.xlsx")
df_lat = pd.read_excel(r"D:\Dothivamoitruong\CMAQ\COORLAT.xlsx")
print(df_lon)
print(df_lat)
#################################################################################



### CREATING DATAFRAMES MULTIPLIER FOR EACH HOURS ###############################
column_names = ['ROW', 'COL']
hours = [str(i).zfill(2) for i in range(24)]
days_months = [f'{str(day).zfill(2)}{str(1).zfill(2)}' for day in range(1, 32)]
column_names.extend(f'{day}-{hour}h' for day in days_months for hour in hours)
df_multiplier = pd.DataFrame(columns=column_names)
# print(df_multiplier)
#################################################################################



### LISTING TIFF FILES ####################################
path_tiff_files = r'D:/Dothivamoitruong/CMAQ/Ca_Mau/Tiff/'
raw_name = os.listdir(path_tiff_files)
outnames = []
for rname in raw_name:
    portion = os.path.splitext(rname)
    temp_name = portion[0] + '.TIFF'
    outnames.append(temp_name)

# for outname in outnames:
#     print(outname)

arcpy.env.overwriteOutput = True
arcpy.env.workspace = path_tiff_files
rasters = arcpy.ListRasters("*", "All")
###########################################################



### READING RASTER USING ARCPY ###########
# for raster in rasters:
#     out_raster = arcpy.Raster(raster)
#     extent = out_raster.extent
#     print("Raster extent:", extent)
##########################################



### READING ONE FILE RASTER FOR VERIFICATION BEFORE USING IT ############
# print(rasters[0])
# raster_tiff = rasterio.open(os.path.join(path_tiff_files, rasters[0]))
# PM_25 = raster_tiff.read(1)
# for i in range(24):
#     print('-'*50)
#     print(i+1)
#     print(PM_25[i])
#########################################################################



### FIXING AND SORTING COLUMNS NAME ############
column_names_df = []
for col in df.columns:
    if (len(col[5:]) == 2):
        col = col[:5] + str(col[5:6]).zfill(2)
    column_names_df.append(col)
df.columns = column_names_df
df = df.reindex(sorted(df.columns), axis=1)
#################################################



### READING RASTER USING RASTERIO #####
date_str = np.array(df.columns)
num_day, max_day = 0, date_str.size
#######################################



### PRINT FORMAT OF HOUR, DAY, MONTH ##########################################
# for date in date_str:
#     print(date)
#     months_standard = int(date_str[num_day][2:4])  # Extract the months
#     days_standard = int(date_str[num_day][:2])  # Extract the days
#     check = 5
#     while (check < len(date_str[num_day]) and date_str[num_day][check] != 'h'):
#         check += 1
#     hours_standard = int(date_str[num_day][5:check])  # Extract the hours
#     print(months_standard)
#     print(days_standard)
#     print(hours_standard)
#     print('-'*100)
#     num_day += 1
################################################################################


for raster in rasters:
    raster_tiff = rasterio.open(os.path.join(path_tiff_files, rasters[0]))
    ### Check the number of bands in the raster file ###
    # print(raster)
    PM_25 = raster_tiff.read(1)
    ### Show Tiff File ###
    # print(PM_25[0].size)  ### Show Values
    # show(PM_25)           ### Show Image 
    row, col, value = [], [], []
    for i in range(61):
        for j in range(55):
            value.append(PM_25[i][j])
            row.append(i) # longitude
            col.append(j) # latitude
    ####################################################

    ### Doing with Raster Calculation Part 1 #############################################
            
        ### Formula Multiplier ###
        # If X == Y or Y < X (X is the smallest multiplier)
        # or Y > X (X is the largest multilier) -> M(X) == M(Y)
        # Else if X < Y < Z -> M(Y) = (M(X)*(Y-X) + M(Z)*(Z-Y))/(Z-X)
    # print(num_day)
    # print(date_str[num_day])
    months_standard = int(date_str[num_day][2:4])  # Extract the months
    days_standard = int(date_str[num_day][:2])  # Extract the days
    check = 5
    while (check < len(date_str[num_day]) and date_str[num_day][check] != 'h'):
        check += 1
    hours_standard = int(date_str[num_day][5:check])  # Extract the hours
    # print(months_standard)
    # print(days_standard)
    # print(hours_standard)
    parts = raster.split("_")
    hours = int(parts[2][0:2])
    days = int(parts[1][0:2])
    months = int(parts[1][2:4])
    date_raster = parts[1][0:2] + parts[1][2:4] + '-' + parts[2][0:2] + 'h'
    print(date_raster) # Watch the progress during running the code
    # print('-'*100)
    df_multiplier['ROW'], df_multiplier['COL'] = row, col
    df_multiplier[date_raster] = value
        ### Extract hours, days, and month ###
    if (hours_standard == 17 and days_standard == 29):
        df_multiplier[date_raster] = df_multiplier[date_raster] * df[date_str[num_day]][2]
    else:
        if (hours == hours_standard and days == days_standard):
            df_multiplier[date_raster] = df_multiplier[date_raster] * df[date_str[num_day]][2]
            num_day = num_day + 1
        elif (hours_standard == 7 and days_standard == 2):
            df_multiplier[date_raster] = df_multiplier[date_raster] * df[date_str[num_day]][2]
        elif (days == days_standard and hours < hours_standard):
            MX, MZ = df[date_str[num_day-1]][2], df[date_str[num_day]][2]
            Y, X, Z = hours+24, int(date_str[num_day-1][5:6]), int(date_str[num_day][5:6])+24
            MY = (MX*(Y-X) + MZ*(Z-Y))/(Z-X)
            df_multiplier[date_raster] = df_multiplier[date_raster] * MY
        elif (days < days_standard):
            MX, MZ = df[date_str[num_day-1]][2], df[date_str[num_day]][2]
            Y, X, Z = hours, int(date_str[num_day-1][5:6]), int(date_str[num_day][5:6])+24
            MY = (MX*(Y-X) + MZ*(Z-Y))/(Z-X)
            df_multiplier[date_raster] = df_multiplier[date_raster] * MY
    ##############################################################################################
    
    ### Raster Calculation Part 2 ###################################################################
        ### Applying the function y = ax^b ###
    a, b = 1.0651978272257991, 0.9369907308570845 # Define a, b of the function
    print(date_raster) # Watching the progress it makes during runnng the code
    df_multiplier[date_raster] = a * (df_multiplier[date_raster] ** b)
    #################################################################################################

    ### Changing Result of Tiff Files ###
    dem = 0
    for i in range(61):
        for j in range(55):
            PM_25[i][j] = df_multiplier[date_raster][dem]
            dem = dem + 1
    # show(PM_25)
    print(np.min(PM_25))
    print(np.max(PM_25))
    #####################################

    ### Exporting Tiff Files from df after Calibrate ###################################################

    ### Approach 1:
    #     # Reshape Values of the longitude, lattitude, values of PM25
    # lon_values = df_lon["value"].values
    # lat_values = df_lat["value"].values
    # for col_name in df_multiplier.columns[2:]:
    #     values = pd.DataFrame()
    #     values["PM25_TOT"] = df_multiplier[col_name].values
    #     values["lon"] = lon_values
    #     values["lat"] = lat_values
    #     new_values = values.to_xarray()
    #     lon = new_values.variables['lon'][:]
    #     lat = new_values.variables['lat'][:]
    #     lon_min, lon_max = lon.min(), lon.max()
    #     lat_min, lat_max = lat.min(), lat.max()
    #     pixel_width = (lon_max - lon_min) / 55
    #     pixel_height = (lat_max - lat_min) / 61
    #     grid_values = df_multiplier[col_name].values
    #     grid_values_reshaped = grid_values.reshape((61, 55))
    #     grid_values_df = pd.DataFrame(grid_values_reshaped)
    #     grid_values_xarray = grid_values_df.to_xarray()

    #     # Construct the output file name
    #     output_filename = f"D:\Dothivamoitruong\CMAQ\Ca_Mau\Tiff_after_Calibrate\{col_name}.tiff"
    #     # Define the transformation
    #     transform = from_origin(lon_values.min(), lat_values.max(), lon_values[1] - lon_values[0], lat_values[0] - lat_values[1])
    #     # Set up TIFF metadata
    #     tif_metadata = {
    #         'count': 1,
    #         'dtype': 'float32',
    #         'driver': 'GTiff',
    #         'height': grid_values_xarray.shape[0],
    #         'width': grid_values_xarray.shape[1],
    #         'crs': 'EPSG:4326',
    #         'transform': transform
    #     }
    #     # Write TIFF file
    #     with rasterio.open(output_filename, 'w', **tif_metadata) as dst:
    #         dst.write(grid_values_xarray, 1)

    ### Approach 2:
    metadata = raster_tiff.meta
    transform = metadata['transform']
    metadata.update({
        'dtype': PM_25.dtype,
        'count': 1,
        'height': PM_25.shape[0],
        'width': PM_25.shape[1],
        'transform': transform
    })
    output_tiff = f"D:\Dothivamoitruong\CMAQ\Ca_Mau\Tiff_after_Calibrate\{date_raster}.tiff"
    with rasterio.open(output_tiff, 'w', **metadata) as dst:
        dst.write(PM_25, 1)
    #######################################################################################################

    print('-'*50)
    ### Delay Time ###
    # time.sleep(0.1)
    ##################

### Check if the df after applying multiplier is correct?
print(df_multiplier)