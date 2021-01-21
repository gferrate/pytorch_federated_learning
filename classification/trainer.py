import sys; sys.path.insert(0, '.')
import os, shutil, time, random
import torch
import numpy as np
import torch.backends.cudnn as cudnn
import logging

from classification.object_cluster_dataset import ObjectClusterDataset


epochs = 1  # Before 30
batch_size = 10
workers = 0

doFilter = True
test = False
large = False


class Trainer(object):

    def __init__(self, port, n_frames, client_id, num_clients, data_split_type):
        # Common init in both childs
        self.port = port
        self.n_frames = n_frames  # Optimal frames == 7
        self.client_id = client_id
        self.num_clients = num_clients
        self.data_split_type = data_split_type
        self.logger = 'logs/{}.log'.format(self.client_id)
        self.init_logger()
        self.metaFile = self.get_meta_file()

    def get_meta_file(self):
        mf = 'data/classification'
        if self.data_split_type == 'iid':
            return '{}/metadata_{}_clients_iid.mat'.format(mf,
                                                           self.num_clients)
        elif self.data_split_type == 'non-iid-a':
            return '{}/metadata_{}_clients_non_iid_a.mat'.format(
                mf, self.num_clients)
        elif self.data_split_type == 'no_split':
            return '{}/metadata.mat'.format(mf)
        else:
            raise Exception('Data split type "{}" not implemented'.format(
                self.data_split_type))

    def init_logger(self):
        logging.basicConfig(
            format='%(asctime)s %(message)s',
            filename=self.logger,
            level=logging.INFO
        )

    def init(self):
        # Init model
        self.val_loader = self.loadDatasets('test', False, False)
        self.initModel()

    def loadDatasets(self,
                     split='train', shuffle=True, useClusterSampling=False):
        return torch.utils.data.DataLoader(
            ObjectClusterDataset(
                split=split, doAugment=(split == 'train'),
                doFilter=doFilter, sequenceLength=self.n_frames,
                metaFile=self.metaFile, useClusters=useClusterSampling
            ),
            batch_size=batch_size,
            shuffle=shuffle,
            num_workers=workers
        )

    def train(self):
        logging.info('[Trainer - {}] Starting...'.format(self.client_id))
        self.counters = {'train': 0, 'test': 0}
        if test:
            self.save_model()
            #self.test()
            return

        # The self.train_split  will 'train_<client_num>' if a client
        # and 'train' if a secure aggregator
        logging.info('[Trainer] Doing split: {}'.format(self.train_split))
        train_loader = self.loadDatasets(self.train_split, True, False)

        for epoch in range(epochs):
            logging.info('Epoch %d/%d....' % (epoch, epochs))
            self.model.updateLearningRate(epoch)
            self.step(train_loader, self.model.epoch, isTrain=True)
        logging.info('DONE')

    def test(self):
        return self.doSink()

    def doSink(self):
        res = {}

        logging.info('Running test...')
        res['test-top1'], res['test-top3'] = self.step(
            self.val_loader, self.model.epoch,
            isTrain=False, sinkName='test')

        logging.info('Running test with clustering...')
        val_loader_cluster = self.loadDatasets('test', False, True)
        res['test_cluster-top1'], res['test_cluster-top3'] = self.step(
            val_loader_cluster, self.model.epoch,
            isTrain=False, sinkName='test_cluster')
        logging.info('--------------\nResults:')
        for k, v in res.items():
            logging.info('\t%s: %.3f %%' % (k, v))
        return res

    def update_model_from_file(self, path):
        state = torch.load(path)
        assert state is not None, \
            'Warning: Could not read checkpoint {}'.format(path)
        logging.info('[Trainer] Loading checkpoint {}...'.format(path))
        self.update_model(state)
        logging.info('[Trainer] Client model updated')

    def update_model(self, state):
        self.model.importState(state)

    def initModel(self):
        cudnn.benchmark = True

        if large:
            # TODO: Not implemented
            # for filter viz only
            from classification.classification_model_large_viz import \
                ClassificationModelLargeViz as Model
        else:
            # the main model
            from classification.classification_model import \
                ClassificationModel as Model

        self.model = Model(
            numClasses=len(self.val_loader.dataset.meta['objects']),
            sequenceLength=self.n_frames)
        self.model.epoch = 0
        self.model.bestPrec = -1e20

    def step(self, data_loader, epoch, isTrain=True, sinkName=None):
        if isTrain:
            data_loader.dataset.refresh()

        batch_time = AverageMeter()
        data_time = AverageMeter()
        losses = AverageMeter()
        top1 = AverageMeter()
        top3 = AverageMeter()

        results = {
            'batch': [],
            'rec': [],
            'frame': [],
        }
        catRes = lambda res, key: res[key].cpu().numpy() \
            if not key in results \
            else np.concatenate((results[key], res[key].cpu().numpy()), axis=0)

        end = time.time()
        for i, (inputs) in enumerate(data_loader):
            data_time.update(time.time() - end)

            inputsDict = {
                'image': inputs[1],
                'pressure': inputs[2],
                'objectId': inputs[3],
            }

            res, loss = self.model.step(inputsDict,
                                        isTrain,
                                        params={'debug': True})

            losses.update(loss['Loss'], inputs[0].size(0))
            top1.update(loss['Top1'], inputs[0].size(0))
            top3.update(loss['Top3'], inputs[0].size(0))

            # measure elapsed time
            batch_time.update(time.time() - end)
            end = time.time()
            if isTrain:
                self.counters['train'] = self.counters['train'] + 1

            logging.info(
                '{phase}: [{0}][{1}/{2}]\t'
                'Time {batch_time.val:.3f} ({batch_time.avg:.3f})\t'
                'Data {data_time.val:.3f} ({data_time.avg:.3f})\t'
                'Loss {loss.val:.4f} ({loss.avg:.4f})\t'
                'Prec@1 {top1.val:.3f} ({top1.avg:.3f})\t'
                'Prec@3 {top3.val:.3f} ({top3.avg:.3f})'
                .format(
                    epoch, i, len(data_loader), batch_time=batch_time,
                    data_time=data_time, loss=losses, top1=top1, top3=top3,
                    phase=('Train' if isTrain else 'Test')
                )
              )

        try:
            self.counters['test'] = self.counters['test'] + 1
        except AttributeError:
            # The secure aggregator only tests without training
            self.counters = {'train': 0, 'test': 1}

        return top1.avg, top3.avg

    def get_checkpoint_path(self):
        return os.path.join(self.snapshotDir, 'checkpoint.tar')

    def get_best_model_path(self):
        return os.path.join(self.snapshotDir, 'model_best.tar')

    @staticmethod
    def file_exists(fn):
        return os.path.isfile(fn)

    def save_model(self):
        state = self.model.exportState()
        if not os.path.isdir(self.snapshotDir):
            os.makedirs(self.snapshotDir, 0o777)
        filename = self.get_best_model_path()
        logging.info('Writing checkpoint to {}...'.format(filename))
        torch.save(state, filename)
        logging.info('\t...Done.')

    #@staticmethod
    #def make():
    #    random.seed(454878 + time.time() + os.getpid())
    #    np.random.seed(int(12683 + time.time() + os.getpid()))
    #    torch.manual_seed(23142 + time.time() + os.getpid())

    #    ex = Trainer()
    #    ex.run()


class SecAggTrainer(Trainer):
    def __init__(self,
                 port,
                 n_frames,
                 num_clients,
                 data_split_type):
        client_id = 'sec_agg'
        super().__init__(port,
                         n_frames,
                         client_id,
                         num_clients,
                         data_split_type)
        self.type = 'secure_aggregator'
        self.snapshotDir = 'secure_aggregator/persistent_storage'
        self.train_split = 'train' # Shouldn't be needed since it doesn't train
        self.init()

    def get_checkpoint_path(self):
        return os.path.join(self.snapshotDir, 'checkpoint.tar')

    def get_best_model_path(self):
        return os.path.join(self.snapshotDir, 'agg_model.tar')


class ClientTrainer(Trainer):
    def __init__(self,
                 port,
                 n_frames,
                 client_number,
                 num_clients,
                 data_split_type,
                 client_id):
        super().__init__(port,
                         n_frames,
                         client_id,
                         num_clients,
                         data_split_type)
        self.type = 'client'
        self.snapshotDir = 'client/snapshots_{}'.format(self.port)
        # Dont do it with the client_id to avoid tons of folders generated
        self.train_split = self.get_train_split()

        # Split dataset if file does not exist
        if self.data_split_type in ('iid', 'non-iid-a', 'non-iid-b'):
            from shared import dataset_tools
            # TODO: Reimplement this with a lock file.
            # If multiple clients are spawned this can be a problem.
            if not self.file_exists(self.metaFile):
                logging.info('[Client Trainer] File {} '
                             'does not exist.'.format(self.metaFile))
                logging.warning(
                    '[Client Trainer] Will attempt to split dataset from '
                    "{}/metadata.mat. THIS WON'T WORK if running in multiple "
                    'servers. If so, please split the file manually '
                    '(using shared/dataset_utils.py) and copy it into '
                    'the different servers manually.'.format(mf))
                fn = '{}/metadata.mat'.format(mf)
                dataset_tools.split_dataset(fn, data_split_type, num_clients)
            else:
                logging.info('File {} already exists. '
                             'Not creating.'.format(self.metaFile))
        self.init()

    def get_train_split(self):
        if self.data_split_type == 'iid':
            return 'train_{}'.format(self.client_number)
        elif self.data_split_type == 'non-iid-a':
            return 'train_{}'.format(self.client_number)
        elif self.data_split_type == 'no_split':
            return 'train'


class AverageMeter(object):
    """Computes and stores the average and current value"""

    def __init__(self):
        self.reset()

    def reset(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0

    def update(self, val, n=1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count

