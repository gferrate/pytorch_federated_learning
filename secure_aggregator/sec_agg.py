import sys; sys.path.insert(0, '.')
import os
import torch
import numpy as np

from classification import trainer


class SecAgg:

    def __init__(self, port, use_cuda=True):
        self.port = port
        # TODO: Num clients don't have to be in SecAgg
        self.num_clients = 2
        self.client_id = 'client_{}'.format(self.port)
        self.init_model()

    def init_model(self):
        self.trainer = trainer.SecAggTrainer(self.client_id)

    @staticmethod
    def load_models():
        print('Loading client models...')
        arr = []
        for root, dirs, files in os.walk('secure_aggregator/client_models/',
                                         topdown=True):
            for name in files:
                if name.endswith('model.tar'):
                    fn = os.path.join(root, name)
                    data = torch.load(fn)
                    # arr.append(np.load(fn, allow_pickle=True))
                    arr.append(data)
        models = np.array(arr)
        print('Done')
        return models

    @staticmethod
    def average_weights(models):
        print('Averaging weights...')
        # FL average
        # TODO: Make this more efficient
        avg_model = models[0].copy()
        for k in avg_model:
            tmp = [w[k] for w in models]
            #avg_model[k] = np.average(tmp)
            avg_model[k] = np.true_divide(sum(tmp), len(tmp))

        ## FL average
        #fl_avg = np.average(weights, axis=0)
        #for i in fl_avg:
        #    print(i.shape)
        print('Done')
        return avg_model

    def aggregate_models(self):
        model_weights = self.load_models()
        avg_weights = self.average_weights(model_weights)
        self.trainer.update_model(avg_weights)
        # TODO: Test here?
        #self.trainer.test()

    def get_model_filename(self):
        return self.trainer.get_best_model_path()

    def save_model(self):
        self.trainer.save_model()

    def test(self):
        test_result = self.trainer.test()
        return test_result
