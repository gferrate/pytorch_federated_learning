import os
import torch
import torch.optim as optim
from model import Model, get_loaders
import torch.nn.functional as F
from torch.optim.lr_scheduler import StepLR

import numpy as np

#lr = 1.0
#log_interval = 10
#dry_run = True
#gamma = 0.7
#epochs = 1
#save_model = True


class SecAgg:

    def __init__(self, port, use_cuda=True):
        self.port = port
        self.client_id = 'client_{}'.format(self.port)
        use_cuda = use_cuda and torch.cuda.is_available()
        if not use_cuda:
            print('\nWARNING: Running without GPU acceleration\n')
        self.use_cuda = use_cuda
        self.init()

    def init(self):
        torch.manual_seed(1)
        self.device = torch.device("cuda" if self.use_cuda else "cpu")
        _, self.test_loader = get_loaders(self.use_cuda)
        self.model = Model().to(self.device)
        #self.optimizer = optim.Adadelta(self.model.parameters(), lr=lr)

    @staticmethod
    def load_models():
        print('Loading client models...')
        arr = []
        for root, dirs, files in os.walk("client_models/", topdown=False):
            for name in files:
                if name.endswith('.tar'):
                    fn = os.path.join(root, name)
                    data = torch.load(fn)
                    #arr.append(np.load(fn, allow_pickle=True))
                    arr.append(data)
        models = np.array(arr)
        print('Done')
        return models

    def average_weights(self, models):
        print('Averaging weights...')

        avg_model = models[0].copy()
        for k in avg_model:
            tmp = [w[k] for w in models]
            #avg_model[k] = np.average(tmp)
            avg_model[k] = sum(tmp)/len(tmp)

        ## FL average
        #fl_avg = np.average(weights, axis=0)
        #for i in fl_avg:
        #    print(i.shape)
        print('Done')
        return avg_model

    def aggregate_models(self):
        model_weights = self.load_models()
        avg_weights = self.average_weights(model_weights)
        self.model.load_state_dict(avg_weights)

    def test(self):
        self.model.eval()
        test_loss = 0
        correct = 0
        with torch.no_grad():
            for data, target in self.test_loader:
                data, target = data.to(self.device), target.to(self.device)
                output = self.model(data)
                # sum up batch loss
                test_loss += F.nll_loss(output, target, reduction='sum').item()
                # get the index of the max log-probability
                pred = output.argmax(dim=1, keepdim=True)
                correct += pred.eq(target.view_as(pred)).sum().item()

        test_loss /= len(self.test_loader.dataset)

        print('\nTest set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format(
            test_loss, correct, len(self.test_loader.dataset),
            100. * correct / len(self.test_loader.dataset)))

    def get_model_location(self):
        return 'agg_model_{}.tar'.format(self.client_id)

    def save_model(self):
        filename = self.get_model_location()
        print('Agg model saved to {}'.format(filename))
        torch.save(self.model.state_dict(), filename)

