# napari_zarr_ims_loader.py

import os
import numpy as np
import dask.array as da
import zarr
from napari_plugin_engine import napari_hook_implementation
from typing import List, Tuple, Any

# Enable asynchronous loading for napari
os.environ["NAPARI_ASYNC"] = "1"

# zarr_reader.py

def zarr_reader(path: str, resolution_level: int = 0) -> List[Tuple[Any, dict]]:
    """
    Reads a specified resolution level from a Zarr file and returns data and metadata for napari.
    """
    import os
    import numpy as np
    import dask.array as da
    import zarr
    from typing import List, Tuple, Any

    # Open the Zarr file
    zarr_root = zarr.open(path, mode='r')

    # Access the DataSet group
    dataset = zarr_root['DataSet']

    # Get resolution levels
    resolution_levels = sorted(dataset.group_keys())
    num_levels = len(resolution_levels)
    print(f"Available resolution levels: {num_levels}")

    # Validate resolution_level
    if resolution_level < 0 or resolution_level >= num_levels:
        raise ValueError(f"resolution_level {resolution_level} is out of bounds. Available levels: 0 to {num_levels - 1}")

    # Get the desired resolution level
    res_level_name = resolution_levels[resolution_level]
    res_level_group = dataset[res_level_name]

    # Assume single time point for simplicity
    timepoint_name = 'TimePoint 0'

    # Check if TimePoint group exists
    timepoint_group = res_level_group.get(timepoint_name, None)
    if timepoint_group is None:
        raise ValueError(f"TimePoint group '{timepoint_name}' not found in the Zarr file.")

    # Determine channels
    channels = sorted(timepoint_group.group_keys())
    num_channels = len(channels)
    print(f"Number of channels: {num_channels}")
    channel_names = [f'Channel {i}' for i in range(num_channels)]
    channel_axis = None

    # Collect data for the specified resolution level
    channel_arrays = []
    for ch in channels:
        ch_group = timepoint_group[ch]
        data_array = ch_group['Data']

        # Convert Zarr array to Dask array
        dask_array = da.from_array(data_array, chunks=data_array.chunks)
        channel_arrays.append(dask_array)

    # Stack channels along a new axis if multiple channels
    if num_channels > 1:
        data = da.stack(channel_arrays, axis=0)  # Stack along axis 0
        channel_axis = 0
    else:
        data = channel_arrays[0]

    # Prepare metadata
    meta = {
        'name': 'Zarr Data',
        'metadata': {
            'fileName': path,
            'resolutionLevels': num_levels,
        },
        'contrast_limits': None,  # Will compute below
        'scale': (1.0, 1.0, 1.0),  # Placeholder, will adjust if voxel sizes are available
        'channel_axis': channel_axis,  # None if single channel
    }

    # Compute contrast limits from the data
    try:
        min_contrast = data.min().compute()
        max_contrast = data.max().compute()
        meta['contrast_limits'] = [float(min_contrast), float(max_contrast)]
    except Exception as e:
        print(f"Could not compute contrast limits: {e}")
        # Set default contrast limits based on data type
        dtype = data.dtype
        if dtype == np.dtype('uint16'):
            meta['contrast_limits'] = [0, 65535]
        elif dtype == np.dtype('uint8'):
            meta['contrast_limits'] = [0, 255]
        else:
            meta['contrast_limits'] = [float(data.min().compute()), float(data.max().compute())]

    # Attempt to extract voxel size from metadata
    try:
        # Access voxel sizes from DataSetInfo/Image
        dataset_info = zarr_root['DataSetInfo']['Image']
        if all(attr in dataset_info.attrs for attr in ['ExtMax0', 'ExtMin0', 'ExtMax1', 'ExtMin1', 'ExtMax2', 'ExtMin2']):
            voxel_sizes = [
                float(dataset_info.attrs['ExtMax0']) - float(dataset_info.attrs['ExtMin0']),
                float(dataset_info.attrs['ExtMax1']) - float(dataset_info.attrs['ExtMin1']),
                float(dataset_info.attrs['ExtMax2']) - float(dataset_info.attrs['ExtMin2']),
            ]
            # Calculate scale factors
            dimensions = data.shape[-3:]  # Assuming the last three axes are Z, Y, X
            scale = [vs / dim for vs, dim in zip(voxel_sizes, dimensions)]
            meta['scale'] = scale
        else:
            print("Voxel size attributes not found in metadata. Using default scale of 1.0.")
            meta['scale'] = (1.0, 1.0, 1.0)
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