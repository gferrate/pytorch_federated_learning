import numpy as np
import os, shutil
import scipy.io as sio


def loadMetadata(filename, silent=False):
    '''
    Loads matlab mat file and formats it for simple use.
    '''
    try:
        # http://stackoverflow.com/questions/6273634/access-array-contents-from-a-mat-file-loaded-using-scipy-io-loadmat-python
        if not silent:
            print('\tReading metadata from %s...' % filename)
        #metadata = sio.loadmat(filename, squeeze_me=True, struct_as_record=False)
        metadata = MatReader().loadmat(filename)
    except:
        print('\tFailed to read the meta file "%s"!' % filename)
        return
    return metadata


def preparePath(path, clear = False):
    if not os.path.isdir(path):
        os.makedirs(path, 0o777)
    if clear:
        files = os.listdir(path)
        for f in files:
            fPath = os.path.join(path, f)
            if os.path.isdir(fPath):
                shutil.rmtree(fPath)
            else:
                os.remove(fPath)
    return path


class MatReader(object):
    '''
    Loads matlab mat file and formats it for simple use.
    '''

    def __init__(self, flatten1D=True):
        self.flatten1D = flatten1D

    def loadmat(self, filename):
        meta = sio.loadmat(filename, struct_as_record=False)

        meta.pop('__header__', None)
        meta.pop('__version__', None)
        meta.pop('__globals__', None)

        meta = self._squeezeItem(meta)
        return meta

    def _squeezeItem(self, item):
        if isinstance(item, np.ndarray):
            if item.dtype == np.object:
                if item.size == 1:
                    item = item[0,0]
                else:
                    item = item.squeeze()
            elif item.dtype.type is np.str_:
                item = str(item.squeeze())
            elif self.flatten1D and len(item.shape) == 2 and (item.shape[0] == 1 or item.shape[1] == 1):
                item = item.flatten()

            if isinstance(item, np.ndarray) and item.dtype == np.object:
                #for v in np.nditer(item, flags=['refs_ok'], op_flags=['readwrite']):
                #    v[...] = self._squeezeItem(v)
                it = np.nditer(item,
                               flags=['multi_index','refs_ok'],
                               op_flags=['readwrite'])
                while not it.finished:
                    item[it.multi_index] = self._squeezeItem(
                        item[it.multi_index])
                    it.iternext()

        if isinstance(item, dict):
            for k, v in item.items():
                item[k] = self._squeezeItem(v)
        elif isinstance(item, sio.matlab.mio5_params.mat_struct):
            for k in item._fieldnames:
                v = getattr(item, k)
                setattr(item, k, self._squeezeItem(v))

        return item


def split_dataset(filename, split_type, num_clients):
    # more info here: https://arxiv.org/pdf/1806.00582.pdf (section 2.1)
    if split_type == 'iid':
        # Split the dataset into <num_clients> uniformally distributed
        metadata = MatReader().loadmat(filename)

        train_split_id = np.argwhere(metadata['splits'] == 'train').flatten()[0]
        test_split_id = np.argwhere(metadata['splits'] == 'test').flatten()[0]

        train_positions = np.argwhere(metadata['splitId']==train_split_id).flatten()
        test_positions = np.argwhere(metadata['splitId']==test_split_id).flatten()

        # Create the new positions for the new splits
        n_train = len(train_positions)
        times = int(np.ceil(n_train/num_clients))
        new_train_split_ids = np.repeat(np.arange(num_clients), times)
        # Extend with remaining ones
        diff = len(new_train_split_ids) - n_train
        new_train_split_ids = new_train_split_ids[:-diff]
        np.random.shuffle(new_train_split_ids)

        new_splits = np.array(
            ['train_{}'.format(i) for i in range(num_clients)] + ['test'],
            dtype=object
        )
        new_test_split_id = np.argwhere(new_splits == 'test').flatten()[0]

        new_split_ids = metadata['splitId'].copy()
        new_split_ids[new_split_ids == test_split_id] = new_test_split_id

        for i, train_pos in enumerate(train_positions):
            new_split_ids[train_pos] = new_train_split_ids[i]

        metadata['splits'] = new_splits
        metadata['splitId'] = new_split_ids
        unique, counts = np.unique(new_split_ids, return_counts=True)
        new_classes = dict(zip(new_splits, counts))
        print('Split into these new classes', new_classes)

        fout = 'data/classification/metadata_{}_clients.mat'.format(num_clients)
        sio.savemat(fout, metadata)
        print('Saved to:', fout)
    elif split_type == 'non-iid-a':
        metadata = MatReader().loadmat(filename)
        distinct_object_ids = np.unique(metadata['objectId'])
        n_objects = len(metadata['objects'])
        oc = np.floor(n_objects/n_objects)
        objects_per_client = [oc for oc in range(oc)]

        import pudb; pudb.set_trace()
        train_split_id = np.argwhere(metadata['splits'] == 'train').flatten()[0]
        test_split_id = np.argwhere(metadata['splits'] == 'test').flatten()[0]

        train_positions = np.argwhere(metadata['splitId']==train_split_id).flatten()
        test_positions = np.argwhere(metadata['splitId']==test_split_id).flatten()

        pass
    elif split_type == 'non-iid-b':
        pass
    else:
        raise Exception('Not implemented')

