import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt


fig, (ax1, ax2) = plt.subplots(2, 1, gridspec_kw={'hspace': 0.4}, figsize=(7,6))

# No FL results
from results_non_fedlearn_7_frames_raw import results
types = ['test-top1', 'test-top3']
legend = {'test-top1': 'top-1', 'test-top3': 'top-3'}
### IMPORTANT!!!!!!! LAST EPOCH IS LAST TEST WITH BEST RESULT AND CLUSTERING
epochs = len(results) - 1
X_AXIS = list(map(lambda x: x+1, range(epochs)))
for t in types:
    y_values = [(e, x[t]) for e, x in results.items()][:-1]
    y_values = list(sorted(y_values, key=lambda t: t[0])) # Order by epoch asc
    y_values = [x[1] for x in y_values]
    ax1.plot(X_AXIS, y_values, linewidth=1, label=legend[t])
    ax1.legend(loc="lower right")

# IID results:
from results_7_frames_iid_5_clients_raw import results
epochs = len(results)
X_AXIS = list(map(lambda x: x+1, range(epochs)))
types = ['test-top1', 'test-top3']
legend = {'test-top1': 'top-1', 'test-top3': 'top-3'}
for t in types:
    y_values = [x['test_result'][t] for x in results]
    ax2.plot(X_AXIS, y_values, linewidth=1, label=legend[t])
    ax2.legend(loc="lower right")

# Add vertical Lines
for i in range(epochs):
    ax1.axvline(i+1, linewidth=0.5, color='black', linestyle='dashed', alpha=0.5)
    ax2.axvline(i+1, linewidth=0.5, color='black', linestyle='dashed', alpha=0.5)

# Limits
ax1.axis(xmin=0, xmax=epochs+1, ymin=0, ymax=100)
ax2.axis(xmin=0, xmax=epochs+1, ymin=0, ymax=100)

ax1.set_title('1 client over 50 epochs (no FL)')
ax1.set_ylabel('Accuracy')
ax1.set_xlabel('Epoch')

ax2.set_title('5 clients over 50 communication rounds')
ax2.set_ylabel('Accuracy')
ax2.set_xlabel('Communication Round')

#plt.title('Accuracy with 1 client over 50 epochs (control/no FL)')
#plt.ylabel('Accuracy')
#plt.xlabel('Epoch')
fig.savefig('result.png', dpi=400)

