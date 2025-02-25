from abc import ABC, abstractmethod
from typing import Any, Dict, Union

import pandas as pd
import numpy as np

class SimulationProcessor(ABC):
    """Abstract base class for simulation data processing and recording."""

    def __init__(self, runner=None):
        """
        Initialize with the output file path.

        Args:
            output_file (str): Path to the HDF5 file for data storage.
        """
        self.runner = runner

    @abstractmethod
    def sim_proc(self, sim_output: Any) -> Union[Dict[str, np.ndarray], pd.DataFrame]:
        """
        Process raw simulation output into a structured format.

        Args:
            sim_output (Any): Raw output from the simulation.

        Returns:
            Dict[str, np.ndarray]: Processed data (e.g., {'time': array, 'signals': array}).
        """
        pass

    # @abstractmethod
    # def gen_metadata(self, sim_output: Any) -> Dict[str, Any]:
    #     """
    #     Generate metadata from the simulation output.

    #     Args:
    #         sim_output (Any): Raw output from the simulation.

    #     Returns:
    #         Dict[str, Any]: Metadata for the simulation output.
    #     """
    #     pass

class OutputPortProcessor(SimulationProcessor):
    """A class to process output ports from a simulation."""

    def __init__(self, runner):
        super().__init__(runner)

    def sim_proc(self, eng, sim_output: Any) -> pd.DataFrame:
        """Process raw simulation output into a structured format."""

        time = np.array(eng.find(sim_output, 'tout'))
        datas = eng.extractTs(eng.find(sim_output, 'yout'))
        sig_names = [signame for signame in datas.keys()]
        datas = [np.array(data) for data in datas.values()]

        Ns = min(arr.shape[0] for arr in datas) # The smallest number of samples
        datas = np.hstack([arr[:Ns] for arr in datas])
        df = pd.DataFrame(datas, columns=sig_names)
        df.insert(0, 'Time', time[:Ns])

        return df
    

        # yout = self.runner.eng.find(sim_output, 'yout') 
        # # The matlabl.Dataset for all output signals
        # sig_names = self.runner.eng.getElementNames(yout)
        # # Get all signal names

        # def _get_data(ds, name):
        #     ds = eng.struct(eng.find(ds, name))
        #     return eng.struct(ds['Values'])['Data']
        
        # time = np.array(eng.find(sim_output, 'tout'))
        # # The timeseries data

        # ndatas = [np.array(_get_data(yout, sig_name)) for sig_name in sig_names]
        
        # Ns = min(arr.shape[0] for arr in ndatas) # The smallest number of samples
        # datas = np.hstack([arr[:Ns] for arr in ndatas])
        # df = pd.DataFrame(datas, columns=sig_names)
        # df.insert(0, 'Time', time[:Ns])

        # return df