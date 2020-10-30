import sys; sys.path.insert(0, '.')
import os
import torch
import logging
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms
from torch.optim.lr_scheduler import StepLR

from classification import mnist_model


batch_size = 32
lr = 1.0
log_interval = 10
dry_run = False
gamma = 0.7
epochs = 1


class Trainer(object):
    def __init__(self):
        # __init__ overrided in child classes
        pass

    def init_logger(self):
        logging.basicConfig(
            format='%(asctime)s %(message)s',
            filename=self.logger,
            level=logging.INFO
        )

    def init(self):
        if self.use_cuda and not self.cuda_available():
            logging.info('\nWARNING: Running without GPU acceleration\n')
            self.use_cuda = False
        self.device = torch.device('cuda' if self.use_cuda else 'cpu')
        self.init_dataset()
        self.init_model()

    def init_dataset(self):
        self.train_loader, self.test_loader = self.get_loaders()

    def init_model(self):
        self.model = mnist_model.Model().to(self.device)
        self.optimizer = optim.Adadelta(self.model.parameters(), lr=lr)

    def get_datasets(self):
        logging.info('Downloading datasets...')
        transform = transforms.Compose([
            transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))
        ])
        train_dataset = datasets.MNIST('data/classification', train=True,
                                       download=True, transform=transform)
        test_dataset = datasets.MNIST('data/classification', train=False,
                                      download=True, transform=transform)
        return train_dataset, test_dataset

    def get_loaders(self):
        train_dataset, test_dataset = self.get_datasets()
        # train_dataset, split_dataset(train_dataset, num_clients)
        kwargs = {'batch_size': batch_size}
        if self.use_cuda:
            kwargs.update({'num_workers': 1,
                           'pin_memory': True,
                           'shuffle': True})

        train_loader = torch.utils.data.DataLoader(train_dataset, **kwargs)
        test_loader = torch.utils.data.DataLoader(test_dataset, **kwargs)
        logging.info('Got loaders')
        return train_loader, test_loader

    def train_epoch(self, epoch):
        self.model.train()
        for batch_idx, (data, target) in enumerate(self.train_loader):
            data, target = data.to(self.device), target.to(self.device)
            self.optimizer.zero_grad()
            output = self.model(data)
            loss = F.nll_loss(output, target)
            loss.backward()
            self.optimizer.step()
            if batch_idx % log_interval == 0:
                logging.info(
                    'Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                        epoch, batch_idx * len(data),
                        len(self.train_loader.dataset),
                        100. * batch_idx / len(self.train_loader),
                        loss.item()
                    ))
                if dry_run:
                    break

    def train(self):
        scheduler = StepLR(self.optimizer, step_size=1, gamma=gamma)
        logging.info('[Trainer - {}] Starting...'.format(self.client_id))
        train_accs = []
        for epoch in range(1, epochs + 1):
            self.train_epoch(epoch)
            res = self.test()
            train_accs.append(res)
            scheduler.step()
        logging.info('\tDone')
        return train_accs

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

        accuracy = 100. * correct / len(self.test_loader.dataset)
        res = {'loss': test_loss, 'accuracy': accuracy}
        logging.info(
            '\nTest set: Average loss: {:.4f}, '\
            'Accuracy: {}/{} ({:.0f}%)\n'.format(
                test_loss,
                correct,
                len(self.test_loader.dataset),
                accuracy
            )
        )
        return res

    @staticmethod
    def cuda_available():
        return torch.cuda.is_available()

    def update_model(self, path):
        self.model.load_state_dict(torch.load(path))
        logging.info('Client model updated')

    def get_model_path(self):
        return os.path.join(self.model_dir, self.model_filename)

    def save_model(self):
        path = self.get_model_path()
        folder, _ = os.path.split(path)
        if not os.path.exists(folder):
            os.makedirs(path, 0o777)
        logging.info('Saving model to {}'.format(path))
        torch.save(self.model.state_dict(), path)


class SecAggTrainer(Trainer):
    def __init__(self, client_id):
        self.client_id = client_id
        self.logger = 'logs/{}.log'.format(self.client_id)
        self.init_logger()
        self.use_cuda = True
        self.type = 'secure_aggregator'
        self.model_dir = 'secure_aggregator/persistent_storage'
        self.client_number = None
        self.model_filename = 'agg_model.tar'
        self.init()


class ClientTrainer(Trainer):
    def __init__(self, client_number, client_id, num_clients):
        self.type = 'client'
        self.use_cuda = True
        self.model_dir = 'client/snapshots_{}'.format(client_id)
        self.model_filename = 'client_model.tar'
        self.client_id = client_id
        self.logger = 'logs/{}.log'.format(self.client_id)
        self.init_logger()
        self.type = 'client'
        self.snapshotDir = 'client/snapshots_{}'.format(self.client_id)
        self.client_number = client_number
        self.init()

