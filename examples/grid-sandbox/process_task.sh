#!/bin/bash

#@helpdesk: SURFsara helpdesk <helpdesk@surfsara.nl>
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
./fractals -o $OUTPUT $INPUT
if [[ "$?" != "0" ]]; then
    echo "Program interrupted. Exit now..."
    exit 1
fi

#Copy output to the grid storage
#globus-url-copy file:///${PWD}/${OUTPUT} gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lsgrid/homer/${OUTPUT}

echo `date`

exit 0
