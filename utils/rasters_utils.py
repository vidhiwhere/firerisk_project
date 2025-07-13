# utils/raster_utils.py
import rasterio
import numpy as np
import pandas as pd
def read_tif_as_df(path, column_name):
    with rasterio.open(path) as src:
        arr = src.read(1).astype('float32')
        arr[arr == src.nodata] = np.nan

        rows, cols = arr.shape
        x, y = np.meshgrid(np.arange(cols), np.arange(rows))
        
        df = pd.DataFrame({
            'x': x.flatten(),
            'y': y.flatten(),
            column_name: arr.flatten()
        })

        return df
