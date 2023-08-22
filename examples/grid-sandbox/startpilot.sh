# @helpdesk: SURFsara helpdesk <helpdesk@surfsara.nl>
#
# usage: . startpilot.sh
# description: 								
#	Configure PiCaS environment for the communication with couchDB 	
#	Start the pilot job                                  		


set -x

JOBDIR=${PWD}  # the directory where the job lands

tar -xvf ${JOBDIR}/picas.tar 
tar -xvf ${JOBDIR}/CouchDB-1.2.tar.gz CouchDB-1.2/couchdb && mv CouchDB-1.2/couchdb couchdb && rmdir CouchDB-1.2

echo "Start the pilot job tasks by contacting PiCaS tokens"

# set permissions for the process_task script and fractals executable
chmod u+x ${JOBDIR}/process_task.sh
chmod u+x ${JOBDIR}/fractals
ls -l ${JOBDIR}

python ${JOBDIR}/grid-example.py
