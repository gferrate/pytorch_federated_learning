import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import datasets, transforms

batch_size = 32

class Model(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 32, 3, 1)
        self.conv2 = nn.Conv2d(32, 64, 3, 1)
        self.dropout1 = nn.Dropout2d(0.25)
        self.dropout2 = nn.Dropout2d(0.5)
        self.fc1 = nn.Linear(9216, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = self.conv1(x)
        x = F.relu(x)
        x = self.conv2(x)
        x = F.relu(x)
        x = F.max_pool2d(x, 2)
        x = self.dropout1(x)
        x = torch.flatten(x, 1)
        x = self.fc1(x)
        x = F.relu(x)
        x = self.dropout2(x)
        x = self.fc2(x)
        output = F.log_softmax(x, dim=1)
        return output


def get_datasets():
    print('Downloading datasets...')
    transform = transforms.Compose([
        transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))
    ])
    train_dataset = datasets.MNIST('../data', train=True,
                                   download=True, transform=transform)
    test_dataset = datasets.MNIST('../data', train=False,
                                  download=True, transform=transform)
    return train_dataset, test_dataset


def split_dataset(train_dataset, num_clients):
    # Split the dataset into the number of clients.
    # This will have to be redone because the data may not be fully
    # completed in all the clients
    print('Splitting dataset into {} clients...'.format(num_clients))
    len_dataset = len(train_dataset)
    num_elms_per_client = int(len_dataset / num_clients)
    train_dataset, _ = torch.utils.data.random_split(
        train_dataset, [num_elms_per_client, len_dataset - num_elms_per_client]
    )
    print('Done')
    return train_dataset


def get_loaders(num_clients, use_cuda):
    train_dataset, test_dataset = get_datasets()
    train_dataset, split_dataset(train_dataset, num_clients)
    kwargs = {'batch_size': batch_size}
    if use_cuda:
        kwargs.update({'num_workers': 1, 'pin_memory': True, 'shuffle': True})

    train_loader = torch.utils.data.DataLoader(train_dataset,**kwargs)
    test_loader = torch.utils.data.DataLoader(test_dataset, **kwargs)
    print('Got loaders')
    return train_loader, test_loader

