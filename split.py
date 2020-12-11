from shared import dataset_tools

num_clients = 9
data_split_type = 'iid'
mf = 'data/classification'

metaFile = '{}/metadata_{}_clients_iid.mat'.format(mf, num_clients)
fn = '{}/metadata.mat'.format(mf)
dataset_tools.split_dataset(fn, data_split_type, num_clients)
