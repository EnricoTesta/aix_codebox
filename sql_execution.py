from argparse import ArgumentParser
from yaml import safe_load
from google.cloud import bigquery
import os


parser = ArgumentParser()
parser.add_argument(
    '--project',
    metavar='project',
    default='aix-backend-prod',
    help='True data project name')
parser.add_argument(
    '--source-dataset',
    metavar='source_dataset',
    default='sample_data',
    help='Source dataset name')
parser.add_argument(
    '--user-dataset',
    metavar='user_dataset',
    default='sFzcFP17ZqWnduyad7S3pUlpEBh2',
    help='User dataset name')
parser.add_argument(
    '--custom-code-path',
    metavar='custom_code_path',
    default='',
    help='Custom code path')

args_dict = vars(parser.parse_args())


try:
    with open(os.path.join(args_dict['custom_code_path'], "sql/dependencies.yaml"), 'r') as f:
        config = safe_load(f)
except FileNotFoundError:
    raise FileNotFoundError

client = bigquery.Client()

job_list = []
for k, v in config.items(): # seems to follow the order in which steps are written
    # Read SQL
    for item in v: # TODO: make multithread
        with open(os.path.join(args_dict['custom_code_path'], f"sql/{item}"), 'r') as f: # can use jinja --> difficult for user ?
            # TODO: replace with regex find/replace so user can write non-templatized query
            sql = ' '.join(f.readlines()).replace('PROJECT_ID', args_dict['project'])\
                .replace('SOURCE_DATASET_ID', args_dict['source_dataset'])\
                .replace('USER_DATASET_ID', args_dict['user_dataset'])

        # Send command to BQ
        job = client.query(query=sql)
        job.result()
        job_list.append(job.job_id)

print(job_list) # used as a return value for Airflow server