
"""
Rasterize the intersection weights of a raster and shape
--------------------------------------------------------
"""
from os.path import join
import geopandas as gpd
import gsxarray
import rioxarray as rio
import matplotlib.pyplot as plt

example_folder = "..//data"
raster = join(example_folder, "sussex.tif")
shapefile = join(example_folder, "sussex.shp")

da = rio.open_rasterio(raster, masked=True)

print(da)

df = gpd.read_file(shapefile)

#%%
# Compute the intersection between shapes in a shapefile and the supply and use rasters.
# Not the sum of use and supply for the polygon will not be equal because the polygon is just a subset of the total computational domain here.

shape = df.geometry.iloc[0]  # Get the first shape from the shapefile

weights = da.gs.intersection_weights(shape)

weighted = da * weights
print(f"weighted sum: {weighted.sum().item()}")

print(weighted.percentile(95).item())

plt.figure()
ax = plt.subplot(131)
da.plot()
_ = plt.subplot(132, sharex=ax, sharey=ax)
weights.plot()
_ = plt.subplot(133, sharex=ax, sharey=ax)
(weighted).plot()

plt.show()