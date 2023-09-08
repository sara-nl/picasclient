#!/bin/bash

#@helpdesk: SURF helpdesk <helpdesk@surf.nl>
#
# usage: ./process_task.sh [input] [tokenid]


# Enable verbosity 
set -x

# GRID needs to find the CVMFS conda environment
export PATH=/cvmfs/softdrive.nl/lodewijkn/miniconda3/bin:$PATH
conda init bash
source $HOME/.bashrc
conda activate snakemake-picas

# Obtain information for the Worker Node
echo ""
echo `date`
echo ${HOSTNAME}

# Initialize job arguments
INPUT=$1      
TOKENID=$2
OUTPUT=output_${TOKENID}
echo $INPUT
echo $TOKENID
echo $OUTPUT

# Start processing
eval $INPUT
#./fractals -o $OUTPUT $INPUT
if [[ "$?" != "0" ]]; then
    echo "Program interrupted. Exit now..."
    exit 1
fi

echo `date`

exit 0
