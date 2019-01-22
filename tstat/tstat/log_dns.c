/*
 *
 * Copyright (c) 2001-2008
 *	Politecnico di Torino.  All rights reserved.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * For bug report and other information please visit Tstat site:
 * http://tstat.polito.it
 *
 * Tstat is deeply based on TCPTRACE. The authors would like to thank
 * Shawn Ostermann for the development of TCPTRACE.
 *
*/

#ifdef HAVE_LDNS

#include <ldns/ldns.h>
#include "tstat.h"

#define UDP_HDR_SZ 8
#define MAX_STR_DNS 256
#define REPLACE_FIELDS 4
#define MAX_SUB 65535
#define swap(x,y) { x = x + y; y = x - y; x = x - y; }
extern FILE *fp_dns_logc;

// Utility function prototype
static inline char * replace_char (char *s, char find, char replace, int max_replace);
static inline char * pkt_rcode2str(ldns_pkt_rcode rcode);
static inline char * rr_class2str(ldns_rr_class rcode);
static inline char * rr_type2str(ldns_rr_type rcode);


void *
check_dns(struct udphdr *pudp, int tproto, void *pdir, void *plast)
{
  /* just pass the complete packet and let the  */
  return (void *) pudp;
}



void dns_flow_stat(struct ip *pip, void *pproto, int tproto, void *pdir,
		int dir, void *hdr, void *plast)
{
  
  ldns_pkt * pkt;
  ldns_rr * rr;
  int i;
  int pkt_id;
  int is_query;
  ldns_pkt_rcode rcode;
  ucb * thisdir;
  ldns_rr_list* rr_list;
  char * type;
  struct sudp_pair *pup;
  int internal_client, crypto_client,  internal_server, crypto_server;

  if (fp_dns_logc == NULL || !(LOG_IS_ENABLED(LOG_DNS_COMPLETE)))
    return;

  // Find UDP control block
  thisdir = (ucb *) pdir;
  pup = thisdir->pup;

  // Check if one of IP addresses is multicast
  if (pup->addr_pair.b_address.addr_vers == 4)
  {
    uint32_t ip_addr_a = ntohl (pup->addr_pair.a_address.un.ip4.s_addr);
    uint32_t ip_addr_b = ntohl (pup->addr_pair.b_address.un.ip4.s_addr);
    if ( (ip_addr_a >= LB_MULTICAST && ip_addr_a < UB_MULTICAST) || (ip_addr_b >= LB_MULTICAST && ip_addr_b < UB_MULTICAST) )
      return;
  }
  #ifdef SUPPORT_IPV6
  else
  {
    if (pup->addr_pair.b_address.un.ip6.s6_addr[0] == 0xFF || pup->addr_pair.a_address.un.ip6.s6_addr[0] == 0xFF)
      return;
  }
  #endif

  // Check it is a well formed DNS packet
  ldns_status ret = ldns_wire2pkt ( &pkt, (const uint8_t *) hdr + UDP_HDR_SZ , getpayloadlength(pip, plast) - UDP_HDR_SZ  ) ;
  if (ret == LDNS_STATUS_OK)
  {

    // Check if it is Request or Response and parse Packet Fields
    if ( ldns_pkt_qr (pkt ) == 1 )
    {
      is_query=0;
      type="RESP";
      rr_list =  ldns_pkt_answer (pkt ) ;
      rcode = ldns_pkt_get_rcode (pkt);
    } 
    else
    {
      is_query=1;
      rr_list =  ldns_pkt_question (pkt ) ;
      type = "REQ";
    }

    // <pkt_id> contains transaction ID 
    pkt_id = ldns_pkt_id (pkt);

    // Get Flags
    int flag_AA = ldns_pkt_aa(pkt);
    int flag_TC = ldns_pkt_tc(pkt);
    int flag_RD = ldns_pkt_rd(pkt);
    int flag_RA = ldns_pkt_ra(pkt);
    int flag_AD = ldns_pkt_ad(pkt);
    int flag_CD = ldns_pkt_cd(pkt);
    int flags   = flag_CD + (flag_AD << 1) + (flag_RA << 2) + (flag_RD << 3) + (flag_TC << 4) + (flag_AA << 5);

    // Get number of Queries, Anwers, Auth Records and additional records
    int qdcount = ldns_pkt_qdcount(pkt);
    int ancount = ldns_pkt_ancount(pkt);
    int nscount = ldns_pkt_nscount(pkt);
    int arcount = ldns_pkt_arcount(pkt);

    // Get PKT size
    int size = ldns_pkt_size(pkt);


    // <tuple_str_src> contains L3 and L4 information for Source
    char tuple_str_src [MAX_STR_DNS]; 
    if (pup->crypto_src==FALSE)
      sprintf (tuple_str_src, "%s %s", HostName (pup->addr_pair.a_address), ServiceName (pup->addr_pair.a_port));
    else
      sprintf (tuple_str_src, "%s %s", HostNameEncrypted (pup->addr_pair.a_address), ServiceName (pup->addr_pair.a_port));
    // Client direction info
    internal_client = pup->internal_src;
    crypto_client = pup->crypto_src;

    // <tuple_str_dst> contains L3 and L4 information for Destination        
    char tuple_str_dst [MAX_STR_DNS]; 
    if (pup->crypto_dst==FALSE)
      sprintf (tuple_str_dst,"%s %s", HostName (pup->addr_pair.b_address), ServiceName (pup->addr_pair.b_port));
    else
      sprintf (tuple_str_dst, "%s %s", HostNameEncrypted (pup->addr_pair.b_address), ServiceName (pup->addr_pair.b_port));
    // Server direction info
    internal_server = pup->internal_dst;
    crypto_server = pup->crypto_dst;

    // Find Client and Server -- Must invert when finding spurious responses...
    char * client_str=tuple_str_src;
    char * server_str=tuple_str_dst;
    if (is_query == 0 && &(pup->c2s) == thisdir)
    {
      client_str= tuple_str_dst;
      server_str= tuple_str_src;
      swap(internal_client, internal_server);
      swap(crypto_client, crypto_server);
    }
    // ... and when finding spurious requests
    if (is_query == 1 && &(pup->c2s) != thisdir)
    {
      client_str= tuple_str_dst;
      server_str= tuple_str_src;
      swap(internal_client, internal_server);
      swap(crypto_client, crypto_server);
    }

    // Check if it is an <error response> and, in case, print Error code and eventual question
    if ( is_query==0 && rcode != LDNS_RCODE_NOERROR )
    { 
      char * type = "RESP_ERR";
      char * rcode_str = pkt_rcode2str(rcode);
      char question [MAX_STR_DNS];
      char * class_str =	"-";
      char * type_str =	"-";

      // Search eventual Question
      ldns_rr_list * rr_list_question =  ldns_pkt_question (pkt ) ;
      strcpy ( question, "--");
      if (ldns_rr_list_rr_count (rr_list_question) > 0)
      {

        // Copy the Owner of the first question
        rr = ldns_rr_list_rr(rr_list_question, 0);
        ldns_rdf* rdf = ldns_rr_owner(rr);
        memcpy(question,rdf->_data,rdf->_size );
        question[rdf->_size]=0;

        //Find and replace the label counts with '.'
        int index=0;
        while (index < rdf->_size)
        {
          int tmp_len=question[index];
          question[index]='.';
          index += (tmp_len+1);
        }
        // Replace empty string with "-"
        if (question[1] == '\0')      
          strcpy(question+1,"-");

        // Get class and type
        class_str =	rr_class2str(ldns_rr_get_class (rr));
        type_str =	rr_type2str (ldns_rr_get_type (rr));

      }
      
      wfprintf (fp_dns_logc,"%s %d %d %s %d %d %f %s 0x%04x %s - %s %s %s 0x%02x %d %d %d %d %d\n",
                client_str, internal_client, crypto_client,
                server_str, internal_server, crypto_server,
                time2double(current_time)/1e3, 
                type,pkt_id,question+1,class_str,type_str,rcode_str,flags,
                qdcount,ancount,nscount,arcount, size);
    }
    // If Query has no error
    else{
      // Iterate over RRs and print a log line for each one
      for(i = 0; i < ldns_rr_list_rr_count(rr_list); i++)
      {
        // It is a query
        if (is_query==1)
        {
          char question [MAX_STR_DNS];
          rr = ldns_rr_list_rr(rr_list, i);
          ldns_rdf* rdf = ldns_rr_owner(rr);

          // Find the Owner of the question
          memcpy(question,rdf->_data,rdf->_size );
          question[rdf->_size]=0;
          
          //Find and replace the label counts with '.'
          int index=0;
          while (index < rdf->_size)
          {
            int tmp_len=question[index];
            question[index]='.';
            index += (tmp_len+1);
          }
          // Replace empty string with "-"
          if (question[1] == '\0')      
            strcpy(question+1,"-");

          // Get class and type
          char * class_str =	rr_class2str(ldns_rr_get_class (rr));
          char * type_str =	rr_type2str (ldns_rr_get_type (rr));

          wfprintf (fp_dns_logc,"%s %d %d %s %d %d %f %s 0x%04x %s - %s %s - 0x%02x %d %d %d %d %d\n",
                    client_str, internal_client, crypto_client,
                    server_str, internal_server, crypto_server,
                    time2double(current_time)/1e3, 
                    type, pkt_id, question+1,class_str,type_str,flags,
                    qdcount,ancount,nscount,arcount, size); 

        }
        // It is a response
        else
        {

          rr = ldns_rr_list_rr(rr_list, i);

          // <rr_str> contains DNS information
          char * rr_str = ldns_rr2str(rr);

          // Replace delimiters with spaces, and intra-field spaces with tabs
          char * last_field = replace_char (rr_str, '\t', ' ',REPLACE_FIELDS);
          replace_char ( last_field, ' ', '\t', MAX_SUB);

          // Remove \n in last position
          int len = strlen(rr_str);
          rr_str[len-1]='\0';

          wfprintf (fp_dns_logc,"%s %d %d %s %d %d %f %s 0x%04x %s 0x%02x %d %d %d %d %d\n",
                    client_str, internal_client, crypto_client,
                    server_str, internal_server, crypto_server,
                    time2double(current_time)/1e3, type, pkt_id, rr_str, flags,
                    qdcount,ancount,nscount,arcount, size); 

          free (rr_str);
        }
      }
    }

    // Free the DNS packet
    if (pkt)
       ldns_pkt_free(pkt);

  }

}


// Utility Function to replace Char with Tab; no more than <max_replace> are performed
static inline char * replace_char (char *s, char find, char replace, int max_replace) {
  int replaced = 0;
  char * last_field = s;

  while (*s != 0)
  {
    if (*s == find && replaced < max_replace){
      *s = replace;
      replaced++;
      last_field=s;
    }
    s++;
  }
  return last_field+1;
}

// Utility Function to get string representation of error codes
static inline char * pkt_rcode2str(ldns_pkt_rcode rcode)
{
  switch (rcode) {
    case LDNS_RCODE_NOERROR:
        return ( "NO_ERROR");
        break;
    case LDNS_RCODE_FORMERR:
        return ( "FORMERR");
        break;
    case LDNS_RCODE_SERVFAIL:
        return ( "SERVFAIL");
        break;
    case LDNS_RCODE_NXDOMAIN:
        return ( "NXDOMAIN");
        break;
    case LDNS_RCODE_NOTIMPL:
        return ( "NOTIMPL");
        break;
    case LDNS_RCODE_REFUSED:
        return ( "REFUSED");
        break;
    case LDNS_RCODE_YXDOMAIN:
        return ( "YXDOMAIN");
        break;
    case LDNS_RCODE_YXRRSET:
        return ( "YXRRSET");
        break;
    case LDNS_RCODE_NXRRSET:
        return ( "NXRRSET");
        break;
    case LDNS_RCODE_NOTAUTH:
        return ( "NOTAUTH");
        break;
    case LDNS_RCODE_NOTZONE:
        return ( "NOTZONE");
        break;
    default:
        return ( "UNKNOWN-ERROR");
  break;
  }
}

// Utility Function to get string representation of error codes
static inline char * rr_class2str(ldns_rr_class rcode)
{
  switch (rcode) 
  {
      case LDNS_RR_CLASS_IN:
          return ( "IN");
          break;
      case LDNS_RR_CLASS_CH:
          return ( "CH");
          break;
      case LDNS_RR_CLASS_HS:
          return ( "HS");
          break;
      case LDNS_RR_CLASS_NONE:
          return ( "NONE");
          break;
      case LDNS_RR_CLASS_ANY:
          return ( "ANY");
          break;
      default:
          return ( "OTHER");
          break;
  }
}

static inline char * rr_type2str(ldns_rr_type rcode)
{
  switch (rcode) {
      case LDNS_RR_TYPE_A:
          return ( "A");
          break;
      case LDNS_RR_TYPE_AAAA:
          return ( "AAAA");
          break;
      case LDNS_RR_TYPE_CNAME:
          return ( "CNAME");
          break;
      case LDNS_RR_TYPE_PTR:
          return ( "PTR");
          break;
      case LDNS_RR_TYPE_SOA:
          return ( "SOA");
          break;
      case LDNS_RR_TYPE_NS:
          return ( "NS");
          break;
      case LDNS_RR_TYPE_MX:
          return ( "MX");
          break;
      case LDNS_RR_TYPE_TXT:
          return ( "TXT");
          break;
      case LDNS_RR_TYPE_HINFO:
          return ( "HINFO");
          break;
      case LDNS_RR_TYPE_SSHFP:
          return ( "SSHFP");
          break;
      case LDNS_RR_TYPE_GPOS:
          return ( "GPOS");
          break;
      case LDNS_RR_TYPE_LOC:
          return ( "LOC");
          break;
      case LDNS_RR_TYPE_DNSKEY:
          return ( "DNSKEY");
          break;
#ifdef LDNS_RR_TYPE_NSEC3PARAM
      case LDNS_RR_TYPE_NSEC3PARAM:
          return ( "NSEC3PARAM");
          break;
#endif /* LDNS_RR_TYPE_NSEC3PARAM */
      case LDNS_RR_TYPE_NSEC3:
          return ( "NSEC3");
          break;
      case LDNS_RR_TYPE_NSEC:
          return ( "NSEC");
          break;
      case LDNS_RR_TYPE_RRSIG:
          return ( "RRSIG");
          break;
      case LDNS_RR_TYPE_DS:
          return ( "DS");
          break;
      case LDNS_RR_TYPE_DNAME:
          return ( "DNAME");
          break;
      case LDNS_RR_TYPE_NAPTR:
          return ( "NAPTR");
          break;
      case LDNS_RR_TYPE_RP:
          return ( "RP");
          break;
      case LDNS_RR_TYPE_SRV:
          return ( "SRV");
          break;
      case LDNS_RR_TYPE_SPF:
          return ( "SPF");
          break;
      case 32:
	  /* Type 32 (0x0020) is wrongly used by NetBios on port 137 (RFC1002) even if
	     officially allocated to NIMLOC/NIMROD (RFC1992)
	    */
          return ( "NB");
          break;
      default:
          return ( "OTHER");
          break;
  }
}


#endif //HAVE_LDNS

