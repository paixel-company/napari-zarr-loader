# resolution_change_widget.py

import os
import napari
from magicgui import magic_factory
from napari_plugin_engine import napari_hook_implementation
from typing import List
from napari.layers import Image
from .reader import zarr_reader

@magic_factory(
    auto_call=False,
    call_button="Update"
)
def resolution_change(
    viewer: napari.Viewer,
    lowest_resolution_level: int = 0
):
    """
    This widget provides a tool to reload data at a selected resolution level.
    Higher numbers (lower resolution) = coarser data.

    Important for 3D rendering. Select the desired resolution level and click Update.
    """
    # Find the first Image layer with 'fileName' in its metadata
    image_layer = None
    for layer in viewer.layers:
        if isinstance(layer, Image) and 'fileName' in layer.metadata:
            image_layer = layer
            break

    if image_layer is None:
        print("No Image layer with 'fileName' in metadata found.")
        return

    # Get the total number of available resolution levels
    total_levels = image_layer.metadata.get('resolutionLevels', None)
    if total_levels is None:
        print("Unable to get the number of available resolution levels.")
        return

    # Validate the lowest_resolution_level is within the valid range
    if lowest_resolution_level < 0 or lowest_resolution_level >= total_levels:
        print(f"The selected resolution level is invalid. Please select a value between 0 and {total_levels - 1}.")
        return

    # Get the file path from the metadata
    file_path = image_layer.metadata['fileName']

    # Use the zarr_reader function to load the data at the desired resolution level
    try:
        layer_data_list = zarr_reader(
            file_path,
            res_level=lowest_resolution_level
        )
    except ValueError as e:
        print(e)
        return

    # Remove old layers
    existing_layer_names = [layer.name for layer in viewer.layers]
    for data, meta in layer_data_list:
        layer_name = meta['name']
        if layer_name in existing_layer_names:
            viewer.layers.remove(layer_name)

    # Add the new layers to the viewer
    for data, meta in layer_data_list:
        viewer.add_image(data, **meta)

@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    return resolution_change