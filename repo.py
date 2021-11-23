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
        # TODO: pip does not seem to find all versions (for example scikit-learn 1.0.0)
        # pip does not find a version if it's not compatible with the python version you are currently using
        # Moreover, pip will download the appropriate wheel for the python version and platform you are running on.
        # To install pip in a specific python environment:
        # 1. curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
        # 2. python3.7 get-pip.py
        pip_cmd = f"python3.7 -m pip download --only-binary :all: --no-cache-dir --destination-directory {missing_packages_dir} -r {filename}"
        run(pip_cmd, shell=True)

        # Store packages in remote repo
        os.remove(filename)
        remote_repo = 'gs://' + args_dict['remote_repo_bucket']
        sync_directory(source_directory=missing_packages_dir, destination_directory=remote_repo)