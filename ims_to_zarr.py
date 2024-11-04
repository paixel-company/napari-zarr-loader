#!/usr/bin/env python3

import h5py
import zarr
import sys
import os

def copy_to_zarr(h5_group, zarr_group):
    """Recursively copy HDF5 groups and datasets to Zarr format."""
    for name, item in h5_group.items():
        if isinstance(item, h5py.Dataset):
            # Check for metadata compatibility
            if not item.dtype.metadata:  # Skip if dtype has complex metadata
                try:
                    print(f"Copying dataset {name}")
                    zarr_group.create_dataset(name, data=item[...], shape=item.shape, dtype=item.dtype)
                except Exception as e:
                    print(f"Skipping dataset {name} due to error: {e}")
            else:
                print(f"Skipping dataset {name} due to incompatible metadata.")
        elif isinstance(item, h5py.Group):
            print(f"Creating group {name}")
            new_zarr_group = zarr_group.create_group(name)
            copy_to_zarr(item, new_zarr_group)

def main(ims_path, zarr_path):
    if not os.path.exists(ims_path):
        print(f"Error: {ims_path} does not exist.")
        sys.exit(1)

    # Open the .ims file and create a new Zarr file
    with h5py.File(ims_path, 'r') as ims_file:
        zarr_file = zarr.open(zarr_path, mode='w')
        copy_to_zarr(ims_file, zarr_file)

    print(f"Conversion complete: {zarr_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python ims_to_zarr.py <input.ims> <output.zarr>")
        sys.exit(1)

    ims_path = sys.argv[1]
    zarr_path = sys.argv[2]
    main(ims_path, zarr_path)
