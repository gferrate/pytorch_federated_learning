from shared import dataset_tools
import logging, sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        #logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)


num_clients = 9
data_split_type = 'non-iid-a'
mf = 'data/classification'
fn = '{}/metadata.mat'.format(mf)
dataset_tools.split_dataset(fn, data_split_type, num_clients)
