import unittest
from os import environ

from picas.jobid import add_job_id, remove_job_id
from picas.documents import Document


class TestJobid(unittest.TestCase):

    def setUp(self):
        self.doc = Document()
        self.env_vars = {
            "DIRACJOBID": "dirac_job_id",
            "SLURM_JOB_ID": "slurm_job_id",
            "GLITE_WMS_JOBID": "wms_job_id",
            "CREAM_JOBID": "cream_job_id",
            "PBS_JOBID": "pbs_job_id"
        }

    def test_add_job_id(self):
        """ Test if job_id is added to token"""
        for test in self.env_vars:
            environ[test] = "http/jobid"
            add_job_id(self.doc)
            self.assertTrue(self.doc[self.env_vars[test]] == "http/jobid")
            environ.pop(test)

        environ["GLITE_WMS_JOBID"] = "jobid"
        add_job_id(self.doc)
        self.assertTrue(self.doc["wms_job_id"] is None)

    def test_remove_job_id(self):
        """ Test if job_id is removed from token"""
        for test in self.env_vars:
            self.doc[self.env_vars[test]] = "jobid"
            remove_job_id(self.doc)
            self.assertRaises(KeyError, self.doc.__getitem__, self.env_vars[test])
