from numpy import zeros, vstack, int32, r_, ceil, floor, sign, arctan2, inf
from .common import get_geometry, localize_xy_to_window
from .window import my_window
from .fast_march import fast_march
from shapely.geometry import MultiPolygon

def boundary_pixels(raster, shape):
    """Get the boundary pixels of a shape with a raster

    Will return duplicate pixel indices for a multipolygon.

    Parameters
    ----------
    raster : _type_
        _description_
    shape : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """
    shape = get_geometry(shape)
    boundaries = []
    if isinstance(shape, MultiPolygon):
        shape = list(shape.geoms)
        for zone in shape:
            boundary = _boundary_pixels(raster, zone)
            boundaries.append(boundary)
        boundaries = vstack(boundaries)
    else:
        boundaries = _boundary_pixels(raster, shape)
    return boundaries

def _boundary_pixels(raster, shape):
    """Get the intersecting pixel of a shape with a raster.

    The returned indices are from 0 - n_pixels where n_pixels is the range of the shape given the pixel size of the raster.

    Parameters
    ----------
    raster :

    shape :

    Returns
    -------
    exterior : array_like
        The intersecting pixels of the shape exterior coordinates
    interiors : list of array_like
        The intersecting pixels of all the shapes interior coordinates

    """
    shape = get_geometry(shape)
    # window = bounding_box(raster, shape)
    window = my_window.from_raster_shape(raster, shape)

    if window is None: # Could not get a bounding box for the shape.
        return zeros((0, 2), dtype=int32)

    off = r_[window.row_off, window.col_off]
    transform = raster.rio.transform()

    x, y = localize_xy_to_window(window, transform, *shape.exterior.coords.xy)
    exterior = fast_march(x, y, window.width, window.height) + off

    # Loop over any interior polygons, and mark the boundaries
    interiors = []
    if len(shape.interiors) > 0:
        for lr in shape.interiors:
            x, y = localize_xy_to_window(window, transform, *lr.xy)
            interior = fast_march(x, y, window.width, window.height)
            interiors.append(interior + off)
    return vstack([exterior, *interiors])