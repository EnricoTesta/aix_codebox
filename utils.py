from argparse import ArgumentParser
from subprocess import run, CalledProcessError
from yaml import safe_load
import os


with open(os.path.join(os.path.dirname(__file__), 'defaults.yaml'), 'r') as f:
    DEFAULTS = safe_load(f)

def get_vault_args():
    """Argument parser.
    Returns:
      Dictionary of arguments.
    """
    parser = ArgumentParser()
    parser.add_argument(
        '--input-directory',
        default= DEFAULTS['vault']['input_directory'],
        metavar='input_directory',
        help='Directory where inputs are stored.')
    parser.add_argument(
        '--output-directory',
        default= DEFAULTS['vault']['output_directory'],
        metavar='output_directory',
        help='Directory where outputs are stored.')
    parser.add_argument(
        '--custom-code-directory',
        default= DEFAULTS['vault']['custom_code_directory'],
        metavar='custom_code_directory',
        help='Directory containing custom code.')
    parser.add_argument(
        '--log-directory',
        default= DEFAULTS['vault']['log_directory'],
        metavar='log_directory',
        help='Directory containing logs.')
    parser.add_argument(
        '--run-mode',
        default=DEFAULTS['vault']['run_mode'],
        metavar='run_mode',
        help='Directory where outputs are stored.')

    return vars(parser.parse_args())

def get_codebox_args():
    """Argument parser.
    Returns:
      Dictionary of arguments.
    """
    parser = ArgumentParser()
    parser.add_argument(
        '--remote-input-directory',
        default= DEFAULTS['codebox']['remote_input_directory'],
        metavar='remote_input_directory',
        help='Directory where remote inputs are stored.')
    parser.add_argument(
        '--remote-output-directory',
        default= DEFAULTS['codebox']['remote_output_directory'],
        metavar='remote_output_directory',
        help='Directory where remote outputs are stored.')
    parser.add_argument(
        '--remote-custom-code-directory',
        default= DEFAULTS['codebox']['remote_custom_code_directory'],
        metavar='remote_custom_code_directory',
        help='Directory where remote custom code is stored.')
    parser.add_argument(
        '--remote-log-directory',
        default= DEFAULTS['codebox']['remote_log_directory'],
        metavar='remote_log_directory',
        help='Directory containing execution logs.')
    parser.add_argument(
        '--input-directory',
        default= DEFAULTS['codebox']['input_directory'],
        metavar='input_directory',
        help='Directory where inputs are stored.')
    parser.add_argument(
        '--output-directory',
        default= DEFAULTS['codebox']['output_directory'],
        metavar='output_directory',
        help='Directory where outputs are stored.')
    parser.add_argument(
        '--custom-code-directory',
        default= DEFAULTS['codebox']['custom_code_directory'],
        metavar='custom_code_directory',
        help='Directory containing custom code.')
    parser.add_argument(
        '--log-directory',
        default= DEFAULTS['codebox']['log_directory'],
        metavar='log_directory',
        help='Directory containing execution logs.')
    parser.add_argument(
        '--vault-log-directory',
        default= DEFAULTS['codebox']['vault_log_directory'],
        metavar='vault_log_directory',
        help='Directory containing vault execution logs.')
    parser.add_argument(
        '--run-mode',
        default=DEFAULTS['codebox']['run_mode'],
        metavar='run_mode',
        help='Directory where outputs are stored.')

    return vars(parser.parse_args())


def sync_directory(source_directory=None, destination_directory=None, environment='GCP'):
    if environment == 'GCP':
        get_input_dir_cmd = f"gsutil -m rsync {source_directory} {destination_directory}"
        try:
            status = run(get_input_dir_cmd, shell=True, capture_output=True, check=True)
        except CalledProcessError as e:
            return e
    else:
        raise NotImplementedError
    return status