import logging
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
file_handler = logging.FileHandler(f'logs/example.log')
ch.setLevel(logging.DEBUG)
file_handler.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)
file_handler.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)
logger.addHandler(file_handler)
