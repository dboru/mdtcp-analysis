# from util.helper import *

from collections import defaultdict
import argparse
import numpy as np
import matplotlib as m
import matplotlib.pyplot as plt
import seaborn as sns

parser = argparse.ArgumentParser()
parser.add_argument('-f', dest="files", required=True)
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
def cdf(values):
  values.sort()
  prob = 0
  l = len(values)
  x, y = [], []
  for v in values:
      prob += 1.0 / l
      x.append(v)
      y.append(prob)
  return (x, y)
def pc95(lst):
  l = len(lst)
  return sorted(lst)[ int(0.95 * l) ]
def pc99(lst):
  l = len(lst)
  return sorted(lst)[ int(0.99 * l) ]
def average_result(input_tuple_list, index):
  input_list=[]
  for x in input_tuple_list:
    input_list.extend(x[index])
  if len(input_list) > 0:
    # print(sum(input_list) / len(input_list))
    return sum(input_list) / len(input_list)
  else:
    return 0
def median_result(input_tuple_list, index):
  L=[]
  for x in input_tuple_list:
    L.extend(x[index])
  size=len(L)
  if size%2==1:
    return L[(size-1)/2]
  else:
    return(L[size/2-1]+L[size/2])/2.0
def p99_result(input_tuple_list, index):
  L=[]
  for x in input_tuple_list:
    L.extend(x[index])
  return sorted(L)[ int(0.99 * len(L)) ]
def p95_result(input_tuple_list, index):
  L=[]
  for x in input_tuple_list:
    L.extend(x[index])
  return sorted(L)[ int(0.95 * len(L)) ]
data={}

# results/pareto1-mdtcp-180908-load1.0bw100g2delay5.0avgalfa1numreqs200ft4qmon0parto_mean60/one_to_several

colors = ['red','blue','black','green','purple','grey','cyan','yellow','#ff0000','#ff7f00',\
'#ffff00','#00ff00','#00ffff', '#0000ff', '#4B0082','#8F00FF']
markers=['o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'X']
patterns = ('-', '+', 'x', '\\', '*', 'o', 'O', '.')

# sns.set()
# plt.style.use('seaborn-paper')
# plt.style.use('dark_background')
m.rc('figure', figsize=(8, 6))
m.rcParams['font.family'] = 'sans'
m.rcParams['font.style']='normal'
# m.rcParams['font.size']=14
# m.rcParams.update({'font.size':14})

flows=[1,2,3,4,5,6,7,8]

def plot_mean_normalized(y):
  fig = plt.figure()
  axPlot = fig.add_subplot(1, 1, 1)
  axPlot.grid(True)
  # mean
  j=0
  for flow in flows:
    if flow==1:
      llabel='DCTCP'
    else:
      llabel='MDTCP['+str(flow)+'SFs]'
    axPlot.bar(xaxis + (flow-1)*xoffset, y['mean_n'][flow], width,edgecolor='black',color=colors[j],hatch=patterns[j],label=llabel)
    j+=1
  axPlot.set_xlabel("Flow size",fontsize=12)
  axPlot.set_xticks(xaxis + 0.35)
  axPlot.set_xticklabels(xticklabel,fontsize=12)
  axPlot.set_ylabel("Normalized mean FCT",fontsize=12)
  axPlot.legend(ncol=2,loc='upper right',fontsize=11)
  plt.savefig('plots/'+args.out+'-nmean.png')

def plot_median_normalized(y):
  fig = plt.figure()
  axPlot = fig.add_subplot(1, 1, 1)
  axPlot.grid(True) 
  j=0
  # median
  for flow in flows:
    if flow==1:
      llabel='DCTCP'
    else:
      llabel='MDTCP['+str(flow)+'SFs]'
    axPlot.bar(xaxis + (flow-1)*xoffset, y['median_n'][flow], width,edgecolor='black',color=colors[j],hatch=patterns[j],label=llabel)
    j+=1
  axPlot.set_xlabel("Flow size",fontsize=12)
  axPlot.set_xticks(xaxis + 0.35)
  axPlot.set_xticklabels(xticklabel,fontsize=12)
  axPlot.set_ylabel("Normalized median FCT",fontsize=12)
  axPlot.legend(ncol=2,loc='upper right',fontsize=11)
  plt.savefig('plots/'+args.out+'-median.png')
def plot_tail99th_normalized(y):
  fig = plt.figure()
  axPlot = fig.add_subplot(1, 1, 1)
  axPlot.grid(True)
  j=0
  # 99th tail latency
  for flow in flows:
    if flow==1:
      llabel='DCTCP'
    else:
      llabel='MDTCP['+str(flow)+'SFs]'
    axPlot.bar(xaxis + (flow-1)*xoffset, y['99_n'][flow], width,edgecolor='black',color=colors[j],hatch=patterns[j],label=llabel)
    j+=1
  axPlot.set_xlabel("Flow size",fontsize=12)
  axPlot.set_xticks(xaxis + 0.35)
  axPlot.set_xticklabels(xticklabel,fontsize=12)
  axPlot.set_ylabel("Normalized 99th FCT",fontsize=12)
  axPlot.legend(ncol=2,loc='upper left',fontsize=11)
  plt.savefig('plots/'+args.out+'-n99.png')

def plot_retransmits(y):
  m.rc('figure', figsize=(6.5, 5))
  fig = plt.figure()
  axPlot = fig.add_subplot(1, 1, 1)
  axPlot.grid(True)
  j=0
  retx=[]
  # print(y['retx'])
  for flow in range(1,9):
    retx.append(y['retx'][flow])
  axPlot.plot(flows, retx,marker='*',markersize=12,linewidth=2)
  axPlot.set_ylabel("No. of retransmissions",fontsize=12)
  axPlot.ticklabel_format(axis='y',style='sci',scilimits=(0,0))
  axPlot.set_xlabel("No. of subflows",fontsize=12)
  plt.savefig('plots/'+args.out+'-retransmit.png')



# process file 
for line in open(args.files).xreadlines():
  fields=line.split(',')
  flow=(fields[-1].split()[0])
  if flow not in data.keys():
    data[flow]={}
    data[flow]['fct']={}
    data[flow]['retx']=[]
  # flow size
  size=int(fields[-3])
  data[flow]['retx'].append(int(fields[-4]))
  # FCT in ms 
  fct=1000.0*float(fields[-2]) 
  if size in data[flow]['fct']:
    # fct in milliseconds
    data[flow]['fct'][size].append(fct)
  else:
    data[flow]['fct'][size]=[fct]
j=0
# flows=[1,2,4,8]
flows=[1,2,3,4,5,6,7,8]
N=3;
xaxis = np.arange(N)  # the x locations for the groups
width = 0.1 
xoffset = 0.119
# normalized values
y={'mean':{},'median':{},'99':{},'95':{},'mean_n':{},'median_n':{},'99_n':{},'95_n':{},'retx':{}}
# print(plt.style.available)
# plt.style.use('seaborn-dark')


fig = plt.figure()
axPlot = fig.add_subplot(1, 1, 1)
axPlot.grid(True)


data_1={}
xticklabel=['(0,100KB)','[100KB,10MB)','[10MB,inf)']
# to get base fct in ms
bw=100.0 
# base RTT
bdelay=0.3

for flow in flows:
  y_all=[]
  x_all=[]
  # patition flows to small, mediumn and large
  for size in sorted(data[str(flow)]['fct'].keys()):
    # if size < 100:
    x_all.append(size)
    bfct=bdelay+size/bw
    y_all.append(average(data[str(flow)]['fct'][size])/bfct)
    # if flow == 1:
    #   data_1[size]=average(data[str(flow)]['fct'][size])

    #   x_all.append(size)
    #   y_all.append(average(data[str(flow)]['fct'][size])/average(data[str(flow)]['fct'][size]))
    # else:
    #   if size in data_1.keys():
    #     x_all.append(size)
    #     # normalize wrt single path
    #     y_all.append(average(data[str(flow)]['fct'][size])/data_1[size])
  small = filter(lambda x: x[0] < 100, data[str(flow)]['fct'].items())
  medium = filter(lambda x: 100 <= x[0] < 10 * 1024, data[str(flow)]['fct'].items())
  large = filter(lambda x: x[0] >= 10 * 1024, data[str(flow)]['fct'].items())

  y['mean'][flow]=[]
  y['median'][flow]=[]
  y['99'][flow]=[]
  y['95'][flow]=[]
  y['retx'][flow]={}
  y['mean_n'][flow]=[]
  y['median_n'][flow]=[]
  y['99_n'][flow]=[]
  y['95_n'][flow]=[]
  
  y['retx'][flow]=sum(data[str(flow)]['retx'])
  # mean, median, 99th,95th real values
  y['mean'][flow].append(average_result(small, 1))
  y['mean'][flow].append(average_result(medium, 1))
  y['mean'][flow].append(average_result(large, 1))

  y['median'][flow].append(median_result(small, 1))
  y['median'][flow].append(median_result(medium, 1))
  y['median'][flow].append(median_result(large, 1))

  y['99'][flow].append(p99_result(small, 1))
  y['99'][flow].append(p99_result(medium, 1))
  y['99'][flow].append(p99_result(large, 1))

  y['95'][flow].append(p95_result(small, 1))
  y['95'][flow].append(p95_result(medium, 1))
  y['95'][flow].append(p95_result(large, 1))
  
  # mean, median, 99th, 95th normalized wrt single path DCTCP 

  y['median_n'][flow].append(median_result(small, 1)/y['median'][1][0])
  y['median_n'][flow].append(median_result(medium, 1)/y['median'][1][1])
  y['median_n'][flow].append(median_result(large, 1)/y['median'][1][2])

  y['99_n'][flow].append(p99_result(small, 1)/y['99'][1][0])
  y['99_n'][flow].append(p99_result(medium, 1)/y['99'][1][1])
  y['99_n'][flow].append(p99_result(large, 1)/y['99'][1][2])

  y['95_n'][flow].append(p95_result(small, 1)/y['95'][1][0])
  y['95_n'][flow].append(p95_result(medium, 1)/y['95'][1][1])
  y['95_n'][flow].append(p95_result(large, 1)/y['95'][1][2])

  y['mean_n'][flow].append(average_result(small, 1)/y['mean'][1][0])
  y['mean_n'][flow].append(average_result(medium, 1)/y['mean'][1][1])
  y['mean_n'][flow].append(average_result(large, 1)/y['mean'][1][2])

  if flow==1:
    llabel='DCTCP'
  else:
    llabel='MDTCP['+str(flow)+'SFs]'
  # all flow sizes
  axPlot.loglog(x_all, y_all,basex=10,basey=10,linewidth=3,label=llabel,\
   color=colors[j],marker=markers[j],markersize=6)
  # ,marker=markers[j],markersize=12
  # axPlot.tick_params(length=6,width=2)
  j=j+1

# print((data[str(flow)]['fct'].keys()))
axPlot.set_ylabel("Normalized mean FCT",fontsize=12)
axPlot.set_xlabel("Flow size [KB]",fontsize=12)
axPlot.legend(ncol=2,loc='upper right',fontsize=11)
# axPlot.scale('log',basey=10,basex=10)
plt.savefig('plots/'+args.out+'-nmean_fct.png')
# plt.show()

plot_mean_normalized(y)
plot_median_normalized(y)
plot_tail99th_normalized(y)
plot_retransmits(y)







