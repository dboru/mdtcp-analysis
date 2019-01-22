#!/usr/bin/perl -w

use Net::CIDR;
use strict;

# Check if an IP address is internal (local) or not
# returns '1' for internal addresses, '0' otherwise
# Needed for versions of Tstat before 2.2 (r330), where 
# internal_dst (column 100) was included in the log.

{
 # @internal contains the list of internal networks,
 # in the ip/bitmask format, equivalent to the one used running
 # tstat (-N option)
  my @internal = qw{
130.192.0.0/16
192.168.0.0/16
224.0.0.0/4
};

my %ips = ();

sub is_internal
{
  my $ip = shift;
    unless (exists $ips{$ip}{'inside'})
     {
       $ips{$ip}{'inside'} =  Net::CIDR::cidrlookup($ip,@internal);
     }
  return $ips{$ip}{'inside'};
}

}

1;
