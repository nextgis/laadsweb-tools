#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# modis1l-prepare4mrtswath.py
# Author: Maxim Dubinin (sim@gis-lab.info)
# About: Prepare prm files for MRT Swath
# Created: 26.06.2015
# Usage example: python modis1l-prepare4mrtswath.py c:\temp\input_hdf_folder\ c:\temp\output_tif_folder\ MYD02QKM MYD03
# ---------------------------------------------------------------------------
import glob
import os
import shutil
import sys


#------------SET THESE BEFORE RUNNING-----------------
swath2grid_path = '/home/sim/MRTSwath/bin/' #'c:/tools/MRTSwath/bin/'
swath2grid_name = 'swath2grid' #swath2grid.exe 
os.environ['MRTSWATH_DATA_DIR'] = '/home/sim/MRTSwath/data' #'c:/tools/MRTSwath/data/'
gdal_calc_name = 'gdal_calc.py' #'gdal_calc.bat'
gdal_merge_name = 'gdal_merge.py' #'gdal_merge'
#-----------------------------------------------------

def create_prm():
    prm = open('temp.prm','wb')
    prm.write('INPUT_FILENAME = ' + wd + f_in + '\n')                                              #D:\MOD02QKM.A2007204.0805.005.2007205121542.hdf
    prm.write('GEOLOCATION_FILENAME = ' + wd + f_in_03 + '\n')                                     #D:\MOD03.A2007204.0805.005.2007205033646.hdf
    prm.write('INPUT_SDS_NAME = ' + dataset_name + ', ' + dataset_bands + '\n')                    #EV_250_RefSB, 1, 1
    prm.write('OUTPUT_SPATIAL_SUBSET_TYPE = LAT_LONG' + '\n')
    prm.write('OUTPUT_SPACE_UPPER_LEFT_CORNER (LONG LAT) = ' + str(ul_x) + ' ' + str(ul_y) + '\n')  #51.8 40.2
    prm.write('OUTPUT_SPACE_LOWER_RIGHT_CORNER (LONG LAT) = ' + str(lr_x) + ' ' + str(lr_y) + '\n') #61.3 30.2
    prm.write('OUTPUT_FILENAME = ' + wd + f_out + '\n')                                            #D:\result
    prm.write('OUTPUT_FILE_FORMAT = GEOTIFF_FMT' + '\n')
    prm.write('KERNEL_TYPE (CC/BI/NN) = NN' + '\n')
    prm.write('OUTPUT_PROJECTION_NUMBER = ALBERS' + '\n')
    prm.write('OUTPUT_PROJECTION_PARAMETER = 0.0 0.0 52.0 64.0 45.0 0.0 8500000.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0' + '\n')
    prm.write('OUTPUT_PROJECTION_SPHERE = 8' + '\n')
    prm.write('OUTPUT_PIXEL_SIZE = ' + str(res) + '\n')
    prm.close()

if __name__ == '__main__':
    #parameters start
    dataset_name = 'EV_250_RefSB'
    numbands = 2
    dataset_bands = '1, 1'
    ul_x = 44.17
    ul_y = 47.3
    lr_x = 47.6
    lr_y = 44.4
    res = 250
    f_out = 'result'
    wd = sys.argv[1]
    od = sys.argv[2]
    product_type = sys.argv[3]
    product_geoloc_type = sys.argv[4]
    #parameters end
    
    os.chdir(wd)
    hdfs = glob.glob(product_type + '*.hdf')
    
    for f_in in hdfs:
        datetime = f_in.split('.')[1] + '.' + f_in.split('.')[2]
        f_in_03 = glob.glob(product_geoloc_type + '.' + datetime + '*.hdf')[0]
        
        create_prm()
        cmd = swath2grid_path + swath2grid_name + ' -pf=temp.prm'
        print(cmd)
        os.system(cmd)
        
        #merge in stack
        bands_list = ''
        for i in range(numbands): bands_list = bands_list + ' ' + f_out + '_' + dataset_name + '_b' + str(i) + '.tif'
        bands_list = bands_list.strip(',')
        
        for i in range(numbands):
            cmd = gdal_calc_name + ' -A ' + f_out + '_' + dataset_name + '_b' + str(i) + '.tif' + ' --outfile=' + f_out + '_' + dataset_name + '_b' + str(i) + '_calc.tif' + ' --calc="A*(A<16000)" --NoDataValue=0'
            os.system(cmd)
            shutil.move(f_out + '_' + dataset_name + '_b' + str(i) + '_calc.tif', f_out + '_' + dataset_name + '_b' + str(i) + '.tif')
        
        cmd = gdal_merge_name + ' -separate -ps ' + str(res) + ' ' + str(res) + ' -o ' + od + datetime + '.tif' + bands_list
        os.system(cmd)
        
        for i in range(numbands): os.remove(f_out + '_' + dataset_name + '_b' + str(i) + '.tif')
        