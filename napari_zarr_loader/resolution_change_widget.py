# resolution_change_widget.py

import os
import napari
from magicgui import magic_factory
from napari_plugin_engine import napari_hook_implementation
from napari.layers import Image
from .reader import zarr_reader

@magic_factory(
    auto_call=False,
    call_button="Update"
)
def resolution_change(
    viewer: napari.Viewer,
    resolution_level: int = 0
):
    """
    This widget allows you to change the resolution level of the Zarr data loaded in napari.
    Select the desired resolution level and click 'Update' to reload the data.
    """

    # Find the first Image layer with 'metadata' containing 'fileName'
    image_layer = None
    for layer in viewer.layers:
        if isinstance(layer, Image) and 'fileName' in layer.metadata:
            image_layer = layer
            break

    if image_layer is None:
        print("No Image layer with 'fileName' in metadata found.")
        return

    # Get the file path from the metadata
    file_path = image_layer.metadata.get('fileName', None)
    if file_path is None:
        print("No 'fileName' found in layer metadata.")
        return

    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"The file '{file_path}' does not exist.")
        return

    # Use the zarr_reader function to load the data at the desired resolution level
    try:
        # Call the zarr_reader with the selected resolution level
        layer_data_list = zarr_reader(file_path, resolution_level=resolution_level)
    except ValueError as e:
        print(e)
        return

    # Remove old layers
    existing_layer_names = [layer.name for layer in viewer.layers]
    for data_tuple in layer_data_list:
        data, meta = data_tuple
        layer_name = meta.get('name', 'Zarr Data')
        if layer_name in existing_layer_names:
            viewer.layers.remove(layer_name)

    # Add the new layers to the viewer
    for data_tuple in layer_data_list:
        data, meta = data_tuple
        viewer.add_image(data, **meta)

@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    return resolution_change