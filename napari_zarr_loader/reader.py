# napari_zarr_ims_loader.py

import os
import numpy as np
import dask.array as da
import zarr
from napari_plugin_engine import napari_hook_implementation
from typing import List, Tuple, Any

# Enable asynchronous loading for napari
os.environ["NAPARI_ASYNC"] = "1"

def zarr_reader(path: str) -> List[Tuple[Any, dict]]:
    """
    Reads a Zarr file converted from an IMS file and returns data and metadata for napari.
    """
    # Open the Zarr file
    zarr_root = zarr.open(path, mode='r')

    # Initialize lists to hold data and metadata
    data = []
    scales = []

    # Access the DataSet group
    dataset = zarr_root['DataSet']

    # Get resolution levels
    resolution_levels = sorted(dataset.group_keys())
    num_levels = len(resolution_levels)
    print(f"Available resolution levels: {num_levels}")

    # Assume single time point for simplicity
    timepoint_name = 'TimePoint 0'

    # Check if TimePoint group exists
    timepoint_group = dataset[resolution_levels[0]].get(timepoint_name, None)
    if timepoint_group is None:
        raise ValueError(f"TimePoint group '{timepoint_name}' not found in the Zarr file.")

    # Determine channels
    channels = sorted(timepoint_group.group_keys())
    num_channels = len(channels)
    print(f"Number of channels: {num_channels}")
    channel_names = [f'Channel {i}' for i in range(num_channels)]
    channel_axis = None

    # Loop over resolution levels and collect data
    for res_level_name in resolution_levels:
        res_level_group = dataset[res_level_name]
        timepoint_group = res_level_group[timepoint_name]
        channel_arrays = []
        for ch in channels:
            ch_group = timepoint_group[ch]
            data_array = ch_group['Data']

            # Convert Zarr array to Dask array
            dask_array = da.from_array(data_array, chunks=data_array.chunks)
            channel_arrays.append(dask_array)

        # Stack channels along a new axis if multiple channels
        if num_channels > 1:
            stacked = da.stack(channel_arrays, axis=0)  # Stack along axis 0
            data.append(stacked)
            channel_axis = 0
        else:
            data.append(channel_arrays[0])

    # Reverse the data list to have scales from low to high resolution
    data = list(reversed(data))

    # Prepare metadata
    meta = {
        'name': channel_names,
        'multiscale': True,
        'contrast_limits': None,  # Will compute below
        'scale': (1.0, 1.0, 1.0),  # Placeholder, will adjust if voxel sizes are available
        'metadata': {},  # Include any additional metadata if available
        'channel_axis': channel_axis,  # None if single channel
    }

    # Compute contrast limits from the smallest data (lowest resolution level)
    try:
        min_contrast = data[0].min().compute()
        max_contrast = data[0].max().compute()
        meta['contrast_limits'] = [float(min_contrast), float(max_contrast)]
    except Exception as e:
        print(f"Could not compute contrast limits: {e}")
        # Set default contrast limits based on data type
        dtype = data[0].dtype
        if dtype == np.dtype('uint16'):
            meta['contrast_limits'] = [0, 65535]
        elif dtype == np.dtype('uint8'):
            meta['contrast_limits'] = [0, 255]
        else:
            meta['contrast_limits'] = [float(data[0].min().compute()), float(data[0].max().compute())]

    # Attempt to extract voxel size from metadata
    try:
        # Access voxel sizes from DataSetInfo/Image
        dataset_info = zarr_root['DataSetInfo']['Image']
        voxel_sizes = [
            float(dataset_info.attrs['ExtMax0']) - float(dataset_info.attrs['ExtMin0']),
            float(dataset_info.attrs['ExtMax1']) - float(dataset_info.attrs['ExtMin1']),
            float(dataset_info.attrs['ExtMax2']) - float(dataset_info.attrs['ExtMin2']),
        ]
        # Calculate scale factors
        dimensions = data[0].shape[-3:]  # Assuming the last three axes are Z, Y, X
        scale = [vs / dim for vs, dim in zip(voxel_sizes, dimensions)]
        meta['scale'] = scale
    except Exception as e:
        print(f"Could not extract voxel sizes from metadata: {e}")
        # Use default scale of 1.0
        meta['scale'] = (1.0, 1.0, 1.0)

    # Return the data and metadata as expected by napari
    return [(data, meta)]

@napari_hook_implementation
def napari_get_reader(path):
    # If the path is a string and ends with '.zarr', use our reader
    if isinstance(path, str) and os.path.isdir(path) and path.endswith('.zarr'):
        return zarr_reader
    return None