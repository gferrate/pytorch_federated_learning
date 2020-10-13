import sys; sys.path.insert(0, '.')
import os, shutil, time, random
import torch
import numpy as np
import torch.backends.cudnn as cudnn

from classification.object_cluster_dataset import ObjectClusterDataset


epochs = 1  # Before 30
nFrames = 1
batch_size = 10
workers = 0

#metaFile = 'data/classification/out.mat'
doFilter = True
test = False
large = False
reset = False


class Trainer(object):
    def __init__(self):
        # __init__ overrided in child objects
        pass

    def init(self):
        # Init model
        self.val_loader = self.loadDatasets('test', False, False)
        self.initModel()

    #def splitDataset(self, dataset, splits=None):
    #    # TODO: Redo this part because this doesn't ensure that all
    #    # data will be trained between all clients
    #    splits = splits or self.num_clients
    #    print('Splitting dataset into {} parts'.format(splits))
    #    ds_l = len(dataset)
    #    lengths = [int(1/splits * ds_l) for _ in range(splits)]
    #    remaining = ds_l - sum(lengths)
    #    lengths[0] += remaining
    #    tm = torch.utils.data.random_split(dataset, lengths)
    #    return tm[0]

    def loadDatasets(self,
                     split='train', shuffle=True, useClusterSampling=False):
        return torch.utils.data.DataLoader(
            ObjectClusterDataset(
                split=split, doAugment=(split == 'train'),
                doFilter=doFilter, sequenceLength=nFrames,
                metaFile=self.metaFile, useClusters=useClusterSampling
            ),
            batch_size=batch_size,
            shuffle=shuffle,
            num_workers=workers
        )

    def train(self):
        print('[Trainer - {}] Starting...'.format(self.client_id))
        self.counters = {'train': 0, 'test': 0}
        if test:
            self.saveCheckpoint(self.model.exportState(), True)
            self.doSink()
            return

        # The self.train_split  will 'train_<client_num>' if a client
        # and 'train' if a secure aggregator
        train_loader = self.loadDatasets(self.train_split , True, False)

        for epoch in range(epochs):
            print('Epoch %d/%d....' % (epoch, epochs))
            self.model.updateLearningRate(epoch)

            self.step(train_loader, self.model.epoch, isTrain=True)
            prec1, _ = self.step(self.val_loader, self.model.epoch,
                                 isTrain=False, sinkName=None)

            # remember best prec@1 and save checkpoint
            is_best = prec1 > self.model.bestPrec
            if is_best:
                self.model.bestPrec = prec1
            self.model.epoch = epoch + 1
            if self.snapshotDir is not None:
                self.saveCheckpoint(self.model.exportState(), is_best)

        # Finally: We want to test it from the app to get the returned results
        #if self.type == 'secure_aggregator':
        #    # Only test if it is a secure aggregator
        #    self.test()
        print('DONE')

    def test(self):
        self.doSink()

    def doSink(self):
        res = {}

        print('Running test...')
        res['test-top1'], res['test-top3'] = self.step(
            self.val_loader, self.model.epoch,
            isTrain=False, sinkName='test')

        print('Running test with clustering...')
        val_loader_cluster = self.loadDatasets('test', False, True)
        res['test_cluster-top1'], res['test_cluster-top3'] = self.step(
            val_loader_cluster, self.model.epoch,
            isTrain=False, sinkName='test_cluster')
        print('--------------\nResults:')
        for k, v in res.items():
            print('\t%s: %.3f %%' % (k, v))
        return res

    def update_model_from_file(self, path):
        state = torch.load(path)
        assert state is not None, \
            'Warning: Could not read checkpoint {}'.format(path)
        print('Loading checkpoint {}...'.format(path))
        self.update_model(state)
        print('Client model updated')

    def update_model(self, state):
        self.model.importState(state)

    def initModel(self):
        cudnn.benchmark = True

        if large:
            # for filter viz only
            from classification.classification_model_large_viz import \
                ClassificationModelLargeViz as Model
            #initShapshot = 'large_viz'
        else:
            # the main model
            from classification.classification_model import \
                ClassificationModel as Model
            #initShapshot = 'default'

        #initShapshot = os.path.join('snapshots',
        #                            'classification',
        #                            '%s_%dx' % (initShapshot, nFrames),
        #                            'checkpoint.pth.tar')

        self.model = Model(
            numClasses=len(self.val_loader.dataset.meta['objects']),
            sequenceLength=nFrames)
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

            print(
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

        self.counters['test'] += 1

        return top1.avg, top3.avg

    def get_checkpoint_path(self):
        return os.path.join(self.snapshotDir, 'checkpoint.tar')

    def get_best_model_path(self):
        return os.path.join(self.snapshotDir, 'model_best.tar')

    def saveCheckpoint(self, state, is_best):
        if not os.path.isdir(self.snapshotDir):
            os.makedirs(self.snapshotDir, 0o777)
        #chckFile = os.path.join(self.snapshotDir, 'checkpoint.pth.tar')
        chckFile = self.get_checkpoint_path()
        print('Writing checkpoint to %s...' % chckFile)
        torch.save(state, chckFile)
        if is_best:
            #bestFile = os.path.join(self.snapshotDir, 'model_best.pth.tar')
            bestFile = self.get_best_model_path()
            print('Copying best checkpoint file to {}'.format(bestFile))
            shutil.copyfile(chckFile, bestFile)
        print('\t...Done.')

    def save_model(self):
        self.saveCheckpoint(self.model.exportState(), True)

    #@staticmethod
    #def make():
    #    random.seed(454878 + time.time() + os.getpid())
    #    np.random.seed(int(12683 + time.time() + os.getpid()))
    #    torch.manual_seed(23142 + time.time() + os.getpid())

    #    ex = Trainer()
    #    ex.run()


class SecAggTrainer(Trainer):
    def __init__(self, client_id):
        self.snapshotDir = 'secure_aggregator/persistent_storage'
        self.client_id = client_id
        self.num_clients = None
        self.client_number = None
        self.type = 'secure_aggregator'
        self.train_split = 'train'
        self.metaFile = 'data/classification/metadata.mat'
        self.init()
        super(Trainer, self).__init__()

    def get_checkpoint_path(self):
        return os.path.join(self.snapshotDir, 'checkpoint.tar')

    def get_best_model_path(self):
        return os.path.join(self.snapshotDir, 'agg_model.tar')


class ClientTrainer(Trainer):
    def __init__(self, client_number, client_id, num_clients):
        self.snapshotDir = 'client/snapshots_{}'.format(client_id)
        self.client_id = client_id
        self.client_number = client_number
        self.num_clients = num_clients
        self.train_split = 'train_{}'.format(client_number)
        self.type = 'client'
        self.metaFile = 'data/classification/metadata_{}_clients.mat'.format(num_clients)
        self.init()
        super(Trainer, self).__init__()


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

