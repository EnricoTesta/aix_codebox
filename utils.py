from argparse import ArgumentParser
from subprocess import check_call


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
        '--remote-log-directory',
        default= None,
        metavar='remote_log_directory',
        help='Directory containing execution logs.')
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
        '--log-directory',
        default= "/codebox/",
        metavar='log_directory',
        help='Directory containing execution logs.')
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