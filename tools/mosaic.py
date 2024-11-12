import os, glob
from osgeo import gdal
from typing import Literal

class CreateMosaic():
    def __init__(self):
        gdal.UseExceptions()

    def create_mosaic(self, dirs:list[str], root:str, output:Literal[1, 2] = 1) -> None:
        """
        dirs: list of folders containing .tif files to be merged
        root: parent folder path of dirs
        output: default 1 - Only generates a .vrt file (faster). 2 - Generates a .tif file along with a .vrt file (slower and larger disk space)
        """
        period = os.path.basename(root)
        merged_folder = os.path.join(root, '{}_merged'.format(period))
        if not os.path.exists(merged_folder):
            print("'merged' folder does not exist. Creating...")
            os.makedirs(merged_folder)

        for dir in dirs:
            loc = os.path.join(root, dir)
            extension = "*.tif"
            q = os.path.join(loc, extension)
            files = glob.glob(q)
            if len(files) == 0:
                print("{} is empty. Continuing to next directory".format(dir))
            else:
                print("Found {} Files. Merging in {} folder".format(len(files), dir))

                if output == 1:
                    vrt_file = os.path.join(merged_folder, 'Merged_{}_{}.vrt'.format(period, dir))
                    vrt = gdal.BuildVRT(vrt_file, files)
                    if output == 2:
                        gdal.Translate(merged_folder, vrt, format="GTiff")
                    vrt = None