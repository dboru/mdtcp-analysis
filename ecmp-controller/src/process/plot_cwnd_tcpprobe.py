# from helper import *
from collections import defaultdict
import argparse
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
# parser.add_argument('-p', '--port', dest="port", default='5001')
parser.add_argument('-f', dest="files", nargs='+', required=True)
parser.add_argument('-o', '--out', dest="out", default=None)
# parser.add_argument('-H', '--histogram', dest="histogram",
#                     help="Plot histogram of sum(cwnd_i)",
#                     action="store_true",
#                     default=False)

args = parser.parse_args()

def first(lst):
    return map(lambda e: e[0], lst)

def second(lst):
    return map(lambda e: e[1], lst)

"""
Sample line:
2.221032535 10.0.0.2:39815 10.0.0.1:5001 32 0x1a2a710c 0x1a2a387c 11 2147483647 14592 85
"""
def parse_file(f):
    cwnd = defaultdict(list)
    for l in open(f).xreadlines():
        fields = l.strip().split(' ')
        # print((fields))
        if '127.0.0.1' in l:
            continue
        elif int(fields[3]) == 32 or int(fields[3])==40:
            srcdst=fields[1]+'_'+fields[2]
            if srcdst not in cwnd.keys() and int(fields[6])==10:
                cwnd[srcdst]={'cwnd':[int(fields[6])],'rtt':[int(fields[9])],'time':[float(fields[0])]}
            else:
                if srcdst in cwnd.keys():
                    cwnd[srcdst]['cwnd'].append(int(fields[6]))
                    cwnd[srcdst]['rtt'].append(int(fields[9]))
                    cwnd[srcdst]['time'].append(float(fields[0]))


        # sport = int(fields[1].split(':')[1])
        # times[sport].append(float(fields[0]))

        # c = int(fields[6])
        # cwnd[sport].append(c * 1480 / 1024.0)
        # srtt.append(int(fields[-1]))
    print(len(cwnd.keys()))
    return cwnd

# added = defaultdict(int)
# events = []

def plot_cwnds():
   
    for f in args.files:
        cwnds = parse_file(f)

        for cwnd in cwnds.keys():
            if (len(cwnds[cwnd]['cwnd'])) > 10:
                fig = plt.figure()
                axPlot = fig.add_subplot(111)
                axPlot.plot(cwnds[cwnd]['time'],cwnds[cwnd]['cwnd'],marker='.')
                axPlot.set_xlabel('Time [sec]')
                axPlot.set_ylabel('CWND [pkts]')
                axPlot.grid(True)
                # plt.savefig(args.out+cwnd+'.pdf')
                plt.show()


plot_cwnds()

# total_cwnd = 0
# cwnd_time = []

# min_total_cwnd = 10**10
# max_total_cwnd = 0
# totalcwnds = []

# m.rc('figure', figsize=(16, 6))
# fig = plt.figure()
# plots = 1
# if args.histogram:
#     plots = 2

# axPlot = fig.add_subplot(1, plots, 1)
# plot_cwnds(axPlot)

# for (t,p,c) in events:
#     if added[p]:
#         total_cwnd -= added[p]
#     total_cwnd += c
#     cwnd_time.append((t, total_cwnd))
#     added[p] = c
#     totalcwnds.append(total_cwnd)

# axPlot.plot(first(cwnd_time), second(cwnd_time), lw=2, label="$\sum_i W_i$")
# axPlot.grid(True)
# axPlot.legend()
# axPlot.set_xlabel("seconds")
# axPlot.set_ylabel("cwnd KB")
# axPlot.set_title("TCP congestion window (cwnd) timeseries")

# if args.histogram:
#     axHist = fig.add_subplot(1, 2, 2)
#     n, bins, patches = axHist.hist(totalcwnds, 50, normed=1, facecolor='green', alpha=0.75)

#     axHist.set_xlabel("bins (KB)")
#     axHist.set_ylabel("Fraction")
#     axHist.set_title("Histogram of sum(cwnd_i)")

# if args.out:
#     print 'saving to', args.out
#     plt.savefig(args.out)
# else:
#     plt.show()