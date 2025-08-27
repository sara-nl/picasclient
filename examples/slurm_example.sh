#!/bin/bash
#
#SBATCH --array=0-5
#SBATCH --export=ALL,DESIGN_DOC=Monitor,VIEW=todo

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

# parse the --task-type arguments using the shift method
TASK_TYPE="echo_cmd"
if [ "$1" == "--task-type" ]; then
  shift
  TASK_TYPE=$1
  shift
fi

echo "current workdir: $(pwd)"
echo "Task type: ${TASK_TYPE}"

python3 local_example.py --design_doc ${DESIGN_DOC} --view ${VIEW} --task-type ${TASK_TYPE}
