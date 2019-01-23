#!/bin/sh
mn -c 

cdate=$(date +"%Y%m%d")

DURATION=20
iperf="iperf"
mdtcp_debug=0
queue_size=400

# test=0 throughput test, test=1 FCT
qmon=1
bwm=1
tcpdump=0
tcpprobe=0

num_reqs=1000
cdir=$(pwd)
echo $cdir
export PYTHONPATH=${PYTHONPATH}:$cdir/src
mkdir -p plots

python src/pox/pox.py DCController --topo=ft,4 --routing=ECMP &
controllerId=$!
echo $controllerId

sleep 1

# proto 0=mptcp, proto=1=mdtcp
m=1
bw=10
delay=1

seed=754

while [ $m -le 1 ] ; 
do
  seed=$(( seed + m )) 

  for mytest in 0 ;
  do 
    for WORKLOAD in 'one_to_one';
    do 
    # 0.2 0.4 0.6 0.8 0.9 ;
    for load in 0.1  ; 
    do 
      
      dload=$(echo "scale=4; $bw*$load" | bc)
     
      #generate traffic for the desired load

      if [ $mytest -eq 1 ]; 
      then 
        echo $dload
        cd ../Trace-generator
        rm  trace_file/mdtcp-output.trace
        ./trace_generator $dload $num_reqs $seed
        cd ../dijkstra-controller
      fi

     
     # cp ../Trace-generator/trace_file/mdtcp-output.trace requests_load$dload

      for pod in 4 ; 
      do 
        for proto in 1 0 ;
        do 
          for subflows in 1 4 ; 
          do
            # find . -name 'ss_clnt_10*' | xargs rm -f
            
            if [ $tcpprobe -eq 1 ] ;
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
              redmax=30001
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

                  if [ $mytest -eq 1 ];
                  then 
                    cp ../Trace-generator/trace_file/mdtcp-output.trace $out_dir/requests_load$dload
                  fi
                  
                  echo 'We are here'

                  python src/fattree.py -d $out_dir -t $DURATION --ecmp --iperf \
                  --workload $WORKLOAD --K $pod --bw $bw --delay $delay --mdtcp $mdtcp --dctcp $dctcp --redmax $redmax\
                  --redmin $redmin --burst  $redburst --queue  $queue_size --prob $redprob --enable_ecn $enable_ecn\
                  --enable_red $enable_red --subflows $subflows --mdtcp_debug $mdtcp_debug --num_reqs $num_reqs\
                  --test $mytest --qmon $qmon --iter $m   --load $load --bwm  $bwm --tcpdump $tcpdump --tcpprobe $tcpprobe

                  sudo mn -c

                # Plots 

                  if [ $mytest -eq 1 ]
                  then 
                    python src/process/process_fct.py  -s $subflows -f results/$subdir/$WORKLOAD/*/flows_10* -o plots/$subdir-$WORKLOAD.png
                  fi

                  if [ $qmon -eq 1 ]
                  then
                    for f in $subflows
                    do
                      python src/process/plot_queue_monitor.py -f results/$subdir/$WORKLOAD/flows$f/queue_size* -o plots/$subdir-$WORKLOAD-flows$f
                    done
                  fi

              	  if [ $bwm -eq 1 ]
              	  then
              	  for f in $subflows
              	  do
                    python src/process/process_bwm_ng_rates.py -f results/$subdir/$WORKLOAD/flows$f/rates_iter* -b $bw -o plots/$subdir-$WORKLOAD-flows$f
              	  done 
              	  fi

                sleep 1

                done #subflow

                if [ $mytest -eq 0 ]
                then 
                  python src/process/plot_hist_all.py -k $pod -w $WORKLOAD -t $DURATION -f results/$subdir/$WORKLOAD/*/client_iperf*  \
                    results/$subdir/$WORKLOAD/max_throughput.txt -o plots/$subdir-$WORKLOAD-throughput.png
                fi

                # End Plots 

              done #protocol type (MDTCP (1), MPTCP(0) )

            done # topology

            sleep 1
            # a=$USER
            sudo chown doljira -R results
            sudo chown doljira -R plots

      done #load for FCT test
    done #workload
  done #mytest
  m=$(( m + 1 ))

done # while
kill -9 $controllerId



