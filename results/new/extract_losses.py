from plot import Plotter
from copy import deepcopy


def extract_training_results(fn):
    data = {}
    with open(fn, 'r') as f:
        epoch = -1
        for l in f:
            if 'RUNNING TRAIN TEST' in l:
                epoch += 1

            if 'Test: [-1]' in l:
                s = l.split('\t')
                loss = float(s[3].split(' ')[1])
                top_1 = float(s[4].split(' ')[1])
                top_3 = float(s[5].split(' ')[1])
                data.setdefault(epoch, {}).setdefault('loss', []).append(loss)
                data.setdefault(epoch, {}).setdefault('acc-top-1', []).append(top_1)
                data.setdefault(epoch, {}).setdefault('acc-top-3', []).append(top_3)
    return data


def extract_val_results(fn):
    data = {}
    clustering = False
    last_clustering = False
    with open(fn, 'r') as f:
        epoch = 0
        for l in f:
            if 'clustering...' in l:
                clustering = True
            if 'Test: [0]' in l:
                s = l.split('\t')
                #epoch = int(s[0].split('[')[1].split(']')[0])
                top_1 = float(s[-2].split(' ')[1].split(' ')[0])
                top_3 = float(s[-1].split(' ')[1].split(' ')[0])
                time = float(s[1].split(' ')[1].split(' ')[0])
                loss = float(s[-3].split(' ')[1])
                if clustering:
                    data.setdefault(epoch, {}).setdefault('loss-clustering', []).append(loss)
                    data.setdefault(epoch, {}).setdefault('acc-clustering-top-1', []).append(top_1)
                    data.setdefault(epoch, {}).setdefault('acc-clustering-top-3', []).append(top_3)
                else:
                    data.setdefault(epoch, {}).setdefault('loss', []).append(loss)
                    data.setdefault(epoch, {}).setdefault('acc-top-1', []).append(top_1)
                    data.setdefault(epoch, {}).setdefault('acc-top-3', []).append(top_3)

                if len(data[epoch].get('loss-clustering', [])) == 1612 and clustering:
                    epoch += 1
                    clustering = False

    return data

def avg(_list):
    return sum(_list) / len(_list)

def average_epochs(data):
    for epoch, d in data.items():
        d['loss'] = avg(d['loss'])
        d['acc-top-1'] = avg(d['acc-top-1'])
        d['acc-top-3'] = avg(d['acc-top-3'])
        if 'loss-clustering' in d:
            d['loss-clustering'] = avg(d['loss-clustering'])
            d['acc-clustering-top-1'] = avg(d['acc-clustering-top-1'])
            d['acc-clustering-top-3'] = avg(d['acc-clustering-top-3'])
    return data

def get_all_val_data(fn):
    data = extract_val_results(fn)
    average_epochs(data)
    return data

def get_all_training_data(fn):
    data = extract_training_results(fn)
    average_epochs(data)
    return data

if __name__ == '__main__':
    filenames = (
        ('plots/5_clients_7_frames_iid.png', '5_clients_iid_7_frames_200_cr/logs/{}', 'sec_agg.log', 5),
        ('plots/5_clients_7_frames_non_iid.png', '5_clients_non_iid_7_frames_200_cr/logs/{}', 'sec_agg.log', 5),
        ('plots/9_clients_7_frames_iid.png', '9_clients_iid_7_frames_200_cr/logs/{}', 'sec_agg.log', 9),
        ('plots/9_clients_7_frames_non_iid.png', '9_clients_non_iid_7_frames_200_cr/logs/{}', 'sec_agg.log', 9),
    )

    plotter = Plotter(export_type='png', smooth=True)

    all_datas = []
    for name, base_fn, secagg_file, n_clients in filenames:
        datas = []
        # Training data
        training_data = get_all_training_data(base_fn.format(secagg_file))
        datas.append((training_data, 'training'))

        # Validation Data
        secagg_path = base_fn.format(secagg_file)
        validation_data = get_all_val_data(secagg_path)
        datas.append((validation_data, 'validation'))
        all_datas.append(datas)

        for _type in ('loss', 'acc-top-1', 'acc-top-3'):
            _name = name.replace('.png', f'_{_type}.png')
            #print(_name, datas)
            plotter.make_plot(_name, datas, _type)
