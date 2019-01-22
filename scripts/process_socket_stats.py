# from util.helper import *

from collections import defaultdict
import argparse
import numpy as np
import matplotlib as m
import matplotlib.pyplot as plt
import re

parser = argparse.ArgumentParser()
parser.add_argument('-f', dest="files",nargs='+', required=True)
parser.add_argument('-o', '--out', dest="out", default=None)
parser.add_argument('-p', '--proto', dest="proto", default=None)
parser.add_argument('-n', '--name', dest="name", default=None)
args = parser.parse_args()


def plot_socket_stats(ss):
  font = {'family' : 'sans serif','weight' :'normal','size': 10}
  plt.rc('font', **font)
  colors=['blue','red','green','black','magenta','cyan','yellow','orange','purple']
  
  params=['cwnd','rtt','retrans','reorder']
  # retrans=[]
  
  for p in params:
    retx_reorder=[]

    fig = plt.figure()
    axPlot = fig.add_subplot(111)
    for cs in ss.keys():
      if (p =='retrans' or p == 'reorder' ) and p in ss[cs].keys():
        retx_reorder.append(ss[cs][p])
      else:
        if  p in ss[cs].keys() and len(ss[cs][p])>0:
          axPlot.plot(ss[cs][p])
    if p == 'cwnd':
      axPlot.set_ylabel('Cwnd [Pkts]')
    elif p=='rtt':
      axPlot.set_ylabel('RTT [ms]')
    elif p=='retrans':
      axPlot.plot(retx_reorder, marker='.')
      # axPlot.plot(retx_reorder)
      axPlot.set_ylabel('No. retrans')
      axPlot.set_xlabel('Connection ID')
    elif p=='reorder':
      # axPlot.plot(retx_reorder)
      axPlot.plot(retx_reorder, marker='.')
      axPlot.set_ylabel('No. reordering')
      axPlot.set_xlabel('Connection ID')

    if 'ss_clnt' in args.files[0]:
      plt.savefig(args.out+'/'+p+'-'+args.name+'.pdf')
    elif 'ss_serv' in args.files[0]:
      plt.savefig(args.out+'/'+p+'-'+args.name+'.pdf')

  
def main():
  # socket stats
  ss={}
  estab=0
  for f in args.files:
    print(f)
    for line in open(f).xreadlines():
      if 'ESTAB' in line:
        estab=1
        aline=(line.split())
        cs=aline[3]+'_'+aline[4]
        if cs not in ss.keys():
          ss[cs]={}
      elif estab and 'cwnd' in line:
        aline=((line.split()))
        for l in range(len(aline)):
          if 'cwnd' in aline[l]:
            cwnd=int(aline[l].split(':')[1])
            if 'cwnd' not in ss[cs].keys():
              ss[cs]['cwnd']=[cwnd]
            else:
              ss[cs]['cwnd'].append(cwnd)
          elif 'retrans' in aline[l]:
            # total retrans
            retx=int(aline[l].split(':')[1].split('/')[1])
            if 'retrans' not in ss[cs].keys():
              ss[cs]['retrans']=retx
            else:
              ss[cs]['retrans']=retx
          elif 'rtt' in aline[l]:
            rtt=float(aline[l].split(':')[1].split('/')[0])
            if 'rtt' not in ss[cs].keys():
              ss[cs]['rtt']=[rtt]
            else:
              ss[cs]['rtt'].append(rtt)
          elif 'reordering' in aline[l]:
            reorder=int(aline[l].split(':')[1])
            if 'reorder' not in ss[cs].keys():
              ss[cs]['reorder']=reorder
            else:
              ss[cs]['reorder']=reorder
        estab=0
        # print(aline)
  
  plot_socket_stats(ss)
    # print(ss)
        
   

  

if __name__ == '__main__':
  
  main()










