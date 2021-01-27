import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import sys
sys.path.insert(0,'..')


MARKER_SIZE=1

# Init
plt.figure()

#epochs = 50
## Add vertical Lines
#for i in range(epochs):
#    plt.axvline(
#        i+1, linewidth=0.5, color='black', linestyle='dotted', alpha=0.5)

# No FL results
from non_fedlearn_1_frame.raw_non_fedlearn_1_frame_200 import results

timings = [(e, x['time']) for e, x in results.items()][:-1]
timings = list(sorted(timings, key=lambda t: t[0])) # Order by epoch asc
timings = [x[1] for x in timings]
last = 0
for i in range(len(timings)):
    timings[i] += last
    last = timings[i]

types = ['test-top1', 'test-top3']
legend = {'test-top1': 'no-fl-top-1', 'test-top3': 'no-fl-top-3'}
for t in types:
    y_values = [(e, x[t]) for e, x in results.items()][:-1]
    y_values = list(sorted(y_values, key=lambda t: t[0])) # Order by epoch asc
    y_values = [x[1] for x in y_values]
    plt.plot(timings, y_values, linewidth=1, label=legend[t], marker='o', markersize=MARKER_SIZE)
    plt.legend(loc="upper right")

# IID results:
from raw_9_clients_iid_1_frames import results
types = ['test-top1', 'test-top3']
legend = {'test-top1': '5-clients-iid-top-1',
          'test-top3': '5-clients-iid-top-3'}
timings = [x['elapsed_time'] for x in results]
for t in types:
    y_values = [x['test_result'][t] for x in results]
    plt.plot(timings,
             y_values,
             linewidth=1,
             label=legend[t],
             linestyle='solid',
             marker="^",
             markersize=MARKER_SIZE)
    plt.legend(loc="upper right")

# NON-IID results:
from raw_9_clients_non_iid_1_frames import results
types = ['test-top1', 'test-top3']
legend = {'test-top1': '5-clients-non-iid-top-1',
          'test-top3': '5-clients-non-iid-top-3'}
timings = [x['elapsed_time'] for x in results]
for t in types:
    y_values = [x['test_result'][t] for x in results]
    plt.plot(timings,
             y_values,
             linewidth=1,
             label=legend[t],
             linestyle='solid',
             marker="s",
             markersize=MARKER_SIZE)
    plt.legend(loc="upper right")

# Limits
plt.axis(ymin=0, ymax=100)

# Labels
#plt.title('1 input frame comparison')
plt.ylabel('Accuracy')
plt.xlabel('Time (seconds)')

# Save
plt.savefig('result_xtime.png', dpi=400)
