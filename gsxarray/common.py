# Hate having a common script.

from numpy import squeeze
import rasterio
from shapely.geometry import Polygon
from pandas import Series
from geopandas import GeoSeries, GeoDataFrame

def get_geometry(shape):
    """Returns the geometry from a geopandas GeoSeries or GeoDataFrame, or self if its already a geometry.


    Parameters
    ----------
    shape : shapely.Geometry or geopandas.GeoSeries or geopandas.GeoDataFrame
        Geometry of a polygon.


    """
    if isinstance(shape, (GeoSeries, GeoDataFrame)):
        return shape.geometry.item()
    elif isinstance(shape, Series):
        return shape.geometry
    else:
        return shape

def localize_xy_to_window(window, transform, x, y):
    x = squeeze(x); y = squeeze(y)
    window_x, window_y = rasterio.transform.xy(cols=window.col_off-0.5, rows=window.row_off-0.5, transform=transform)
    return (x - window_x) / transform.a, (y - window_y) / transform.e