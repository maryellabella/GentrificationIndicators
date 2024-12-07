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

app_dir = os.path.dirname(os.path.abspath(__file__))  
fc_gdf_shapefile_path = os.path.join(app_dir, 'data', 'fc_gdf_shapefile', 'fc_gdf_shapefile.shp')
fc_gdf_shapefile = gpd.read_file(fc_gdf_shapefile_path)

fc_gdf = fc_gdf_shapefile.rename(columns={
    'num_fore_1': 'num_foreclosure_in_half_mile_past_5_years_mean',  
    'num_forecl': 'num_foreclosure_in_half_mile_past_5_years',  
    'pri_neigh': 'fc_pri_neigh',
    'geometry': 'fc_geometry',
    'year' : 'fc_year'
})

app_dir = os.path.dirname(os.path.abspath(__file__))  
ps_gdf_shapefile_path = os.path.join(app_dir, 'data', 'ps_gdf_shapefile', 'ps_gdf_shapefile.shp')
ps_gdf_shapefile = gpd.read_file(ps_gdf_shapefile_path)

ps_gdf = ps_gdf_shapefile.rename(columns={
    'nbhd': 'neighborhood_code',  
    'town_nbhd': 'township_neighborhood_code',
    'township_c': 'township_code',  
    'township_n': 'township_name',
    'triad_code': 'triad_code',
    'triad_name': 'triad_name',
    'pri_neigh': 'ps_pri_neigh',  
    'sec_neigh': 'ps_sec_neigh',
    'neighborho': 'neighborhood_code_clean',  
    'sale_price': 'sale_price_mean',  
    'sale_pri_1': 'sale_price_median',
    'geometry': 'ps_geometry',
    'year': 'ps_year'
})