import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import sys
sys.path.insert(0,'..')

MARKER_SIZE=0


def make_plot(name, datas):
    plt.figure()
    epochs = 200
    X_AXIS = list(map(lambda x: x+1, range(epochs)))
    for data, label in datas:
        y_values = [data[i]['loss'] for i in range(len(data))]
        plt.plot(X_AXIS,
                 y_values,
                 linewidth=1,
                 label=label,
                 linestyle='solid',
                 marker="^",
                 markersize=MARKER_SIZE)

    plt.legend(loc="upper right")
    # Limits
    plt.axis(xmin=0, xmax=epochs+1)#, ymin=2, ymax=4.5)
    # Labels
    #plt.title('1 input frame comparison with 9 clients')
    plt.ylabel('Loss')
    plt.xlabel('Communication Round')
    # Save
    plt.savefig(name, dpi=400)

