import torch
import numpy as np

from classification.touch_dataset import TouchDataset, MetadataLoader


class ObjectDataset(TouchDataset):
    def __init__(self, split='train', doAugment=False, doFilter=True,
                 doBalance=True, sequenceLength=5, objectId=None,
                 notObjectId=None, metaFile='', inputSize=32):

        self.metaFile = metaFile
        self.doFilter = doFilter
        self.doBalance = doBalance
        self.objectId = objectId
        self.notObjectId = notObjectId

        TouchDataset.initialize(self, split=split, doAugment=doAugment,
                                sequenceLength=sequenceLength,
                                inputSize=inputSize)

    @staticmethod
    def getName():
        return 'ObjectDataset'

    def loadDataset(self):
        meta = MetadataLoader.getInstance().getMeta(self.metaFile)
        valid = np.ones((len(meta['frame']),), np.bool)
        if self.objectId is not None:
            isCorrectObject = meta['objectId'].flatten() == self.objectId
            valid = np.logical_and(valid, isCorrectObject)
        if self.notObjectId is not None:
            isCorrectObject = meta['objectId'].flatten() == self.notObjectId
            valid = np.logical_and(valid, np.logical_not(isCorrectObject))
        if self.doFilter:
            hasValidLabel = meta['hasValidLabel'].flatten().astype(np.bool)
            valid = np.logical_and(valid, hasValidLabel)
        validN = valid  # for samples 1+

        if self.doBalance:
            isBalanced = meta['isBalanced'].flatten().astype(np.bool)
            valid0 = np.logical_and(validN, isBalanced)  # for sample 0
        else:
            valid0 = validN

        pressure = self.transformPressure(meta['pressure'])
        return meta, valid0, validN, pressure

    def __getitem__(self, indexExt):
        row, image, pressure = self.getItemBase(indexExt)
        index = row[0]
        objectId = self.meta['objectId'][index]

        # to tensor
        objectId = torch.LongTensor([int(objectId)])

        return row, image, pressure, objectId

