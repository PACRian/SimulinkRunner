# my_project/model.py
from typing import Any, Dict, Union, Iterator
import re

from ._utiltis.model_args import GridArguments  # Lazy import

class Model:
    """
    Class to manage a Simulink model, iterable over parameter sets.

    Total methods below:
    - __init__(self, eng, model_name: str, model_args: Any = None)
    - load_model(self)
    - save_model(self)
    - close_model(self)
    - _set_parameters(self, **prop_dict)
    - run_simulation(self, sim_args: list[str])
    """

    def __init__(self, eng, model_name: str, model_args: Any = None):
        """
        Initialize the model with MATLAB engine and arguments.

        Args:
            eng (matlab.engine): MATLAB engine instance.
            model_name (str): Name of the Simulink model.
            model_args (Any): Model arguments (e.g., parameters to set).
        """
        self.eng = eng
        self.model_handle = None
        self.model_name = model_name
        self._init_args(model_args) 
        
    def prepare_model(self, model_path: str='', dependencies: list=[]) -> None:
        """Prepare the model for simulation."""
        if not self.eng:
            raise RuntimeError("MATLAB Engine is not running")
        try:
            # Switch current workspace to the `model_path`
            if model_path:
                self.eng.cd(model_path, nargout=0)

            # Add dependencies to the MATLAB path
            if dependencies:
                for dep in dependencies:
                    self.eng.addpath(dep, nargout=0)
            self.load_model()
        except Exception as e:
            raise RuntimeError(f"Failed to load model '{self.model_name}')': {e}")

    def load_model(self):
        """Load a Simulink model."""
        if not self.eng:
            raise RuntimeError("MATLAB Engine is not running")
        try:
            self.eng.load_system(self.model_name, nargout=0)
            self.model_handle = self.eng.Simulink.SimulationInput(self.model_name)
        except Exception as e:
            raise RuntimeError(f"Failed to load model '{self.model_name}': {e}")

    def save_model(self):
        """Save the current model."""
        if not self.eng or not self.model_name:
            raise RuntimeError("No model loaded or engine not running")
        try:
            self.eng.save_system(self.model_name, nargout=0)
        except Exception as e:
            raise RuntimeError(f"Failed to save model: {e}")

    def close_model(self):
        """Close the current model."""
        if not self.eng or not self.model_name:
            raise RuntimeError("No model loaded or engine not running")
        try:
            self.eng.close_system(self.model_name, nargout=0)
            self.model_handle = None
        except Exception as e:
            raise RuntimeError(f"Failed to close model: {self.model_name}: {e}")
        
    def _init_args(self, model_args: Union[Dict[str, str], GridArguments, str, None]):
        """Initialize the model arguments."""
        if model_args is None:
            self.model_args = None
        elif isinstance(model_args, dict):
            self.model_args = GridArguments(model_args)
        elif isinstance(model_args, GridArguments):
            self.model_args = model_args
        elif isinstance(model_args, str) and model_args.endswith('.json'):
            self.model_args = GridArguments.from_json(model_args)
        else:
            raise ValueError("Invalid model arguments")

    def set_parameters(self, prop_dict: Dict[str, str]):
        """Set a parameter for the loaded model."""
        if not self.eng or not self.model_handle:
            raise RuntimeError("No model loaded or engine not running")

        si = self.model_handle
        for prop_name, prop_value in prop_dict.items():
            try:
                pathlist = re.split(r'/', prop_name)
                if len(pathlist) == 1:
                    si = self.eng.setVariable(si, prop_name, prop_value)
                    # mdl_wks = self.eng.get_param(self.model_name, 'ModelWorkspace')
                    # self.eng.workspace['temp_value'] = prop_value
                    # self.eng.eval(f"assignin({mdl_wks}, '{prop_name}', temp_value)", nargout=0)
                else:
                    
                    block_path = self.model_name + '/' + '/'.join(pathlist[:-1])
                    prop_name = pathlist[-1]
                    si = self.eng.setBlockParameter(si, block_path, prop_name, prop_value)
                
                self.model_handle = si
            except Exception as e:
                raise RuntimeError(f"Failed to set parameter: {e}")
            
    def _set_parameters(self):
        """Set the current model parameters."""
        # print(self.model_args, type(self.model_args))
        try:
            self.set_parameters(next(self.model_args))
            return True
        except StopIteration:
            return False
            
    def _get_parameters(self):
        """Get the current model parameters."""
        return self.model_args.current() if self.model_args is not None else {}
    
    def __len__(self) -> int:
        """Return the number of parameter sets."""
        return self.model_args.totals() if self.model_args else 1
    
    def run_sim(self, sim_args: Dict[str, str]):
        """Run the simulation with provided arguments."""
        if not self.eng or not self.model_handle:
            raise RuntimeError("No model loaded or engine not running")
        
        si = self.model_handle
        for arn, arv in sim_args.items():
            si = self.eng.setModelParameter(si, arn, arv)

        return self.eng.sim(si)
        
        # si = self.eng.Simulink.SimulationInput(self.model_name)
        for arn, arv in sim_args.items():
            self.eng.set_param(self.model_name, arn, arv, nargout=0)
            # si = self.eng.setModelParameter(si, arn, arv)
            # self.model_handle = self.eng.setModelParameter(self.model_handle, arn, arv)
            # self.model_handle = self.model_handle.setVariable(arn, arv)
        
        return self.eng.sim(self.model_name)
        # return self.eng.sim(self.model_name.rsplit('.', 1)[0])

        # return self.eng.sim_the_model('modelName', self.model_name.rsplit('.', 1)[0],
        #         'ConfigureForDeployment', 0, 'SimArguments', sim_args)
        # return self.eng.sim(self.model_name, *sim_args)

    def __iter__(self) -> Iterator['Model']:
        """
        Make the Model iterable over its parameter sets.

        Yields:
            Model: The instance itself, configured with each parameter set from model_args.
        """
        if self.model_args is None:
            # If no model_args, yield the model once as-is
            yield self
        else:
            # Iterate over parameter sets in model_args
            while self._set_parameters():
                yield self

            # for param_set in self.model_args:
            #     self.set_parameters(param_set)
            #     yield self

    def __repr__(self):
        return self.model_name