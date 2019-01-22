#!/usr/bin/perl
#
# Decode_YT_SiteName - Decode the YouTube obfuscated cache names
#
# Copyright (C) 2012-2015 Maurizio Matteo Munafo'
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#

#
# This script translate occurrences of obfuscated YouTube cache names
# in the old format exposing the airport name
# It expects data from STDIN
# Possible usage: 
#
#   $ perl decode_yt_sitename.pl < filein
# 
# N.B.: Only one occurrence on each line is translated.

sub decode
{
  my $name = shift;
  $name =~ tr/0-9a-z/uzpkfa50vqlgb61wrmhc72xsnid83ytoje94/;
  return $name;
}

sub encode
{
  my $name = shift;
  $name =~ tr/0-9a-z/7elsz6dkry5cjqx4bipw3ahov29gnu08fmt1/;
  return $name;
}

while (<>)
  {
   if (/---sn-/)
    {
     if (/---sn-([0-9a-z]{8})---/ || 
         /---sn-([0-9a-z]{8})\./ )
       {
         ($a,$b,$c) = /(.+?)---sn-([0-9a-z]{8})(.+)/;
          print "$a---",decode($b),"$c\n";
       }
     elsif (/---sn-([0-9a-z]+-[0-9a-z]{4})---/ || 
            /---sn-([0-9a-z]+-[0-9a-z]{4})\./ )
       {
         ($a,$b,$c) = /(.+?)---sn-([0-9a-z]+-[0-9a-z]{4})(.+)/;
          print "$a---",decode($b),"$c\n";
       }
     else { print; }
     
    }
   elsif (/\.sn-/)
    {
     if (/\.sn-([0-9a-z]{8})---/ || 
         /\.sn-([0-9a-z]{8})\./ )
       {
         ($a,$b,$c) = /(.+?).sn-([0-9a-z]{8})(.+)/;
          print "$a.",decode($b),"$c\n";
       }
     elsif (/\.sn-([0-9a-z]+-[0-9a-z]{4})---/ || 
            /\.sn-([0-9a-z]+-[0-9a-z]{4})\./ )
       {
         ($a,$b,$c) = /(.+?)\.sn-([0-9a-z]+-[0-9a-z]{4})(.+)/;
          print "$a.",decode($b),"$c\n";
       }
     else { print; }
    }
   else 
    {
     print;
    }
  }

