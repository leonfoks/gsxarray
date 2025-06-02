# Author: Leon Foks
from .common import get_geometry
from numpy import argwhere, empty, int32, isnan, nan, nansum, r_, sort, vstack
from shapely.geometry import Polygon, MultiPolygon
from .window import my_window
from .intersection_weights import _get_intersection_area_weights

def conservative_stats(raster, shape, **kwargs):

    shape = get_geometry(shape)

    c = 0
    s = 0.0
    if isinstance(shape, MultiPolygon):

        shape = list(shape.geoms)

        indices = []

        for i, zone in enumerate(shape):
                sm, ind = _conservative_stats(raster, zone, **kwargs)
                s += sm

                # The boundary starts at 0 because its local to the shape.
                # Add back in the Polygon's window offset to correctly get unique indices
                indices.append(ind)

    else:
        # Single Polygon
        sm, indices = _conservative_stats(raster, shape, **kwargs)
        s += sm;

    return s, c


def _conservative_stats(raster, shape, chunk_x=None, chunk_y=None, plot=False):
    shape = get_geometry(shape)

    assert isinstance(shape, Polygon), TypeError("shape must have type shapely.Polygon")

    # Get the bounding box of the polygon to check its size in n_pixels
    window = my_window.from_raster_shape(raster, shape)

    if window is None:
        return nan, 0

    chunk_x = window.width if chunk_x is None else chunk_x
    chunk_y = window.height if chunk_y is None else chunk_y

    s = 0.0
    if (window.height > chunk_y) or (window.width > chunk_x):

        boxes, windows = window.chunk(chunk_x, chunk_y, transform=raster.rio.transform())

        indices = empty((0, 2), dtype=int32)

        for box, win in zip(boxes, windows):

            compute = True
            tmp = window.from_raster_shape(raster, box)

            try:
                values = raster.rio.clip([box], from_disk = True, all_touched=True)

                values = values.rio.clip([shape], all_touched=True)
                compute = True
            except Exception as e:
                compute = False

            if compute:
                # Do the intersection on the chunk
                wts = _get_intersection_area_weights(values, shape)

                # Non-Nan indices for the shape are relative to the shapes window into raster
                indices = vstack([indices, argwhere(~isnan(wts.values)) + r_[tmp.row_off, tmp.col_off]])

                if wts is not None:
                    s += nansum(sort(wts * values))

    else:
        values = raster.rio.clip([shape], from_disk=True, all_touched=True)
        wts = _get_intersection_area_weights(raster, shape)

        # Non-Nan indices for the shape are relative to the shapes window into raster
        indices = argwhere(~isnan(wts.values)) + r_[window.row_off, window.col_off]

        if wts is not None:
            s = nansum((wts * values).values).item()

    return s, indices