def extract_results(fn):
    data = {}
    last_epoch = -1
    clustering = False
    with open(fn, 'r') as f:
        for l in f:
            if 'clustering...' in l:
                clustering = True
            if l.startswith('Test'):
                s = l.split('\t')
                epoch = int(s[0].split('[')[1].split(']')[0])
                top_1 = float(s[-2].split(' ')[1].split(' ')[0])
                top_3 = float(s[-1].split(' ')[1].split(' ')[0])
                if clustering:
                    data.setdefault(epoch, {}).setdefault('test-top1-clustering', []).append(top_1)
                    data[epoch].setdefault('test-top3-clustering', []).append(top_3)
                else:
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
        if 'test-top1-clustering' in d:
            d['test-top1-clustering'] = avg(d['test-top1-clustering'])
            d['test-top3-clustering'] = avg(d['test-top3-clustering'])
    return data

if __name__ == '__main__':
    fn = '7_frames_non_fedlearn.log'
    data = extract_results(fn)
    average_epochs(data)
    print(data)


