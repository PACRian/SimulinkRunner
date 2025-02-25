# SimulinkRunner
`SimulinkRunner` is an automation tool designed to streamline the process of running and managing Simulink models. This provides a simple API to simulate the model multiple times for further recording and testing, helpful for control system design and analysis.

## Prerequisite
To enable this library, the [Matlab engine for Python](https://github.com/mathworks/matlab-engine-for-python) should be manually installed on your PC, according to your MATLAB version.

## Installation
The package can be installed via `pip`
```sh
pip install simulinkrunner
```
And it can also be installed from source code:
```sh
git clone https://github.com/<>.git
cd simulinkRunner
pip install .
```

## Quickstart
Firstly, import related utiltis from `simulinkRunner` and initialize the `matlab.engine` object
```python
import matlab.engine
from simulinkRunner import Model, Runner, OutputPortProcessor, HDF5Recorder

eng = matlab.engine.start_matlab()
``` 

Two main classes should be utilized, one is `Model` used to initialize a Simulink model reference object:
```python
model = Model(eng, MODEL_NAME)
```

Then you need to introduce a `Runner` instance to construct the simulation framework, for parameter management, data processing, recording, etc.
```python
runner = Runner(model, 
        model_path=MODEL_PATH,
        model_args=MODEL_MULTI_ARGS,
        sim_args=SIM_ARGS,
        rec_path=HDF5_PATH,
        rec_cls=HDF5Recorder,
        proc_cls=OutputPortProcessor)
```
Call `runner` to perform the simulation, and close the content by calling `close()`:
```python
runner()
runner.close()
```

A simple demo `run_batch_test.py` along with a simple Simulink model `test.slx` (located in `tests/simulink_model`) can be found, execute the script to run the Simulink model multi-batch.
```bash
python .\run_batch_test.py
```