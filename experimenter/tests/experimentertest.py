import unittest
import shutil
import os
import json
from git import Repo
from experimenter import ExperimentRecorder, ExperimentData


class TestExperimenter(unittest.TestCase):

    __original_content_test1 = "This is a test!"
    __original_content_test2 = "This is another test!"

    def setUp(self):
        self.__test_repo = "/tmp/experimenter-tests/samplerepo"
        if os.path.exists(self.__test_repo):
            shutil.rmtree(self.__test_repo)
        repo = Repo.init(path=self.__test_repo)

        # Create file in some/package/test1.txt
        os.makedirs(os.path.join(self.__test_repo, "a/package"))
        self.__test1_dir = os.path.join(self.__test_repo, "a/package/", "test1.txt")
        with open(self.__test1_dir, 'w') as f:
            f.write(self.__original_content_test1)

        # Create file in some/test2.txt
        self.__test2_dir = os.path.join(self.__test_repo, "test2.txt")
        with open(self.__test2_dir, 'w') as f:
            f.write(self.__original_content_test2)

        # Commit files
        repo.index.add([self.__test1_dir, self.__test2_dir])
        repo.index.commit("Initial dummy commit")


    def test_simple(self):
        repo = Repo(self.__test_repo)
        self.assertIsNotNone(repo)

        self.assertEqual(len(repo.untracked_files), 0)
        self.assertEqual(len(repo.tags), 0)

        # Create an experiment
        experiment = ExperimentRecorder("unittest", {"testParams": True}, directory=self.__test_repo)
        self.assertEqual(len(repo.tags), 1)
        self.assertEqual(repo.tags[0].name, experiment.name())

        # Store results
        experiment.record_results({"data":10})
        self.assertEqual(len(repo.tags), 1)
        self.assertEqual(repo.tags[0].name, experiment.name())
        data = json.loads(repo.tags[0].object.message)
        self.assertEqual(data["parameters"], {"testParams": True})
        self.assertTrue("results" in data)
        self.assertEqual(data["results"], {"data":10})

        # Test with data
        d = ExperimentData(directory=self.__test_repo)
        self.assertEqual(len(d.experiment_results()), 1)
        self.assertEqual(d.experiment_results()[0], data)
        self.assertEqual(d.experiment_results(repo.tags[0].object.hexsha)[0], data)

        # Create second experiment
        experiment2 = ExperimentRecorder("unittest2", {"testParams": True}, directory=self.__test_repo)
        self.assertEqual(len(repo.tags), 2)
        self.assertEqual(repo.tags[1].name, experiment2.name())
        self.assertEqual(len(d.experiment_results()), 2)
        self.assertEqual(len(d.experiment_results(must_contain_results=True)), 1)

        experiment2.record_results({"test": "test"})
        self.assertEqual(len(repo.tags), 2)
        self.assertEqual(len(d.experiment_results(must_contain_results=True)), 2)
        self.assertEqual(len(d.experiment_results()), 2)
        self.assertEqual(d.experiment_results(repo.tags[0].object.hexsha)[0], data)
        self.assertEqual(len(d.experiment_results(repo.tags[0].object.hexsha)), 2)

        result = d.delete(experiment2.name())
        self.assertTrue(result, experiment2.name())
        self.assertEqual(len(repo.tags), 1)
        self.assertEqual(d.experiment_results(repo.tags[0].object.hexsha)[0], data)

        self.assertTrue(d.delete(experiment.name()))

    def test_uncommmited(self):
        repo = Repo(self.__test_repo)
        self.assertIsNotNone(repo)

        self.assertEqual(len(repo.untracked_files), 0)
        self.assertEqual(len(repo.tags), 0)
        with open(self.__test1_dir, 'w') as f:
            f.write(self.__original_content_test1)
            f.write("Updated!")

        experiment = ExperimentRecorder("unittest", {"testParams": True}, directory=self.__test_repo)
        self.assertNotEqual(repo.tags[0].object.hexsha, repo.head.object.hexsha)
        self.assertEqual(repo.tags[0].commit.parents[0], repo.head.object)

        with open(self.__test1_dir) as f:
            content = f.read()
        self.assertEqual(content, self.__original_content_test1+"Updated!")

        # Restore
        d = ExperimentData(directory=self.__test_repo)
        d.delete(experiment.name())
        with open(self.__test1_dir, 'w') as f:
            f.write(self.__original_content_test1)


    def tearDown(self):
        shutil.rmtree(self.__test_repo)

if __name__ == '__main__':
    unittest.main()