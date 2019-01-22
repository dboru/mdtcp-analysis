#!/bin/sh

for stream in 'tshark -r $1 -T fields -e tcp.stream | sort -n | uniq'
do
    echo $stream

    tshark -r $1 -w stream-$stream.cap -R "tcp.stream==$stream"

done