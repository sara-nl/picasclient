#!/bin/bash
#
#SBATCH --array=0-5
#SBATCH -t 00:30:00
#SBATCH --export=ALL,DESIGN_DOC=Monitor,VIEW=todo

#how to use this example:
#1.clone the Picasclient github
#git clone https://github.com/sara-nl/picasclient.git
#cd picasclient
#2.install packages
#pip install picas
#3.create examples/picasconfig.py using template picasconfig_example.py
#4.submit pilot job
#sbatch spider_example.sh


## adding software modules load for Spider
source /cvmfs/software.eessi.io/versions/2023.06/init/bash
module load Python/3.11.3-GCCcore-12.3.0

# parse the --task-type arguments using the shift method
TASK_TYPE="echo_cmd"
if [ "$1" == "--task-type" ]; then
  shift
  TASK_TYPE=$1
  shift
fi

echo "current workdir: $(pwd)"
echo "Task type: ${TASK_TYPE}"

#pip install --user picas
cd ~/picas_tutorial/picasclient
. .venv/picas-tutorial/bin/activate
cd examples

# You may set environmental variables needed in the SLURM job
# For example, when using the LUMI container wrapper:
# export PATH="/path/to/install_dir/bin:$PATH"
python local_example.py --design_doc ${DESIGN_DOC} --view ${VIEW} --task-type ${TASK_TYPE}
