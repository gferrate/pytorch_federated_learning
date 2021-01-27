import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import sys
sys.path.insert(0,'..')


MARKER_SIZE = 1
USE_MARKERS = False
LEGEND_POS  = 'lower right'
LEGEND_SIZE = 7
DEDUCT_AVG_TIME = True
AVG_CLUSTERING_TIME = 53  # 53: 7 frames; 17: 1 frame

def remove_clustering_time(timings):
    if not DEDUCT_AVG_TIME:
        print('NOT REMOVING TIME')
        return timings
    diffs = [timings[0]]
    for i in range(1, len(timings)):
        diffs.append(timings[i] - timings[i-1])
    diffs = [d - AVG_CLUSTERING_TIME for d in diffs]
    timings = [diffs[0]]
    for i in range(1, len(diffs)):
        timings.append(diffs[i] + timings[i-1])
    return timings


# Init
plt.figure()

# No FL results
from non_fedlearn_7_frames.raw_non_fedlearn_7_frames_50 import results

diffs = [(e, x['time']) for e, x in results.items()][:-1]
diffs = list(sorted(diffs, key=lambda t: t[0])) # Order by epoch asc
diffs = [x[1] for x in diffs]
timings = [diffs[0]]
for i in range(1, len(diffs)):
    timings.append(diffs[i] + timings[i-1])

types = ['test-top1', 'test-top3']
legend = {'test-top1': 'no-fl-top-1', 'test-top3': 'no-fl-top-3'}
marker = 'o' if USE_MARKERS else None
for t in types:
    y_values = [(e, x[t]) for e, x in results.items()][:-1]
    y_values = list(sorted(y_values, key=lambda t: t[0])) # Order by epoch asc
    y_values = [x[1] for x in y_values]
    plt.plot(timings,
             y_values,
             linewidth=1,
             label=legend[t],
             marker=marker,
             markersize=MARKER_SIZE)

# IID results:
from raw_5_clients_iid_7_frames import results
types = ['test-top1', 'test-top3']
legend = {'test-top1': '5-clients-iid-top-1',
          'test-top3': '5-clients-iid-top-3'}
timings = [x['elapsed_time'] for x in results]
timings = remove_clustering_time(timings)

marker = '^' if USE_MARKERS else None
for t in types:
    y_values = [x['test_result'][t] for x in results]
    plt.plot(timings,
             y_values,
             linewidth=1,
             label=legend[t],
             linestyle='solid',
             marker=marker,
             markersize=MARKER_SIZE)

# NON-IID results:
from raw_5_clients_non_iid_7_frames import results
types = ['test-top1', 'test-top3']
legend = {'test-top1': '5-clients-non-iid-top-1',
          'test-top3': '5-clients-non-iid-top-3'}
marker = 's' if USE_MARKERS else None
timings = [x['elapsed_time'] for x in results]
timings = remove_clustering_time(timings)
for t in types:
    y_values = [x['test_result'][t] for x in results]
    plt.plot(timings,
             y_values,
             linewidth=1,
             label=legend[t],
             linestyle='solid',
             marker=marker,
             markersize=MARKER_SIZE)

# Legend
plt.legend(loc=LEGEND_POS, prop={'size': LEGEND_SIZE})

# Limits
plt.axis(ymin=0, ymax=100)

# Labels
#plt.title('1 input frame comparison')
plt.ylabel('Accuracy')
plt.xlabel('Time (seconds)')

# Save
if DEDUCT_AVG_TIME:
    plt.savefig('result_xtime_deducted.png', dpi=400)
else:
    plt.savefig('result_xtime.png', dpi=400)
