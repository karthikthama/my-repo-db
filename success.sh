#!/bin/bash
comm -12 <(sort /jenkins/checksum/OUTPUT2.txt) <(sort /jenkins/checksum/OUTPUT1.txt) >> /jenkins/checksum/MATCHEDOUTPUT.txt
while read line
do
$line=$(comm -12 <(sort /jenkins/checksum/OUTPUT2.txt) <(sort /jenkins/checksum/OUTPUT1.txt))

shouldbe1=$(cat /jenkins/checksum/OUTPUT2.txt | sed -n '1p')
shouldbe2=$(cat /jenkins/checksum/OUTPUT2.txt | sed -n '2p')
shouldbe3=$(cat /jenkins/checksum/OUTPUT2.txt | sed -n '3p')
shouldbe4=$(cat /jenkins/checksum/OUTPUT2.txt | sed -n '4p')
shouldbe5=$(cat /jenkins/checksum/OUTPUT2.txt | sed -n '5p')
shouldbe6=$(cat /jenkins/checksum/OUTPUT2.txt | sed -n '6p')
shouldbe7=$(cat /jenkins/checksum/OUTPUT2.txt | sed -n '7p')
shouldbe8=$(cat /jenkins/checksum/OUTPUT2.txt | sed -n '8p')
shouldbe9=$(cat /jenkins/checksum/OUTPUT2.txt | sed -n '9p')
shouldbe10=$(cat /jenkins/checksum/OUTPUT2.txt | sed -n '10p')


if [[ "$line" == "$shouldbe1" ]];
then
     echo "$(ls /var/lib/jenkins/workspace/Automated-Database-Deployment-Production | sed -n '1p')"
elif [[ "$line" == "$shouldbe2" ]];
then
     echo "$(ls /var/lib/jenkins/workspace/Automated-Database-Deployment-Production | sed -n '2p')"
elif [[ "$line" == "$shouldbe3" ]];
then
     echo "$(ls /var/lib/jenkins/workspace/Automated-Database-Deployment-Production | sed -n '3p')"
elif [[ "$line" == "$shouldbe4" ]];
then
     echo "$(ls /var/lib/jenkins/workspace/Automated-Database-Deployment-Production | sed -n '4p')"
elif [[ "$line" == "$shouldbe5" ]];
then
     echo "$(ls /var/lib/jenkins/workspace/Automated-Database-Deployment-Production | sed -n '5p')"
elif [[ "$line" == "$shouldbe6" ]];
then
     echo "$(ls /var/lib/jenkins/workspace/Automated-Database-Deployment-Production | sed -n '6p')"
elif [[ "$line" == "$shouldbe7" ]];
then
     echo "$(ls /var/lib/jenkins/workspace/Automated-Database-Deployment-Production | sed -n '7p')"
elif [[ "$line" == "$shouldbe8" ]];
then
     echo "$(ls /var/lib/jenkins/workspace/Automated-Database-Deployment-Production | sed -n '8p')"
elif [[ "$line" == "$shouldbe9" ]];
then
     echo "$(ls /var/lib/jenkins/workspace/Automated-Database-Deployment-Production | sed -n '9p')"
elif [[ "$line" == "$shouldbe10" ]];
then
     echo "$(ls /var/lib/jenkins/workspace/Automated-Database-Deployment-Production | sed -n '10p')"
else
     echo "-_-_-_-"
fi
done < /jenkins/checksum/MATCHEDOUTPUT.txt
