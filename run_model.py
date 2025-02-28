# Provides a CLI-tool for running Simulink model 
import logging
import configparser
import argparse
import os
import sys
import ast

from simulinkRunner import Model, Runner, HDF5Recorder, OutputPortProcessor

# CONFIGURATION CONSTANTS   
DEFAULT_CONFIG = 'tests/config/basecfg.ini'
DEFAULT_H5_PATH ='tests/datas/sims_{}.h5'
DEFAULT_LOG_PATH = '.logs/sims_{}.log'

# Self-defined Action for parsing 'k-v' pairs   
class KeyValueAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        kvgroups = {}
        current_key = None
        for value in values:
            if '=' in value:
                # Process 'key=value' pairs (A new 'kv-pair' starts)
                current_key, val_part = value.split('=', 1)
                vals = val_part.split() if val_part else []
                kvgroups.setdefault(current_key, []).extend(vals)
            elif current_key is not None:
                # Continue the current 'kv-pair'
                kvgroups[current_key].extend(value)
            else:
                parser.error(f"Value '{value}' is not a key-value pair")

        setattr(namespace, self.dest, kvgroups)

_split = lambda x, deli: x.split(deli) if len(x.split(deli)) > 1 else x
sep_arr = lambda arr: dict([(subarr[0][0], _split(subarr[0][1], '-')) for subarr in arr])
# split_args = lambda x: dict([i.split('=') for i in x])
csv_list = lambda value: [x.split('=') for x in value.split(', ')]
get_ini_args = lambda cfg, section, argname: ast.literal_eval(cfg.get(section, argname, fallback="{}"))
descr_func = lambda model_args, _: f"Simbatch with arguments:  {', '.join('{}={}'.format(k, v) for k, v in model_args.items())}"

    
###### Read arguments
parser = argparse.ArgumentParser(description='Run Simulink model')
parser.add_argument('model', help='Path to Simulink model')
parser.add_argument('-p', '--path', default='.', help='Model path')
parser.add_argument('-s', '--simulation-args', nargs='+', type=csv_list, help='Simulation arguments')
# parser.add_argument('-m', '--model-args', nargs='+', help='Model arguments')
# parser.add_argument('-m', '--model-args', nargs='+', type=csv_list, help='Model arguments')
parser.add_argument('-m', '--model-args', nargs='+', action=KeyValueAction, help='Model arguments')
parser.add_argument('-a', '--model-args-file', default=None, help='Model arguments file (json format)')
parser.add_argument('-o', '--output', default=None, help='Output file')
parser.add_argument('-c', '--config', default=DEFAULT_CONFIG, help='Path to the onfig file')
parser.add_argument('-l', '--log', default=None, help='Path to the log file')
parser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode')
parser.add_argument('-e', '--error', action='store_true', help='Error mode (Enable to pass errors)')

args = parser.parse_args()

###### Get configuration
config = configparser.ConfigParser()
config.read(args.config)

# Model basics
model_name = args.model
model_path = args.path if args.path else config.get('model', 'path', fallback='.')

# Model arguments Config<Section: model>

# sep_arr = lambda arr: dict([(subarr[0][0], subarr[0][1].split('-')) for subarr in arr])
# print(args.model_args, type(args.model_args), end='\n===MODEL ARGS===\n')
# print(sep_arr(args.model_args), end='\n=== SEP MODEL ARGS===\n')
model_args = args.model_args_file if args.model_args_file else get_ini_args(config, 'model', 'args')
if args.model_args:
    model_args.update(args.model_args)
    # model_args.update(sep_arr(args.model_args))

# Simulation arguments Config<Section: simulation>
sim_args = get_ini_args(config, 'simulation', 'args')
# sim_args = config.get('simulation', 'args', fallback={}) # As the base
if args.simulation_args:
    sim_args.update(sep_arr(args.simulation_args))

# Output file
if args.output:
    output_file = args.output
else:
    output_file = config.get('output', 'file', fallback=DEFAULT_H5_PATH)
    try:
        output_file = output_file.format(model_name)
    except Exception as e:
        pass 

# Error mode
error_mode = True if args.error else config.getboolean('output', 'error', fallback=False)

# Log file
if args.log:
    log_file = args.log
else:
    log_file = config.get('logging', 'file', fallback=DEFAULT_LOG_PATH)
    try:
        log_file = log_file.format(model_name)
    except Exception as e:
        pass

###### Configure logging handler
logging_level = logging.DEBUG if args.verbose else logging.INFO

logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
console_handler.setFormatter(logging.Formatter('[%(asctime)s] - [%(levelname)s] - | %(message)s.'))
file_handler.setFormatter(logging.Formatter('[%(asctime)s] - [%(name)s] - [%(levelname)s] - %(message)s.'))
logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.setLevel(logging_level)

# Show configuration
logger.info(f"Successfully read configuration from: {args.config}")
logger.info(f"Basic info below: \nModel: {model_name}, \t Model path: {model_path}\nData output to: {output_file}, \tLogging file: {log_file}")
logger.info(f"Logging level is set to: {'Debug' if logging_level == logging.DEBUG else 'Info'}")
if isinstance(model_args, dict):
    logger.debug(f"Model arguments listed as: {', '.join(['{}={}'.format(k, v.__repr__()) for k, v in model_args.items()])}")
elif isinstance(model_args, str):
    logger.debug(f"Model arguments can be read from JSON-file: {model_args}")

logger.debug(f"Simulation arguments listed as: {', '.join(['{}={}'.format(k, v.__repr__()) for k, v in sim_args.items()])}")
logger.info(f"Error mode is {'enabled' if error_mode else 'disabled'}")

###### Run the model
if __name__ == '__main__':
    running_disp = lambda batch_idx, batch_descr, _: logger.info(f"Running batch {batch_idx}: {batch_descr}")
    # Engine start
    try:
        import matlab.engine
        eng = matlab.engine.start_matlab() # Start MATLAB engine
        logger.debug(f"MATLAB engine started successfully at: {eng}")
    except:
        logger.error("Failed to start MATLAB engine")
        raise RuntimeError("Failed to start MATLAB engine, try to install MATLAB engine API for Python")

    logger.info(f"Matlab engine started, prepare to run the model: {model_name}")

    # Model statement
    model = Model(eng, model_name)
    model.prepare_model(model_path)
    logger.debug(f"Model {model_name} loaded successfully at: {model}")

    runner = Runner(model, 
                    model_args=model_args,
                    sim_args=sim_args,
                    rec_path=output_file,
                    rec_cls=HDF5Recorder,
                    proc_cls=OutputPortProcessor)
    logger.debug(f"Runner created successfully at: {runner}")

    # Running process
    logger.info(f"Prepared to run the model: {model_name}")
    runner(descr_func=descr_func, afteproc_func=running_disp)
    runner.close()
    logger.info(f"Simulation completed successfully, data saved to: {output_file}")

    # Engine close
    eng.quit()
    logger.info("Matlab engine closed successfully, simulation finished.")
