#!/bin/bash

#@helpdesk: SURF helpdesk <helpdesk@surf.nl>
#
# usage: ./process_task.sh [input] [tokenid]

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
echo $INPUT
echo $TOKENID
echo $OUTPUT

#
# start processing
#

# short example, just echo the input
# use this command for the short example
bash -c "$INPUT"

# long example, run the fractals program (uncomment the next line to use it)
# use this command for the fractals example
#bin/fractals -o $OUTPUT $INPUT

if [[ "$?" != "0" ]]; then
    echo "Program interrupted. Exit now..."
    exit 1
fi

#Copy output to the remote storage, e.g.
#globus-url-copy file:///${PWD}/${OUTPUT} gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lsgrid/homer/${OUTPUT}

echo `date`

exit 0
