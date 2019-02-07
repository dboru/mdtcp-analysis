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
int    header_size               = 54; //54(TCP_hdr+IPv4_hdr+Ethernet) 86(MPTCP header,max_packet size 1428, TCP 1448) 
int    max_ether_size            = 1500;//1500

/* IP address configuration */
/*const char * const host_ip[] = {
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
  };*/

/* Port usage (port id used) */
/*int host_port_offset[] = {
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
  };*/

/* Get the next available port id of the host */
static int get_host_next_port(int host,int host_port_offset[]) 
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

	int req_per_sec=0;

	int num_sch=0;
	double time_ref=0.0;
        int hosts_per_edge=2;
	int seed=754;


	if (argc > 3) {
		load=atof(argv[1]);
		flow_total_num=atoi(argv[2]);
		seed=atoi(argv[3]);
                hosts_per_edge=atoi(argv[4]);
                host_num=8*hosts_per_edge;
	} else if (argc < 2  && argc > 1)
	{
		load=atof(argv[1]);
	}


	int p, e,h;
	char host_ip[host_num+1][30];
	int ipcount=0;
	int host_port_offset[host_num+1];

	for (p=0;p<4;p++)
		for (e=0; e<2;e++)
			for (h=2;h<(hosts_per_edge+2);h++){
				char ip[80];
				strcpy(ip, "10.");
				sprintf(ip, "%s%d", ip, p);
				strcat(ip, ".");
				sprintf(ip, "%s%d", ip, e);
				strcat(ip, ".");
				sprintf(ip, "%s%d", ip, h);
				strcpy(host_ip[ipcount], ip);
				host_port_offset[ipcount]=20000;

				ipcount++;

				//printf("Ip address: %s\n",ipList[0]);

			}

	flow_size_dist = (struct cdf_table*)malloc(sizeof(struct cdf_table));
	init_cdf(flow_size_dist);
	load_cdf(flow_size_dist, flow_cdf_file);
	// header_size=20B(IPv4)+20B(TCP+checksum)+14B(Ethernet)+4B(FCS)+12B(InterframeGap)+8B(Preamble)=78B

	/* Average request arrival interval (in microsecond) */
	double mean_flowsize = avg_cdf(flow_size_dist); 

	req_per_sec=((1000000*host_num*load)/(8*mean_flowsize+(8*mean_flowsize*header_size/max_payload_size)));

	period_us = 8.0*(mean_flowsize+(mean_flowsize*header_size/max_payload_size))/(host_num*load); 


	// period_us = (8*avg_cdf(flow_size_dist)*(max_ether_size + 66))/(host_num*load*max_payload_size); 
	//per server period
	float period_sec = (8*avg_cdf(flow_size_dist)*max_ether_size)/(load*max_payload_size*1000000.0); 

	printf("req_per_sec  %d \n", req_per_sec);

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

		if (num_sch < req_per_sec){
			num_sch=num_sch+1;
		}

		else if (num_sch>=req_per_sec)
		{
			num_sch=1;

			if ((flow_start_time-time_ref)<1)
				flow_start_time=1.0+time_ref+(((float)rand()/(float)(RAND_MAX)) * 0.5);
			time_ref=flow_start_time;
		}

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
				get_host_next_port(src_host,host_port_offset),
				get_host_next_port(dst_host,host_port_offset),
				flow_size,
				flow_start_time);
		if (flow_id==flow_total_num-1)
			fprintf(output_flow_file, "%d %s %s %d %d %d %.9f\n",
					flow_id,
					host_ip[src_host],
					host_ip[dst_host],
					get_host_next_port(src_host,host_port_offset),
					get_host_next_port(dst_host,host_port_offset),
					flow_size,
					period_sec);

		fclose(output_flow_file);

	}

	return 0;
}
