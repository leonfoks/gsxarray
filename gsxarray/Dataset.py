from xarray import register_dataset_accessor
from .conservative_stats import conservative_stats

@register_dataset_accessor("gs")
class Dataset:

    def __init__(self, xarray_obj):
        self._obj = xarray_obj

#     def weighted_stats(self, shape,  stats=['sum'], crs=None, **kwargs):
#         sm, cnt = conservative_stats(self._obj, shape, **kwargs)
#         results_complete[:] = sm

#         return results_complete