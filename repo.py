from argparse import ArgumentParser
from tempfile import TemporaryDirectory
from logging import Logger
from utils import sync_directory, get_required_packages
from subprocess import run
import os

logger = Logger("Repo_Logger")

parser = ArgumentParser()
parser.add_argument(
    '--remote-repo-bucket',
    default='aix_pypi_repo',
    metavar='remote_repo_bucket',
    help='Bucket where remote packages are stored.')
parser.add_argument(
    '--remote-requirement-directory',
    default='gs://mock_custom_code',
    metavar='remote_requirement_directory',
    help='Directory containing remote requirement directory.')
parser.add_argument(
    '--remote-log-directory',
    default='gs://aix-data-stocks-bucket/repo_logs',
    metavar='remote_log_directory',
    help='Directory containing execution logs.')

args_dict = vars(parser.parse_args())

logger.info("Parsed arguments:")
logger.info(f"Remote repo bucket:{args_dict['remote_repo_bucket']}")
logger.info(f"Remote log directory:{args_dict['remote_log_directory']}")

logger.info("Fetching requirement files...")
required_packages = get_required_packages(args_dict['remote_requirement_directory'])

with TemporaryDirectory() as missing_packages_dir:

    filename = os.path.join(missing_packages_dir, 'requirements.txt')
    with open(filename, 'w') as f:
        for package in required_packages:
            f.write(package)
    # To install pip in a specific python environment:
    # 1. curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    # 2. python3.7 get-pip.py
    pip_cmd = f"python3.8 -m pip download --only-binary :all: --no-cache-dir --destination-directory {missing_packages_dir} -r {filename}"
    run(pip_cmd, shell=True)

    # Store packages in remote repo
    os.remove(filename)
    remote_repo = 'gs://' + args_dict['remote_repo_bucket']
    sync_directory(source_directory=missing_packages_dir, destination_directory=remote_repo)
