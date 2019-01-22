#!/bin/sh

INPUT_DIR=inputs
OUTPUT_DIR=results
# INPUT_FILES='stag_prob_0_2_3_data stag_prob_1_2_3_data stag_prob_2_2_3_data stag_prob_0_5_3_data stag_prob_1_5_3_data stag_prob_2_5_3_data stride1_data stride2_data stride4_data stride8_data random0_data random1_data random2_data random0_bij_data random1_bij_data random2_bij_data random_2_flows_data random_3_flows_data random_4_flows_data hotspot_one_to_one_data'

# rm -rf results
INPUT_FILES='hotspot_one_to_one_data'
DURATION=60

WORKLOAD="one_to_one one_to_several"


iperf="iperf"
bw=10
delay=0.25
redmax=30001
redmin=30000
redburst=21
redprob=1
enable_ecn=1
enable_red=1
mdtcp=0
dctcp=0
g=4
subflows=4
pod=4
queue_size=150
qmon=0
mean_flow_length=500  # in packets 

avg_alfa=0
mdtcp_debug=0
num_reqs=1000

# test=0 throughput test, test=1 FCT
load=0.8
bwm=1

mn -c 

cdir=$(pwd)
echo $cdir

export PYTHONPATH=${PYTHONPATH}:$cdir

# Note that the link delay is in ms

# if [ -n "$2" ]
# then
#   qmon="--qmon"
#   qmon_status="True"
# fi


mkdir -p plots

# proto 0=mptcp, proto=1=mdtcp
m=1

bw=10
delay=1

while [ $m -le 1 ] ; do 

 
for mytest in 0 ;

do 


for WORKLOAD in 'one_to_one';

do 
# 0.2 0.4 0.6 0.8 0.9 ;

for load in 1.0 ; 
 
do 

dload=$(echo "scale=4; $bw*$load" | bc)
#./../../Trace-Generator/trace_generator 100

#generate traffic for the desired load

if [ $mytest -eq 1 ] ;

then 
  echo $dload

  rm ../Trace-Generator/trace_file/mdtcp-output.trace
  ./../Trace-Generator/trace_generator $dload $num_reqs

fi 


for pod in 4 ; 

do 

for proto in 1 0;

do 


# find . -name 'ss_clnt_10*' | xargs rm -f

modprobe tcp_probe
#echo > /dev/null | sudo tee /var/log/syslog
#echo > /dev/null | sudo tee /var/log/kern.log



echo "python /home/doljira/pox/pox.py DCController --topo=ft,"$pod "--routing=ECMP"
# export PYTHONPATH=${PYTHONPATH}:/home/doljira/workspace/mdtcp-cong/mdtcp-cong/scripts
# "sudo python /home/doljira/pox/pox.py DCController --topo=ft,4 --routing=ECMP"

#gnome-terminal -e "python /home/doljira/pox/pox.py DCController --topo=ft,"$pod "--routing=ECMP" --window-with-profile=newt

sleep 1

echo "Iteration "$m" load: "$load

rm ss_clnt* ss_serv* flows_10* log_10*

for subflows in 1 2 4 8; 

do

python pox/pox.py DCController --topo=ft,4 --routing=ECMP &

controllerId=$!

echo $controllerId

sleep 5

for f in $INPUT_FILES;
do
        input_file=$INPUT_DIR/$f
        cdate=$(date +"%Y%m%d")
        if [ $proto -eq 1 ] ;
        then 
            redmax=31500
            redmin=30000
            redburst=21
            redprob=1
            enable_ecn=1
            enable_red=1
            mdtcp=1
            dctcp=0

            if [ $mytest -eq 1 ] ;
            then
                DURATION=60
                subdir='mdtcp-fct-webdiv-'$cdate'-bw'$bw'delay'$delay'ft'$pod'load'$load'num_reqs'$num_reqs
                
            elif [ $mytest -eq 0 ]; 
                then
                DURATION=60
                subdir='mdtcp-goodput-'$cdate'-bw'$bw'delay'$delay'ft'$pod'runtime'$DURATION
                 
            fi


        elif [ $proto -eq 0 ]; 

        then
            
            enable_ecn=0
            enable_red=1
            mdtcp=0
            dctcp=0

            if [ $mytest -eq 1 ] ;
            then
                DURATION=60
                subdir='mptcp-fct-webdiv-'$cdate'-bw'$bw'delay'$delay'ft'$pod'load'$load'num_reqs'$num_reqs
                
            elif [ $mytest -eq 0 ]; 
                then
                DURATION=60
                subdir='mptcp-goodput-'$cdate'-bw'$bw'delay'$delay'ft'$pod'runtime'$DURATION
                 
            fi

        fi

       
                #statements

            #statements
        out_dir=$OUTPUT_DIR/$subdir/$WORKLOAD
        echo "Iteration "$m" output: "$out_dir

        # sudo python -u fattree.py \
        #                  -i $input_file \
        #                  -d $out_dir \
        #                  -t $DURATION --ecmp \
        #                  --iperf \
        #                  --workload $WORKLOAD \
        #                  --K $pod \
        #                  --bw $bw \
				    #       --delay $delay\
				    #       --mdtcp $mdtcp\
				    #       --dctcp $dctcp\
				    #       --redmax $redmax\
				    #       --redmin $redmin\
				    #       --burst  $redburst\
				    #       --queue  $queue_size\
				    #       --prob $redprob\
				    #       --enable_ecn $enable_ecn\
				    #       --enable_red $enable_red\
				    #       --g 4\
				    #       --subflows $subflows\
				    #       --avg_alfa 0\
        #                   --mdtcp_debug $mdtcp_debug\
        #                   --num_reqs $num_reqs\
        #                   --test $mytest \
        #                   --qmon $qmon\
        #                   --iter $m   \
        #                   --load $load  \
        #                   --avg_flow_length $mean_flow_length \
        #                   --bwm  $bwm  
        # sudo mn -c
done

kill -9 $controllerId

if [ $mytest -eq 1 ]

   then 
        python process_fct.py  -s $subflows -f results/$subdir/$WORKLOAD/*/flows_10* -o plots/$subdir-$WORKLOAD.png
       #  python plot_cpu_fct.py -w $WORKLOAD -k $pod -g $g -f results/$subdir/$WORKLOAD/flows*/cpu_utilization.txt -o plots/$subdir-$WORKLOAD-cpu_util.png
       #  python iperf3Jsontocsv.py -f results/$subdir/$WORKLOAD/*/client_iperf3* -o plots/$subdir-$WORKLOAD-iperf3.csv
       # python iperf3Jsontocsv.py -f results/$subdir/$WORKLOAD -o plots/$subdir-$WORKLOAD-iperf3.csv
       # python process_iperf3_csv_fct.py -f plots/$subdir-$WORKLOAD-iperf3.csv -o $subdir-$WORKLOAD 

fi


done 
done 

done 


# plot cpu utilization
#python plot_cpu.py -w $WORKLOAD -k $pod -g $g -f results/$subdir/$WORKLOAD/flows*/cpu_utilization.txt -o plots/$subdir-$WORKLOAD-cpu_util.png

# sudo python clean.py

# if [ $mytest -eq 1 ]

#    then 
#         python process_fct.py  -f results/$subdir/$WORKLOAD/*/flows_10* -o plots/$subdir-$WORKLOAD.png
#        #  python plot_cpu_fct.py -w $WORKLOAD -k $pod -g $g -f results/$subdir/$WORKLOAD/flows*/cpu_utilization.txt -o plots/$subdir-$WORKLOAD-cpu_util.png
#        #  python iperf3Jsontocsv.py -f results/$subdir/$WORKLOAD/*/client_iperf3* -o plots/$subdir-$WORKLOAD-iperf3.csv
#        # python iperf3Jsontocsv.py -f results/$subdir/$WORKLOAD -o plots/$subdir-$WORKLOAD-iperf3.csv
#        # python process_iperf3_csv_fct.py -f plots/$subdir-$WORKLOAD-iperf3.csv -o $subdir-$WORKLOAD 

# fi

# python iperf3Jsontocsv.py -k $pod -w $WORKLOAD -f results/'bw'$bw'g'$g'delay'$delay'avgalfa'$avg_alfa'ft'$pod/$WORKLOAD/*/client_iperf3* -o plots/'bw'$bw'g'$g'delay'$delay'avgalfa'$avg_alfa'ft'$pod-$WORKLOAD-iperf3.csv
# python plot_ping.py -k $pod -w $WORKLOAD -f results/'bw-iperf-lat-ping'$bw'g'$g'delay'$delay'avgalfa'$avg_alfa'ft'$pod/$WORKLOAD/*/client_ping* -o plots/'bw-iperf-lat-ping'$bw'g'$g'delay'$delay'avgalfa'$avg_alfa'ft'$pod-$WORKLOAD-ping.png

if [ $mytest -eq 0 ]

   then 
       python plot_hist_all.py -k $pod -w $WORKLOAD -t $DURATION -f results/$subdir/$WORKLOAD/*/client_iperf* results/$subdir/$WORKLOAD/max_throughput.txt -o plots/$subdir-$WORKLOAD-throughput.png
       # python plot_cpu_fct.py -w $WORKLOAD -k $pod -g $g -f results/$subdir/$WORKLOAD/flows*/cpu_utilization.txt -o plots/$subdir-$WORKLOAD-cpu_util.png

fi
# # plot link util
# python plot_link_util.py -k $pod -w $WORKLOAD -f results/$subdir/$WORKLOAD/*/link_util* -o plots/$subdir-$WORKLOAD-link_util.png

# # plot queue sizes

if [ $qmon -eq 1 ]

    then
    for f in 1 4
    do
        echo $f
        python plot_queue_monitor.py -f results/$subdir/$WORKLOAD/flows$f'g'$g/queue_size* -o plots/$subdir-$WORKLOAD-flows$f
    done
fi

if [ $bwm -eq 1 ]

    then
    for f in 1 2 4 8
    do

    python process_bwm_ng_rates.py -f results/$subdir/$WORKLOAD/flows$f'g'$g/rates_iter* -o plots/$subdir-$WORKLOAD-flows$f
    
    done 
fi


# plot cpu utilization
# python plot_cpu.py -w $WORKLOAD -k $pod -g $g -f results/$subdir/$WORKLOAD/flows*/cpu_utilization.txt -o plots/$subdir-$WORKLOAD-cpu_util.png


sleep 1

sudo chown doljira -R results

sudo chown doljira -R plots

#echo > /dev/null | sudo tee /var/log/syslog

done 
done 

done

m=$((m + 1))

done 
  
