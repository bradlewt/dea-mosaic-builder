import os, glob, warnings, rasterio, folium, json
import numpy as np
import xarray as xr
import geopandas as gpd
import matplotlib.pyplot as plt
import rioxarray as rio
import pandas as pd
from rasterio.merge import merge
from rasterio.plot import show
from shapely.geometry import Point
from shapely.geometry import Polygon
from datacube.utils.geometry import Geometry
from typing import Literal

from tools.gdrive import GDrive
from tools.deamethods import lee_filter, S1_water_classifier
import tools.vars as vars

from deafrica_tools.spatial import xr_rasterize
from deafrica_tools.datahandling import load_ard
from deafrica_tools.plotting import display_map, rgb
from deafrica_tools.areaofinterest import define_area

from IPython.display import clear_output
from IPython.display import display

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------- #
#                     Main utility class for mosaic builder                    #
# ---------------------------------------------------------------------------- #


class GenMosaic:
    def __init__(self):
        self.gd = GDrive()
        pass

    def gen_output(
        self,
        DS: xr.DataArray,
        i: list,
        poly: Geometry,
        cell: int,
        aoi_m: list,
        period: Literal["preflood", "flood", "postflood", "flood_extents", "maxflood"],
        measure: Literal["mean", "median", "max"],
    ) -> list:
        """
        Generates file names and uploads tp Google Drive

        Parameters:
        DS: xr.DataArray, required
            Dataset to be converted into raster output.
        i: list, required
            Index of centroid list.
        poly: Geometry, required
            Polygon feature used to create the DS.
        cell: int, required
            Cell number being processed.
        aoi_m: list, required
            List of geojson feature collection (cells) that make up the entire grid.
        period: Literal["preflood", "flood", "postflood", "flood_extents"], required
            Time period of the process - PRE_FLOOD, FLOOD.
        measure: Literal["mean", "median"], required
            Central tendency measurement of the DS - mean, median.

        Returns:
        err: list
            Error log list of [x, y, cell_id and None]. None will store the error "P" - Processing or "U" - Upload.
        """

        err = []

        pm_dict = {
            "preflood_mean": [vars.pre_flood, vars.PRF_MN_FID],
            "preflood_median": [vars.pre_flood, vars.PRF_MD_FID],
            "flood_mean": [vars.flood, vars.F_MN_FID],
            "flood_median": [vars.flood, vars.F_MD_FID],
            "postflood_mean": [vars.post_flood, vars.POF_MN_FID],
            "postflood_median": [vars.post_flood, vars.POF_MD_FID],
            "flood_extents_mean": [vars.timerange, vars.FE_MN_FID],
            "flood_extents_median": [vars.timerange, vars.FE_MD_FID],
            "maxflood_max": [vars.timerange, vars.MF_MX_FID],
        }

        poly_gdf = gpd.GeoDataFrame(geometry=[poly], crs=poly.crs)
        lat_range = (poly_gdf.total_bounds[1], poly_gdf.total_bounds[3])
        lon_range = (poly_gdf.total_bounds[0], poly_gdf.total_bounds[2])
        g = poly_gdf.centroid

        data_val = (
            "CELL_" + str(i[2]) + "_{}_{}".format(period.upper(), measure.upper())
        )
        data_name = data_val + ".tif"
        data_out = "output/{}/".format(period) + data_name
        DS.rio.to_raster(data_out)

        # preflood meta
        data_dict = {
            "GRID_CELL_ID": i[2],
            "start_time": pm_dict["{}_{}".format(period, measure)][0][
                0
            ],  # pre_flood[0]
            "end_time": pm_dict["{}_{}".format(period, measure)][0][
                -1
            ],  # pre_flood[-1]
            "lat": lat_range,
            "lon": lon_range,
            "centroid": "{}, {}".format(g.y[0], g.x[0]),
            "crs": str(poly.crs),
        }

        text_flie_name = data_val + "_META.json"
        data_meta_path = "output/{}/".format(period) + text_flie_name
        with open(data_meta_path, "w") as f:
            json.dump(data_dict, f)

        try:
            self.gd.upload_files(
                [data_out, data_meta_path], pm_dict["{}_{}".format(period, measure)][1]
            )  # pm_dict['preflood_mean'][1] = FOLDER_ID
        except Exception as e:
            err.append([g.x[0], g.y[0], i[2], "U-PRF"])
            print(
                "\n\n"
                + "\033[31m"
                + "ERROR UPLOADING GRID CELL ID {} NO.  {}/{} CENTROID ({}, {}). LOGGED CENTROID INFO in e_log".format(
                    i[2], cell, len(aoi_m), round(g.y[0], 5), round(g.x[0], 5)
                )
                + "\033[0m"
            )
            print("UPLOAD ERROR: {}".format(e))

        return err

    def gen_elog(self, e_log: list) -> list:
        """
        Writes a the error log json file and uploads it to the google drive folder ID, if specified.

        Parameters:
        e_log: list, required
            Error log list of [x, y, cell_id and None]. None will store the error "P" - Processing or "U" - Upload.

        Returns:
        e_log: list
            Error log list having the same values as the input parameter
        """
        e_log = np.array(e_log)
        with open("error_centroids.json", "w") as filehandle:
            json.dump(e_log.tolist(), filehandle)

        # read error log from disk
        with open("error_centroids.json") as f:
            e_log = json.load(f)
        for e in e_log:
            e[0] = float(e[0])
            e[1] = float(e[1])
            e[2] = int(e[2])

        try:
            self.gd.upload_files(["error_centroids.json"], vars.ERR_FOLDER_ID, False)
        except Exception as e:
            print("FAILED TO UPLOAD ERROR LOG FILE REASON:{}".format(e))

        return e_log

    # ---------------------- Iterate through the input grid ---------------------- #

    def iterate_grid(self, aoi_m: list, c: list) -> list:
        """
        Iterates through every feature (cell) in the AOI grid.

        Parameters:
        aoi_m: list, required
            List of geojson feature collection (cells) that make up the entire grid.
        c: list, required
            List of [x, y, cell_id and None]. None will store the error "P" - Processing or "U" - Upload, if executio fails

        Returns:
        e_log: list
            Error log list of [x, y, cell_id and None]. None will store the error "P" - Processing or "U" - Upload.
        """

        e_log = []
        cell = 1
        for aoi, i in zip(aoi_m, c):
            geopolygon = Geometry(aoi["features"][0]["geometry"], crs="epsg:4326")
            geopolygon_gdf = gpd.GeoDataFrame(geometry=[geopolygon], crs=geopolygon.crs)
            g = geopolygon_gdf.centroid
            print(
                "\n\n"
                + "\033[32m"
                + "PROCESSING GRID CELL ID {} NO. {}/{} CENTROID ({}, {})".format(
                    i[2], cell, len(aoi_m), round(g.y[0], 5), round(g.x[0], 5)
                )
                + "\033[0m"
            )

            # Get the latitude and longitude range of the geopolygon
            lat_range = (geopolygon_gdf.total_bounds[1], geopolygon_gdf.total_bounds[3])
            lon_range = (geopolygon_gdf.total_bounds[0], geopolygon_gdf.total_bounds[2])

            # Load Sentinel1 data
            try:
                S1 = load_ard(
                    dc=vars.dc,
                    products=["s1_rtc"],
                    measurements=["vh"],
                    y=lat_range,
                    x=lon_range,
                    time=vars.timerange,
                    output_crs="EPSG:6933",
                    resolution=(-20, 20),
                    group_by="solar_day",
                    dtype="native",
                )
            except Exception as e:
                # Log error aoi centroids and keep looping
                e_log.append([g.x[0], g.y[0], i[2], "P"])
                print(
                    "\n\n"
                    + "\033[31m"
                    + "ERROR PROCESSING GRID CELL {}/{} CENTROID ({}, {}). LOGGED CENTROID INFO in e_log".format(
                        i[2], len(aoi_m), round(g.y[0], 5), round(g.x[0], 5)
                    )
                    + "\033[0m"
                )
                print("PROCESS ERROR: {}".format(e))
                cell += 1
                continue

            # timesteps = [2, 4, 6, 9, 11]

            # The lee filter above doesn't handle null values
            # We therefore set null values to 0 before applying the filter
            valid = np.isfinite(S1)
            S1 = S1.where(valid, 0)

            # Create a new entry in dataset corresponding to filtered VV and VH data
            # S1["filtered_vh"] = S1.vh.groupby("time").apply(lee_filter, size=7)

            # Null pixels should remain null
            S1["filtered_vh"] = S1.vh.where(valid.vh)

            # Convert the digital numbers to dB
            S1["filtered_vh"] = 10 * np.log10(S1.filtered_vh)

            threshold_vh = vars.th_aoi

            S1["water"] = S1_water_classifier(S1.filtered_vh, threshold_vh).s1_water
            S1Water = S1.water
            S1_BIN = S1Water.where(S1Water > 0)
            FS1 = S1_BIN
            PRFS1 = S1_BIN

            # Creating outputs
            # Export to raster - upload to g-drive - delete from sandbox

            print("Uploading...")
            # -------------- maxflood ----------------
            if i[3] in [None, "P", "U-PRF"]:
                S1_MX = S1_BIN.sel(time=vars.max_flood, method="nearest").max(
                    dim="time"
                )
                err = self.gen_output(
                    S1_MX, i, geopolygon, cell, aoi_m, "maxflood", "max"
                )

            # # -------------- preflood ----------------
            # if i[3] in [None, "P", "U-PRF"]:
            #     S1_PRF_MD = PRFS1.sel(time=pre_flood, method="nearest").median(dim="time")
            #     S1_PRF_MN = PRFS1.sel(time=pre_flood, method="nearest").mean(dim="time")
            #     err = gen_output(
            #         S1_PRF_MD, i, geopolygon, cell, aoi_m, "preflood", "median"
            #     )
            #     if len(err) > 0:
            #         e_log.extend(err)
            #     err = gen_output(S1_PRF_MN, i, geopolygon, cell, aoi_m, "preflood", "mean")
            #     if len(err) > 0:
            #         e_log.extend(err)

            # # --------------- flood ------------------
            # if i[3] in [None, "P", "U-F"]:
            #     S1_F_MD = FS1.sel(time=flood, method="nearest").median(dim="time")
            #     S1_F_MN = FS1.sel(time=flood, method="nearest").mean(dim="time")
            #     err = gen_output(S1_F_MD, i, geopolygon, cell, aoi_m, "flood", "median")
            #     if len(err) > 0:
            #         e_log.extend(err)
            #     err = gen_output(S1_F_MN, i, geopolygon, cell, aoi_m, "flood", "mean")
            #     if len(err) > 0:
            #         e_log.extend(err)

            # # ------------ flood-extents --------------
            # if i[3] in [None, "P", "U-FE"]:
            #     S1_FE_MD = S1_F_MD - S1_PRF_MD
            #     S1_FE_MN = S1_F_MN - S1_PRF_MN
            #     err = gen_output(
            #         S1_FE_MD, i, geopolygon, cell, aoi_m, "flood_extents", "median"
            #     )
            #     if len(err) > 0:
            #         e_log.extend(err)
            #     err = gen_output(
            #         S1_FE_MN, i, geopolygon, cell, aoi_m, "flood_extents", "mean"
            #     )
            #     if len(err) > 0:
            #         e_log.extend(err)

            cell += 1
            # clear_output()

        if len(e_log) == 0:
            print(
                "\n\n"
                + "\033[32m"
                + "GRID PROCESSED AND UPLOADED SUCCESSFULLY"
                + "\033[0m"
                + "\n\n"
            )

        # e_log = gen_elog(e_log)

        # return e_log to be run again
        return e_log

    # ----------------------- Create the aoi-mosaic - aoi_m ---------------------- #

    def gen_aoim(self, c: list, c_buffer: float) -> list:
        """
        Generates the feature collection list (list of cells) using centroid coordinates and a buffer distance. Calls the main iterator for execution as well.

        Parameters:
        c: list, required
            List of [x, y, cell_id and None]. None will store the error "P" - Processing or "U" - Upload, if executio fails.
        c_buffer: float, required
            Cell half-dimension in degrees (EPSG:4326). Creates a cell by adding this distance to the centroid coordinates.

        Returns:
        e_log: list
            Error log list of [x, y, cell_id and None]. None will store the error "P" - Processing or "U" - Upload.
        """
        aoi_m = []
        for i in c:
            aoi_m.append(define_area(i[1], i[0], buffer=c_buffer))
        # print(c, len(aoi_m))
        e_log = self.iterate_grid(aoi_m, c)

        # return e_log to be run again
        return e_log

    # --------------------------- Visualize input file --------------------------- #

    def view_input(self, gdf_list: list[gpd.GeoDataFrame], grid_c: list) -> None:
        """
        Visualizes cells and respective IDs  on a basemap.

        Parameters:
        gdf_list:list[gpd.GeoDataFrame], required
            List of geodataframes to be visualized.
        grid_c:list, required
            List of [x, y, cell_id and None]. None will store the error "P" - Processing or "U" - Upload, if executio fails.

        Returns:
        None

        """
        print("Visualizing data...")
        p = gdf_list[0].dissolve()
        center = p.centroid
        map = folium.Map(location=[center.y, center.x], tiles="CartoDB Positron")

        for gdf in gdf_list:
            folium.GeoJson(gdf, name="{}".format(gdf)).add_to(map)

        for c in grid_c:
            folium.Marker(
                location=[c[1], c[0]],
                popup=f"Centroid: {c[1]}, {c[0]}",
                icon=folium.DivIcon(
                    icon_size=(10, 10),
                    icon_anchor=(0, 0),
                    html='<div style="font-size: 10pt">{}</div>'.format(c[2]),
                ),
            ).add_to(map)

        bounds = gdf_list[0].total_bounds.tolist()
        map.fit_bounds([bounds[:2][::-1], bounds[2:][::-1]])
        display(map)

    # -------------------------------- Create grid ------------------------------- #

    def create_grid(self, adm0: gpd.GeoDataFrame, size: float) -> gpd.GeoDataFrame:
        """
        Divides adm0 AOI vectorfile into square grid based on cell size

        Parameters:
        adm0:gpd.GeoDataFrame, required
            AMD0 GeoDataFrame created from ADM0 input vector file
        size:float, required
            Grid cell size in degrees (EPSG:4326)

        Returns:
        grid: gpd.GeoDataFrame
            The generated grid GeoDataFrame
        """
        bounds = adm0.bounds
        minx = bounds.minx[0]  # only 1 feature at the 0th index
        miny = bounds.miny[0]
        maxx = bounds.maxx[0]
        maxy = bounds.maxy[0]

        grid = gpd.GeoDataFrame()
        for x0 in np.arange(minx, maxx, size):
            for y0 in np.arange(miny, maxy, size):
                x1 = x0 + size
                y1 = y0 + size
                d = {"geometry": [Polygon([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])]}
                cell = gpd.GeoDataFrame(d, crs="EPSG:4326")
                flag = adm0.intersection(cell)
                if flag[0].is_empty == False:
                    grid = pd.concat([grid, cell])

        return grid

    # -------------------- Checks CRS and converts if required ------------------- #

    def crs_check(self, shp: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """
        Checks input GeoDataFrame CRS and converts to EPSG 4326, if different.

        Parameters:
        shp: gpd.GeoDataFrame, required
            Input GeoDataFrame to check.

        Returns:
        shp: gpd.GeoDataFrame
            As is or converted GeoDataFrame.
        """
        if shp.crs != "EPSG:4326":
            print("Added ADM0 CRS is {}. Converting to EPSG:4326...".format(shp.crs))
            shp = shp.to_crs("EPSG:4326")
            if shp.crs == "EPSG:4326":
                print("Done")

        return shp

    # --------------------- Checks 'y' or 'n' as valid input --------------------- #

    def check_inp(self, x: str) -> None:
        """
        Checks if input is "y" or "n"

        Parameters:
        x: str, required
            String input to be checked

        Returns:
        None
        """
        if x not in ["y", "n"]:
            raise ValueError("Invalid input, must be 'y' or 'n'")
        elif x == "n":
            raise RuntimeError(
                "Excecution terminated. Make necessary changes before running again"
            )

    # -------------- Conducts necessary checks before main execution ------------- #

    def exec_checks(self, c, buffer) -> list:
        """
        Performs checks and Run the entire application

        Parameters:
        c: list, required
            List of [x, y, cell_id and None]. None will store the error "P" - Processing or "U" - Upload, if executio fails.
        b: float, required
            Cell half-dimension in degrees (EPSG:4326). Creates a cell by adding this distance to the centroid coordinates.

        Returns:
        Returns:
        e_log: list
            Error log list of [x, y, cell_id and None]. None will store the error "P" - Processing or "U" - Upload.
        """

        inst = """
    Before running the execution, ensure all requirements have been met:
    1. Create appropriate folders in Google Drive and add their Folder IDs here
    2. Check input shapefile
    3. Check grid size
        
        """
        self.print(inst)

        x = input("Folder IDs verified? (y/n):")
        self.check_inp(x)

        x = input("Input shapefile/geojson verified? (y/n):")
        self.check_inp(x)

        input("Grid (size) verified? (y/n):")
        self.check_inp(x)

        z = input("\nBegin execution for entire input shapefile/geojson? (y/n):")
        if z not in ["y", "n"]:
            raise ValueError("Invalid input, must be 'y' or 'n'")
        elif z == "n":
            raise RuntimeError(
                "Excecution terminated. Make necessary changes before running again"
            )
        elif z == "y":
            print("Starting execution...")
            # get e_log with centroids, cell_id and error message
            # Calling gen_aoim will run the entire iteration process
            e_log = self.gen_aoim(c, buffer)
            print(len(e_log))
            return e_log

    def add_adm(
        self,
        shp: str,
        boundary_buffer: float,
        cell_size: float,
    ) -> list | gpd.GeoDataFrame | pd.DataFrame:
        """
        Processes the input ADM file. File does not have to be ADM0 and can be any vectorfile.

        Parameters:
        shp: str, required
            Path of input vectorfile. Will be converted to EPSG:4326.
        boundary_buffer: float, required
            Outer boundary buffer to be given to the input vector file in degrees (EPSG:4326)
        cell_size: float, required
            Grid cell size in degrees (EPSG:4326)

        Returns:
        c: list
            List of [x, y, cell_id and None]. None will store the error "P" - Processing or "U" - Upload, if executio fails.
        grid: GeoDataFrame
            Grid file generated from input file
        adm_df: Dataframe
            Input file information
        """
        adm0_b = gpd.read_file(shp)  # adm0 base
        adm0_b = adm0_b.dissolve()
        adm0_buf = adm0_b.buffer(boundary_buffer)  # adm0 with 20KM boundary buffer
        adm0 = self.crs_check(adm0_buf)
        size = cell_size  # Grid cell size 0.5 ~ 55KM
        buffer = size / 2  # cell buffer around the centroid to create the cell

        grid = self.create_grid(adm0, size)
        # Calculate centroids and store in centroid list c[].
        c = []
        g = grid.centroid

        cell_id = 1
        for i in g:
            c.append(
                [round(i.x, 5), round(i.y, 5), cell_id, None]
            )  # The array c[] has four values: x, y, cell_id and None. None will store the "P" or "U" error value
            cell_id += 1

        adm_data = {
            "Parameter": [
                "File Path",
                "Area",
                "Area with Buffer",
                "Cell Size",
                "Number of Cells",
            ],
            "Value": [
                shp,
                "{} KM2".format(
                    round((adm0_b.to_crs("EPSG:3857").area).iloc[0] / (10**6), 2)
                ),
                "{} KM2".format(
                    round((adm0.to_crs("EPSG:3857").area).iloc[0] / (10**6), 2)
                ),
                cell_size,
                len(c),
            ],
        }
        adm_df = pd.DataFrame(adm_data)
        adm_df.style.set_caption("Input Data")

        self.view_input([grid, adm0], c)
        print("\n")

        return (c, grid, adm_df)
