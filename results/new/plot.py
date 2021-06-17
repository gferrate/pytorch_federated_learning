import numpy as np
import csv
from savitzky_golay import savitzky_golay
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

import sys
sys.path.insert(0,'..')

MARKER_SIZE=0

class Plotter:

    def __init__(self, export_type='png', smooth=True):
        assert export_type in ('latex', 'png')
        self.export_type = export_type
        self.extension = '.png' if export_type == 'png' else '.pgf'
        if self.export_type == 'latex':
            matplotlib.use("pgf")
            matplotlib.rcParams.update({
                "pgf.texsystem": "pdflatex",
                'font.family': 'serif',
                'text.usetex': True,
                'pgf.rcfonts': False,
            })
        self.smooth = smooth

    # _type = acc, loss
    def make_plot(self, name, datas, _type):
        if self.smooth:
            name = name.replace('.png', '_smooth.png')
        plt.figure()
        epochs = len(datas[0][0])
        X_AXIS = list(map(lambda x: x+1, range(epochs)))
        for data, label in datas:
            y_values = [data[i][_type] for i in range(len(data))]
            if self.smooth:
                y_values = np.asarray(y_values)
                y_values = savitzky_golay(y_values, 51, 3) # window size 51, polynomial order 3

            raw_csv_name = name.replace('.png', f'_{label}.csv').replace('plots/', 'plots/csvs/')
            with open(raw_csv_name, 'w') as f:
                writer = csv.writer(f)
                zipped = zip(X_AXIS, y_values)
                for row in zipped:
                    writer.writerow(row)

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
        name = name.replace('.png', self.extension)
        if self.export_type == 'png':
            plt.savefig(name, dpi=400)
        else:
            plt.savefig(name)

