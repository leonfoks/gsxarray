
"""
Compute out of memory stats without rasterizing the shape
---------------------------------------------------------
"""
from os.path import join
import geopandas as gpd
import gsxarray
import rioxarray as rio


example_folder = "..//data"
raster = join(example_folder, "sussex.tif")
shapefile = join(example_folder, "sussex.shp")

ds = rio.open_rasterio(raster, masked=True)

# print(ds)

df = gpd.read_file(shapefile)

#%%
# Compute the intersection between shapes in a shapefile and the supply and use rasters.
# Not the sum of use and supply for the polygon will not be equal because the polygon is just a subset of the total computational domain here.

shape = df.geometry.iloc[0]  # Get the first shape from the shapefile

sum = ds.gs.conservative_stats(shape, 'sum')

print(f"weighted {sum=}")

sum = ds.gs.conservative_stats(shape, chunk=(1000, 1000), stats=['sum'])

print(f"weighted {sum=}")
