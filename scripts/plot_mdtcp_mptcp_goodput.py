from monitor.helper import *
from collections import defaultdict
import argparse
import numpy as np


m.rc('figure', figsize=(8, 6))
fig = plt.figure()
# title = 'Fat Tree (k=%s), %s workload' % (args.k, args.workload)
# plot rank of flow
# axPlot = fig.add_subplot(1, 1, 1)
# axPlot.grid(True)

colors = ['#ff0000','#ff7f00','#ffff00','#00ff00','#00ffff', '#0000ff', '#4B0082','#8F00FF']

fmptcp =open('mptcp_goodput','r')
fmdtcp =open('mdtcp_goodput','r')
data={}
data['mdtcp']=[]
data['mptcp']=[]
subflows=[]

for line in open('mdtcp_goodput').xreadlines():
  data['mdtcp'].append(float(line.split(',')[1]))
  subflows.append(int(line.split(',')[0]))

for line in open('mptcp_goodput').xreadlines():
  data['mptcp'].append(float(line.split(',')[1]))


N = 8
# labels = ('1', '2', '3', '4')
labels = ('1', '2', '3', '4', '5', '6', '7', '8')
xaxis = np.arange(N)  # the x locations for the groups
width = 0.35 
xoffset = (1 - width) / 2

axHist = fig.add_subplot(1, 1, 1)
axHist.grid(True)
axHist.bar(xaxis + xoffset+0.25, data['mptcp'], width, color='blue',label='MPTCP') #, yerr=menStd)
axHist.bar(xaxis + xoffset+0.623, data['mdtcp'], width, color='black',label='MDTCP') #, yerr=menStd)
axHist.set_xlabel("Number of Subflows")
axHist.set_ylabel("Average throughput (% of optimal)")
# axHist.set_title( title )
axHist.set_xticks(xaxis + width+0.07 + xoffset)
axHist.set_xticklabels( labels )
axHist.legend(loc='upper left')
# axHist.set_ylim(0, 100)

# if args.out:
#     print 'saving to', args.out
plt.savefig("plots/goodput_mdtcp_mptcp.png")
# else:
plt.show()



