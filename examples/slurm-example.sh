#!/bin/bash
#SBATCH --array=0-5
#SBATCH --export=DESIGN_DOC=Monitor,VIEW=todo

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



# You may set environmental variables needed in the SLURM job
# For example, when using the LUMI container wrapper:
# export PATH="/path/to/install_dir/bin:$PATH"

python local_example.py --design_doc $DESIGN_DOC --view $VIEW
