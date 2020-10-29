import sys; sys.path.insert(0, '.')
import os
import shutil
import torch
import numpy as np

from classification import trainer


class SecAgg:

    def __init__(self, port, use_cuda=True):
        self.port = port
        # TODO: Num clients don't have to be in SecAgg
        self.client_id = 'client_{}'.format(self.port)
        self.client_models_folder = 'secure_aggregator/client_models'
        self.init_model()

    def init_model(self):
        self.trainer = trainer.SecAggTrainer(self.client_id)

    def load_models(self):
        print('Loading client models...')
        arr = []
        for root, dirs, files in os.walk(self.client_models_folder,
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
            # avg_model[k] = np.average(tmp)
            avg_model[k] = np.true_divide(sum(tmp), len(tmp))

        ## FL average
        #fl_avg = np.average(weights, axis=0)
        #for i in fl_avg:
        #    print(i.shape)
        print('\tDone')
        return avg_model

    def aggregate_models(self):
        model_weights = self.load_models()
        avg_weights = self.average_weights(model_weights)
        self.trainer.update_model(avg_weights)

    def get_model_filename(self):
        return self.trainer.get_best_model_path()

    def save_model(self):
        self.trainer.save_model()

    def delete_client_models(self):
        print('Deleting client models...')
        for filename in os.listdir(self.client_models_folder):
            if not filename.endswith('.tar'):
                continue
            file_path = os.path.join(self.client_models_folder, filename)
            print('\tDeleting {}'.format(file_path))
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
        print('\tDone')

    def test(self):
        test_result = self.trainer.test()
        return test_result

