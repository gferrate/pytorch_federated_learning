import sys; sys.path.insert(0, '.')

from classification import trainer


class Client:

    def __init__(self, port, n_frames,
                 client_number, num_clients, split_type, client_id):
        self.n_frames = n_frames
        self.split_type = split_type
        self.client_number = client_number
        self.port = port
        self.client_id = client_id
        self.num_clients = num_clients
        self.init_model()

    def init_model(self):
        try:
            del self.trainer
        except:
            pass
        self.trainer = trainer.ClientTrainer(self.port,
                                             self.n_frames,
                                             self.client_number,
                                             self.num_clients,
                                             self.split_type,
                                             self.client_id)

    def train(self):
        self.trainer.train()

    def test(self):
        return self.trainer.test()

    def save_model(self):
        self.trainer.save_model()

    def update_model(self, path):
        # TODO: init_model here may not be necessary but it is to
        # make sure that all weights are set to start
        # self.init_model()
        self.trainer.update_model_from_file(path)

    def get_model_filename(self):
        return self.trainer.get_best_model_path()

