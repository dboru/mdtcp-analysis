# from util.helper import *
from collections import defaultdict

import argparse

import numpy as np

import matplotlib as m

import matplotlib.pyplot as plt

import re



parser = argparse.ArgumentParser()

parser.add_argument('-f', dest="file", required=True)

parser.add_argument('-o', '--out', dest="out", default=None)

parser.add_argument('-p', '--proto', dest="proto", default=None)


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



def plot_retransmits(y):

  fig = plt.figure()

  axPlot = fig.add_subplot(1, 1, 1)

  axPlot.grid(True)

  j=0

  y=[]

  # 99th tail latency

  for flow in flows:

    y.append(y['retx'][flow])

  axPlot.plot(flows, y['retx'][flow],marker='x',markersize=10)

  axPlot.set_ylabel("No. of retransmissions")

  axPlot.set_xlabel("No. of subflows")

  plt.savefig('plots/'+args.out+'-retransmit.png')





def layer(name,K):

    ''' Return layer of node '''

    # node = self.node_gen(name = name) 

    name=name.split('-')

    iface=name[1]

    name=name[0]

    name_str=name.split('h')

    if int(name_str[0])==K:

      return 'core'

    elif int(name_str[2])==1:

      if int(name_str[1]) < K/2:

        return 'edge'

      else:

        return 'agg'

    else:

        return 'host'



def link_util():

  bwmng={} 

  tstart=0

  flow = 4

  if flow not in bwmng.keys():

    # bwmng[flow]={'all-in':[],'all-out':[]}

    bwmng[flow]={}

    # 1536776549,2h3h1-eth1,769960.44,4248653.50,5018614.00,429114,77766,980.20,15653.47,16633.66,1581,99,0.00,0.00,0,0

  for line in open(args.file).xreadlines():



    if 'lo' not in line and 'total' not in line and 'eno1' not in line:

      bw=line.split(',')

      if len(bw) ==16 and (8*float(bw[2])/1e6 > 10.0 or 8*float(bw[3])/1e6 > 10.0):

        if bw[1] not in bwmng[flow].keys():

          bwmng[flow][bw[1]]={}

          bwmng[flow][bw[1]]['in']=[0.8*float(bw[3])/1e6]

          bwmng[flow][bw[1]]['out']=[0.8*float(bw[2])/1e6]



          if tstart==0.0:

            bwmng[flow][bw[1]]['time']=[0]

            tstart=int(bw[0])

          else:

            bwmng[flow][bw[1]]['time']=[int(bw[0])-tstart]



        else:

          bwmng[flow][bw[1]]['in'].append(0.8*float(bw[3])/1e6)

          bwmng[flow][bw[1]]['out'].append(0.8*float(bw[2])/1e6)

          bwmng[flow][bw[1]]['time'].append(int(bw[0])-tstart)

        # bwmng[flow]['all-in'].append(8*float(bw[3])/1e6)

        # bwmng[flow]['all-out'].append(8*float(bw[2])/1e6)

      else:

        continue

    else:

      pass



  return bwmng





def main():

  font = {'family' : 'sans serif','weight' :'normal','size': 10}

  plt.rc('font', **font)

  colors=['blue','red','green','black','magenta','cyan','yellow','orange','purple']

  ulink=link_util()



  core=[]

  agg=[]

  edge=[]

  hosts=[]

  for iface in ulink[4].keys():

    if 'total' not in iface:

      net=layer(iface,4)

      if net=='core':

        core.append(iface)

      elif net=='agg':

        agg.append(iface)

      elif net=='edge':

        edge.append(iface)

      else:

        hosts.append(iface)



  agg=(sorted(agg))

  core=(sorted(core))

  edge=(sorted(edge))



#Plot utiliations 

  # core layer utilization 

  fig=plt.figure()

  for k in range(4):

    axPlot = fig.add_subplot(2, 2, k+1)

    c=0

    for iface in core[4*k:4+4*k]:

      axPlot.plot(ulink[4][iface]['time'],ulink[4][iface]['in'],label='UL_'+iface.split('-')[1],color=colors[c])

      c=c+1

      axPlot.plot(ulink[4][iface]['time'],ulink[4][iface]['out'],label='DL_'+iface.split('-')[1],color=colors[c])

      c=c+1

    if k==0 :
      axPlot.legend(loc='upper center', bbox_to_anchor=(1.1, 1.3),ncol=4, fontsize=8, columnspacing=1.0, handlelength=0.5,fancybox=False, shadow=True)
    if k%2==0:
      axPlot.set_ylabel('Utlization',fontsize=8)
    # axPlot.set_yticks(np.arange(0, 1.2, 0.3))
    if k==2 or k==3:
      axPlot.set_xlabel('Time (secs)')
    else:
      axPlot.set_xticklabels([])
    if k==1:
      axPlot.set_title('Core('+str(k)+')',fontsize=6,loc='right')
    else:
      axPlot.set_title('Core('+str(k)+')',fontsize=6,loc='left')

    plt.savefig(args.out+'-core-util.pdf')

  # elif 'flows1g4' in args.file and 'mdtcp' in args.file:

  

  #Aggregation layer utilization

  fig = plt.figure()

  for k in range(8):

    axPlot = fig.add_subplot(4, 2, k+1)

    c=0

    for iface in edge[4*k:4+4*k]:

      if 'eth1' in iface or 'eth2' in iface:

        axPlot.plot(ulink[4][iface]['time'],ulink[4][iface]['in'],label='UL_'+iface.split('-')[1],color=colors[c])

        c=c+1

        axPlot.plot(ulink[4][iface]['time'],ulink[4][iface]['out'],label='DL_'+iface.split('-')[1],color=colors[c])

        c=c+1
    if k==0 :
      axPlot.legend(loc='upper center', bbox_to_anchor=(1.2, 1.4),ncol=4, fontsize=8, columnspacing=1.0, handlelength=0.5,fancybox=False, shadow=True)
    if k%2==0:
      axPlot.set_ylabel('Utlization',fontsize=8)
    axPlot.set_yticks(np.arange(0, 1.2, 0.3))
    if k==6 or k==7:
      axPlot.set_xlabel('Time (secs)')
    else:
      axPlot.set_xticklabels([])
    if k==1:
      axPlot.set_title('Agg('+str(k)+')',fontsize=6,loc='right')
    else:
      axPlot.set_title('Agg('+str(k)+')',fontsize=6,loc='left')

  plt.savefig(args.out+'-agg-util.pdf')

  

  #Edge layer (host-to edge)

  fig = plt.figure()

  for k in range(8):

    axPlot = fig.add_subplot(4, 2, k+1)

    c=0

    for iface in edge[4*k:4+4*k]:

      if 'eth1' in iface or 'eth2' in iface:

        axPlot.plot(ulink[4][iface]['time'],ulink[4][iface]['in'],label='UL_'+iface.split('-')[1],color=colors[c])

        c=c+1

        axPlot.plot(ulink[4][iface]['time'],ulink[4][iface]['out'],label='DL_'+iface.split('-')[1],color=colors[c])

        c=c+1

    if k==0:
      axPlot.legend(loc='upper center', bbox_to_anchor=(1.2, 1.4),ncol=4, fontsize=8, columnspacing=1.0, handlelength=0.5,fancybox=False, shadow=True)
    if k%2==0:
      axPlot.set_ylabel('Utlization',fontsize=8)
    axPlot.set_yticks(np.arange(0, 1.2, 0.3))
    if k==6 or k==7:
      axPlot.set_xlabel('Time (secs)')
    else:
      axPlot.set_xticklabels([])
    if k==1:
      axPlot.set_title('Edge('+str(k)+')',fontsize=6,loc='right')
    else:
      axPlot.set_title('Edge('+str(k)+')',fontsize=6,loc='left')

    

  # if 'flows4g4' in args.file and 'mdtcp' in args.file:

  plt.savefig(args.out+'-edge-util.pdf')

if __name__ == '__main__':
  main()





















