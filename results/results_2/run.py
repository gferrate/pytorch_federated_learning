import matplotlib.pyplot as plt
import numpy as np
from results_2_raw import results

types = ['test-top1', 'test-top3']#, 'test_cluster-top1', 'test_cluster-top3']
types_interpolated = ['test-top1', 'test-top1 fit', 'test-top3', 'test-top3 fit']
for t in types:
    y_values = [x['test_result'][t] for x in results]
    x = list(range(len(y_values)))
    z = np.polyfit(x, y_values, 7)
    p = np.poly1d(z)
    plt.plot(x, y_values, label=t)
    plt.plot(x, p(x), linewidth=1, linestyle='dashed')

times = [
    '00:05:30',
    '00:11:00',
    '00:16:30',
    '00:22:04',
    '00:27:40',
    '00:33:13',
    '00:38:40',
    '00:44:10',
    '00:49:40',
    '00:55:14',
    '01:00:51',
    '01:06:18',
    '01:11:48',
    '01:17:18',
    '01:22:47',
    '01:28:16',
    '01:33:39',
    '01:39:12',
    '01:44:43',
    '01:50:14',
    '01:55:44',
    '02:01:11',
    '02:06:42',
    '02:12:15',
    '02:17:44',
    '02:23:11',
    '02:28:41',
    '02:34:10',
    '02:39:40',
    '02:45:07',
]

for i, t in enumerate(times):
    plt.axvline(i, linewidth=0.5, color='black', linestyle='dashed', alpha=0.5)
    plt.text(i+0.1, 1.5, t, rotation=90, fontsize=5)

plt.title('Accuracy with two clients over 30 communication rounds.\nIID dataset split and 1 epoch per CR')
plt.ylabel('Accuracy')
plt.xlabel('Communication round')

plt.legend(types_interpolated, bbox_to_anchor=(0.7, 0.15))
plt.savefig('result.png', dpi=400)

