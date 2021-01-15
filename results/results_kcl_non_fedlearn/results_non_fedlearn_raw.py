

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
#    fn = 'results_non_fedlearn.log'
#    data = extract_results(fn)
#    average_epochs(data)
#    print(data)


results = {0: {'test-top1': 19.580853174603174, 'test-top3': 46.437198412698415}, 1: {'test-top1': 24.283180555555557, 'test-top3': 49.85712103174603}, 2: {'test-top1': 31.01411507936508, 'test-top3': 55.799527777777776}, 3: {'test-top1': 33.58107936507937, 'test-top3': 57.97694444444445}, 4: {'test-top1': 36.70607936507937, 'test-top3': 60.68517063492064}, 5: {'test-top1': 39.98797619047619, 'test-top3': 62.74073809523809}, 6: {'test-top1': 36.34025595238096, 'test-top3': 60.98899007936508}, 7: {'test-top1': 37.004777777777775, 'test-top3': 60.53204761904762}, 8: {'test-top1': 38.01544246031746, 'test-top3': 61.20169047619047}, 9: {'test-top1': 37.15951785714286, 'test-top3': 61.79935515873016}, 10: {'test-top1': 38.04159126984127, 'test-top3': 60.12282142857143}, 11: {'test-top1': 39.04335912698413, 'test-top3': 62.07729563492063}, 12: {'test-top1': 37.37060119047619, 'test-top3': 60.04383333333333}, 13: {'test-top1': 38.83524206349206, 'test-top3': 62.30185714285714}, 14: {'test-top1': 40.23491468253968, 'test-top3': 62.364938492063494}, 15: {'test-top1': 37.453900793650796, 'test-top3': 60.15678968253968}, 16: {'test-top1': 37.162482142857144, 'test-top3': 59.754841269841265}, 17: {'test-top1': 36.61307341269841, 'test-top3': 59.43754365079365}, 18: {'test-top1': 34.92413888888889, 'test-top3': 58.993271825396825}, 19: {'test-top1': 36.91554563492064, 'test-top3': 59.379043650793655}, 20: {'test-top1': 36.266930555555554, 'test-top3': 60.387011904761906}, 21: {'test-top1': 37.29376984126984, 'test-top3': 59.19033531746032}, 22: {'test-top1': 35.96311111111111, 'test-top3': 57.280613095238095}, 23: {'test-top1': 35.391325396825394, 'test-top3': 58.86414087301587}, 24: {'test-top1': 40.02437103174603, 'test-top3': 62.484095238095236}, 25: {'test-top1': 39.73672619047619, 'test-top3': 61.43919246031746}, 26: {'test-top1': 36.39093849206349, 'test-top3': 60.02496428571428}, 27: {'test-top1': 38.78051587301587, 'test-top3': 60.88547023809524}, 28: {'test-top1': 39.431557539682544, 'test-top3': 60.93264682539682}, 29: {'test-top1': 38.783212301587305, 'test-top3': 60.11716071428571}, 30: {'test-top1': 38.783212301587305, 'test-top3': 60.11716071428571}}
