import os, glob
from osgeo import gdal
from typing import Literal

class CreateMosaic():
    def __init__(self):
        gdal.UseExceptions()

    def create_mosaic(self, indirs:list[str], root:str, a3:str, tifdir:str = None) -> None:
        """
        indirs: list of folders containing .tif files to be merged
        root: parent folder path of indirs
        a3: alpha3 code of the country
        tifdir: output directory for .the tif files
        """
        period = os.path.basename(root)
        merged_folder = os.path.join(root, '{}_merged'.format(period))

        if not os.path.exists(merged_folder):
            print("'merged' folder does not exist. Creating...")
            os.makedirs(merged_folder)

        for dir in indirs:
            loc = os.path.join(root, dir)
            ext = "*.tif"
            q = os.path.join(loc, ext)
            files = glob.glob(q)
            if len(files) == 0:
                print("{} is empty. Continuing to next directory".format(dir))
            else:
                print("Found {} Files. Merging in {} folder".format(len(files), dir))
                outname = '{}_{}_merged_{}'.format(a3, period, dir)
                vrt_file = os.path.join(merged_folder, outname + ".vrt")

                if os.path.exists(vrt_file):
                    print("{}.vrt exists.".format(outname))
                else:
                    # create vrt if it does not exist
                    print("Creating {}.vrt".format(outname))
                    vrt = gdal.BuildVRT(vrt_file, files)

                if tifdir != None:
                    # create tif if output dir is specified
                    vrt = gdal.Open(vrt_file)
                    tif_out = os.path.join(tifdir, outname + ".tif")
                    print("Creating {}.tif".format(outname))
                    gdal.Translate(tif_out, vrt, format="GTiff")

    # def vrt2tif(self, indir:str, outdir:str) -> None:
    #     ext = '*.vrt'
    #     q = os.path.join(indir, ext)
    #     files = glob.glob(q)
    #     if len(files) == 0:
    #         print("No .vrt files found. Check folder name or first generate .vrt files by running cm.create_mosiac()")
    #     else:
    #         print("Generating...")
    #         for f in files:
    #             outname = os.path.splitext(os.path.basename(f))[0]
    #             print("Converting {}.vrt to {}.tif".format(outname, outname))
    #             outpath = os.path.join(outdir, outname + ".tif")
    #             vrt = gdal.Open(f)
    #             gdal.Translate(outpath, vrt, format="GTiff")
