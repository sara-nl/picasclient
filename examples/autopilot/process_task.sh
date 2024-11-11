#!/bin/bash

#@helpdesk: SURF helpdesk <helpdesk@surf.nl>
#
# usage: ./process_task.sh [input] [tokenid]


#Enable verbosity 
set -x

#Obtain information for the Worker Node
echo ""
echo `date`
echo ${HOSTNAME}

#Initialize job arguments
INPUT=$1      
TOKENID=$2
OUTPUT=output_${TOKENID}
echo $INPUT
echo $TOKENID
echo $OUTPUT

#Start processing
bash -c "$INPUT"
if [[ "$?" != "0" ]]; then
    echo "Program interrupted. Exit now..."
    exit 1
fi

echo `date`

exit 0
