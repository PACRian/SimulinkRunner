import h5py
import pandas as pd
import numpy as np

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union


class Recorder(ABC):
    def __init__(self):
        pass
    
    @abstractmethod
    def save_batch(self, **kwargs):
        pass

class HDF5Recorder(Recorder):
    """Class to handle HDF5 file operations for simulation data."""

    def __init__(self, h5_path: str):
        """
        Initialize the HDF5 recorder.

        Args:
            h5_path (str): Path to the HDF5 file.
        """
        self.h5f = h5py.File(h5_path, 'w')

    def save_batch(self, batch_id: int = 0, 
                   batch_descr: str = '',
                   batch_fmt: str = '',
                   data: Union[Dict[str, np.ndarray], pd.DataFrame, np.ndarray, None] = None, 
                   metadata: Optional[Dict[str, Any]] = None,
                   remain_time: bool = True):
        """
        Save a batch's data and metadata to HDF5.

        Args:
            batch_idx (int): Batch index.
            data (Dict[str, np.ndarray]): Data to save (e.g., time, signals).
            metadata (Dict[str, Any], optional): Metadata (e.g., signal names).
        """

        batch_fmt = batch_fmt if batch_fmt else 'batch_{batch_id}_{batch_descr}'
        batch_descr = batch_fmt.format(batch_id=batch_id, batch_descr=batch_descr) if batch_fmt else batch_descr
        group = self.h5f.create_group(batch_descr)

        if isinstance(data, pd.DataFrame):
            if remain_time:
                group.create_dataset('time', data=data['Time'].values)

            for key, subdf in data.items():
                group.create_dataset(key, data=subdf.values)
        elif isinstance(data, np.ndarray):
            if remain_time:
                group.create_dataset('time', data=data[:, 0]) 
                group.create_dataset('data', data=data[:, 1:])
            else:
                group.create_dataset('data', data=data)
        elif isinstance(data, dict):
            for key, value in data.items():
                group.create_dataset(key, data=value)   

        else:
            raise ValueError(f"Data type {type(data)} not supported.")

        if metadata:
            for key, value in metadata.items():
                group.attrs[key] = value

    def close(self):
        """Close the HDF5 file."""
        self.h5f.close()

    def read_batch(self, batch_idx: int) -> Dict[str, np.ndarray]:
        """
        Read a batch's data from HDF5.

        Args:
            batch_idx (int): Batch index.

        Returns:
            Dict[str, np.ndarray]: Data for the batch.
        """
        with h5py.File(self.h5f.filename, 'r') as h5f:
            batch = h5f[f'batch_{batch_idx}']
            return {key: batch[key][:] for key in batch.keys()}