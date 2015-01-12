import csv
import copy
from analyze import TalosAnalyzer
from analyze_graphapi import GraphAPISource, TestSeries

source = GraphAPISource('http://graphs.mozilla.org/api')
start_time = 1388545200 #2014-01-01
series = source.getTestSeries(['Mozilla-Inbound'], start_time, [])
data = source.getTestData(series, start_time)

# Constants from analysis.cfg
back_window = 12
threshold = 7
machine_threshold = 15
machine_history_size = 5

analysis = []
window_sizes = [3, 6, 12]

for fore_window in window_sizes:
    analyzer = TalosAnalyzer()
    analyzer.addData(copy.deepcopy(data))
    analysis.append(analyzer.analyze_t(back_window, fore_window,
                           threshold, machine_threshold,
                           machine_history_size))

ans = []
runs = len(analysis[2])
precisions = []

for size in window_sizes:
    precisions.append(0.0)

for i in range(runs):
    testrun_id = analysis[0][i].testrun_id
    assert testrun_id == analysis[1][i].testrun_id and testrun_id == analysis[2][i].testrun_id
    line = [testrun_id]

    for a in analysis:
        line.append(a[i].state)

    good_count = 0

    for j in range(len(window_sizes)):
        if analysis[j][i].state == analysis[-1][i].state:
            precisions[j] += 1
            good_count += 1

    if good_count != len(window_sizes):
        line.append('http://graphs.mozilla.org/api/test/runs/values?id=' + str(testrun_id))
        if line not in ans:
            ans.append(line)

with open('window_size.csv', 'wb') as report:
    out = csv.writer(report, quoting=csv.QUOTE_ALL)
    out.writerow(['testrun id'] + window_sizes + ['url for different ones'])

    for line in ans:
        out.writerow(line)
    out.writerow([runs] + [p/runs for p in precisions])
