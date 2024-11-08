#!/bin/bash
#SBATCH --array=0-5


#@helpdesk: SURF helpdesk <helpdesk@surf.nl>
#
#usage: sbatch slurm-example.sh
#description:
#    Connect to PiCaS server
#    Get the next token in todo View
#    Fetch the token parameters, e.g. input value
#    Run main job (process_task.sh) with the input argument
#    When done, return the exit code to the token
#    Attach the logs to the token


cd $PWD
# You need to load your environment here
# mamba activate MAMBA-ENV
# source /PATH/TO/VENV/bin/activate
python local_example.py
