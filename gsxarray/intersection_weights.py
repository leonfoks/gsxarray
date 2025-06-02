from .common import get_geometry
from numpy import empty, int32, isnan, r_, vstack
from shapely.geometry import Polygon, MultiPolygon
from numpy import r_, dstack, asarray
from .window import my_window
from .common import localize_xy_to_window
from .fast_march import fast_march
from .boundary import boundary_pixels
import rasterio
from geopandas import GeoDataFrame

def intersection_weights(da, shape, split=False):
    """Compute the intersection area between a polygon and its touching pixels in a raster

    Parameters
    ----------
    da : xr.DataArray
        Variable to instersect with the shape. The raster should have a CRS attached to it.
    shape : geopandas.Series or shapely.geometry
        Single geometric shape like Polygon or MultiPolygon or a row from a Geopandas Dataframe with attached geometry.
    split : bool
        If shape is a MultiPolygon, return weights for each Polygon that makes up the MultiPolygon. Otherwise, a single weights array will be created that contains the
        entire extent of the MultiPolygon. For MultiPolygons with a very high spatial extent, splitting will help with potential memory issues.

    Returns
    -------
    weights : xarray.DataArray of list of xarray.DataArray
        The weights for either a whole Multipolygon/Polygon or each Polygon in a MultiPolygon
    box : xarray.DataArray of list of xarray.DataArray
        The raster values for either a whole Multipolygon/Polygon or each Polygon in a MultiPolygon

    """
    shape = get_geometry(shape)

    if isinstance(shape, MultiPolygon) and split:
            shape = list(shape.geoms)
            weights = [_get_intersection_area_weights(da, shape) for shape in shape]
    else:
        weights = _get_intersection_area_weights(da, shape)

    return weights

def _get_intersection_area_weights(da, shape):

    # Get the bounding box of the shape.  If its provided its to save repeated reads from disk.
    shape = get_geometry(shape)

    weights = da.rio.clip([shape], from_disk=True, all_touched=True).squeeze()

    gwin = my_window.from_raster_shape(da, shape)
    offset = r_[gwin.row_off, gwin.col_off]

    # All boundaries are integerized from 0 to N.  When we assign the boundaries to the box, we need that offset.
    # bbox = bounding_box(weights, shape);
    transform = weights.rio.transform()

    # Fast march along the exterior and interior coordinates
    boundary = boundary_pixels(da, shape) - offset

    # Initialize the weights if buffer not provided.
    weights.values[~isnan(weights)] = 1.0
    weights.values[boundary[:, 0], boundary[:, 1]] = 0.0

    if boundary.shape[0] > 0:
        # for boundary in [exterior, *interiors]:
        # This next section can be sped up by creating an "integerized" transform. This would eliminate the calculation of each corner's global xy position.
        # I think integerizing the shape might be easier. I just havnt figured it out yet
        # Unnecessary remap to global coordinates.
        y = dstack([boundary + r_[-0.5, -0.5], boundary + r_[0.5, -0.5], boundary + r_[0.5, 0.5], boundary + r_[-0.5, 0.5]])

        # Create the array of polygons only on the boundaries
        polys = empty(y.shape[0], dtype=object)
        for i, t in enumerate(y):
            polys[i] = Polygon(asarray(rasterio.transform.xy(cols=t[1], rows=t[0], transform=transform)).T)

        # Do the intersection, and assign the 0 <= weights <= 1.0 on the boundary pixels
        df = GeoDataFrame(geometry=polys, crs=da.rio.crs)

        # offset to the box.
        pixel_area = df.iloc[[0]].area.item()

        try:
            weights.values[boundary[:, 0], boundary[:, 1]] += df.intersection(shape).area / pixel_area
        except:
            pass

    return weights
