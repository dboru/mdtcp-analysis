# from util.helper import *



from collections import defaultdict



import argparse



import numpy as np



import matplotlib as m



m.use('Agg')



import statsmodels.api as sm 

# recommended import according to the docs



import matplotlib.pyplot as plt

import os

import re





parser = argparse.ArgumentParser()



# parser.add_argument('-f', dest="files",nargs='+', required=True)

# parser.add_argument('-path', '--path', dest="path", default=None)

parser.add_argument('-o', '--out', dest="out", default=None)

parser.add_argument('-b', '--bw', dest="bw",type=int, default=10)

parser.add_argument('-m', '--maxq', dest="maxq",type=int, default=1000)

parser.add_argument('-p', '--proto', dest="proto", default=None)



args = parser.parse_args()





NUM_COLORS = 36

cm = plt.get_cmap('gist_rainbow')



colors=[cm(1.*i/NUM_COLORS) for i in range(NUM_COLORS)]



def emcdf(data):

  ecdf = sm.distributions.ECDF(data)

  x = np.linspace(min(data), max(data))

  y = ecdf(x)

  return x,y





def parse_queue(f):

  # goodput-mdtcp-20190204-bw10delay0.1ft4runtime60



  queue=[]

  first_time=0

  

  for line in open(f).xreadlines():

    aline=line.split(',')

    if len(aline)==2 and int(aline[1]) <= (5*1000*args.maxq):

      if first_time==0:

        first_time=float(aline[0]);

      elif float(aline[0]) - first_time > 2.0:

        queue.append((int(aline[1])/1000.0))



  return queue





def main():



  font = {'family' : 'sans serif','weight' :'normal','size': 10}



  plt.rc('font', **font)



  colors=['blue','red','green','black','magenta','cyan','yellow','orange','purple']



  fig=plt.figure()

  axPlot = fig.add_subplot(1, 1, 1)

  i=0
  for f in ['dctcp-n3-bw100/qlen_s1-eth1.txt','mdtcp-n3-bw100/qlen_s1-eth1.txt','mptcp-n3-bw100/qlen_s1-eth1.txt','tcpecn-n3-bw100/qlen_s1-eth1.txt','tcp-n3-bw100/qlen_s1-eth1.txt']:
  
    queue=parse_queue(f)

    queue_x,cdf_y=emcdf(queue)

    if 'dctcp' in f:
      llabel='DCTCP'
    elif 'mdtcp' in f:
      llabel='MDTCP[SF4]'
    elif 'mptcp' in f:
      llabel='MPTCP[SF4]'
    elif 'tcpecn' in f:
      llabel='TCP-RED-ECN'
    elif 'tcp-n3' in f:
      llabel='TCP-RED'

   
    axPlot.plot(queue_x,cdf_y,label=llabel,color=colors[i],linewidth=4,marker='.')

    i+=1



  axPlot.set_xlabel('Queue (KBytes)')

  axPlot.set_ylabel('CDF')

  axPlot.grid(True)

  plt.legend(ncol=1,loc='lower right')

  plt.savefig(args.out+'-queue.pdf')

  



if __name__ == '__main__':

  main()















































