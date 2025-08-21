import geopandas as gpd

# Read the GeoPackage
gdf = gpd.read_file("Uganda map data/ug_districts.gpkg")

# Save as GeoJSON
gdf.to_file("uganda_districts.json", driver="GeoJSON")

import geopandas as gpd

# Read the GeoPackage
gdf = gpd.read_file("Uganda map data/ug_regions.gpkg")

# Save as GeoJSON
gdf.to_file("uganda_regions.json", driver="GeoJSON")
