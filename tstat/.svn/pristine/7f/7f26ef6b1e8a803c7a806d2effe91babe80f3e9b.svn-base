#!/usr/bin/perl -w
# Usage: merge_http_flows.pl [-x] filename
# Author: Maurizio M. Munafo'

use strict;
use Getopt::Std;

my %opts= ();
getopts("xh",\%opts);

if ($opts{h})
 {
   print <<EOL;
Usage: $0 [-x] filename
  Joins matching HTTP requests and response from a Tstat log_http_complete file.
  If 'filename' is missing, it gets the data from STDIN (so you can use pipes). 
  Output is sent to STDOUT.
  When -x is used, only the UNMATCHED entries are printed (e.g. to feed the 
  processing of further files). Unmatched entries are unsorted, so they should 
  be sorted by timestamp (`sort -n -k 5`) before further elaborations.
EOL
exit;
 }

my $print_unmatched = 0;

$print_unmatched = 1 if $opts{x};

my %request = ();
my %response = ();

while (<>)
 {
   next if (/^#/);
   chomp;
   my @a = split "\t";
   my $key = "$a[0] $a[1] $a[2] $a[3]";
   unless ($a[5] =~ /HTTP/)
    {
      $request{$key}{'time'} = $a[4];
      $request{$key}{'line'} = $_;
      $request{$key}{'pending'} = 1;
    }
   else
    {
      if (exists($request{$key}) && $request{$key}{'pending'} == 1)
       {
         print $request{$key}{'line'},"\t",$_,"\n" unless $print_unmatched;
	 delete $request{$key};
       }
      else
       {
         $response{$key}{'time'} = $a[4];
         $response{$key}{'line'} = $_;
         $response{$key}{'pending'} = 1;
       }
    }
 }

if ($print_unmatched)
{
my $pending;
foreach $pending (keys %request)
 {
   print $request{$pending}{'line'},"\n" if ($request{$pending}{'pending'}==1);
 }
 
foreach $pending (keys %response)
 {
   print $response{$pending}{'line'},"\n" if ($response{$pending}{'pending'}==1);
 }
}
