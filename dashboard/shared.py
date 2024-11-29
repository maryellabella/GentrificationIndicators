from pathlib import Path
import geopandas as gpd
import pandas as pd
import os

app_dir = Path(__file__).parent
merged_gdf_shapefile_path = os.path.join(app_dir, 'data', 'merged_gdf_shapefile', 'merged_gdf_shapefile.shp')

merged_gdf_shapefile = gpd.read_file(merged_gdf_shapefile_path)

merged_gdf = merged_gdf_shapefile.rename(columns={
    'certifie_1': 'certified_tot_mean',  
    'certified_': 'certified_tot',  
    'township_1': 'township_code',  
    'neighborho': 'neighborhood_code_clean', 
})


