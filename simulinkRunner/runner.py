# my_project/runner.py
from typing import Dict, Any, Union, List

from .model import Model  # Lazy import
from ._utiltis.data_processers import SimulationProcessor # Lazy import
from ._utiltis.data_recorders import Recorder  # Lazy import

MATLAB_DEPS_FOLDER = '\\_matlab_func'


class Runner:
    """Class to run simulations, process outputs, and record to HDF5."""

    def __init__(self, model: Model, 
                 model_path: str='',
                 model_deps: List[str]=[],
                 model_args: Union[Dict[str, str], None] = None,
                 sim_args: Union[Dict[str, str], None] = None, 
                 proc_cls: Union['SimulationProcessor', None] = None, 
                 rec_cls: Union['Recorder', None] = None,
                 rec_path: str = '',
                 recorder : Union['Recorder', None]= None):
        """
        Initialize the runner with a model, output file, and simulation arguments.

        Args:
            model: Instance of Model class.
            output_file (str): Path to HDF5 file for recording.
            sim_args (Union[Dict[str, str], None]): Simulation arguments.
            proc_cls (Union[SimulationProcessor, None]): Simulation processor class.
        """
        # Register model and load model dependencies
        self.model = model
        self.model._init_args(model_args)
        self.prepare(model_path, model_deps)

        # Store simulation arguments and data-processor
        self.sim_args = sim_args if sim_args is not None else {}
        self.proc = proc_cls(self) if proc_cls is not None else None

        # Initialize recorder
        self.rec = recorder if recorder else rec_cls(rec_path)

        # Add MATLAB dependencies
        if not _add_matlab_dependencies(self.model.eng):
            raise RuntimeError("Failed to add MATLAB dependencies %s", MATLAB_DEPS_FOLDER)

    def __call__(self, **kwargs):
        """Run the loaded model and save results to HDF5."""
        dproc_func = kwargs.pop('proc_func', None)
        meta_func  = kwargs.pop('meta_func', None)
        rec_func   = kwargs.pop('rec_func', None)
        descr_func = kwargs.pop('descr_func', None)
        after_proc = kwargs.pop('afteproc_func', None)
        res_func   = kwargs.pop('res_func', None)
        batch_fmt  = kwargs.pop('descr', '')
        remain_time = kwargs.pop('remain_time', True) # Default to True, propagated

        try:
            sim_args = self.sim_args
            sim_args.update(kwargs) if kwargs else sim_args

            results = []
            for batch_idx, model_instance in enumerate(self.model):
                # Run simulation
                sim_out = model_instance.run_sim(sim_args)

                # Data pre-processing
                if dproc_func:
                    sim_out = dproc_func(sim_out)
                else:
                    sim_out = self._proc(sim_out)

                # Description and metadata
                model_args = model_instance._get_parameters()
                batch_descr = descr_func(model_args, sim_args) if descr_func else ''
                
                if meta_func:
                    metadata = meta_func(model_args, sim_args)
                else:
                    metadata = {'descr': batch_descr, 'id': batch_idx}

                # Data saving (Save to HDF5)
                if rec_func:
                    batch_descr = batch_fmt.format(batch_id=batch_idx, batch_descr=batch_descr) if batch_fmt else batch_descr
                    rec_func(batch_descr, sim_out, metadata, remain_time)
                elif self.rec:
                    self.rec.save_batch(batch_idx, batch_descr, batch_fmt, sim_out, metadata, remain_time)
                
                # After processing
                # We suggest if you want to save the intermediate results or sim-hinting, 
                # complete the after_proc_func as you wish
                if after_proc:
                    after_proc(batch_idx, batch_descr, sim_out)

                # Results processing
                if res_func:
                    results.append(res_func(sim_out))
                
                # # Save to HDF5
                # if isinstance(processed_out, dict) and all(isinstance(v, np.ndarray) for v in processed_out.values()):
                #     data = processed_out  # Already in dict of numpy arrays
                # else:
                #     # Default processing if not already formatted
                #     data = {'raw_output': np.array(sim_out) if hasattr(sim_out, '__array__') else np.array([])}
                # metadata = {'signal_names': ['raw']}  # Adjust based on processor output
                # self.recorder.save_batch(batch_idx, data, metadata)
                # print(f"Saved batch {batch_idx} to {self.output_file}")

                # results.append(processed_out)
            return results

        except Exception as e:
            raise RuntimeError(f"Failed to run model '{self.model.model_name}': {e}")

    def _proc(self, sim_out):
        """Process the simulation output."""
        if self.proc is not None:
            return self.proc.sim_proc(self.model.eng, sim_out)
        return sim_out
    
    def prepare(self, model_path: str='', dependencies: list=[]):
        """Prepare the model for simulation."""
        self.model.prepare_model(model_path, dependencies)

    def close(self):
        try:
            self.model.close_model()
            self.rec.close()
        except Exception as e:
            pass 


def _add_matlab_dependencies(eng):
    """Add MATLAB dependencies to the path."""
    import os
    _matlab_func_path = os.path.dirname(__file__) + MATLAB_DEPS_FOLDER
    eng.addpath(_matlab_func_path, nargout=0)
    return True