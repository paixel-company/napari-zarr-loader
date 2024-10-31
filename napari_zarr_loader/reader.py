import os
from napari_plugin_engine import napari_hook_implementation
import numpy as np
import dask.array as da
import zarr
from typing import List, Tuple, Any

def zarr_reader(
    path: str,
    res_level: int = 0,
    **kwargs
) -> List[Tuple[Any, dict]]:
    """
    Reads a Zarr file and returns data and metadata for napari.

    Parameters:
    - path (str): Path to the Zarr file.
    - res_level (int): Resolution level to load. Default is 0 (highest resolution).

    Returns:
    - List of tuples containing (data, metadata).
    """
    # Open the Zarr dataset
    zarr_root = zarr.open(path, mode='r')

    # Check for multiple resolution levels
    if 'resolution_levels' in zarr_root.attrs:
        num_levels = zarr_root.attrs['resolution_levels']
        # Validate res_level
        if res_level < 0 or res_level >= num_levels:
            raise ValueError(f"res_level {res_level} is out of bounds. Available levels: 0 to {num_levels - 1}")
        # Access the specified resolution level
        res_group = zarr_root[f'resolution_level_{res_level}']
    else:
        # Single resolution level
        res_group = zarr_root

    # Get the list of datasets (assumed to be channels)
    datasets = [key for key in res_group.array_keys()]

    layer_data = []

    for idx, dataset_name in enumerate(datasets):
        data_array = res_group[dataset_name]
        # Convert to Dask array
        data_dask = da.from_array(data_array, chunks='auto')

        # Prepare metadata
        meta = {
            'name': dataset_name,
            'metadata': {
                'fileName': path,
                'resolutionLevels': num_levels if 'num_levels' in locals() else 1,
            },
            'multiscale': False,  # Adjust if needed
        }

        # Add the data and metadata to the list
        layer_data.append((data_dask, meta))

    return layer_data

@napari_hook_implementation
def napari_get_reader(path):
    if isinstance(path, str):
        if os.path.isdir(path) and path.endswith('.zarr'):
            return zarr_reader
    return None