from argparse import ArgumentParser
from subprocess import run, CalledProcessError
from tempfile import TemporaryDirectory
import os


def get_codebox_args():
    """Argument parser.
    Returns:
      Dictionary of arguments.
    """
    parser = ArgumentParser()
    parser.add_argument(
        '--config-file-uri',
        default= './config/process_config.yaml',
        help='Absolute path to configuration file.')

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

def get_custom_module_name(code_directory=None):
    dirs = []
    for dir in os.listdir(code_directory):
        if os.path.isdir(os.path.join(code_directory, dir)) and not dir.endswith('sql'): # ignore sql code directory
            dirs.append(os.path.join(code_directory, dir))
    if len(dirs) > 1 or len(dirs) == 0:
        raise ValueError(f"Should find a single directory in path. Found {len(dirs)}")
    return dirs[0].split("/")[-1], dirs[0]

def sync_directory(source_directory=None, destination_directory=None, recursive=False, environment='GCP'):
    if environment == 'GCP':
        if recursive:
            get_input_dir_cmd = f"gsutil -m rsync -r {source_directory} {destination_directory}"
        else:
            get_input_dir_cmd = f"gsutil -m rsync {source_directory} {destination_directory}"
        try:
            status = run(get_input_dir_cmd, shell=True, capture_output=False, check=True)
        except CalledProcessError as e:
            return e
    else:
        raise NotImplementedError
    return status


def copy_file(source_file=None, destination_file=None, environment='GCP'):
    if environment == 'GCP':
        get_file_cmd = f"gsutil cp {source_file} {destination_file}"
        try:
            status = run(get_file_cmd, shell=True, capture_output=True, check=True)
        except CalledProcessError as e:
            return e
    else:
        raise NotImplementedError
    return status