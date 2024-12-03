# -*- coding: utf-8 -*-
"""
@author Maarten Kooyman
"""

from os import environ


def add_job_id(doc):
    """
    Add job number id to a token/document. For batch jobs,
    adds information of the highest level of batch system,
    since job submision systems may be layered e.g:
    A glite wms system makes underneath use of a cream system which makes use
    of PBS. In such a case only the glite wms id instead of all of them.
    """

    dirac_jobid = environ.get("DIRACJOBID")
    wms_jobid = environ.get("GLITE_WMS_JOBID")
    cream_jobid = environ.get("CREAM_JOBID")
    pbs_jobid = environ.get("PBS_JOBID")
    slurm_jobid = environ.get("SLURM_JOB_ID")
    slurm_array_jobid = environ.get("SLURM_ARRAY_JOB_ID")
    slurm_array_taskid = environ.get("SLURM_ARRAY_TASK_ID")

    if dirac_jobid is not None:
        doc["dirac_job_id"] = dirac_jobid
    elif wms_jobid is not None:
        if not wms_jobid.startswith("http"):
            wms_jobid = None
        doc["wms_job_id"] = wms_jobid
    elif cream_jobid is not None:
        doc["cream_job_id"] = cream_jobid
    elif pbs_jobid is not None:
        doc["pbs_job_id"] = pbs_jobid
    elif slurm_array_jobid is not None:
        doc["slurm_job_id"] = slurm_array_jobid+"_"+slurm_array_taskid
    elif slurm_jobid is not None:
        doc["slurm_job_id"] = slurm_jobid


def remove_job_id(doc):
    """
    removes all job id from doc/token
    """
    if "slurm_job_id" in doc:
        del doc["slurm_job_id"]
    if "dirac_job_id" in doc:
        del doc["dirac_job_id"]
    if "wms_job_id" in doc:
        del doc["wms_job_id"]
    if "cream_job_id" in doc:
        del doc["cream_job_id"]
    if "pbs_job_id" in doc:
        del doc["pbs_job_id"]
