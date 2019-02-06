from monitor.helper import *
from collections import defaultdict
import argparse
import numpy as np
import scipy.stats

parser = argparse.ArgumentParser()
parser.add_argument('-f', dest="files", nargs='+', required=True)
parser.add_argument('-o', '--out', dest="out", default=None)
parser.add_argument('-k', dest="k", default=None)
parser.add_argument('-w', dest="workload", default=None)
parser.add_argument('-bw', dest="bw",type=int, default=10)
parser.add_argument('-t', dest="time", type=int, default=None)

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
    times = defaultdict(list)
    cwnd = defaultdict(list)
    srtt = []
    for l in open(f).xreadlines():
        fields = l.strip().split(' ')
        if len(fields) != 10:
            break
        if fields[2].split(':')[1] != args.port:
            continue
        sport = int(fields[1].split(':')[1])
        times[sport].append(float(fields[0]))

        c = int(fields[6])
        cwnd[sport].append(c * 1480 / 1024.0)
        srtt.append(int(fields[-1]))
    return times, cwnd

added = defaultdict(int)
events = []

def mean_95conf(data,ci=0.95):
  a=1.0*np.array(data)
  n=len(a)
  m,se=np.mean(a),scipy.stats.sem(a)
  h=se*scipy.stats.t.ppf((1+ci)/2., n-1)
  return m, m-h,m+h

def constant_factory(value):
     return itertools.repeat(value).next

throughput = defaultdict(list)
max_throughput = 0
iperf_data_columns = 9
for f in args.files:
  #print f

  flow = f[f.find('flows') + len('flows')]
  output = []
  for line in open(f).xreadlines():
    data = line.rstrip().split(',')
    if len(data) != iperf_data_columns:
        continue
    interval = data[-3].split('-')
    if len(interval) != 2:
        continue
    if float(interval[0]) == 0.0 or float(interval[1]) > args.time:
      continue
    output.append(float(data[-1]))

  if len(output) > 0:
    val = np.mean(output)
    if f.find('client') >= 0:
      throughput[flow].append(float(val))
    else:
      max_throughput = float(val)
  else:
    #print "         ERROR!!!!!!!!!!!!!!!!!!!"  
    pass

#print throughput 

avgThroughput = []
tcp_points = []
mptcp_points = []


xaxis=[]
ymean=[]
ymin_mean=[]
ymax_mean=[]


m.rc('figure', figsize=(8, 6))
fig = plt.figure()
title = 'Fat Tree (k=%s), %s workload' % (args.k, args.workload)
# plot rank of flow
axPlot = fig.add_subplot(1, 1, 1)
axPlot.grid(True)

colors = ['#ff0000','#ff7f00','#ffff00','#00ff00','#00ffff', '#0000ff', '#4B0082','#8F00FF']

fmdtcp =open('mdtcp_goodput','w')

max_throughput=float((20.0*1e6))
print(max_throughput)

for i in sorted(throughput.keys()):
  #print i 
  vals = [ 100.0 * x / max_throughput  for x in throughput[i] ] 
  avgThroughput.append(np.mean(vals))
  avg,avg_lci,avg_hci = mean_95conf(throughput[i])
  fmdtcp.write(str(i)+','+str(np.mean(vals))+'\n')

  #fmdtcp.write(str(i)+','+str(avg)+','+str(avg_lci)+','+str(avg_hci)+'\n')

  tcp_points = sorted(vals)
  xaxis = range(len(tcp_points))
  
   
  slabel=str(i)+" subflows"
  

  axPlot.plot(xaxis, tcp_points, lw=2, label=slabel,color=colors[int(i)-1])
fmdtcp.close()

#print avgThroughput
#print max_throughput


axPlot.legend(loc='lower right')
axPlot.set_xlabel("Rank of Flow")
axPlot.set_ylabel("Throughput (% of optimal)")
# axPlot.set_ylim(0, 105)
axPlot.grid(True)
# axPlot.set_title( title )
rank="plots/rank"+args.out.split("/")[1]

plt.savefig(rank)
# plot histogram
 
m.rc('figure', figsize=(8, 6))
fig = plt.figure()
N = 8
# # labels = ('1', '2', '3', '4')
labels = ('1', '2', '3', '4', '5', '6', '7', '8')
xaxis = np.arange(N)  # the x locations for the groups
width = 0.5 
xoffset = (1 - width) / 2

axHist = fig.add_subplot(1, 1, 1)
axHist.grid(True)
axHist.bar(xaxis + xoffset+0.25, avgThroughput, width, color='k') #, yerr=menStd)

axHist.set_xlabel("Number of subflows")
axHist.set_ylabel("Throughput (% of optimal)")
# # axHist.set_title( title )
axHist.set_xticks(xaxis + width/2 + xoffset)
axHist.set_xticklabels( labels )
# # axHist.set_yticks(np.arange(0, 100, step=15))
# axHist.set_ylim(0, 105)

if args.out:
     print 'saving to', args.out
     plt.savefig(args.out)
else:
     plt.show()

