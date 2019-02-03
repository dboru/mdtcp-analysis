# from util.helper import *

from collections import defaultdict

import argparse

import numpy as np

import matplotlib as m

m.use('Agg')

import matplotlib.pyplot as plt

import re


parser = argparse.ArgumentParser()

parser.add_argument('-f', dest="files",nargs='+', required=True)

parser.add_argument('-o', '--out', dest="out", default=None)
parser.add_argument('-b', '--bw', dest="bw",type=int, default=10)
parser.add_argument('-m', '--maxq', dest="maxq",type=int, default=1000)
parser.add_argument('-p', '--proto', dest="proto", default=None)

args = parser.parse_args()


NUM_COLORS = 36
cm = plt.get_cmap('gist_rainbow')

colors=[cm(1.*i/NUM_COLORS) for i in range(NUM_COLORS)]


def plot_queue_stats(queue):

  font = {'family' : 'sans serif','weight' :'normal','size': 10}

  plt.rc('font', **font)

  # colors=['blue','red','green','black','magenta','cyan','yellow','orange','purple']


  fig = plt.figure()

  axplot = fig.add_subplot(221)

  axplot1 = fig.add_subplot(222)

  axplot2 = fig.add_subplot(223)

  c=0;
  max_q=0

  for a in sorted(queue.keys()):
    if 'core' in a and len(queue[a]['time'])>0:
      # core.append(queue[a])
      # print(queue[a]['time'][0])
      queue[a]['time'][0]=0
      # if max(queue[a]['queue']) > max_q:
      #   max_q=max(queue[a]['queue'])
      #   print(len(queue[a]['queue']),max_q)
      axplot.plot(queue[a]['time'],queue[a]['queue'],color=colors[c])
    elif 'agg' in a and len(queue[a]['time'])>0:
      # print(a,queue[a]['queue'])
      queue[a]['time'][0]=0
      # if max(queue[a]['queue']) > max_q:
      #   max_q=max(queue[a]['queue'])
      #   print(len(queue[a]['queue']),max_q)
      axplot1.plot(queue[a]['time'],queue[a]['queue'],color=colors[c])
      # agg.append(queue[a])
    elif 'edge' in a and len(queue[a]['time'])>0:
      
      queue[a]['time'][0]=0
      # if max(queue[a]['queue']) > max_q:
      #   max_q=max(queue[a]['queue'])
      #   print(len(queue[a]['queue']),max_q)
      axplot2.plot(queue[a]['time'],queue[a]['queue'],color=colors[c])
    if c==len(colors)-1:
      c=0
    else:
      c=c+1

      # edge.append(queue[a])

  axplot.set_title('Core')
  axplot.set_ylabel('Queue [Kbytes]')
  axplot.set_xticklabels([])
  # axplot.set_xlim(5,30)
  # axplot.set_ylim(0,max_q+5)

  axplot1.set_title('Agg')
  # axplot1.set_ylabel('Queue [Pkts]')
  axplot1.set_xlabel('Time [secs]')
  # axplot1.set_xlim(5,30)
  # axplot1.set_ylim(0,max_q+5)
  axplot1.grid(True)
  axplot2.grid(True)
  axplot.grid(True)

  axplot2.set_title('Edge')
  axplot2.set_ylabel('Queue [Kbytes]')
  axplot2.set_xlabel('Time [secs]')
  # axplot2.set_xlim(5,30)
  # axplot2.set_ylim(0,max_q+5)
  plt.savefig(args.out+'queue.pdf')


def main():

  queue={}
  first_time=0;

  for f in args.files:
    layer=None
    # queue_size_core-4_2_2-eth4_iter1.txt

    if 'queue_size' in f:
      ll=(f.split('queue_size'))
      for l in range (len(ll)):
        if '-eth' in ll[l]:
          layer=ll[l].split('iter')[0].strip('_')
          break
      
      if layer:

        if layer not in queue.keys():
          queue[layer]={'time':[],'queue':[]}
          first_entry=0

        for line in open(f).xreadlines():
          aline=(line.split(','))
          if len(aline)==2 and int(aline[1]) <= (1024*args.maxq):
            if first_time==0:
              first_time=float(aline[0]);
            elif float(aline[0]) - first_time > 5.0:
              if first_entry==0:
                queue[layer]['time'].append(float(aline[0]))
                queue[layer]['queue'].append((int(aline[1])/1000.0))
                first_entry=1
              else:
                diff_time=float(aline[0])-queue[layer]['time'][0]
                queue[layer]['time'].append(diff_time)
                queue[layer]['queue'].append((int(aline[1])/1000.0))


  if queue:
    plot_queue_stats(queue)

if __name__ == '__main__':
  main()





















