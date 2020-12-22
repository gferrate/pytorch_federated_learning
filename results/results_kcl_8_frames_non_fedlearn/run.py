import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

import numpy as np
from datetime import timedelta, datetime
from scipy.interpolate import make_interp_spline, BSpline
from string import Template

from results_non_fedlearn_8_frames_raw import results


class DeltaTemplate(Template):
    delimiter = "%"


def strfdelta(tdelta, fmt='%H:%M:%S'):
    d = {"D": tdelta.days}
    hours, rem = divmod(tdelta.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    d["H"] = '{:02d}'.format(hours)
    d["M"] = '{:02d}'.format(minutes)
    d["S"] = '{:02d}'.format(seconds)
    t = DeltaTemplate(fmt)
    return t.substitute(**d)

"""
results: dict (31) [pub]
| 0: dict (2) [pub]
| | 'test-top1': 19.580853174603174
| | 'test-top3': 46.437198412698415
| 1: dict (2)
| 2: dict (2)
"""

types = ['test-top1', 'test-top3']#, 'test_cluster-top1', 'test_cluster-top3']
types_interpolated = ['test-top1', 'test-top1 fit', 'test-top3', 'test-top3 fit']
for t in types:
    y_values = [x[t] for e, x in results.items()]
    x = list(range(len(y_values)))
    z = np.polyfit(x, y_values, 7)
    p = np.poly1d(z)
    plt.plot(x, y_values, label=t)
    plt.plot(x, p(x), linewidth=1, linestyle='dashed', label='t {}'.format('fitted'))

## We don't have elapsed time in control
#ts = [x['elapsed_time'] for x in results]
#last_time = 0
#times = []
#for time in ts:
#    inc = timedelta(seconds=(time - last_time))
#    times.append(strfdelta(inc))


#for i, t in enumerate(times):
#    plt.axvline(i, linewidth=0.5, color='black', linestyle='dashed', alpha=0.5)
#    plt.text(i+0.1, 4.8, t, rotation=90, fontsize=5)

plt.title('Accuracy with 1 client over 30 communication rounds and 8 input frames')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')

plt.legend(types_interpolated, bbox_to_anchor=(0.7, 0.25))
plt.savefig('result.png', dpi=400)
