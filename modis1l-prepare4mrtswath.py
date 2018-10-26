#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# modis1l-prepare4mrtswath.py
# Author: Maxim Dubinin (sim@gis-lab.info)
# About: Prepare prm files for MRT Swath
# Created: 26.06.2015, Last updated: 26.10.2018
# Usage example: 
#       python modis1l-prepare4mrtswath.py -i c:\temp\input_hdf_folder\ -o c:\temp\output_tif_folder\ -m MYD02QKM -n MYD03
# ---------------------------------------------------------------------------
import glob
import os
import shutil
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-r','--region', help='Set region')
parser.add_argument('-i','--indir', help='Input directory')
parser.add_argument('-o','--outdir', help='Output directory')
parser.add_argument('-m','--mod02type', help='MOD02 type')
parser.add_argument('-n','--mod03type', help='MOD03 types')
parser.add_argument('-d','--debug', help='Show debug stuff')
args = parser.parse_args()

#------------SET THESE BEFORE RUNNING-----------------
swath2grid_path = 'c:/tools/MRTSwath/bin/' #'/home/sim/MRTSwath/bin/'
swath2grid_name = 'swath2grid.exe' #'swath2grid'
os.environ['MRTSWATH_DATA_DIR'] = 'c:/tools/MRTSwath/data/' #'/home/sim/MRTSwath/data'
gdal_calc_name = 'gdal_calc.bat' #'gdal_calc.py'
gdal_merge_name = 'gdal_merge' #'gdal_merge.py'
#-----------------------------------------------------

def create_prm():
    prm = open('temp.prm','wb')
    prm.write('INPUT_FILENAME = ' + wd + f_in + '\n')                                              #D:\MOD02QKM.A2007204.0805.005.2007205121542.hdf
    prm.write('GEOLOCATION_FILENAME = ' + wd + f_in_03 + '\n')                                     #D:\MOD03.A2007204.0805.005.2007205033646.hdf
    prm.write('INPUT_SDS_NAME = ' + dataset_name + ', ' + dataset_bands + '\n')                    #EV_250_RefSB, 1, 1
    if args.region:
        prm.write('OUTPUT_SPATIAL_SUBSET_TYPE = LAT_LONG' + '\n')
        prm.write('OUTPUT_SPACE_UPPER_LEFT_CORNER (LONG LAT) = ' + str(ul_x) + ' ' + str(ul_y) + '\n')  #51.8 40.2
        prm.write('OUTPUT_SPACE_LOWER_RIGHT_CORNER (LONG LAT) = ' + str(lr_x) + ' ' + str(lr_y) + '\n') #61.3 30.2
    prm.write('OUTPUT_FILENAME = ' + wd + f_out + '\n')                                            #D:\result
    prm.write('OUTPUT_FILE_FORMAT = GEOTIFF_FMT' + '\n')
    prm.write('KERNEL_TYPE (CC/BI/NN) = NN' + '\n')
    #prm.write('OUTPUT_PROJECTION_NUMBER = ALBERS' + '\n')
    #prm.write('OUTPUT_PROJECTION_PARAMETER = 0.0 0.0 52.0 64.0 45.0 0.0 8500000.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0' + '\n')
    #prm.write('OUTPUT_PROJECTION_SPHERE = 8' + '\n')
    prm.write('OUTPUT_PROJECTION_NUMBER = MERCAT' + '\n')
    prm.write('OUTPUT_PROJECTION_SPHERE = 8' + '\n')
    prm.write('OUTPUT_PIXEL_SIZE = ' + str(res) + '\n')
    prm.close()

if __name__ == '__main__':
    #parameters start
    dataset_name = 'EV_250_RefSB'
    numbands = 2
    dataset_bands = '1, 1'
    if args.region:
        ul_x = 44.17
        ul_y = 47.3
        lr_x = 47.6
        lr_y = 44.4
    res = 250
    f_out = 'result'
    wd = args.indir
    od = args.outdir
    product_type = args.mod02type
    product_geoloc_type = args.mod03type
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
            if args.debug: print(cmd)
            os.system(cmd)
            shutil.move(f_out + '_' + dataset_name + '_b' + str(i) + '_calc.tif', f_out + '_' + dataset_name + '_b' + str(i) + '.tif')
        
        cmd = gdal_merge_name + ' -a_nodata 0 -separate -ps ' + str(res) + ' ' + str(res) + ' -o ' + od + datetime + '.tif' + bands_list
        if args.debug: print(cmd)
        print(cmd)
        os.system(cmd)
        
        #for i in range(numbands): os.remove(f_out + '_' + dataset_name + '_b' + str(i) + '.tif')
        