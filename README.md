# SimulinkRunner
`SimulinkRunner` is an automation tool designed to streamline the process of running and managing Simulink models. This provides a simple API to simulate the model multiple times for further recording and testing, helpful for control system design and analysis.

## Prerequisite
To enable this library, the [Matlab engine for Python](https://github.com/mathworks/matlab-engine-for-python) should be manually installed on your PC, according to your MATLAB version.

## Installation
The package can be installed via `pip`
```sh
pip install simulinkRunner
```
And it can also be installed from source code:
```sh
git clone git@github.com:PACRian/SimulinkRunner.git
cd simulinkRunner
pip install -e .
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

Check the simple demo [`run_batch_test.py`](https://github.com/PACRian/SimulinkRunner/blob/master/run_batch_test.py) along with a simple Simulink model [`test.slx`](https://github.com/PACRian/SimulinkRunner/tree/master/tests/simulink_model)(located in `tests/simulink_model`), execute the script to run the Simulink model multi-batch.
```bash
python .\run_batch_test.py
```

## Command line tool
A simple script `run_model.py` provides CLI tools for running Simulink models. The syntax is as follows:
```bash
python run_model.py [-h] [-p PATH] [-s SIMULATION_ARGS [SIMULATION_ARGS ...]] [-m MODEL_ARGS [MODEL_ARGS ...]] [-a MODEL_ARGS_FILE] [-o OUTPUT] [-c CONFIG] [-l LOG] [-v] [-e] model
```

### Options
- `-p`, `--path`: Specify the model path.
- `-s`: Provide simulation arguments.
- `-m`: Provide multiple model parameters.
- `-a`: Specify a file containing model arguments.
- `-o`: Specify the output path.
- `-c`: Provide a configuration file.
- `-l`: Specify a log file.
- `-v`: Enable verbose mode.
- `-e`: Enable error logging.

### Example Usage
To run the `test.slx` model with a discrete step of 0.001:
```bash
python run_model.py test -p tests/simulink_model -s FixedStep=.001
```
To run it with multiple batches configured by arguments stated after the `-m` flag:
```bash
python run_model.py test -p tests/simulink_model -m DUnit/DelayLength=2 oGain/Gain=2 1 dGain/Gain=2 3 4 -s FixedStep=.001 -v
```