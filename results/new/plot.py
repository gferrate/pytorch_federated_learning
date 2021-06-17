import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import sys
sys.path.insert(0,'..')

MARKER_SIZE=0


# _type = acc, loss
def make_plot(name, datas, _type):
    plt.figure()
    epochs = len(datas[0][0])
    X_AXIS = list(map(lambda x: x+1, range(epochs)))
    for data, label in datas:
        y_values = [data[i][_type] for i in range(len(data))]
        label_ = f'{label}_{_type}'

        plt.plot(X_AXIS,
                 y_values,
                 linewidth=1,
                 label=label_,
                 linestyle='solid',
                 marker="^",
                 markersize=MARKER_SIZE)

    plt.legend(loc="upper right")
    # Limits
    plt.axis(xmin=0, xmax=epochs+1)#, ymin=2, ymax=4.5)
    # Labels
    title = name.split('/')[-1].replace('.png', '').replace('_', ' ').title()
    plt.title(title)
    plt.ylabel(_type.title())
    plt.xlabel('Communication Round')
    # Save
    plt.savefig(name, dpi=400)

