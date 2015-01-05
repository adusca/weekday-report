from datetime import datetime
import compare
import csv 
import numpy 
import collections

def get_branch(platform):
    if platform == 'Android' or platform.startswith('OSX'):
        return 63
    return 131

test_tuples = []
for test in compare.test_map:
    for platform in compare.platform_map:
        test_tuples.append((compare.test_map[test]['id'], get_branch(platform), compare.platform_map[platform], test, platform))

with open('report.csv', 'wb') as report:
    with open('avgs.csv', 'wb') as avgs:
        # Writing the headers
        report_header = csv.writer(report, quoting=csv.QUOTE_ALL)
        report_header.writerow(['test', 'date', 'variance', 'weekday'])
        avgs_header = csv.writer(avgs, quoting=csv.QUOTE_ALL)
        avgs_header.writerow(['test, platform', 'weekday', 'average'])

        for test in test_tuples:
            testid, branchid, platformid = test[:3]
            data_dict = compare.getGraphData(testid, branchid, platformid)
            if data_dict:
                data = data_dict['test_runs']
                time_dict = collections.OrderedDict()
                days = {}
                for point in data:
                    time = datetime.fromtimestamp(point[2]).strftime('%Y-%m-%d')
                    time_dict[time] = time_dict.get(time, []) + [point[3]]
                for time in time_dict:
                    weekday = datetime.strptime(time, '%Y-%m-%d').strftime('%A')
                    variance = numpy.var(time_dict[time])
                    days[weekday] = days.get(weekday, []) + [variance]
                    new_line = [" ".join(test[3:])]
                    new_line.extend([time, variance, weekday])
                    wr = csv.writer(report, quoting=csv.QUOTE_ALL)
                    wr.writerow(new_line)

                for day in days:
                    average = numpy.average(days[day])
                    line = [test[3:], day, "%.3f" %  average]
                    out = csv.writer(avgs, quoting=csv.QUOTE_ALL)
                    out.writerow(line)
