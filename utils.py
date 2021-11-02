from argparse import ArgumentParser
from subprocess import run
from yaml import safe_load
import os


with open(os.path.join(os.path.dirname(__file__), 'defaults.yaml'), 'r') as f:
    DEFAULTS = safe_load(f)

def get_args():
    """Argument parser.
    Returns:
      Dictionary of arguments.
    """
    parser = ArgumentParser()
    parser.add_argument(
        '--remote-input-directory',
        default= DEFAULTS['remote_input_directory'],
        metavar='remote_input_directory',
        help='Directory where remote inputs are stored.')
    parser.add_argument(
        '--remote-output-directory',
        default= DEFAULTS['remote_output_directory'],
        metavar='remote_output_directory',
        help='Directory where remote outputs are stored.')
    parser.add_argument(
        '--remote-custom-code-directory',
        default= DEFAULTS['remote_custom_code_directory'],
        metavar='remote_custom_code_directory',
        help='Directory where remote custom code is stored.')
    parser.add_argument(
        '--remote-log-directory',
        default= DEFAULTS['remote_log_directory'],
        metavar='remote_log_directory',
        help='Directory containing execution logs.')
    parser.add_argument(
        '--input-directory',
        default= DEFAULTS['input_directory'],
        metavar='input_directory',
        help='Directory where inputs are stored.')
    parser.add_argument(
        '--output-directory',
        default= DEFAULTS['output_directory'],
        metavar='output_directory',
        help='Directory where outputs are stored.')
    parser.add_argument(
        '--custom-code-directory',
        default= DEFAULTS['custom_code_directory'],
        metavar='custom_code_directory',
        help='Directory containing custom code.')
    parser.add_argument(
        '--log-directory',
        default= DEFAULTS['log_directory'],
        metavar='log_directory',
        help='Directory containing execution logs.')
    parser.add_argument(
        '--run-mode',
        default=DEFAULTS['run_mode'],
        metavar='run_mode',
        help='Directory where outputs are stored.')

    return vars(parser.parse_args())


def sync_directory(source_directory=None, destination_directory=None, environment='GCP'):
    if environment == 'GCP':
        get_input_dir_cmd = f"gsutil -m rsync {source_directory} {destination_directory}"
        run(get_input_dir_cmd, shell=True)
    else:
        raise NotImplementedError