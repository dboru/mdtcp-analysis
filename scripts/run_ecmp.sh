#!/bin/sh
mn -c 

cdate=$(date +"%Y%m%d")

DURATION=60
iperf="iperf"
mdtcp_debug=0
queue_size=400

# test=0 throughput test, test=1 FCT
qmon=1
bwm=1
tcpdump=1
tcpprobe=1


num_reqs=10000

cdir=$(pwd)
echo $cdir
export PYTHONPATH=${PYTHONPATH}:$cdir
mkdir -p plots

python pox/pox.py DCController --topo=ft,4 --routing=ECMP &
controllerId=$!
echo $controllerId
sleep 2

# proto 0=mptcp, proto=1=mdtcp
m=1
bw=10
delay=1

seed=754

while [ $m -le 1 ] ; 
do
  seed=$(( seed + m)) 
  for mytest in 1 ;
  do 
    for WORKLOAD in 'one_to_several';
    do 
    # 0.2 0.4 0.6 0.8 0.9 ;
    for load in 0.1  ; 
    do 
      
      dload=$(echo "scale=4; $bw*$load" | bc)
     
      #generate traffic for the desired load
      echo $dload
      rm ../Trace-Generator/trace_file/mdtcp-output.trace
      ./../Trace-Generator/trace_generator $dload $num_reqs $seed
     
     # cp ../Trace-Generator/trace_file/mdtcp-output.trace requests_load$dload

      for pod in 4 ; 
      do 
        for proto in 1 0 ;
        do 
          for subflows in 1 4; 
          do
            # find . -name 'ss_clnt_10*' | xargs rm -f
            
            if [ $tcpprobe -eq 1] ;
            then 
              modprobe tcp_probe
            fi

            #echo > /dev/null | sudo tee /var/log/syslog
            #echo > /dev/null | sudo tee /var/log/kern.log
            
           
            echo "Iteration "$m" load: "$load
            rm ss_clnt* ss_serv* flows_10* log_10*
            # cdate=$(date +"%Y%m%d")
            if [ $proto -eq 1 ] ;
            then 
              redmax=35000
              redmin=30000
              redburst=31
            	redprob=1
            	enable_ecn=1
            	enable_red=1
            	mdtcp=1
            	dctcp=0
              if [ $mytest -eq 1 ] ;
              then
               
                subdir='fct-mdtcp-'$cdate'-bw'$bw'delay'$delay'ft'$pod'load'$load'num_reqs'$num_reqs
              elif [ $mytest -eq 0 ]; 
                then
                  
                  subdir='goodput-mdtcp-'$cdate'-bw'$bw'delay'$delay'ft'$pod'runtime'$DURATION
                fi
              elif [ $proto -eq 0 ]; 
                then
                  enable_ecn=0
                	enable_red=1
                  redmax=90000
                  redmin=30000
                  redburst=55
                  redprob=0.01
                	mdtcp=0
                	dctcp=0
                  if [ $mytest -eq 1 ] ;
                  then
                    
                    subdir='fct-mptcp-'$cdate'-bw'$bw'delay'$delay'ft'$pod'load'$load'num_reqs'$num_reqs
                  elif [ $mytest -eq 0 ]; 
                    then
                     
                      subdir='goodput-mptcp-'$cdate'-bw'$bw'delay'$delay'ft'$pod'runtime'$DURATION
                    fi
                  fi
                  
                  out_dir=results/$subdir/$WORKLOAD

                  cp ../Trace-Generator/trace_file/mdtcp-output.trace $out_dir/requests_load$dload

                  
                  sudo python -u fattree.py -d $out_dir -t $DURATION --ecmp --iperf \
                  --workload $WORKLOAD --K $pod --bw $bw --delay $delay --mdtcp $mdtcp --dctcp $dctcp --redmax $redmax\
                  --redmin $redmin --burst  $redburst --queue  $queue_size --prob $redprob --enable_ecn $enable_ecn\
                  --enable_red $enable_red --subflows $subflows --mdtcp_debug $mdtcp_debug --num_reqs $num_reqs\
                  --test $mytest --qmon $qmon --iter $m   --load $load --bwm  $bwm --tcpdump $tcpdump --tcpprobe $tcpprobe

                  sudo mn -c
                  if [ $mytest -eq 1 ]
                  then 
                    python process_fct.py  -s $subflows -f results/$subdir/$WORKLOAD/*/flows_10* -o plots/$subdir-$WORKLOAD.png
                  fi
                  if [ $qmon -eq 1 ]
                  then
                    for f in $subflows
                    do
                      python plot_queue_monitor.py -f results/$subdir/$WORKLOAD/flows$f/queue_size* -o plots/$subdir-$WORKLOAD-flows$f
                    done
                  fi

              	  if [ $bwm -eq 1 ]
              	  then
              	  for f in $subflows
              	  do
                    python process_bwm_ng_rates.py -f results/$subdir/$WORKLOAD/flows$f/rates_iter* -o plots/$subdir-$WORKLOAD-flows$f
              	  done 
              	  fi

                  sleep 5 
                done #subflow

                if [ $mytest -eq 0 ]
                then 
                  python plot_hist_all.py -k $pod -w $WORKLOAD -t $DURATION -f results/$subdir/$WORKLOAD/*/client_iperf*  \
                    results/$subdir/$WORKLOAD/max_throughput.txt -o plots/$subdir-$WORKLOAD-throughput.png
                fi

              done #protocol type (MDTCP (1), MPTCP(0) )

            done # topology

            sleep 1
            sudo chown $USER -R results
            sudo chown $USER -R plots

      done #load for FCT test
    done #workload
  done #mytest
  m=$((m + 1))

done # while
kill -9 $controllerId



