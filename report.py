from datetime import datetime
import compare
import csv 
import numpy 
import collections
import argparse

def get_branch(platform):
    if platform == 'Android' or platform.startswith('OSX'):
        return 63
    return 131

def get_all_test_tuples():
    ret = []
    for test in compare.test_map:
        for platform in compare.platform_map:
            ret.extend(get_tuple(test, platform))
    return ret

def get_tuple(test, platform):
    return [(compare.test_map[test]['id'], get_branch(platform), compare.platform_map[platform], test, platform)]

def generate_report(tuple_list, filepath='report.csv', filepath2='average.csv', mode='b'):
    """
    Mode can be c for the complete data or a for just the averages or b for both
    """ 
    avg = []
    rep = []

    for test in tuple_list:
        testid, branchid, platformid = test[:3]
        data_dict = compare.getGraphData(testid, branchid, platformid)
        week_avgs = []
        
        if data_dict:
            data = data_dict['test_runs']
            data.sort(key=lambda x: x[3])
            data = data[int(0.1*len(data)):int(0.9*len(data) + 1)]
            time_dict = collections.OrderedDict()
            days = {}

            for point in data:
                time = datetime.fromtimestamp(point[2]).strftime('%Y-%m-%d')
                time_dict[time] = time_dict.get(time, []) + [point[3]]
                
            for time in time_dict:
                weekday = datetime.strptime(time, '%Y-%m-%d').strftime('%A')
                variance = numpy.var(time_dict[time])
                test_runs = len(time_dict[time])
                days[weekday] = days.get(weekday, []) + [variance]
                new_line = [" ".join(test[3:])]
                new_line.extend([time, "%.3f" % variance, weekday, test_runs])
                rep.append(new_line)
            
            tmp_avg = []
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
                average = numpy.average(sorted(days[day])[5:45])
                line = [" ".join(test[3:]), day, "%.3f" %  average]
                tmp_avg.append(line)
                week_avgs.append(average)
            
            outliers = is_normal(week_avgs)
            for j in range(7):
                line = tmp_avg[j]
                if j in outliers:
                    tmp_avg[j] = line + ['No']

            avg.extend(tmp_avg)

    if mode == 'c' or mode == 'b':
        # Complete mode
        with open(filepath, 'wb') as report:  
            report_header = csv.writer(report, quoting=csv.QUOTE_ALL)
            report_header.writerow(['test', 'date', 'variance', 'weekday', 'test runs'])
            rep = sorted(rep)
            for line in rep:
                wr = csv.writer(report, quoting=csv.QUOTE_ALL)
                wr.writerow(line)

    if mode == 'a' or mode == 'b':
        # Averages mode
        with open(filepath2, 'wb') as report:  
            avgs_header = csv.writer(report, quoting=csv.QUOTE_ALL)
            avgs_header.writerow(['test, platform', 'weekday', 'average', 'is normal?'])
            for line in avg:
                out = csv.writer(report, quoting=csv.QUOTE_ALL)
                out.writerow(line)

def is_normal(y):
    limit = 1.5
    clean_week = []
    outliers = []
    # find a baseline for the week
    if (min(y[0:4]) * limit) <= max(y[0:4]):
        for i in range(1,5):
            if y[i] > (y[i-1]*limit) or y[i] > (y[i+1]*limit):
                outliers.append(i)
                continue
            clean_week.append(y[i])
    else:
        clean_week = y

    # look at weekends now
    avg = sum(clean_week) / len(clean_week)
    for i in range(5,7):
        # look for something outside of the 20% window
        if (y[i]*1.2) < avg or y[i] > (avg*1.2):
            outliers.append(i)
    return outliers

def main():
    parser = argparse.ArgumentParser(description="Generate weekdays reports")
    parser.add_argument("s", type=str, help="all - report with averages for all tests, \
    test platform - complete daily report for that platform")
    args = parser.parse_args()
    if args.s == 'all':
        tests = get_all_test_tuples()[:3]
        generate_report(tests, mode='a')
    else:
        test, platform = args.s.split(" ")
        f = ' report-' + test + '-' + platform + '.csv'
        generate_report(get_tuple(test, platform), filepath=f, mode='c')

if __name__ == "__main__":
    main()
