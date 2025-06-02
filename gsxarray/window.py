from .common import get_geometry
from numpy import arange, hstack, s_
import rasterio
from rasterio.windows import Window
from shapely.geometry import Polygon
from shapely import prepare

class my_window(Window):

    @classmethod
    def from_raster_shape(cls, raster, shape):

        shape = get_geometry(shape)

        class tmp(object):
            def __init__(self, this):
                self.transform = this.rio.transform()
                self.width = this.rio.width
                self.height = this.rio.height

        try:
            cut = rasterio.features.geometry_window(tmp(raster), [shape])
            return cls(row_off=cut.row_off, col_off=cut.col_off, width=cut.width, height=cut.height)
        except:
            return None


    def chunk(self, chunk_x, chunk_y, transform=None):

        assert transform is not None, ValueError("transform required. Use raster.rio.transform()")
        xy = rasterio.transform.xy; t = transform

        row_index = hstack([arange(0, self.height, chunk_y), self.height+1]) + self.row_off
        nr = row_index.size-1

        col_index = hstack([arange(0, self.width,  chunk_x), self.width+1])  + self.col_off
        nc = col_index.size-1

        boxes = []
        windows = []
        for ii in range(nr):
            i = row_index[ii]; i1 = row_index[ii+1] - 1
            for jj in range(nc):
                j = col_index[jj]; j1 = col_index[jj+1] - 1

                corners = ((xy(t, i, j)), (xy(t, i, j1)), (xy(t, i1, j1)), (xy(t, i1, j)))
                p = Polygon(corners); prepare(p); boxes.append(p)

                windows.append(Window.from_slices(rows= s_[i, i1+1], cols= s_[j, j1+1]))

        return boxes, windows