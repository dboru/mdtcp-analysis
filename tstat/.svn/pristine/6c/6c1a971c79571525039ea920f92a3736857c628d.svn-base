/*
 *
 * Copyright (c) 2001
 *      Politecnico di Torino.  All rights reserved.
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
 * v1.2.0 memcpy optimization
*/

/*
 * Functions to correlate IPv4 and IPv6 addresses.
 * They are defined here separately, so they can be located and changed
 * according to the needs
 */

#include "tstat.h"

#if defined(SUPPORT_IPV6) && defined(SUPPORT_MIXED_DNS)

void correlate_6to4(struct in6_addr *ip_src6,struct in_addr *ip_src4)
{
  // We implement here the rule to extrapolate an IPv4 address from IPv6
  
  // Operator rule: <ISP 32 Prefix>:<ipv4>::/64
  ip_src4->s_addr = ip_src6->s6_addr32[1];
  
  /*
  
  Alternative rules:
  
  6over4 fe80::ipv4 
   ip_src4->s_addr = ip_src6->s6_addr32[3];
   
  6to4 2002::/16 -> 2002:ipv4::/48
   ip_src4->s_addr = (ip_src6->s6_addr32[0]|0x0000ffff)<<16 +
                     (ip_src6->s6_addr32[1]|0xffff0000)>>16 
            (verify endianess)
  */
  
  return;
}

void normalize_6to4(struct in6_addr *ip_src6,struct in6_addr *ip_dest6)
{
  // We implement here the rule to normalize an IPv6 address to a IPv4->6 address
  // (i.e. the IPv6 DNSCache equivalent format for an IPv4 address
  
  // Equivalent to the conversion from IPv6 to IPv4 and then the mapping of the
  // IPv4 address to the normalized format used by DNSCache like in map_4to6()

  // Operator rule: <ISP 32 Prefix>:<ipv4>::/64
  
  ip_dest6->s6_addr32[0] = 0;
  ip_dest6->s6_addr32[1] = 0;
  ip_dest6->s6_addr32[2] = 0;
  ip_dest6->s6_addr32[3] = ip_src6->s6_addr32[1];
  
  /*
  
  Rules similar to correlate_6to4()
  
  6over4
  ip_dest6->s6_addr32[0] = 0;
  ip_dest6->s6_addr32[1] = 0;
  ip_dest6->s6_addr32[2] = 0;
  ip_dest6->s6_addr32[3] = ip_src6->s6_addr32[3];
  
  6to4
  ip_dest6->s6_addr32[0] = 0;
  ip_dest6->s6_addr32[1] = 0;
  ip_dest6->s6_addr32[2] = 0;
  ip_dest6->s6_addr32[3] = (ip_src6->s6_addr32[0]|0x0000ffff)<<16 +
                           (ip_src6->s6_addr32[1]|0xffff0000)>>16 
            (verify endianess)
  */
  
  return;
}

#endif
