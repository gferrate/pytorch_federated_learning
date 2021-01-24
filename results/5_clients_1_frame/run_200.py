import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt


MARKER_SIZE=1
V_LINES = False

# Init
plt.figure()

if V_LINES:
    epochs = 200
    # Add vertical Lines
    for i in range(epochs):
        plt.axvline(
            i+1, linewidth=0.5, color='black', linestyle='dotted', alpha=0.5)

# NON-IID results:
from raw_5_clients_non_iid_1_frame_200_cr import results
epochs = len(results)
X_AXIS = list(map(lambda x: x+1, range(epochs)))
types = ['test-top1', 'test-top3']
legend = {'test-top1': '5-clients-non-iid-top-1',
          'test-top3': '5-clients-non-iid-top-3'}
for t in types:
    y_values = [x['test_result'][t] for x in results]
    plt.plot(X_AXIS,
             y_values,
             linewidth=1,
             label=legend[t],
             linestyle='solid',
             marker="s",
             markersize=MARKER_SIZE)
    plt.legend(loc="lower right")

# Limits
plt.axis(xmin=0, xmax=epochs+1, ymin=0, ymax=100)

# Labels
plt.title('1 input frames, 5 clients, 200 CR, non-iid dataset split')
plt.ylabel('Accuracy')
plt.xlabel('Communication Round')

# Save
plt.savefig('result_200.png', dpi=400)
