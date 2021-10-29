from argparse import ArgumentParser
from importlib import import_module
from subprocess import check_call, run
from logging import getLogger


logger = getLogger('codebox_logger')

def get_args():
    """Argument parser.
    Returns:
      Dictionary of arguments.
    """
    parser = ArgumentParser()
    parser.add_argument(
        '--remote-input-directory',
        default= None,
        metavar='remote_input_directory',
        help='Directory where remote inputs are stored.')
    parser.add_argument(
        '--remote-output-directory',
        default= None,
        metavar='remote_output_directory',
        help='Directory where remote outputs are stored.')
    parser.add_argument(
        '--remote-custom-code-directory',
        default= None,
        metavar='remote_custom_code_directory',
        help='Directory where remote custom code is stored.')
    parser.add_argument(
        '--input-directory',
        default= "/codebox/test/sample_input_transform/",
        metavar='input_directory',
        help='Directory where inputs are stored.')
    parser.add_argument(
        '--output-directory',
        default= "/codebox/test/sample_output_transform/",
        metavar='output_directory',
        help='Directory where outputs are stored.')
    parser.add_argument(
        '--custom-code-directory',
        default= "/codebox/sample_code",
        metavar='custom_code_directory',
        help='Directory containing custom code.')
    parser.add_argument(
        '--run-mode',
        default='transform',
        metavar='run_mode',
        help='Directory where outputs are stored.')

    return vars(parser.parse_args())


def sync_directory(source_directory=None, destination_directory=None, environment='GCP'):
    if environment == 'GCP':
        get_input_dir_cmd = f"gsutil -m rsync {source_directory} {destination_directory}"
        check_call(get_input_dir_cmd)
    else:
        raise NotImplementedError

logger.info("Getting arguments...")
args_dict = get_args()

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
