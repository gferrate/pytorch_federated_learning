import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import sys
sys.path.insert(0,'..')



MARKER_SIZE = 1
USE_MARKERS = False
LEGEND_POS  = 'lower right'
LEGEND_SIZE = 7

# Init
plt.figure()

#epochs = 50
## Add vertical Lines
#for i in range(epochs):
#    plt.axvline(
#        i+1, linewidth=0.5, color='black', linestyle='dotted', alpha=0.5)

# No FL results
from non_fedlearn_7_frames.raw_non_fedlearn_7_frames_200 import results
types = ['test-top1', 'test-top3']
legend = {'test-top1': 'no-fl-top-1', 'test-top3': 'no-fl-top-3'}
### IMPORTANT!!!!!!! LAST EPOCH IS LAST TEST WITH BEST RESULT AND CLUSTERING
epochs = len(results) - 1
X_AXIS = list(map(lambda x: x+1, range(epochs)))
for t in types:
    y_values = [(e, x[t]) for e, x in results.items()][:-1]
    y_values = list(sorted(y_values, key=lambda t: t[0])) # Order by epoch asc
    y_values = [x[1] for x in y_values]
    marker = 'o' if USE_MARKERS else None
    plt.plot(X_AXIS,
             y_values,
             linewidth=1,
             label=legend[t],
             marker=marker,
             markersize=MARKER_SIZE)

# IID results:
from raw_9_clients_iid_7_frames_200 import results
epochs = len(results)
X_AXIS = list(map(lambda x: x+1, range(epochs)))
types = ['test-top1', 'test-top3']#, 'test_cluster-top1', 'test_cluster-top3']
legend = {'test-top1': '9-clients-iid-top-1',
          'test-top3': '9-clients-iid-top-3',
          'test_cluster-top1': '9-clients-iid-cluster-top-1',
          'test_cluster-top3': '9-clients-iid-cluster-top-3'}
for t in types:
    y_values = [x['test_result'][t] for x in results]
    marker = '^' if USE_MARKERS else None
    plt.plot(X_AXIS,
             y_values,
             linewidth=1,
             label=legend[t],
             linestyle='solid',
             marker=marker,
             markersize=MARKER_SIZE)

# NON-IID results:
from raw_9_clients_non_iid_7_frames_200 import results
epochs = len(results)
X_AXIS = list(map(lambda x: x+1, range(epochs)))
types = ['test-top1', 'test-top3']
legend = {'test-top1': '9-clients-non-iid-top-1',
          'test-top3': '9-clients-non-iid-top-3'}
for t in types:
    y_values = [x['test_result'][t] for x in results]
    marker = 's' if USE_MARKERS else None
    plt.plot(X_AXIS,
             y_values,
             linewidth=1,
             label=legend[t],
             linestyle='solid',
             marker=marker,
             markersize=MARKER_SIZE)

# Legend
plt.legend(loc=LEGEND_POS)#, prop={'size': LEGEND_SIZE})


# Limits
epochs = 200
plt.axis(xmin=0, xmax=epochs+1, ymin=0, ymax=100)

# Labels
#plt.title('1 input frame comparison with 9 clients')
plt.ylabel('Accuracy')
plt.xlabel('Epoch / Communication Round')

# Save
plt.savefig('result.png', dpi=400)
