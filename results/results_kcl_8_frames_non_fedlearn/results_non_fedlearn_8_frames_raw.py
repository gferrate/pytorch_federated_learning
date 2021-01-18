def extract_results(fn):
    data = {}
    last_epoch = -1
    with open(fn, 'r') as f:
        for l in f:
            if l.startswith('Test'):
                s = l.split('\t')
                epoch = int(s[0].split('[')[1].split(']')[0])
                top_1 = float(s[-2].split(' ')[1].split(' ')[0])
                top_3 = float(s[-1].split(' ')[1].split(' ')[0])
                data.setdefault(epoch, {}).setdefault('test-top1', []).append(top_1)
                data[epoch].setdefault('test-top3', []).append(top_3)
                if last_epoch != epoch:
                    print('Extracting epoch', epoch)
                    last_epoch = epoch
    return data

def avg(_list):
    return sum(_list) / len(_list)

def average_epochs(data):
    for epoch, d in data.items():
        d['test-top1'] = avg(d['test-top1'])
        d['test-top3'] = avg(d['test-top3'])
    return data


if __name__ == '__main__':
    fn = 'results_non_fedlearn_8_frames.results'
    data = extract_results(fn)
    average_epochs(data)
    print(data)

results = {0: {'test-top1': 66.28008531746032, 'test-top3': 90.19851984126983}, 1: {'test-top1': 62.80354960317461, 'test-top3': 87.03550992063491}, 2: {'test-top1': 40.99082341269841, 'test-top3': 72.91639682539683}, 3: {'test-top1': 63.01786706349206, 'test-top3': 86.30116666666667}, 4: {'test-top1': 53.816478174603176, 'test-top3': 78.91784126984126}, 5: {'test-top1': 38.45567063492064, 'test-top3': 69.45495833333334}, 6: {'test-top1': 63.491523809523805, 'test-top3': 88.38557936507937}, 7: {'test-top1': 63.55676388888889, 'test-top3': 83.68432936507936}, 8: {'test-top1': 52.45104365079365, 'test-top3': 80.5844007936508}, 9: {'test-top1': 49.15512896825397, 'test-top3': 78.273}, 10: {'test-top1': 59.10649603174603, 'test-top3': 86.13618253968254}, 11: {'test-top1': 47.83687103174603, 'test-top3': 76.11876785714286}, 12: {'test-top1': 56.5815873015873, 'test-top3': 76.81186309523808}, 13: {'test-top1': 62.212625, 'test-top3': 83.51691865079366}, 14: {'test-top1': 62.89332142857143, 'test-top3': 83.07669047619048}, 15: {'test-top1': 44.29024404761905, 'test-top3': 73.54209722222221}, 16: {'test-top1': 59.44401388888889, 'test-top3': 85.38350793650794}, 17: {'test-top1': 62.96772619047619, 'test-top3': 84.04395238095239}, 18: {'test-top1': 66.0504007936508, 'test-top3': 85.80729166666667}, 19: {'test-top1': 62.212355158730155, 'test-top3': 85.37326388888889}, 20: {'test-top1': 66.30758333333333, 'test-top3': 86.16098412698412}, 21: {'test-top1': 65.13543849206349, 'test-top3': 82.79767261904762}, 22: {'test-top1': 63.365628968253965, 'test-top3': 84.92683531746032}, 23: {'test-top1': 73.5283492063492, 'test-top3': 91.62218650793652}, 24: {'test-top1': 57.37981944444444, 'test-top3': 78.05059523809524}, 25: {'test-top1': 67.18911706349206, 'test-top3': 90.53576785714286}, 26: {'test-top1': 76.16082142857142, 'test-top3': 90.4265873015873}, 27: {'test-top1': 63.62631547619048, 'test-top3': 83.69295634920636}, 28: {'test-top1': 63.79183928571428, 'test-top3': 86.49957936507937}, 29: {'test-top1': 56.41148015873016, 'test-top3': 78.26895634920635}, 30: {'test-top1': 54.269108134920636, 'test-top3': 75.9927371031746}}
