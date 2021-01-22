import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

import numpy as np
from datetime import timedelta, datetime
from string import Template

from results_raw import results


class DeltaTemplate(Template):
    delimiter = "%"


def strfdelta(tdelta, fmt='%H:%M:%S'):
    d = {"D": tdelta.days}
    hours, rem = divmod(tdelta.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    d["H"] = '{:02d}'.format(hours)
    d["M"] = '{:02d}'.format(minutes)
    d["S"] = '{:02d}'.format(seconds)
    t = DeltaTemplate(fmt)
    return t.substitute(**d)


types = ['test-top1', 'test-top3']#, 'test_cluster-top1', 'test_cluster-top3']
legend = ['top1', 'top3']#, 'test_cluster-top1', 'test_cluster-top3']
### IMPORTANT!!!!!!! LAST EPOCH IS LAST TEST WITH BEST RESULT AND CLUSTERING
epochs = len(results) - 1
for t in types:
    y_values = [(e, x[t]) for e, x in results.items()][:-1]
    y_values = list(sorted(y_values, key=lambda t: t[0])) # Order by epoch asc
    y_values = [x[1] for x in y_values]
    x = list(map(lambda x: x+1, list(range(len(y_values)))))
    plt.plot(x, y_values, label=t)

## Last epoch:
#last_test = results[epochs]
#print(last_test)
#types = ['test-top1', 'test-top3', 'test-top1-clustering', 'test-top3-clustering']
#legend = ['top1', 'top3', 'cluster-top1', 'cluster-top3']
#n_points = len(y_values)
#for t in types:
#    y_values = [last_test[t] for _ in range(n_points)]
#    x = list(range(len(y_values)))
#    plt.plot(x, y_values, label=t)

# Add vertical Lines
for i in range(epochs):
    plt.axvline(i+1, linewidth=0.5, color='black', linestyle='dashed', alpha=0.5)

plt.xlim([0, epochs+1])

plt.title('Accuracy with 1 client over 50 epochs (control/no FL)')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')

plt.legend(legend, bbox_to_anchor=(0.7, 0.25))
plt.savefig('result.png', dpi=400)

