import os
from utils import get_codebox_args, sync_directory
from subprocess import run
from logging import getLogger, basicConfig, DEBUG


args_dict = get_codebox_args()
# TODO: trace execution metadata (timing, memory, ...)

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

input_dir_arg = f"--input-directory={args_dict['input_directory']}"
output_dir_arg = f"--output-directory={args_dict['output_directory']}"
custom_code_dir_arg = f"--custom-code-directory={args_dict['custom_code_directory']}"
vault_log_dir_arg = f"--log-directory={args_dict['vault_log_directory']}"
run_mode_arg = f"--run-mode={args_dict['run_mode']}"

vault_cmd = f"python vault.py {input_dir_arg} {output_dir_arg} {custom_code_dir_arg} {vault_log_dir_arg} {run_mode_arg}"
vault_process = run(vault_cmd, shell=True, capture_output=True)

# TODO: restore network access @ this point

# STEP 6 - Export outputs
sync_directory(source_directory=args_dict['output_directory'], destination_directory=args_dict['remote_output_directory'])
sync_directory(source_directory=args_dict['log_directory'], destination_directory=args_dict['remote_log_directory'])
