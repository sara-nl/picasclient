#!/bin/bash

#@helpdesk: SURF helpdesk <helpdesk@surf.nl>
#
# usage: ./process_task.sh [task_type] [input] [tokenid]
#
# task_type:
#   - echo_cmd
#   - fractals
#
# enable verbosity
set -x

# obtain/dump the information for the Worker Node to stdout
echo ""
echo `date`
echo ${HOSTNAME}

# initialize job arguments
INPUT=$1      
TOKENID=$2
OUTPUT=output_${TOKENID}

echo "----------- input argument ----------------"
echo "Input command: ${INPUT}"
echo "Token ID: ${TOKEN_ID}"
echo "Output file: ${OUTPUT}"
echo "------------ end input argument ---------------"

#
# start processing
#

# Use this command for the short example
bash -c "$INPUT"
# Use this command for the fractals example
# bin/fractals -o $OUTPUT $INPUT

if [[ "$?" != "0" ]]; then
    echo "Program interrupted. Exit now..."
    exit 1
fi


# Optionally, copy output to the remote storage, e.g. if run on the Grid:
# globus-url-copy file:///${PWD}/${OUTPUT} gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lsgrid/homer/${OUTPUT}

echo `date`

exit 0