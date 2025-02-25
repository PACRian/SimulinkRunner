import matlab.engine

from simulinkRunner import Model, Runner, OutputPortProcessor, HDF5Recorder

MODEL_PATH = "./tests/simulink_model/"
HDF5_PATH = './tests/datas/simulation_test.h5'
MODEL_NAME = 'test'

SIM_ARGS = {
    'SimulationMode': 'normal', 
    'SolverName':'FixedStepDiscrete', 
    'StartTime': '0', 
    'StopTime': '10', 
    'FixedStep': '1'
}
MODEL_MULTI_ARGS = {
    'DUnit/DelayLength': '2',
    'oGain/Gain': ['2', '1'],
    'dGain/Gain': ['3', '1']
}


def run_mutiple_model_withHDF5(eng):
    model = Model(eng, MODEL_NAME)

    runner = Runner(model, 
                    model_path=MODEL_PATH,
                    model_args=MODEL_MULTI_ARGS,
                    sim_args=SIM_ARGS,
                    rec_path=HDF5_PATH,
                    rec_cls=HDF5Recorder,
                    proc_cls=OutputPortProcessor)
    
    print(f"[Info] Runner created suceeded with model: {model}.slx")
    descr_func = lambda model_args, _: f"Simulation batch with arguments: \
        {', '.join('{propName}={propVal}'.format(propName=k, propVal=v) for k, v in model_args.items())}"
    run_disp = lambda batch_idx, batch_descr, _: print(f"[Info] Running batch {batch_idx}: {batch_descr}")
    runner(descr_func=descr_func, afteproc_func=run_disp)
    runner.close()

if __name__ == '__main__':
    
    eng = matlab.engine.start_matlab() # Start MATLAB engine
    print("[Info] MATLAB engine started successfully, prepared to run the model.")
    run_mutiple_model_withHDF5(eng)
    print("[Info] MATLAB model run completed successfully.")
    eng.quit()  # Close MATLAB engine
    print("[Info] MATLAB engine closed successfully.")