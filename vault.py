from utils import get_vault_args
from importlib import import_module
from logging import getLogger, basicConfig, DEBUG
import os

args_dict = get_vault_args()

basicConfig(filename=os.path.join(args_dict['log_directory'], 'logs.log'),
            filemode='w',
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=DEBUG)
logger = getLogger('vault_logger')
logger.info("Logging started...")

logger.info("Importing custom module...")
custom_module = import_module(f"{args_dict['custom_code_directory'].split('/')[-1]}.main") # expect to import process & transform

try:
    logger.info("Fetching function handler...")
    fn_callable = getattr(custom_module, args_dict['run_mode'])
except AttributeError:
    logger.error(f"Function {args_dict['run_mode']} undefined in custom module.")
    raise AttributeError(f"Function {args_dict['run_mode']} undefined in custom module.")

try:
    logger.info(f"Executing function {args_dict['run_mode']}")
    fn_callable(input_directory=args_dict['input_directory'], output_directory=args_dict['output_directory'])
except Exception as e:
    pass

logger.info("Process Complete.")