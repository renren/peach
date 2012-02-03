#!/bin/bash
FN=access.log.1
WL=`wc -l $FN|cut -f1 -d' '`
C=100
echo $FN $WL $C
for i in `seq 1 $(($WL / $C))`
do
	t=$(($i * $C))
	#echo $t
	head -n $t $FN | tail -n $C | curl -NT - http://10.2.76.28:8000/tornado
	sleep 8
done
