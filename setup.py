# setup.py

from setuptools import setup, find_packages

setup(
    name='napari-zarr-reader',
    version='0.1.0',
    author='Your Name',
    description='A napari plugin to read Zarr files with resolution levels.',
    packages=find_packages(),
    install_requires=[
        'napari',
        'napari-plugin-engine',
        'magicgui',
        'zarr',
        'dask[array]',
    ],
    entry_points={
        'napari.plugin': [
            'napari-zarr-reader = napari_zarr_reader',
        ],
    },
)