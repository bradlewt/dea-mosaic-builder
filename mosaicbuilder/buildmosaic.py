import os
import glob
from osgeo import gdal


class BuildMosaic:
    def __init__(self):
        gdal.UseExceptions()
        gdal.SetConfigOption("CHECK_DISK_FREE_SPACE", "NO")

    def create_mosaic(
        self, root: str, a3: str, indirs: list[str] = None, tifdir: str = None
    ) -> None:
        """
        Creates a .vrt mosaic of input rasters. Creates .tif if tifdir is specified.

        Parameters:
        indirs: None, optional
            List of folders containing .tif files to be merged.
        root: str, required
            Parent folder path of indirs.
        a3: str, required
            Alpha3 code of the country.
        tifdir: str = None, optional
        Output directory for .the tif files (not recommended).

        Returns:
        None
        """
        period = os.path.basename(root)
        merged_folder = os.path.join(root, "{}_merged".format(period))

        if not os.path.exists(merged_folder):
            print("'merged' folder does not exist. Creating...")
            os.makedirs(merged_folder)

        if indirs == None:
            dir = os.path.basename(root)
            loc = root
            ext = "*.tif"
            q = os.path.join(loc, ext)
            files = glob.glob(q)
            if len(files) == 0:
                print("{} is empty. Continuing to next directory".format(dir))
            else:
                print("Found {} Files. Merging in {} folder".format(len(files), dir))
                outname = "{}_{}_merged_{}".format(a3, period, dir)
                vrt_file = os.path.join(merged_folder, outname + ".vrt")

                if os.path.exists(vrt_file):
                    print("{}.vrt exists.".format(outname))
                else:
                    # create vrt if it does not exist
                    print("Creating {}.vrt".format(outname))
                    vrt = gdal.BuildVRT(vrt_file, files)
                    vrt = None

                if tifdir != None and os.path.exists(vrt_file):
                    # create tif if output dir is specified
                    vrt = gdal.Open(vrt_file)
                    tif_out = os.path.join(tifdir, outname + ".tif")
                    print("Creating {}.tif".format(outname))
                    gdal.Translate(tif_out, vrt, format="GTiff")
                    vrt = None
        else:
            for dir in indirs:
                loc = os.path.join(root, dir)
                ext = "*.tif"
                q = os.path.join(loc, ext)
                files = glob.glob(q)
                if len(files) == 0:
                    print("{} is empty. Continuing to next directory".format(dir))
                else:
                    print(
                        "Found {} Files. Merging in {} folder".format(len(files), dir)
                    )
                    outname = "{}_{}_merged_{}".format(a3, period, dir)
                    vrt_file = os.path.join(merged_folder, outname + ".vrt")

                    if os.path.exists(vrt_file):
                        print("{}.vrt exists.".format(outname))
                    else:
                        # create vrt if it does not exist
                        print("Creating {}.vrt".format(outname))
                        vrt = gdal.BuildVRT(vrt_file, files)
                        vrt = None

                    if tifdir != None and os.path.exists(vrt_file):
                        # create tif if output dir is specified
                        vrt = gdal.Open(vrt_file)
                        tif_out = os.path.join(tifdir, outname + ".tif")
                        print("Creating {}.tif".format(outname))
                        gdal.Translate(tif_out, vrt, format="GTiff")
                        vrt = None

    def vrt2tif(self, indir: str, outdir: str) -> None:
        """
        Converts .vrt to .tif. Recommemded to use QGIS instead as it used gdal-C and this works on gdal-python.

        Parameters:
        indir: str, required
        Input directory of the .vrt files
        outdir: str, required
        Output directory of the tif files

        Returns:
        None
        """
        ext = "*.vrt"
        q = os.path.join(indir, ext)
        files = glob.glob(q)
        if len(files) == 0:
            print(
                "No .vrt files found. Check folder name or first generate .vrt files by running cm.create_mosiac()"
            )
        else:
            print("Generating...")
            for f in files:
                outname = os.path.splitext(os.path.basename(f))[0]
                print("Converting {}.vrt to {}.tif".format(outname, outname))
                outpath = os.path.join(outdir, outname + ".tif")
                vrt = gdal.Open(f)
                gdal.Translate(outpath, vrt, format="GTiff")
