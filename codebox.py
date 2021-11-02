import os
from utils import get_args, sync_directory
from importlib import import_module
from subprocess import run
from logging import getLogger, basicConfig, DEBUG


args_dict = get_args()

basicConfig(filename=os.path.join(args_dict['log_directory'], 'logs.log'),
                    filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=DEBUG)
logger = getLogger('codebox_logger')
logger.info("Logging started...")

# STEP 1 - Retrieve remote input directory
logger.info("Syncing input directory...")
sync_directory(source_directory=args_dict['remote_input_directory'], destination_directory=args_dict['input_directory'])

# STEP 2 - Retrieve custom code
logger.info("Syncing custom code directory...")
sync_directory(source_directory=args_dict['remote_custom_code_directory'], destination_directory=args_dict['custom_code_directory'])

# STEP 3 - pip install to ensure requirements are fullfilled
logger.info("Installing custom code...")
pip_cmd = f"python -m pip install {args_dict['custom_code_directory']}"
run(pip_cmd, shell=True)

# TODO: remove all internet and network access @ this point. Either spawn process as another user or use iptables on current user.

# STEP 4 - Import Module
logger.info("Importing custom module...")
custom_module = import_module(f"{args_dict['custom_code_directory'].split('/')[-1]}.main") # expect to import process & transform
process = getattr(custom_module, 'process')
transform = getattr(custom_module, 'transform')

# STEP 5 - Run Custom Code
if args_dict['run_mode'] == 'process':
    logger.info("Running process function...")
    try:
        process(input_directory=args_dict['input_directory'], output_directory=args_dict['output_directory'])
    except Exception as e:
        pass # get stacktrace
elif args_dict['run_mode'] == 'transform':
    logger.info("Running transform function...")
    try:
        transform(input_directory=args_dict['input_directory'], output_directory=args_dict['output_directory'])
    except Exception as e:
        pass # get stacktrace
else:
    raise ValueError(f"Run mode must be either 'process' or 'transform'. Found {args_dict['run_mode']}")

# TODO: restore network access @ this point

# STEP 6 - Export outputs
sync_directory(source_directory=args_dict['output_directory'], destination_directory=args_dict['remote_output_directory'])
sync_directory(source_directory=args_dict['log_directory'], destination_directory=args_dict['remote_log_directory'])
