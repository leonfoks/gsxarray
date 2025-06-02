from xarray import register_dataarray_accessor
from .conservative_stats import conservative_stats
from .intersection_weights import intersection_weights

@register_dataarray_accessor("gs")
class DataArray:

    def __init__(self, xarray_obj):
        self._obj = xarray_obj

    # def conservative_stats(self, shape,  stats=['sum'], **kwargs):

    #     if isinstance(shape, Polygon):
    #         return self.weighted_stats(shape, stats, **kwargs)
    #     elif isinstance(shape, (GeoSeries, GeoDataFrame)):
    #         return
    #     elif isinstance(shape, Series):
    #         return

    def conservative_stats(self, shape,  stats=['sum'], **kwargs):

        sm, cnt = conservative_stats(self._obj, shape, **kwargs)

        return sm

    def intersection_weights(self, shape, **kwargs):
        """
        Compute the intersection weights of a raster and a shape.
        """
        return intersection_weights(self._obj, shape, **kwargs)