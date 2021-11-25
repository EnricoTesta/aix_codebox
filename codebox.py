import os
from importlib import import_module
from utils import get_codebox_args, sync_directory
from subprocess import run
from yaml import safe_load
from logging import getLogger, basicConfig, DEBUG


config_file_uri = get_codebox_args()['config_file_uri']
status = sync_directory(source_directory=config_file_uri, destination_directory=os.getcwd())
with open(os.path.join(os.getcwd(), config_file_uri.split("/")[-1]), 'r') as f:
    args_dict = safe_load(f)
# TODO: trace execution metadata (timing, memory, ...)

basicConfig(filename=os.path.join(args_dict['log_directory'], 'logs.log'),
                    filemode='w',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=DEBUG)
logger = getLogger('codebox_logger')
logger.info("Logging started...")
logger.info(f"Current directory is {os.getcwd()}")

identity_check = run('whoami', shell=True, capture_output=True)
current_user = identity_check.stdout.decode('utf-8').replace('\n', '')
logger.info(f"Currently user is {current_user}...")

# STEP 1 - Retrieve remote input directory
logger.info("Syncing input directory...")
status = sync_directory(source_directory=args_dict['remote_input_directory'], destination_directory=args_dict['input_directory'])
if status.returncode != 0:
    logger.error(f"Return code {status.returncode}. Stderr: {status.stderr}")
    sync_directory(source_directory=args_dict['log_directory'], destination_directory=args_dict['remote_log_directory'])
    sync_directory(source_directory=args_dict['vault_log_directory'], destination_directory=args_dict['remote_vault_log_directory'])
    raise ChildProcessError

# STEP 2 - Retrieve custom code
logger.info("Syncing custom code directory...")
status = sync_directory(source_directory=args_dict['remote_custom_code_directory'], destination_directory=args_dict['custom_code_directory'], recursive=True)
if status.returncode != 0:
    logger.error(f"Return code {status.returncode}. Stderr: {status.stderr}")
    sync_directory(source_directory=args_dict['log_directory'], destination_directory=args_dict['remote_log_directory'])
    sync_directory(source_directory=args_dict['vault_log_directory'], destination_directory=args_dict['remote_vault_log_directory'])
    raise ChildProcessError


logger.info("Syncing package repo...")
status = sync_directory(source_directory=args_dict['remote_repo_directory'], destination_directory=args_dict['repo_directory'])
if status.returncode != 0:
    logger.error(f"Return code {status.returncode}. Stderr: {status.stderr}")
    sync_directory(source_directory=args_dict['log_directory'], destination_directory=args_dict['remote_log_directory'])
    sync_directory(source_directory=args_dict['vault_log_directory'], destination_directory=args_dict['remote_vault_log_directory'])
    raise ChildProcessError

# STEP 3 - pip install to ensure requirements are fullfilled
# Using "sudo -H python -m pip" makes packages install globally (i.e. they can be used also by other users)
# In this case there is redundancy between setup.py and requirements.txt. Moreover, packages are installed also on current user
# using setup.py which is useless.
logger.info("Installing custom code...")
pip_cmd = f"sudo -H python -m pip install --no-index --find-links={args_dict['repo_directory']} -r {os.path.join(args_dict['custom_code_directory'], 'requirements.txt')}; sudo -H python -m pip install {args_dict['custom_code_directory']}"
pip_process = run(pip_cmd, shell=True, capture_output=True)
if pip_process.returncode != 0:
    logger.error("Pip process failed. Stderr: ")
    logger.error(f"{pip_process.stderr.decode('utf-8')}")
    sync_directory(source_directory=args_dict['log_directory'], destination_directory=args_dict['remote_log_directory'])
    sync_directory(source_directory=args_dict['vault_log_directory'], destination_directory=args_dict['remote_vault_log_directory'])
    raise ChildProcessError

logger.info("Importing custom module...")
custom_module_name = args_dict['custom_code_directory'].split('/')[-1]
custom_module = import_module(f"{custom_module_name}.{custom_module_name}.main")

try:
    logger.info("Fetching function handler...")
    fn_callable = getattr(custom_module, args_dict['run_mode'])
except AttributeError:
    logger.error(f"Function {args_dict['run_mode']} undefined in custom module.")
    raise AttributeError(f"Function {args_dict['run_mode']} undefined in custom module.")

try:
    logger.info(f"Executing function {args_dict['run_mode']}...")
    fn_callable(input_directory=args_dict['input_directory'], output_directory=args_dict['output_directory'])
except Exception as e:
    logger.error("Custom callable function error.")
    logger.error(f"{str(e)}")
    raise RuntimeError

# STEP 6 - Export outputs
logger.info("Syncing output directory with remote path...")
status = sync_directory(source_directory=args_dict['output_directory'], destination_directory=args_dict['remote_output_directory'])
if status.returncode != 0:
    logger.error(f"Return code {status.returncode}. Stderr: {status.stderr}")
    sync_directory(source_directory=args_dict['log_directory'], destination_directory=args_dict['remote_log_directory'])
    sync_directory(source_directory=args_dict['vault_log_directory'], destination_directory=args_dict['remote_vault_log_directory'])
    raise ChildProcessError

logger.info("Syncing log directory with remote path...")
status = sync_directory(source_directory=args_dict['log_directory'], destination_directory=args_dict['remote_log_directory'])
if status.returncode != 0:
    logger.error(f"Return code {status.returncode}. Stderr: {status.stderr}")
    raise ChildProcessError