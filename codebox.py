import os
import sys
from importlib import import_module
from utils import get_codebox_args, get_custom_module_name
from subprocess import run
from yaml import safe_load
from logging import getLogger, basicConfig, DEBUG


config_file_uri = get_codebox_args()['config_file_uri']
with open(config_file_uri, 'r') as f:
    args_dict = safe_load(f)
# TODO: trace execution metadata (timing, memory, ...)

if args_dict['run_mode'] == 'process':
    log_file_name = 'process_logs.log'
elif args_dict['run_mode'] == 'transform':
    log_file_name = 'transform_logs.log'
else:
    raise ValueError(f"Run mode can be either 'process' or 'transform'. Got {args_dict['run_mode']}.")

basicConfig(filename=os.path.join(args_dict['log_directory'], log_file_name),
                    filemode='w',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=DEBUG)
logger = getLogger('codebox_logger')
logger.info("Logging started...")
logger.info(f"Current directory is {os.getcwd()}")

identity_check = run('whoami', shell=True, capture_output=True)
current_user = identity_check.stdout.decode('utf-8').replace('\n', '')
logger.info(f"Current user is {current_user}...")

# STEP 3 - pip install to ensure requirements are fullfilled
# Using "sudo -H python -m pip" makes packages install globally (i.e. they can be used also by other users)
# In this case there is redundancy between setup.py and requirements.txt. Moreover, packages are installed also on current user
# using setup.py which is useless.
logger.info("Installing custom code...")
custom_module_name, custom_module_abs_path = get_custom_module_name(args_dict['custom_code_directory'])
# pip_cmd = f"sudo -H python -m pip install --no-index --find-links={args_dict['repo_directory']} -r {os.path.join(args_dict['custom_code_directory'], 'requirements.txt')}; sudo -H python -m pip install {args_dict['custom_code_directory']}"
pip_cmd = f"sudo -H python -m pip install --ignore-installed --no-index --find-links={args_dict['repo_directory']} -r {os.path.join(args_dict['custom_code_directory'], 'requirements.txt')}"
pip_process = run(pip_cmd, shell=True, capture_output=True)
if pip_process.returncode != 0:
    logger.error("Pip process failed. Stderr: ")
    logger.error(f"{pip_process.stderr.decode('utf-8')}")
    run('shutdown now', shell=True)

logger.info("Importing custom module...")
sys.path.append(os.path.join(args_dict['custom_code_directory'], custom_module_name))
custom_module = import_module("main", package=custom_module_name)

try:
    logger.info("Fetching function handler...")
    fn_callable = getattr(custom_module, args_dict['run_mode'])
except AttributeError:
    logger.error(f"Function {args_dict['run_mode']} undefined in custom module.")
    run('shutdown now', shell=True)

try:
    logger.info(f"Executing function {args_dict['run_mode']}...")
    fn_callable(input_directory=args_dict['input_directory'], output_directory=args_dict['output_directory'])
except Exception as e:
    logger.error("Custom callable function error.")
    logger.error(f"{str(e)}")
    run('shutdown now', shell=True)

run('shutdown now', shell=True)