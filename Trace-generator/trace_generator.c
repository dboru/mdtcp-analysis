/*
   The code generates the output_flow_file based on flow_cdf_file
 */
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>

#include "cdf.h"

/* Basic flow settings */
int    host_num                  = 16; /* number of hosts */
int    flow_total_num            = 1000; /* total number of flows to generate */
int    flow_total_time           = 0; /* total time to generate requests (in seconds) */
//int    load                      = 100; /* average network load in Mbps per host */
int    incast                    = 0; /* all-to-one when set to 1 */
struct cdf_table *flow_size_dist = NULL; /* flow distribution table*/
char   flow_cdf_file[100]        = "cdf/dctcp.cdf"; /* flow size distribution file */
int    header_size               = 54;
int    max_ether_size            = 1500;

/* IP address configuration */
const char * const host_ip[] = {
	"10.0.0.2",
	"10.0.0.3",
	"10.0.1.2",
	"10.0.1.3",
	"10.1.0.2",
	"10.1.0.3",
	"10.1.1.2",
	"10.1.1.3",
	"10.2.0.2",
	"10.2.0.3",
	"10.2.1.2",
	"10.2.1.3",
	"10.3.0.2",
	"10.3.0.3",
	"10.3.1.2",
	"10.3.1.3"
};

/* Port usage (port id used) */
int host_port_offset[] = {
	20000,
	20000,
	20000,
	20000,
	20000,
	20000,
	20000,
	20000,
	20000,
	20000,
	20000,
	20000,
	20000,
	20000,
	20000,
	20000
};

/* Get the next available port id of the host */
static int get_host_next_port(int host) 
{
	host_port_offset[host]++;
	return (host_port_offset[host]);
}

/* Generate poission process arrival interval */
double poission_gen_interval(double avg_rate)
{
	if (avg_rate > 0)
		return -logf(1.0 - (double)(rand() % RAND_MAX) / RAND_MAX) / avg_rate;
	else
		return 0;
}

int main(int argc, char **argv) 
{
	FILE   *output_flow_file = NULL;
	char   output_filename[100] = "trace_file/mdtcp-output.trace";
	int    flow_id = 0;
	int    flow_size = 0;
	double flow_start_time = 0.0; /* in second */
	int    max_payload_size = max_ether_size - header_size;
	double period_us;
	double load=100.0;/*load */

	int seed=754;
	float elephant_time[16];
	int  flows[16];

	double flows_time[16];
	
	int i=0;

	for (i=0;i<16;i++){
		elephant_time[i]=0.0;
		flows[i]=0;
		flows_time[i]=0.0;
	}

	if (argc > 3) {
		load=atof(argv[1]);
		flow_total_num=atoi(argv[2]);
		seed=atoi(argv[3]);
	} else if (argc < 2  && argc > 1)
	{
		load=atof(argv[1]);
	}

	flow_size_dist = (struct cdf_table*)malloc(sizeof(struct cdf_table));
	init_cdf(flow_size_dist);
	load_cdf(flow_size_dist, flow_cdf_file);

	/* Average request arrival interval (in microsecond) */
	period_us = ((avg_cdf(flow_size_dist)*8.0/max_payload_size)*max_ether_size)/(host_num*load); 
	/*
	   printf("host_num        %d \n", host_num);
	   printf("flow_total_num  %d \n", flow_total_num);
	   printf("flow_total_time %d \n", flow_total_time);
	   printf("load            %d \n", load);
	   printf("avg_flowsize    %f \n", avg_cdf(flow_size_dist));
	   printf("period_us       %f \n", period_us);
	 */	   
	//printf("period_us       %f \n", period_us);
	/* Convert flow_total_time to flow_total_num */
	if (flow_total_num == 0 && flow_total_time > 0)
		flow_total_num = flow_total_time * 1000000 / period_us;

	/* Set random seed */
	srand(seed); 

	/* Generate traffic flows */
	for (flow_id=0; flow_id<flow_total_num; flow_id++) {

		int src_host = rand() % host_num;
		int dst_host = rand() % host_num;

		/* Skip if the src_host and dst_host are the same */
		while (src_host == dst_host)
			dst_host = rand() % host_num;


		/* Assign flow size and start time */
		flow_start_time = flow_start_time + poission_gen_interval(1.0 / period_us) / 1000000;

		flow_size = gen_random_cdf(flow_size_dist);

		/*schedule one elephant flow per 50ms for a server (median value of large flows=1 from DCTCP paper)*/

		if (flow_size > 1000000 && elephant_time[dst_host] > 0 && (flow_start_time-elephant_time[dst_host]<0.05))
			continue;
		else if (flow_size > 1000000)
			elephant_time[dst_host]=flow_start_time;

		int num_pkts=(flows[dst_host]+flow_size)/max_ether_size;

		

		/*don't overload the server*/ 
        
        if (flows_time[dst_host]> 0.0 && (flow_start_time-flows_time[dst_host])>0)
        {
        	if ((8*(flows[dst_host]+flow_size+num_pkts*header_size)/(1000000*(flow_start_time-flows_time[dst_host]))) > load)
        		continue;
        	else
        		flows[dst_host]+=flow_size;
        } 
        else if(flows_time[dst_host] == 0.0)
        	flows_time[dst_host]=flow_start_time;


		/* Incast: only accept dst_host = 0 */
		if (incast && dst_host != 0) {
			flow_id--;
			continue;
		}

		/* Write to output file */
		output_flow_file = fopen(output_filename, "a");
		fprintf(output_flow_file, "%d %s %s %d %d %d %.9f\n",
				flow_id,
				host_ip[src_host],
				host_ip[dst_host],
				get_host_next_port(src_host),
				get_host_next_port(dst_host),
				flow_size,
				flow_start_time);
		fclose(output_flow_file);

	}

	return 0;
}
