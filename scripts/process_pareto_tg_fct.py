from monitor.helper import *
from collections import defaultdict
import argparse
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('-f', dest="files", nargs='+', required=True)
parser.add_argument('-o', '--out', dest="out", default=None)
parser.add_argument('-k', dest="k", default=None)
parser.add_argument('-w', dest="workload", default=None)

args = parser.parse_args()

def first(lst):
    return map(lambda e: e[0], lst)

def second(lst):
    return map(lambda e: e[1], lst)

def median(L):
  size=len(L)
  if size%2==1:
    return L[(size-1)/2]
  else:
    return(L[size/2-1]+L[size/2])/2.0
def average(L):
  return sum(L)/len(L)


data={}

# results/pareto1-mdtcp-180908-load1.0bw100g2delay5.0avgalfa1numreqs200ft4qmon0parto_mean60/one_to_several


for f in args.files:
  print f

  flow = f[f.find('flows') + len('flows')]
  print(flow)
  if flow not in data:
    data[flow]={}
  for line in open(f).xreadlines():
    fields=line.split()
    if len(fields) > 2:
      x=int(fields[0])
      y=float(fields[2])
      if x in data[flow]:
        data[flow][x].append(y)
      else:
        data[flow][x]=[y]

for flow in data.items():
  x_plot=[]
  y_min=[]
  y_max=[]
  y_median=[]
  y_mean=[]
  for t in sorted(data[flow].items()):
    x_plot.append(t[0])
    y_min.append(min(t[1]))
    y_max.append(max(t[1]))

    y_median.append(median(t[1]))
    y_mean.append(average(t[1]))
  line_mean=plt.plot(x_plot,y_mean)
  line_mean.set_linestyle('dashed')
  line_mean.set_label(flow)

# plot.title("Flow durations")
plt.ylabel("Mean FCT [secs]")
plt.grid()
plt.yscale('log')
plt.x


# print (data)



# # set up plot
# m.rc('figure', figsize=(8, 6))
# fig = plt.figure()
# title = 'Fat Tree (k=%s), %s workload' % (args.k, args.workload)
# # plot rank of flow
# axPlot = fig.add_subplot(1, 1, 1)
# #axPlot.plot(first(cwnd_time), second(cwnd_time), lw=2, label="$MPTCP$")
# #axPlot.plot(first(cwnd_time), second(cwnd_time), lw=2, label="$x$")
# colors = ['#ff0000','#ff7f00','#ffff00','#00ff00','#00ffff', '#0000ff', '#4B0082',
#           '#8F00FF']
# for flow in sorted(link_util.keys()):
#     xaxis = range(len(link_util[flow]))
#     if flow == '1':
#         label = "DCTCP"
#     else:
#         label = "MDTCP, %s subflows" % flow
#     axPlot.plot(xaxis, link_util[flow], lw=2, label=label, color=colors[int(flow) - 1])
# axPlot.grid(True)
# axPlot.legend(loc='lower right')
# axPlot.set_xlabel("Rank of Link")
# axPlot.set_ylabel("% of full link utilization)")
# # axPlot.set_title(title)

# if args.out:
#     print 'saving to', args.out
#     plt.savefig(args.out)
# else:
#     plt.show()
