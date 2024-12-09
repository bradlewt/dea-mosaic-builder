import datacube
import geopandas as gpd

# Create folder ids by copying the ID from the g-drive folder url
F_MN_FID = "1KBig_UZLT0fgFXsACMHQTb7c_Poao-wh"
F_MD_FID = "1dWde-mzh8Sc9BIEMNUByq7Z6Yags0JZh"

PRF_MN_FID = "1MVAMwv0E3sZ6qK8E93MlnGcPTr6yXge4"
PRF_MD_FID = "1oROFY5hKi3w7pbkrCnHtGLIJT_nBraog"

POF_MN_FID = None
POF_MD_FID = None

FE_MN_FID = "1RpE2-Pe-KihKdCk0TKLvTzZgrv5QGOeu"
FE_MD_FID = "1KDTiwmmdaV5LBh6Dj1qAB5KTRNQu_-Xq"

MF_MX_FID = "100Xf41aDRLwZHiPxXzSMHbiCh4JWosaD"

# Define main time period of analysis
timerange = ("2023-11", "2024-11")

# Define sub-periods of analysis - should be within main time period
pre_flood = ["2024-02", "2024-03", "2024-04"]
flood = ["2024-05", "2024-06", "2024-07", "2024-08", "2024-09"]
post_flood = []
max_flood = ["2023-11", "2024-11"]

# Run 1. aoi-threshold.ipynb to get the value of th_aoi and store it here.
th_aoi = -21

dc = datacube.Datacube(app="Radar_water_detection")
