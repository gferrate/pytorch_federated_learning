import torch
import torch.optim as optim
from model import Model, get_loaders
import torch.nn.functional as F
from torch.optim.lr_scheduler import StepLR

lr = 1.0
log_interval = 10
dry_run = False
gamma = 0.7
epochs = 5

class Client:

    def __init__(self, port, num_clients, use_cuda=True):
        self.port = port
        self.client_id = 'client_{}'.format(self.port)
        self.num_clients = num_clients
        use_cuda = use_cuda and torch.cuda.is_available()
        if not use_cuda:
            print('\nWARNING: Running without GPU acceleration\n')
        self.use_cuda = use_cuda
        self.init()

    def init(self):
        torch.manual_seed(1)
        self.device = torch.device('cuda' if self.use_cuda else 'cpu')
        self.train_loader, self.test_loader = get_loaders(self.num_clients,
                                                          self.use_cuda)
        self.model = Model().to(self.device)
        self.optimizer = optim.Adadelta(self.model.parameters(), lr=lr)

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
                print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                    epoch, batch_idx * len(data), len(self.train_loader.dataset),
                    100. * batch_idx / len(self.train_loader), loss.item()))
                if dry_run:
                    break

    def train(self):
        scheduler = StepLR(self.optimizer, step_size=1, gamma=gamma)
        for epoch in range(1, epochs + 1):
            self.train_epoch(epoch)
            self.test()
            scheduler.step()

    def update_model(self, path):
        self.model.load_state_dict(torch.load(path))
        print('Client model updated')

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

    def get_model_filename(self):
        return 'model_{}.tar'.format(self.client_id)

    def save_model(self):
        filename = self.get_model_filename()
        print('Saving model to {}'.format(filename))
        torch.save(self.model.state_dict(), filename)
        # TODO: Try with named_parameters instead of state dict since it is lighter

