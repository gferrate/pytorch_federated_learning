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


#if __name__ == '__main__':
#    fn = 'results_non_fedlearn_7_frames.results'
#    data = extract_results(fn)
#    average_epochs(data)
#    print(data)

results = {0: {'test-top1': 61.32893452380952, 'test-top3': 85.02873809523808}, 1: {'test-top1': 72.7470992063492, 'test-top3': 89.06142261904762}, 2: {'test-top1': 64.37737301587302, 'test-top3': 87.68169841269841}, 3: {'test-top1': 53.61510119047619, 'test-top3': 81.75977976190475}, 4: {'test-top1': 37.6275119047619, 'test-top3': 73.23585317460318}, 5: {'test-top1': 59.32728373015873, 'test-top3': 85.04868650793651}, 6: {'test-top1': 60.053539682539686, 'test-top3': 82.98611111111111}, 7: {'test-top1': 63.76137698412698, 'test-top3': 84.05635317460317}, 8: {'test-top1': 60.35627976190476, 'test-top3': 81.02705555555555}, 9: {'test-top1': 71.67362103174602, 'test-top3': 88.71446825396825}, 10: {'test-top1': 58.39318055555556, 'test-top3': 81.2624007936508}, 11: {'test-top1': 59.48552976190476, 'test-top3': 81.87624007936508}, 12: {'test-top1': 58.89810912698413, 'test-top3': 81.66326984126984}, 13: {'test-top1': 77.75944642857142, 'test-top3': 94.36276190476191}, 14: {'test-top1': 51.03465674603175, 'test-top3': 78.31478571428572}, 15: {'test-top1': 71.33879960317459, 'test-top3': 89.83539285714286}, 16: {'test-top1': 60.35924603174603, 'test-top3': 80.38491071428572}, 17: {'test-top1': 68.09302777777778, 'test-top3': 86.30952380952381}, 18: {'test-top1': 69.54904166666667, 'test-top3': 89.01936706349206}, 19: {'test-top1': 65.43197817460317, 'test-top3': 85.1600238095238}, 20: {'test-top1': 70.6489384920635, 'test-top3': 89.61810912698414}, 21: {'test-top1': 62.67037698412698, 'test-top3': 83.90646626984126}, 22: {'test-top1': 70.67104563492065, 'test-top3': 88.43005952380952}, 23: {'test-top1': 61.897751984126984, 'test-top3': 83.89891666666666}, 24: {'test-top1': 71.53936904761905, 'test-top3': 90.54816865079366}, 25: {'test-top1': 69.35656150793652, 'test-top3': 89.89335317460318}, 26: {'test-top1': 66.48442857142858, 'test-top3': 86.36532738095238}, 27: {'test-top1': 64.76611111111112, 'test-top3': 84.9578373015873}, 28: {'test-top1': 69.89734325396824, 'test-top3': 86.85515873015873}, 29: {'test-top1': 67.70590674603174, 'test-top3': 85.7328869047619}, 30: {'test-top1': 69.21880357142858, 'test-top3': 83.3953373015873}}
