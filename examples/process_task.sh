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
TASK_TYPE=$1
INPUT=$2
TOKEN_ID=$3

OUTPUT=output_${TOKEN_ID}
echo "----------- input argument ----------------"
echo "Task type: ${TASK_TYPE}"
echo "Input command: ${INPUT}"
echo "Token ID: ${TOKEN_ID}"
echo "Output file: ${OUTPUT}"
echo "------------ end input argument ---------------"

#
# start processing
#

# execute the task based on the task type
if [[ "${TASK_TYPE}" == "fractals" ]]; then
    # long example, run the fractals program
    bin/fractals -o $OUTPUT $INPUT
elif [[ "${TASK_TYPE}" == "echo_cmd" ]]; then
    # short example, just echo the input
    bash -c "$INPUT"
else
    echo "Unknown task type: ${TASK_TYPE}"
    exit 1
fi

if [[ "$?" != "0" ]]; then
    echo "Program interrupted. Exit now..."
    exit 1
fi

#Copy output to the remote storage, e.g.
#globus-url-copy file:///${PWD}/${OUTPUT} gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lsgrid/homer/${OUTPUT}

echo `date`

exit 0
