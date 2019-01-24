import sys
import os
import argparse
import csv
# import matplotlib as m
# import matplotlib.pyplot as plt
import numpy as np
from numpy import average, std
from math import sqrt
# from monitor.helper import *

parser = argparse.ArgumentParser()
parser.add_argument('-f', dest="files", nargs='+', required=True)
parser.add_argument('-o', '--out', dest="out", default=None)
# parser.add_argument('-k', dest="k", default=None)
# parser.add_argument('-w', dest="workload", default=None)
parser.add_argument('-s', dest="subflows", type=int, default=None)

args = parser.parse_args()


''' Parse a file to get FCT and goodput results '''
def parse_file(file_name,results,subflow):
    
    f = open(file_name)
    size_transfer=0
    while True:
        line = f.readline().rstrip()

        if not line:
            break
        arr = line.split(',')
        # Size:34075, Duration(usec):9098403
        
        '''Size:flowsize, Duration(usec):fct'''
        if len(arr) >= 2:
            '''[size, fct]'''

            size=int(arr[0].split(':')[1])
            fct_ms=float(arr[1].split(':')[1])/1000.0;
            if  size < 100*1024:
                results[subflow]['small']['size'].append(size)
                results[subflow]['small']['fct'].append(fct_ms)
            elif size>=100*1024 and size <10 * 1024 * 1024:
                results[subflow]['medium']['size'].append(size)
                results[subflow]['medium']['fct'].append(fct_ms)
            elif size>=10 * 1024 * 1024:
                results[subflow]['large']['size'].append(size)
                results[subflow]['large']['fct'].append(fct_ms)

            results[subflow]['all']['size'].append(size)
            results[subflow]['all']['fct'].append(fct_ms)

            size_transfer+=size
    results[subflow]['total_GB']=float("{0:.4f}".format(size_transfer/(1024.0*1024.0*1024.0)))
    
    f.close()
    return results

''' Get average result '''
def average_result(input_tuple_list, index):
    input_list = [x[index] for x in input_tuple_list]
    if len(input_list) > 0:
        return sum(input_list) / len(input_list)
    else:
        return 0
def median_result(input_tuple_list, index):
    input_list = [x[index] for x in input_tuple_list]
    if len(input_list) > 0:
        return np.median(input_list)
    else:
        return 0

''' Get cumulative distribution function (CDF) result '''
def cdf_result(input_tuple_list, index, cdf):
    input_list = [x[index] for x in input_tuple_list]
    input_list.sort()
    if len(input_list) > 0 and cdf >= 0 and cdf <= 1:
        return input_list[int(cdf * len(input_list))]
    else:
        return 0

def average_fct_result(input_tuple_list):
    return average_result(input_tuple_list, 1)

def median_fct_result(input_tuple_list):
    return median_result(input_tuple_list, 1)

def average_goodput_result(input_tuple_list):
    return average_result(input_tuple_list, 2)

def cdf_fct_result(input_tuple_list, cdf):
    return cdf_result(input_tuple_list, 1, cdf)

def cdf_goodput_result(input_tuple_list, cdf):
    return cdf_result(input_tuple_list, 2, cdf)

def compute_fct_stats(results,subflow):
    

    results[subflow]['overall']=float("{0:.4f}".format(np.mean(results[subflow]['all']['fct'])))
    results[subflow]['(0, 100KB)']=float("{0:.4f}".format(np.mean(results[subflow]['small']['fct'])))
    results[subflow]['(0, 100KB)_50']=float("{0:.4f}".format(np.median(results[subflow]['small']['fct'])))
    results[subflow]['(0, 100KB)_99']=float("{0:.4f}".format(np.percentile(results[subflow]['small']['fct'], 0.99)))

    
    results[subflow]['[100KB, 10MB)']=float("{0:.4f}".format(np.mean(results[subflow]['medium']['fct'])))
    results[subflow]['[100KB, 10MB)_50']=float("{0:.4f}".format(np.median(results[subflow]['medium']['fct'])))
    # results[subflow]['[100KB, 10MB)_95']=np.percentile(results[subflow]['medium']['fct'],0.95)
    results[subflow]['[100KB, 10MB)_99']=float("{0:.4f}".format(np.percentile(results[subflow]['medium']['fct'],0.99)))
    
    results[subflow]['[10MB, )']=float("{0:.4f}".format(np.mean(results[subflow]['large']['fct'])))
    results[subflow]['[10MB, )_50']=float("{0:.4f}".format(np.median(results[subflow]['large']['fct'])))

    # results[subflow]['[10MB, )_95']=float(cdf_fct_result(large, 0.95))
    results[subflow]['[10MB, )_99']= float("{0:.4f}".format(np.percentile(results[subflow]['large']['fct'],0.99)))

   
    return results


if __name__ == '__main__':

    # fct-bw10g-2delay-0.025avgalfa-1num_reqs-50ft-8
    final_results={}
    # num_file_parse=0
   
    load=0
    protocol=''
    for f in args.files:
        if load == 0:
            load=float(f[f.find('load')+len('load')+2])/10
        if 'mptcp' in f:
            protocol='mptcp'
        elif 'mdtcp' in f:
            protocol='mdtcp'
        subflow=int(args.subflows)
        final_results[subflow]={'small':{'size':[],'fct':[]},\
        'medium':{'size':[],'fct':[]},'large':{'size':[],'fct':[]},'all':{'size':[],'fct':[]}}
        final_results=parse_file(f,final_results,subflow)
        
    final_results=compute_fct_stats(final_results,subflow)
           
        
    
    # print('subflow','load','overall','avg_(0, 100KB)','avg_[100KB, 10MB)','avg_[10MB, )',\
    #'median_(0, 100KB)','median_[100KB, 10MB)','median_[10MB, )',\
    #'99th_(0, 100KB)','99th_[100KB, 10MB)','99th_[10MB, )')
    # overall-mean,small-mean,medium-mean,large-mean; 
    with open('fct_one2three_webdiv_nreq200_190106',mode='a') as csv_file:
        fct_writer=csv.writer(csv_file,delimiter=',')
        nflows=[args.subflows]
        for i in nflows:

            fct_writer.writerow([protocol,i,load,final_results[i]['overall'],final_results[i]['(0, 100KB)'],\
                final_results[i]['[100KB, 10MB)'],final_results[i]['[10MB, )'],\
                final_results[i]['(0, 100KB)_50'],final_results[i]['[100KB, 10MB)_50'],final_results[i]['[10MB, )_50'],\
                final_results[i]['(0, 100KB)_99'],final_results[i]['[100KB, 10MB)_99'],final_results[i]['[10MB, )_99'],\
                final_results[i]['total_GB']])

            
