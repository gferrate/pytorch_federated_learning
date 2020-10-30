import sys; sys.path.insert(0, '.')

from classification import trainer


class Client:

    def __init__(self, client_number, port, num_clients):
        self.client_number = client_number
        self.port = port
        self.client_id = 'client_{}'.format(self.port)
        self.num_clients = num_clients
        self.init_trainer()

    def init_trainer(self):
        self.trainer = trainer.ClientTrainer(self.client_number,
                                             self.client_id,
                                             self.num_clients)

    def train(self):
        return self.trainer.train()

    def test(self):
        return self.trainer.test()

    def save_model(self):
        self.trainer.save_model()

    def update_model(self, path):
        # TODO: This may not be necessary but it is to make sure that all
        # weights are set to start
        self.init_trainer()
        self.trainer.update_model_from_file(path)

    def get_model_filename(self):
        return self.trainer.get_model_path()

