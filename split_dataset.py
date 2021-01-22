from shared import dataset_tools
import logging, sys
import argparse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        #logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)

def split_dataset(num_clients, split_type):
    mf = 'data/classification'
    fn = '{}/metadata.mat'.format(mf)
    dataset_tools.split_dataset(fn, split_type, num_clients)

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Split dataset')
    parser.add_argument('-n', '--num_clients', type=int, required=True,
                        help='Num clients. Example: 5')
    parser.add_argument('-s', '--split-type', type=str, required=True,
                        help=('Metadata split type. '
                              'Example: no_split, iid, non-iid-a'))
    args = parser.parse_args()
    split_dataset(args.num_clients, args.split_type)
