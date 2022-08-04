#!/bin/bash
var=$(comm -12 <(sort -u /jenkins/checksum/OUTPUT1.txt) <(sort -u /jenkins/checksum/OUTPUT2.txt) | wc -l)
shouldbe=$(wc -l < /jenkins/checksum/OUTPUT2.txt)
if [[ "$var" != "$shouldbe" ]];
then
        echo "-----------CHECKSUM IS NOT VERIFIED--------------------"
        echo "UNMATCHED CHECKSUM NUMBERS ARE :
$(comm -23 <(sort /jenkins/checksum/OUTPUT2.txt) <(sort /jenkins/checksum/OUTPUT1.txt))"
        echo "UNMATCHED FILES ARE
$(bash /jenkins/checksum/failure.sh)"
        exit 1
else
        echo "-----------CHECKSUM IS VERIFIED--------------------"
        echo "MATCHED CHECKSUM NUMBERS ARE :
$(comm -12 <(sort /jenkins/checksum/OUTPUT2.txt) <(sort /jenkins/checksum/OUTPUT1.txt))"
        echo "MATCHED FILES ARE
$(bash /jenkins/checksum/success.sh)"