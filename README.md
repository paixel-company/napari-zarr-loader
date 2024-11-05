# napari-zarr-loader

[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A napari plugin for loading and visualizing Zarr files converted from IMS (Imaris) files, with support for multi-resolution datasets and dynamic resolution level changes.

## Description

**napari-zarr-loader** is a plugin for [napari](https://napari.org/), an open-source image viewer for multi-dimensional data. This plugin allows users to load Zarr files, particularly those converted from IMS files, into napari for visualization and analysis. It supports multi-resolution datasets and provides a widget to change resolution levels on-the-fly. The plugin also handles multi-channel data, allowing channels to be loaded either independently or stacked together.

## Features

- **Load Zarr Files Converted from IMS Files**: Easily load Zarr files that have been converted from Imaris IMS files.
- **Multi-Resolution Support**: Navigate through different resolution levels of your dataset.
- **Dynamic Resolution Change Widget**: Use the provided widget to change resolution levels without reloading the file manually.
- **Multi-Channel Handling**: Load multi-channel data either as separate layers or stacked along a specified axis.
- **Voxel Size Extraction**: Automatically extract and apply voxel size metadata if available in the file.

## Installation

You can install `napari-zarr-loader` via `pip`:

```bash
pip install napari-zarr-loader
git clone https://github.com/paixel/napari-zarr-loader.git
cd napari-zarr-loader
pip install -e .
```
## Usage
- **Loading Zarr Files**
	1.	**Open napari**: Launch napari from the command line:
  ```bash
  napari
  ```
  2.	**Load Your Zarr File**: In napari, go to File > Open... and select your .zarr file. If prompted to choose a plugin, select napari-zarr-loader.

- **Using the Resolution Change Widget**

	1.	**Access the Widget**: Go to Plugins > napari-zarr-loader > Resolution Change to open the widget.
	2.	**Select Resolution Level**:
	•	Use the resolution_level slider or input box to select the desired resolution level.
	•	0 corresponds to the highest resolution available in the dataset.
	3.	**Update the Data**:
	•	Click the Update button to reload the data at the selected resolution level.
	•	The existing layers loaded by this plugin will be updated accordingly.

- **Handling Multi-Channel Data**

	•	Independent Channels: By default, each channel in the dataset is loaded as a separate layer.
	•	Adjusting Channel Loading:
	•	If you prefer to stack channels together, you can modify the colorsIndependant parameter in the code to False.
	•	This will load all channels into a single layer with a specified channel_axis.

## Example Code Snippet
Here’s how you might call the zarr_reader function in your code:
```python
from napari_zarr_loader import zarr_reader

# Load data at resolution level 0
layer_data_list = zarr_reader('path_to_your_file.zarr', resolution_level=0)

# Add data to napari viewer
for data, meta in layer_data_list:
    viewer.add_image(data, **meta)
```
## Requirements

	•	Python 3.7+
	•	napari 0.4.5 or later
	•	Dependencies:
	•	numpy
	•	dask
	•	zarr
	•	magicgui
	•	napari-plugin-engine

## Contributing

Contributions are welcome! If you’d like to contribute to this project, please follow these steps:

	1.	Fork the Repository: Click the “Fork” button at the top right of this page.
	2.	Clone Your Fork:
```bash
git clone https://github.com/paixel/napari-zarr-loader.git
```
	3.	Create a New Branch:
```bash
git checkout -b feature/your-feature-name
```
	4.	Make Your Changes: Implement your feature or bug fix.
	5.	Commit Your Changes:
```bash
git commit -am 'Add new feature'
```
  6.	Push to Your Fork:
```bash
git push origin feature/your-feature-name
```
  7.	Submit a Pull Request: Open a pull request to the main repository’s master branch.
## Issues

If you encounter any problems or have suggestions, please open an issue on the GitHub issues page.

## License

This project is licensed under the terms of the MIT license. See the LICENSE file for details.

## Acknowledgments

	•	Thanks to the napari team for providing a powerful and flexible image visualization platform.
	•	The development of this plugin was inspired by the need to handle large, multi-resolution microscopy datasets efficiently.
	•	Contributions and feedback from the open-source community are greatly appreciated.