import sys
import os
import argparse
# import matplotlib as m
# import matplotlib.pyplot as plt
import numpy as np
from numpy import average, std
from math import sqrt
from monitor.helper import *


from statsmodels.distributions.empirical_distribution import ECDF



parser = argparse.ArgumentParser()
parser.add_argument('-f', dest="files", nargs='+', required=True)
parser.add_argument('-o', '--out', dest="out", default=None)
# parser.add_argument('-k', dest="k", default=None)
# parser.add_argument('-w', dest="workload", default=None)
# parser.add_argument('-t', dest="time", type=int, default=None)

args = parser.parse_args()


''' Parse a file to get FCT and goodput results '''
def parse_file(file_name):
    results = []
    f = open(file_name)

    while True:
        line = f.readline().rstrip()

        if not line:
            break
        arr = line.split(',')
        # Size:34075, Duration(usec):9098403
        
        '''Size:flowsize, Duration(usec):fct'''
        if len(arr) == 2:
            '''[size, fct]'''
            results.append([int(arr[0].split(':')[1]), int(arr[1].split(':')[1])])
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
     # (0, 100KB)
    small = filter(lambda x: x[0] < 100 * 1024, results['size_fct'][subflow])
    

    # (100KB, 10MB)
    medium = filter(lambda x: 100 * 1024 <= x[0] < 10 * 1024 * 1024, results['size_fct'][subflow])
    # (10MB, infi)
    large = filter(lambda x: x[0] >= 10 * 1024 * 1024, results['size_fct'][subflow])

    results[subflow]={}
    results[subflow]['small'] = [x[1]/1000000.0 for x in small]
    results[subflow]['medium']= [x[1]/1000000.0 for x in medium]
    results[subflow]['large']=[x[1]/1000000.0 for x in large]

    results[subflow]['overall']=float(average_fct_result(results['size_fct'][subflow]))
    results[subflow]['(0, 100KB)']=float(average_fct_result(small))
    results[subflow]['(0, 100KB)_90']=float(median_fct_result(small))
    results[subflow]['(0, 100KB)_95']=float(cdf_fct_result(small, 0.95))
    results[subflow]['(0, 100KB)_99']=float(cdf_fct_result(small, 0.99))

    
    results[subflow]['[100KB, 10MB)']=float(average_fct_result(medium))
    results[subflow]['[100KB, 10MB)_90']=float(median_fct_result(medium))
    results[subflow]['[100KB, 10MB)_95']=float(cdf_fct_result(medium, 0.95))
    results[subflow]['[100KB, 10MB)_99']=float(cdf_fct_result(medium,0.99))
    
    results[subflow]['[10MB, )']=float(average_fct_result(large))
    results[subflow]['[10MB, )_90']=float(median_fct_result(large))
    results[subflow]['[10MB, )_95']=float(cdf_fct_result(large, 0.95))
    results[subflow]['[10MB, )_99']=float(cdf_fct_result(large,0.99))

    return results
def myECDF(data):
    # create a sorted series of unique data
    raw_data = np.array(data)
    cdfx = np.sort(data)
  # x-data for the ECDF: evenly spaced sequence of the uniques
    x_values = np.linspace(start=min(cdfx),stop=max(cdfx),num=len(cdfx))
    
    # size of the x_values
    size_data = raw_data.size
    # y-data for the ECDF:
    y_values = []
    for i in x_values:
        # all the values in raw data less than the ith value in x_values
        temp = raw_data[raw_data <= i]
        # fraction of that value with respect to the size of the x_values
        value = temp.size / size_data
        # pushing the value in the y_values
        y_values.append(value)
    # return both x and y values    
    return x_values,y_values





    # print '%d flows/requests overall average completion time: %d us' % (len(results), average_fct_result(results))
    # print '%d flows/requests (0, 100KB) average completion time: %d us' % (len(small), average_fct_result(small))
    # print '%d flows/requests (0, 100KB) 99th percentile completion time: %d us' % (len(small), cdf_fct_result(small, 0.99))
    # print '%d flows/requests [100KB, 10MB) average completion time: %d us' % (len(medium), average_fct_result(medium))
    # print '%d flows/requests [10MB, ) average completion time: %d us' % (len(large), average_fct_result(large))
    # print '%d flows/requests overall average goodput: %d Mbps' % (len(results), average_goodput_result(results))

def plot_fct(results):
    m.rc('figure', figsize=(8, 6))
    m.rcParams['font.family'] = 'sans'
    m.rcParams['font.style']='normal'
    m.rcParams['font.size']=10
    fig = plt.figure()
    # m.rc('figure', figsize=(8, 6))
    axPlot = fig.add_subplot(2, 1, 1)
    axPlot.grid(True)
    patterns=['-','+','x','\\\\','*','o','0','.']
   
    colors = ['red','blue','green','cyan','magenta', '#ff0000','yellow', '#4B0082','#8F00FF','#ff0000','#ff7f00','#ffff00','#00ff00','#00ffff', '#0000ff', '#4B0082','#8F00FF']
    # colors=['red','blue','magenta']
    hatches=['//','\\','++/','xx','*','o//','//--','\\.']
    fct=[]
    N=3;
    xaxis = np.arange(N)  # the x locations for the groups
    width = 0.1 
    xoffset = 0.1

    # flows=[1,2,3,4,5,6,7,8]
    flows=[1,2,3,4,5]
    sizes=['(0, 100KB)_n','[100KB, 10MB)_n','[10MB, )_n']
    xticklabel=['<100KB','100KB-10MB','>=10MB']
    bars=''
    j=0
    for f in flows:
        y=[]
        for s in sizes:
            y.append(results[str(f)][s])
        axPlot.bar(xaxis + (f-1)*xoffset, y, width,label=str(f), color=colors[j],edgecolor='black',hatch=hatches[j]) #, yerr=menStd)
        j=j+1
        if(j==len(colors)):
            j=0
        

    # axPlot.legend(loc='upper right',ncol=2,columnspacing=0.3,title='No.subflows')
    axPlot.set_xlim(xmin=-0.1,xmax=2.85)
    # axPlot.set_ylim(ymax=1.05)
    axPlot.set_ylabel("Normalized mean FCT")
    # axPlot.set_xlabel("Flow sizes",fontsize=14)
    axPlot.set_xticklabels(xticklabel)
    axPlot.set_xticks(xaxis + 0.35)
    axPlot.legend(loc='upper center', bbox_to_anchor=(0.5, 1.3),fancybox=True, columnspacing=0.3,shadow=True, ncol=8,title='No. subflows')
    

    axPlot = fig.add_subplot(2, 1, 2)
    axPlot.grid(True)
    sizes=['(0, 100KB)_99_n','[100KB, 10MB)_99_n','[10MB, )_99_n']

    j=0
    for f in flows:
        y=[]
        for s in sizes:
            y.append(results[str(f)][s])
        axPlot.bar(xaxis + (f-1)*xoffset, y, width,label=str(f), color=colors[j],edgecolor='black',hatch=hatches[j]) #, yerr=menStd)
        j=j+1
        if(j==len(colors)):
            j=0
    
    # axPlot.legend(loc='upper right',ncol=2,columnspacing=0.3,title='No.subflows')
    axPlot.set_xlim(xmin=-0.1,xmax=2.85)
    # axPlot.set_ylim(ymax=1.05)
    axPlot.set_ylabel("Normalized 99th FCT")
    axPlot.set_xlabel("Flow size")
    axPlot.set_xticklabels(xticklabel)
    axPlot.set_xticks(xaxis + 0.35)
    plt.savefig(args.out)


    fig = plt.figure()

    axPlot = fig.add_subplot(2, 1, 1)
    axPlot.grid(True)

    sizes=['(0, 100KB)','[100KB, 10MB)','[10MB, )']

    xticklabel=['<100KB','100KB-10MB','>=10MB']
    j=0
    for f in flows:
        y=[]
        for s in sizes:
            y.append(results[str(f)][s]/1000.0)
        axPlot.bar(xaxis + (f-1)*xoffset, y, width,label=str(f), color=colors[j],edgecolor='black',hatch=hatches[j]) #, yerr=menStd)
        j=j+1
        if(j==len(colors)):
            j=0
        

    # axPlot.legend(loc='upper right',ncol=2,columnspacing=0.3,title='No.subflows')
    axPlot.set_xlim(xmin=-0.1,xmax=2.85)
    # axPlot.set_ylim(ymax=1.05)
    axPlot.set_ylabel("Average FCT [ms]")
    # axPlot.set_xlabel("Flow sizes",fontsize=14)
    axPlot.set_xticklabels(xticklabel)
    axPlot.set_xticks(xaxis + 0.35)
    axPlot.legend(loc='upper center', bbox_to_anchor=(0.5, 1.3),fancybox=True, columnspacing=0.3,shadow=True, ncol=8,title='No. subflows')

    axPlot = fig.add_subplot(2, 1, 2)
    axPlot.grid(True)

    sizes=['(0, 100KB)_99','[100KB, 10MB)_99','[10MB, )_99']

    j=0
    for f in flows:
        y=[]
        for s in sizes:
            y.append(results[str(f)][s]/1000.0)
        axPlot.bar(xaxis + (f-1)*xoffset, y, width,label=str(f), color=colors[j],edgecolor='black',hatch=hatches[j]) #, yerr=menStd)
        j=j+1
        if(j==len(colors)):
            j=0
    
    # axPlot.legend(loc='upper right',ncol=2,columnspacing=0.3,title='No.subflows')
    axPlot.set_xlim(xmin=-0.1,xmax=2.85)
    # axPlot.set_ylim(ymax=1.05)
    axPlot.set_ylabel("99th FCT [ms]")
    axPlot.set_xlabel("Flow size")
    axPlot.set_xticklabels(xticklabel)
    axPlot.set_xticks(xaxis + 0.35)
    plt.savefig(args.out+'real.png')



    # plt.show()

    fig = plt.figure()

    axPlot = fig.add_subplot(2, 1, 1)
    axPlot.grid(True)
    sizes=['(0, 100KB)_90_n','[100KB, 10MB)_90_n','[10MB, )_90_n']

    j=0
    for f in flows:
        y=[]
        for s in sizes:
            y.append(results[str(f)][s])
        axPlot.bar(xaxis + (f-1)*xoffset, y, width,label=str(f), color=colors[j],edgecolor='black',hatch=hatches[j]) #, yerr=menStd)
        j=j+1
        if(j==len(colors)):
            j=0
        

    # axPlot.legend(loc='upper center',ncol=2,columnspacing=0.3,title='No.subflows')
    axPlot.legend(loc='upper center', bbox_to_anchor=(0.5, 1.3),fancybox=True, columnspacing=0.3,shadow=True, ncol=8,title='No. subflows')

    axPlot.set_xlim(xmin=-0.1,xmax=2.85)
    # axPlot.set_ylim(ymax=1.05)
    axPlot.set_ylabel("Normalized Median FCT")
    axPlot.set_xlabel("Flow Size")
    axPlot.set_xticklabels(xticklabel)
    axPlot.set_xticks(xaxis + 0.35)

    axPlot = fig.add_subplot(2, 1, 2)
    axPlot.grid(True)
    sizes=['(0, 100KB)_90','[100KB, 10MB)_90','[10MB, )_90']

    j=0
    for f in flows:
        y=[]
        for s in sizes:
            y.append(results[str(f)][s]/1000.0)
        axPlot.bar(xaxis + (f-1)*xoffset, y, width,label=str(f), color=colors[j],edgecolor='black',hatch=hatches[j]) #, yerr=menStd)
        j=j+1
        if(j==len(colors)):
            j=0
        
    
    # axPlot.legend(loc='upper right',ncol=2,columnspacing=0.3,title='No.subflows')
    axPlot.set_xlim(xmin=-0.1,xmax=2.85)
    # axPlot.set_ylim(ymax=1.05)
    axPlot.set_ylabel("Median FCT")
    axPlot.set_xlabel("Flow Size")
    axPlot.set_xticklabels(xticklabel)
    axPlot.set_xticks(xaxis + 0.35)
    plt.savefig(args.out+'median.png')


    # CDF 
    # fig=plt.figure()

    # # axPlot = fig.add_subplot(2, 1, 2)
    # # axPlot.grid(True)
    # sizes=['(0, 100KB)','[100KB, 10MB)','[10MB, )']
    # sizes=['small','medium','large']

    
    # i=0
    # for s in sizes:
    #     j=0
    #     if i==0:
    #         axPlot = fig.add_subplot(2, 2, 1)
    #         for f in flows:
    #             ecdf = ECDF(results[str(f)][s])
    #             print(ecdf.x)
    #             axPlot.plot(ecdf.x,ecdf.y,color=colors[j])
    #             j=j+1;
    #         axPlot.set_xlim(xmax=200)
                
    #     elif i==1:
    #         j=0
    #         axPlot = fig.add_subplot(2, 2, 2)
    #         for f in flows:
    #             ecdf = ECDF(results[str(f)][s])
             
    #             axPlot.plot(ecdf.x,ecdf.y,color=colors[j])
    #             j=j+1;
    #         axPlot.set_xlim(xmax=200)

    #     else:
    #         j=0
    #         axPlot = fig.add_subplot(2, 2, 3)
    #         for f in flows:
    #             ecdf = ECDF(results[str(f)][s])
                
    #             axPlot.plot(ecdf.x,ecdf.y,color=colors[j])
    #             j=j+1;
        
    #         axPlot.set_xlim(xmax=200)
    #     i=i+1
    # plt.show()

    # plt.savefig(args.out+'cdf.png')




        # plt.show()
   
    # plt.savefig(args.out+'median.png')


if __name__ == '__main__':

    # fct-bw10g-2delay-0.025avgalfa-1num_reqs-50ft-8
    final_results={'size_fct':{}}
    # num_file_parse=0
    psubflow=0;
    for f in args.files:
        subflow = f[f.find('flows') + len('flows')]
        if psubflow<subflow:
            if psubflow>0:
                final_results=compute_fct_stats(final_results,psubflow)
            psubflow=subflow
            final_results['size_fct'][subflow]=[]
        
        if os.path.isfile(f):
            final_results['size_fct'][subflow].extend(parse_file(f))
            # num_file_parse = num_file_parse + 1
    final_results=compute_fct_stats(final_results,psubflow)
    # print('subflow','overall','avg_(0, 100KB)','(0, 100KB)_99','avg_[100KB, 10MB)','[10MB, )')
    for i in range(1,6):
        if i == 1:
            final_results[str(i)]['overall_n']=1.0
           
            final_results[str(i)]['(0, 100KB)_n']=1.0
            final_results[str(i)]['(0, 100KB)_90_n']=1.0
            final_results[str(i)]['(0, 100KB)_95_n']=1.0
            final_results[str(i)]['(0, 100KB)_99_n']=1.0
            

            final_results[str(i)]['[100KB, 10MB)_n']=1.0
            final_results[str(i)]['[100KB, 10MB)_90_n']=1.0
            final_results[str(i)]['[100KB, 10MB)_95_n']=1.0
            final_results[str(i)]['[100KB, 10MB)_99_n']=1.0

            final_results[str(i)]['[10MB, )_n']=1.0
            final_results[str(i)]['[10MB, )_90_n']=1.0
            final_results[str(i)]['[10MB, )_95_n']=1.0
            final_results[str(i)]['[10MB, )_99_n']=1.0
        else:
            final_results[str(i)]['overall_n']=float(final_results[str(i)]['overall']/final_results[str(1)]['overall'])
            
            final_results[str(i)]['(0, 100KB)_n']=float(final_results[str(i)]['(0, 100KB)']/final_results[str(1)]['(0, 100KB)'])
            
            final_results[str(i)]['(0, 100KB)_90_n']=float(final_results[str(i)]['(0, 100KB)_90']/final_results[str(1)]['(0, 100KB)_90'])
            final_results[str(i)]['(0, 100KB)_95_n']=float(final_results[str(i)]['(0, 100KB)_95']/final_results[str(1)]['(0, 100KB)_95'])
            final_results[str(i)]['(0, 100KB)_99_n']=float(final_results[str(i)]['(0, 100KB)_99']/final_results[str(1)]['(0, 100KB)_99'])

            final_results[str(i)]['[100KB, 10MB)_n']=float(final_results[str(i)]['[100KB, 10MB)']/final_results[str(1)]['[100KB, 10MB)'])
            final_results[str(i)]['[100KB, 10MB)_90_n']=float(final_results[str(i)]['[100KB, 10MB)_90']/final_results[str(1)]['[100KB, 10MB)_90'])
            final_results[str(i)]['[100KB, 10MB)_95_n']=float(final_results[str(i)]['[100KB, 10MB)_95']/final_results[str(1)]['[100KB, 10MB)_95'])
            final_results[str(i)]['[100KB, 10MB)_99_n']=float(final_results[str(i)]['[100KB, 10MB)_99']/final_results[str(1)]['[100KB, 10MB)_99'])
            

            final_results[str(i)]['[10MB, )_n']=float(final_results[str(i)]['[10MB, )']/final_results[str(1)]['[10MB, )'])
            final_results[str(i)]['[10MB, )_90_n']=float(final_results[str(i)]['[10MB, )_90']/final_results[str(1)]['[10MB, )_90'])
            final_results[str(i)]['[10MB, )_95_n']=float(final_results[str(i)]['[10MB, )_95']/final_results[str(1)]['[10MB, )_95'])
            final_results[str(i)]['[10MB, )_99_n']=float(final_results[str(i)]['[10MB, )_99']/final_results[str(1)]['[10MB, )_99'])





        # print (i,final_results[str(i)]['overall_n'],final_results[str(i)]['(0, 100KB)_n'],\
        #     final_results[str(i)]['(0, 100KB)_99_n'],final_results[str(i)]['[100KB, 10MB)_n'],\
        #     final_results[str(i)]['[10MB, )_n'])

    plot_fct(final_results)
        # print (final_results[str(i)]['(0, 100KB)'])
    


    
    # if len(sys.argv) < 2:
    #     print 'Usages: %s <file1> [file2 ...]' % sys.argv[0]
    #     sys.exit()

    # files = sys.argv[1:]
    # final_results = []
    # num_file_parse = 0

    # for f in files:
    #     if os.path.isfile(f):
    #         final_results.extend(parse_file(f))
    #         num_file_parse = num_file_parse + 1

    # if num_file_parse <= 1:
    #     print "Parse %d file" % num_file_parse
    # else:
    #     print "Parse %d files" % num_file_parse

    # print_result(final_results)
