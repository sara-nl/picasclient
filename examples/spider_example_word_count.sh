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

# force a safer target and reinit EESSI
module purge
export EESSI_ARCHDETECT_OPTIONS_OVERRIDE="x86_64/generic"
source /cvmfs/software.eessi.io/versions/2023.06/init/bash

# confirm what EESSI picked
echo "EESSI subdir: $EESSI_SOFTWARE_SUBDIR"   # should say x86_64/generic

# check CPU model and flags
lscpu | egrep 'Model name|Flags'
# look for avx2, fma, bmi2, etc.

# load python again and run
module load Python/3.11.3-GCCcore-12.3.0
python3 -V
python3 -c "import sys; print(sys.version)"

echo "current workdir: $(pwd)"

#pip install --user picas
cd ~/picas_tutorial/picasclient
python3 -m venv .venv/picas-tutorial
. .venv/picas-tutorial/bin/activate
#pip install .
cd examples

python3 word_count_example.py
