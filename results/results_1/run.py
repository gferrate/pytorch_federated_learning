import matplotlib.pyplot as plt
from results_1_raw import results_1

types = ['test-top1', 'test-top3']#, 'test_cluster-top1', 'test_cluster-top3']
for t in types:
    y_values = [x['test_result'][t] for x in results_1]
    x = range(len(y_values))
    plt.plot(x, y_values, label=t)

times = [
    '00:09:36',
    '00:19:08',
    '00:28:38',
    '00:38:12',
    '00:47:48',
    '00:57:29',
    '01:07:00',
    '01:16:44',
    '01:26:19',
    '01:35:53',
    '01:45:26',
    '01:54:56',
    '02:04:27',
    '02:13:52',
    '02:23:32',
    '02:33:05',
    '02:42:38',
    '02:52:10',
    '03:01:38',
    '03:11:07',
    '03:20:35',
    '03:30:11',
    '03:39:44',
    '03:49:11',
    '03:58:39',
    '04:08:11',
    '04:17:39',
    '04:27:12',
    '04:36:43',
    '04:46:15',
]

for i, t in enumerate(times):
    plt.axvline(i, linewidth=0.5, color='black', linestyle='dashed', alpha=0.5)
    plt.text(i+0.1, 1.5, t, rotation=90, fontsize=5)

plt.title('Accuracy with two clients over 30 communication rounds.\nNo dataset split and 1 epoch per CR')
plt.ylabel('Accuracy')
plt.xlabel('Communication round')

plt.legend(types, bbox_to_anchor=(0.75, 0.3))
plt.savefig('result.png', dpi=400)

