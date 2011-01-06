#!/bin/sh
for f in $*
do
    url=$(curl -s -S -F "file1=@$f" http://ompldr.org/upload | grep "File:" | cut -c 70-94)
    echo "$url"
done
