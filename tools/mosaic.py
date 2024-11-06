import os, glob, rasterio
from osgeo import gdal
from typing import Literal
from rasterio.merge import merge


class CreateMosaic():
    def __init__(self):
        gdal.UseExceptions()
        

    def merge_single(self, dir:str, root:str, mprocess:Literal[1, 2]) -> None:
        """
        dir: single folder containing .tif files to be merged
        root: parent folder path of dir
        """
        merged_folder = os.path.join(root, 'merged')
        if not os.path.exists(merged_folder):
            print("merged FOLDER DOES NOT EXIST. CREATING.")
            os.makedirs(merged_folder)

        loc = os.path.join(root, dir)
        out_file = "Merged_{}.tif".format(dir)
        out = os.path.join(merged_folder, out_file)
        extension = "*.tif"
        q = os.path.join(loc, extension)
        files = glob.glob(q)
        print("Found {} Files. Merging in {} Folder".format(len(files), dir))

        if mprocess == 1:
            self.use_rasterio(files=files, out=out)
        else:
            self.use_gdal(files=files, out=out, dir=dir)

    def merge_multiple(self, dirs:list[str], root:str, mprocess:Literal[1, 2]) -> None:
        """
        dirs: list of folders containing .tif files to be merged
        root: parent folder path of dirs
        """
        merged_folder = os.path.join(root, 'merged')
        if not os.path.exists(merged_folder):
            print("merged FOLDER DOES NOT EXIST. CREATING.")
            os.makedirs(merged_folder)

        for dir in dirs:
            loc = os.path.join(root, dir)
            out_file = "Merged_{}.tif".format(dir)
            out = os.path.join(merged_folder, out_file)
            extension = "*.tif"
            q = os.path.join(loc, extension)
            files = glob.glob(q)
            print("Found {} Files. Merging in {} Folder".format(len(files), dir))

            if mprocess == 1:
                self.use_rasterio(files=files, out=out)
            else:
                self.use_gdal(files=files, out=out, dir=dir)

    def use_rasterio(self, files:list[str], out:str):
        r =[]
        for f in files:
            s = rasterio.open(f)
            r.append(s)
        if len(r)>0:
            mosaic, out_trans = merge(r)
            out_meta = s.meta.copy()
            out_meta.update({"driver": "GTiff",
                        "height": mosaic.shape[1],
                        "width": mosaic.shape[2],
                        "transform": out_trans
                        })
            with rasterio.open(out, "w", **out_meta) as dest:
                dest.write(mosaic)

    def use_gdal(self, files:list[str], out:str, dir):
        loc = os.path.dirname(out)
        vrt_file = os.path.join(loc, 'Merged_{}.vrt'.format(dir))
        vrt = gdal.BuildVRT(vrt_file, files)
        # gdal.Translate(out, vrt, format="GTiff")
        vrt = None