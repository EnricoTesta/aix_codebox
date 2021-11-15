from argparse import ArgumentParser
from tempfile import TemporaryDirectory
from logging import Logger
from utils import sync_directory, get_repo_packages, get_required_packages, get_missing_packages
from subprocess import run
import os

logger = Logger("Repo_Logger")

parser = ArgumentParser()
parser.add_argument(
    '--remote-repo-bucket',
    default= 'pypi_repo',
    metavar='remote_repo_bucket',
    help='Bucket where remote packages are stored.')
parser.add_argument(
    '--remote-requirement-directory',
    default= 'gs://mock_custom_code',
    metavar='remote_requirement_directory',
    help='Directory containing remote requirement directory.')
parser.add_argument(
    '--remote-log-directory',
    default= None,
    metavar='remote_log_directory',
    help='Directory containing execution logs.')

args_dict = vars(parser.parse_args())

logger.info("Parsed arguments:")
logger.info(f"Remote repo bucket:{args_dict['remote_repo_bucket']}")
logger.info(f"Remote log directory:{args_dict['remote_log_directory']}")

logger.info("Fetching requirement files...")
required_packages = get_required_packages(args_dict['remote_requirement_directory'])

logger.info("Fetching available packages in repo...")
available_packages = get_repo_packages(args_dict['remote_repo_bucket'])


missing_packages = get_missing_packages(required_packages, available_packages)

if missing_packages:
    with TemporaryDirectory() as missing_packages_dir:

        filename = os.path.join(missing_packages_dir, 'requirements.txt')
        with open(filename, 'w') as f:
            for package in missing_packages:
                f.write(package)

        pip_cmd = f"python -m pip download --destination-directory {missing_packages_dir} -r {filename}"
        run(pip_cmd, shell=True, capture_output=True)

        # Store packages in remote repo
        os.remove(filename)
        remote_repo = 'gs://' + args_dict['remote_repo_bucket']
        sync_directory(source_directory=missing_packages_dir, destination_directory=remote_repo)