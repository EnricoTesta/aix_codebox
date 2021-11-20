from argparse import ArgumentParser
from subprocess import run, CalledProcessError
from yaml import safe_load
from tempfile import TemporaryDirectory
import os

try:
    with open(os.path.join(os.path.dirname(__file__), 'defaults.yaml'), 'r') as f:
        DEFAULTS = safe_load(f)
except FileNotFoundError:
    DEFAULTS = {'vault': {'input_directory': None, 'output_directory': None,
                          'custom_code_directory': None, 'log_directory': None,
                          'run_mode': None},
                'codebox': {'remote_input_directory': None, 'remote_output_directory': None,
                            'remote_custom_code_directory': None, 'remote_log_directory': None,
                            'remote_vault_log_directory': None, 'vault_log_directory': None,
                            'input_directory': None, 'output_directory': None,
                            'custom_code_directory': None, 'log_directory': None,
                            'run_mode': None}}

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
        '--remote-repo-directory',
        default= DEFAULTS['codebox']['remote_repo_directory'],
        metavar='remote_repo_directory',
        help='Directory where remote custom code is stored.')
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
        '--remote-vault-log-directory',
        default= DEFAULTS['codebox']['remote_vault_log_directory'],
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
        '--repo-directory',
        default= DEFAULTS['codebox']['repo_directory'],
        metavar='repo_directory',
        help='Repo directory.')
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

def get_repo_packages(repo_bucket_name=None, environment='GCP'):
    if environment == 'GCP':
        from google.cloud import storage
        client = storage.Client()
        return [blob.name for blob in client.list_blobs(repo_bucket_name, prefix=None)]
    else:
        raise NotImplementedError

def get_required_packages(source_url=None, environment='GCP'):
    if environment == 'GCP':
        with TemporaryDirectory() as tmpdir:
            sync_directory(source_directory=source_url, destination_directory=tmpdir)
            req_file = [f for f in os.listdir(tmpdir) if os.path.isfile(os.path.join(tmpdir, f)) and f == 'requirements.txt']
            if len(req_file) > 1:
                raise ValueError("Found more than one requirement file!")
            with open(os.path.join(tmpdir, req_file[0]), 'r') as f:
                requirements = f.readlines()
        return requirements
    else:
        raise NotImplementedError

def get_missing_packages(required_packages=None, available_packages=None):

    missing_packages = []
    for req in required_packages:
        found = False
        req_search = req.replace("==", "-").replace("\n", "")
        for avail in available_packages:
            if avail.startswith(req_search) \
               or avail.lower().startswith(req_search.lower()) \
               or avail.lower().replace("_", "-").startswith(req_search):
                found = True
                break
        if not found:
            missing_packages.append(req)
    return missing_packages

def sync_directory(source_directory=None, destination_directory=None, recursive=False, environment='GCP'):
    if environment == 'GCP':
        if recursive:
            get_input_dir_cmd = f"gsutil -m rsync -r {source_directory} {destination_directory}"
        else:
            get_input_dir_cmd = f"gsutil -m rsync {source_directory} {destination_directory}"
        try:
            status = run(get_input_dir_cmd, shell=True, capture_output=True, check=True)
        except CalledProcessError as e:
            return e
    else:
        raise NotImplementedError
    return status