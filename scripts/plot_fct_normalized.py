import sys
import os
import argparse
import csv
# import matplotlib as m
# import matplotlib.pyplot as plt
import numpy as np
from numpy import average, std
from math import sqrt
# from util.helper import *

import matplotlib.pyplot as plt
# import numpy as np

# tshark -r trace-iface-0h0h1-eth4.pcap -q -z io,stat,5,
# "COUNT(tcp.analysis.retransmission)tcp.analysis.retransmission",
# "COUNT(tcp.analysis.duplicate_ack)tcp.analysis.duplicate_ack","COUNT(tcp.analysis.lost_segmentent)tcp.analysis.lost_segment",
# "COUNT(tcp.analysis.fast_retransmission)tcp.analysis.fast_retransmission"


fcts={'mdtcp':{'4':{'overall':[],'avg_sf':[],'avg_mf':[],'avg_lf':[],'50p_sf':[],\
'50p_mf':[],'50p_lf':[],'99p_sf':[],'99p_mf':[],'99p_lf':[]},\
'1':{'overall':[],'avg_sf':[],'avg_mf':[],'avg_lf':[],'50p_sf':[],'50p_mf':[],\
'50p_lf':[],'99p_sf':[],'99p_mf':[],'99p_lf':[]}},'mptcp':{'4':{'overall':[],\
'avg_sf':[],'avg_mf':[],'avg_lf':[],'50p_sf':[],'50p_mf':[],'50p_lf':[],\
'99p_sf':[],'99p_mf':[],'99p_lf':[]},'1':{'overall':[],'avg_sf':[],'avg_mf':[],\
'avg_lf':[],'50p_sf':[],'50p_mf':[],'50p_lf':[],'99p_sf':[],'99p_mf':[],'99p_lf':[]}}}


with open('fct_mptcp_mdtcp_webtest_181230',mode='r') as csv_file:
    csv_reader=csv.reader(csv_file,delimiter=',')
    for row in csv_reader:
    	if 'mdtcp' in row and row[1]=='1':
    		fcts['mdtcp']['1']['overall'].append(float(row[3]))
            
    		fcts['mdtcp']['1']['avg_sf'].append(float(row[4]))
    		fcts['mdtcp']['1']['avg_mf'].append(float(row[5]))
    		fcts['mdtcp']['1']['avg_lf'].append(float(row[6]))

    		fcts['mdtcp']['1']['50p_sf'].append(float(row[7]))
    		fcts['mdtcp']['1']['50p_mf'].append(float(row[8]))
    		fcts['mdtcp']['1']['50p_lf'].append(float(row[9]))

    		fcts['mdtcp']['1']['99p_sf'].append(float(row[10]))
    		fcts['mdtcp']['1']['99p_mf'].append(float(row[11]))
    		fcts['mdtcp']['1']['99p_lf'].append(float(row[12]))
    	elif 'mdtcp' in row and row[1]=='4':
    		fcts['mdtcp']['4']['overall'].append(float(row[3]))

    		fcts['mdtcp']['4']['avg_sf'].append(float(row[4]))
    		fcts['mdtcp']['4']['avg_mf'].append(float(row[5]))
    		fcts['mdtcp']['4']['avg_lf'].append(float(row[6]))

    		fcts['mdtcp']['4']['50p_sf'].append(float(row[7]))
    		fcts['mdtcp']['4']['50p_mf'].append(float(row[8]))
    		fcts['mdtcp']['4']['50p_lf'].append(float(row[9]))

    		fcts['mdtcp']['4']['99p_sf'].append(float(row[10]))
    		fcts['mdtcp']['4']['99p_mf'].append(float(row[11]))
    		fcts['mdtcp']['4']['99p_lf'].append(float(row[12]))

    	elif 'mptcp' in row and row[1]=='1':
    		fcts['mptcp']['1']['overall'].append(float(row[3]))

    		fcts['mptcp']['1']['avg_sf'].append(float(row[4]))
    		fcts['mptcp']['1']['avg_mf'].append(float(row[5]))
    		fcts['mptcp']['1']['avg_lf'].append(float(row[6]))

    		fcts['mptcp']['1']['50p_sf'].append(float(row[7]))
    		fcts['mptcp']['1']['50p_mf'].append(float(row[8]))
    		fcts['mptcp']['1']['50p_lf'].append(float(row[9]))

    		fcts['mptcp']['1']['99p_sf'].append(float(row[10]))
    		fcts['mptcp']['1']['99p_mf'].append(float(row[11]))
    		fcts['mptcp']['1']['99p_lf'].append(float(row[12]))
    		
    	elif 'mptcp' in row and row[1]=='4':
    		fcts['mptcp']['4']['overall'].append(float(row[3]))

    		fcts['mptcp']['4']['avg_sf'].append(float(row[4]))
    		fcts['mptcp']['4']['avg_mf'].append(float(row[5]))
    		fcts['mptcp']['4']['avg_lf'].append(float(row[6]))

    		fcts['mptcp']['4']['50p_sf'].append(float(row[7]))
    		fcts['mptcp']['4']['50p_mf'].append(float(row[8]))
    		fcts['mptcp']['4']['50p_lf'].append(float(row[9]))

    		fcts['mptcp']['4']['99p_sf'].append(float(row[10]))
    		fcts['mptcp']['4']['99p_mf'].append(float(row[11]))
    		fcts['mptcp']['4']['99p_lf'].append(float(row[12]))




font = {'family' : 'sans serif',
        'weight' : 'normal',
        'size'   : 14}

plt.rc('font', **font)


# m.rc('figure', figsize=(8, 6))
fig = plt.figure(figsize=(10, 8))
axPlot = fig.add_subplot(2, 2, 1)
axPlot.grid(True)
xaxis=[0.2,0.4,0.6,0.8,1.0]

colors = ['#ff0000','#ff7f00','#ffff00','#00ff00','#00ffff', '#0000ff', '#4B0082','#8F00FF']
dctcp=[]
mdtcp=[]
mptcp=[]
sptcp=[]
for v in range (len(fcts['mdtcp']['1']['overall'])):
    dctcp.append(1.0)
    mdtcp.append(fcts['mdtcp']['4']['overall'][v]/fcts['mdtcp']['1']['overall'][v])
    mptcp.append(fcts['mptcp']['4']['overall'][v]/fcts['mdtcp']['1']['overall'][v])
    sptcp.append(fcts['mptcp']['1']['overall'][v]/fcts['mdtcp']['1']['overall'][v])


axPlot.plot(xaxis, sptcp, lw=4, label='TCP',color='black',marker='o')
axPlot.plot(xaxis, mptcp, lw=4, label='MPTCP',color='red',marker='<')
# axPlot.plot(xaxis, dctcp, lw=4, label='DCTCP',color='red',marker='x')
axPlot.plot(xaxis, mdtcp,lw=4, label='MDTCP',color='blue',marker='v')



axPlot.legend(loc='lower right',ncol=3,fontsize=12)
axPlot.set_title('(a) Overall FCT',fontsize=12)
# axPlot.set_xlabel("Load")
axPlot.set_ylabel("Normalized FCT")


axPlot1 = fig.add_subplot(2, 2, 2)
axPlot1.grid(True)
xaxis=[0.2,0.4,0.6,0.8,1.0]
# print(str(fcts['mdtcp']['1']['avg_sf']))

dctcp=[]
mdtcp=[]
mptcp=[]
sptcp=[]
for v in range (len(fcts['mdtcp']['1']['avg_sf'])):
    dctcp.append(1.0)
    mdtcp.append(fcts['mdtcp']['4']['avg_sf'][v]/fcts['mdtcp']['1']['avg_sf'][v])
    mptcp.append(fcts['mptcp']['4']['avg_sf'][v]/fcts['mdtcp']['1']['avg_sf'][v])
    sptcp.append(fcts['mptcp']['1']['avg_sf'][v]/fcts['mdtcp']['1']['avg_sf'][v])

axPlot1.plot(xaxis, sptcp, lw=4, label='TCP',color='black',marker='o')
axPlot1.plot(xaxis, mptcp, lw=4, label='MPTCP',color='red',marker='<')
# axPlot1.plot(xaxis, dctcp, lw=4, label='DCTCP',color='red',marker='x')
axPlot1.plot(xaxis, mdtcp,lw=4, label='MDTCP',color='blue',marker='v')


axPlot1.legend(loc='lower right',ncol=3,fontsize=12)
# axPlot1.set_xlabel("Load")
axPlot1.set_title('(b) Mean FCT [0,100KB)',fontsize=12)
axPlot1.set_ylabel("Normalized FCT")

axPlot2 = fig.add_subplot(2, 2, 3)
axPlot2.grid(True)

dctcp=[]
mdtcp=[]
mptcp=[]
sptcp=[]

for v in range (len(fcts['mdtcp']['1']['avg_mf'])):
    dctcp.append(1.0)
    mdtcp.append(fcts['mdtcp']['4']['avg_mf'][v]/fcts['mdtcp']['1']['avg_mf'][v])
    mptcp.append(fcts['mptcp']['4']['avg_mf'][v]/fcts['mdtcp']['1']['avg_mf'][v])
    sptcp.append(fcts['mptcp']['1']['avg_mf'][v]/fcts['mdtcp']['1']['avg_mf'][v])


axPlot2.plot(xaxis,  sptcp, lw=4, label='TCP',color='black',marker='o')
axPlot2.plot(xaxis, mptcp, lw=4, label='MPTCP',color='red',marker='<')
# axPlot2.plot(xaxis, dctcp, lw=4, label='DCTCP',color='red',marker='x')
axPlot2.plot(xaxis, mdtcp,lw=4, label='MDTCP',color='blue',marker='v')



axPlot2.legend(loc='lower right',ncol=3,fontsize=12)
axPlot2.set_xlabel("Load")
axPlot2.set_title('(c) Mean FCT [100KB, 10MB)',fontsize=12)
axPlot2.set_ylabel("Normalized FCT")



axPlot3 = fig.add_subplot(2, 2, 4)
axPlot3.grid(True)
dctcp=[]
mdtcp=[]
mptcp=[]
sptcp=[]
for v in range (len(fcts['mdtcp']['1']['avg_lf'])):
    dctcp.append(1.0)
    mdtcp.append(fcts['mdtcp']['4']['avg_lf'][v]/fcts['mdtcp']['1']['avg_lf'][v])
    mptcp.append(fcts['mptcp']['4']['avg_lf'][v]/fcts['mdtcp']['1']['avg_lf'][v])
    sptcp.append(fcts['mptcp']['1']['avg_lf'][v]/fcts['mdtcp']['1']['avg_lf'][v])

axPlot3.plot(xaxis, sptcp, lw=4, label='TCP',color='black',marker='o')
axPlot3.plot(xaxis, mptcp, lw=4, label='MPTCP',color='red',marker='<')

# axPlot3.plot(xaxis, dctcp, lw=4, label='DCTCP',color='red',marker='x')
axPlot3.plot(xaxis, mdtcp,lw=4, label='MDTCP',color='blue',marker='v')

axPlot3.legend(loc='lower right',ncol=3,fontsize=12)
axPlot3.set_xlabel("Load")
axPlot3.set_title('(d) Mean FCT [10MB, 30MB]',fontsize=12)
axPlot3.set_ylabel("Normalized FCT")
plt.tight_layout()

plt.savefig('plots/overall_websearch-load100_norm.pdf')



# Plot median FCT


# m.rc('figure', figsize=(8, 6))
fig = plt.figure(figsize=(10, 8))
axPlot = fig.add_subplot(2, 2, 1)
axPlot.grid(True)
xaxis=[0.2,0.4,0.6,0.8,1.0]

dctcp=[]
mdtcp=[]
mptcp=[]
sptcp=[]
for v in range (len(fcts['mdtcp']['1']['50p_sf'])):
    dctcp.append(1.0)
    mdtcp.append(fcts['mdtcp']['4']['50p_sf'][v]/fcts['mdtcp']['1']['50p_sf'][v])
    mptcp.append(fcts['mptcp']['4']['50p_sf'][v]/fcts['mdtcp']['1']['50p_sf'][v])
    sptcp.append(fcts['mptcp']['1']['50p_sf'][v]/fcts['mdtcp']['1']['50p_sf'][v])

axPlot.plot(xaxis, sptcp, lw=4, label='TCP',color='black',marker='o')
axPlot.plot(xaxis, mptcp, lw=4, label='MPTCP',color='red',marker='<')
# axPlot.plot(xaxis, dctcp, lw=4, label='DCTCP',color='red',marker='x')
axPlot.plot(xaxis, mdtcp,lw=4, label='MDTCP',color='blue',marker='v')

axPlot.legend(loc='lower right',ncol=3,fontsize=12)
axPlot.set_title('(a) Median FCT (0,100KB)',fontsize=12)
# axPlot.set_xlabel("Load")
axPlot.set_ylabel("Normalized FCT")

axPlot2 = fig.add_subplot(2, 2, 2)


dctcp=[]
mdtcp=[]
mptcp=[]
sptcp=[]
for v in range (len(fcts['mdtcp']['1']['50p_mf'])):
    dctcp.append(1.0)
    mdtcp.append(fcts['mdtcp']['4']['50p_mf'][v]/fcts['mdtcp']['1']['50p_mf'][v])
    mptcp.append(fcts['mptcp']['4']['50p_mf'][v]/fcts['mdtcp']['1']['50p_mf'][v])
    sptcp.append(fcts['mptcp']['1']['50p_mf'][v]/fcts['mdtcp']['1']['50p_mf'][v])


axPlot2.plot(xaxis, sptcp, lw=4, label='TCP',color='black',marker='o')
axPlot2.plot(xaxis, mptcp, lw=4, label='MPTCP',color='red',marker='<')
# axPlot2.plot(xaxis, dctcp, lw=4, label='DCTCP',color='red',marker='x')
axPlot2.plot(xaxis, mdtcp,lw=4, label='MDTCP',color='blue',marker='v')


axPlot2.legend(loc='lower right',ncol=2,fontsize=12)
axPlot2.set_xlabel("Load")
axPlot2.set_title('(b) Median FCT [100KB, 10MB)',fontsize=12)
axPlot2.grid(True)
axPlot2.set_ylabel("Normalized FCT")

axPlot3 = fig.add_subplot(2, 2, (3,4))
axPlot3.grid(True)


dctcp=[]
mdtcp=[]
mptcp=[]
sptcp=[]
for v in range (len(fcts['mdtcp']['1']['50p_lf'])):
    dctcp.append(1.0)
    mdtcp.append(fcts['mdtcp']['4']['50p_lf'][v]/fcts['mdtcp']['1']['50p_lf'][v])
    mptcp.append(fcts['mptcp']['4']['50p_lf'][v]/fcts['mdtcp']['1']['50p_lf'][v])
    sptcp.append(fcts['mptcp']['1']['50p_lf'][v]/fcts['mdtcp']['1']['50p_lf'][v])

axPlot3.plot(xaxis, sptcp, lw=4, label='TCP',color='black',marker='o')
axPlot3.plot(xaxis, mptcp, lw=4, label='MPTCP',color='red',marker='<')
# axPlot3.plot(xaxis, dctcp, lw=4, label='DCTCP',color='red',marker='x')
axPlot3.plot(xaxis, mdtcp,lw=4, label='MDTCP',color='blue',marker='v')

axPlot3.legend(loc='lower right',ncol=3,fontsize=12)
axPlot3.set_xlabel("Load")
axPlot3.set_title('(c) Median FCT [10MB, 30MB]',fontsize=12)
axPlot3.set_ylabel("Normalized FCT")
plt.tight_layout()

plt.savefig('plots/median_websearch-load100_norm.pdf')

#plt.show()

# Plot 99th FCT


# m.rc('figure', figsize=(8, 6))
fig = plt.figure(figsize=(10, 8))
axPlot = fig.add_subplot(2, 2, 1)
axPlot.grid(True)
xaxis=[0.2,0.4,0.6,0.8,1.0]



dctcp=[]
mdtcp=[]
mptcp=[]
sptcp=[]
for v in range (len(fcts['mdtcp']['1']['99p_sf'])):
    dctcp.append(1.0)
    mdtcp.append(fcts['mdtcp']['4']['99p_sf'][v]/fcts['mdtcp']['1']['99p_sf'][v])
    mptcp.append(fcts['mptcp']['4']['99p_sf'][v]/fcts['mdtcp']['1']['99p_sf'][v])
    sptcp.append(fcts['mptcp']['1']['99p_sf'][v]/fcts['mdtcp']['1']['99p_sf'][v])


axPlot.plot(xaxis, sptcp, lw=4, label='TCP',color='black',marker='o')
axPlot.plot(xaxis, mptcp, lw=4, label='MPTCP',color='red',marker='<')

# axPlot.plot(xaxis, dctcp, lw=4, label='DCTCP',color='red',marker='x')
axPlot.plot(xaxis, mdtcp,lw=4, label='MDTCP',color='blue',marker='v')


axPlot.legend(loc='lower right',ncol=3,fontsize=12)
axPlot.set_title('(a) 99th FCT (0,100KB)',fontsize=12)
# axPlot.set_xlabel("Load")
axPlot.set_ylabel("Normalized FCT")

axPlot2 = fig.add_subplot(2, 2, 2)

dctcp=[]
mdtcp=[]
mptcp=[]
sptcp=[]
for v in range (len(fcts['mdtcp']['1']['99p_mf'])):
    dctcp.append(1.0)
    mdtcp.append(fcts['mdtcp']['4']['99p_mf'][v]/fcts['mdtcp']['1']['99p_mf'][v])
    mptcp.append(fcts['mptcp']['4']['99p_mf'][v]/fcts['mdtcp']['1']['99p_mf'][v])
    sptcp.append(fcts['mptcp']['1']['99p_mf'][v]/fcts['mdtcp']['1']['99p_mf'][v])

axPlot2.plot(xaxis, sptcp, lw=4, label='TCP',color='black',marker='o')
axPlot2.plot(xaxis, mptcp, lw=4, label='MPTCP',color='red',marker='<')

# axPlot2.plot(xaxis, dctcp, lw=4, label='DCTCP',color='red',marker='x')
axPlot2.plot(xaxis, mdtcp,lw=4, label='MDTCP',color='blue',marker='v')


axPlot2.legend(loc='lower right',ncol=3,fontsize=12)
axPlot2.set_xlabel("Load")
axPlot2.set_title('(b) 99th FCT [100KB, 10MB)',fontsize=12)
axPlot2.grid(True)
axPlot2.set_ylabel("Normalized FCT")

axPlot3 = fig.add_subplot(2, 2, (3,4))
axPlot3.grid(True)

dctcp=[]
mdtcp=[]
mptcp=[]
sptcp=[]
for v in range (len(fcts['mdtcp']['1']['99p_lf'])):
    dctcp.append(1.0)
    mdtcp.append(fcts['mdtcp']['4']['99p_lf'][v]/fcts['mdtcp']['1']['99p_lf'][v])
    mptcp.append(fcts['mptcp']['4']['99p_lf'][v]/fcts['mdtcp']['1']['99p_lf'][v])
    sptcp.append(fcts['mptcp']['1']['99p_lf'][v]/fcts['mdtcp']['1']['99p_lf'][v])


# axPlot3.plot(xaxis, dctcp, lw=4, label='DCTCP',color='red',marker='x')
axPlot3.plot(xaxis, sptcp, lw=4, label='TCP',color='black',marker='o')
axPlot3.plot(xaxis, mptcp, lw=4, label='MPTCP',color='red',marker='<')
axPlot3.plot(xaxis, mdtcp,lw=4, label='MDTCP',color='blue',marker='v')


axPlot3.legend(loc='lower right',ncol=3,fontsize=12)
axPlot3.set_xlabel("Load")
axPlot3.set_title('(c) 99th FCT [10MB, 30MB]',fontsize=12)
axPlot3.set_ylabel("Normalized FCT")
plt.tight_layout()
plt.savefig('plots/tail_websearch-load100_norm.pdf')

#plt.show()






