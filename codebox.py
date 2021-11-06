import os
from utils import get_codebox_args, sync_directory
from subprocess import run
from logging import getLogger, basicConfig, DEBUG


args_dict = get_codebox_args()
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
status = sync_directory(source_directory=args_dict['remote_custom_code_directory'], destination_directory=args_dict['custom_code_directory'])
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
pip_cmd = f"sudo -H python -m pip install -r {os.path.join(args_dict['custom_code_directory'], 'requirements.txt')}; sudo -H python -m pip install {args_dict['custom_code_directory']}"
pip_process = run(pip_cmd, shell=True, capture_output=True)
if pip_process.returncode != 0:
    logger.error("Vault process failed. Stderr: ")
    logger.error(f"{pip_process.stderr.decode('utf-8')}")
    sync_directory(source_directory=args_dict['log_directory'], destination_directory=args_dict['remote_log_directory'])
    sync_directory(source_directory=args_dict['vault_log_directory'], destination_directory=args_dict['remote_vault_log_directory'])
    raise ChildProcessError

input_dir_arg = f"--input-directory={args_dict['input_directory']}"
output_dir_arg = f"--output-directory={args_dict['output_directory']}"
custom_code_dir_arg = f"--custom-code-directory={args_dict['custom_code_directory']}"
vault_log_dir_arg = f"--log-directory={args_dict['vault_log_directory']}"
run_mode_arg = f"--run-mode={args_dict['run_mode']}"

python_cmd = f"python vault.py {input_dir_arg} {output_dir_arg} {custom_code_dir_arg} {vault_log_dir_arg} {run_mode_arg}"
vault_cmd = f"sudo -u vault_user {python_cmd}"
logger.info("Run custom code in vault...")

# Remove all internet and network access for vault_user (uid 1500)
# Cannot disable gsutil for specific user is not possible
logger.info("Configuring iptables...")
iptables_cmd = "sudo iptables -A OUTPUT -m owner --uid-owner 1500 -j DROP"
iptables_process = run(iptables_cmd, shell=True, capture_output=True)
if iptables_process.returncode != 0:
    logger.error("Failed to configure iptables.")
    logger.error(f"{iptables_process.stderr.decode('utf-8')}")
    sync_directory(source_directory=args_dict['log_directory'], destination_directory=args_dict['remote_log_directory'])
    sync_directory(source_directory=args_dict['vault_log_directory'], destination_directory=args_dict['remote_vault_log_directory'])
    raise ChildProcessError

vault_process = run(vault_cmd, shell=True, capture_output=True)
if vault_process.returncode != 0:
    logger.error("Vault process failed. Stderr: ")
    logger.error(f"{vault_process.stderr.decode('utf-8')}")
    sync_directory(source_directory=args_dict['log_directory'], destination_directory=args_dict['remote_log_directory'])
    sync_directory(source_directory=args_dict['vault_log_directory'], destination_directory=args_dict['remote_vault_log_directory'])
    raise ChildProcessError

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