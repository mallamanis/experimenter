import unittest
import shutil
import os
import json
from git import Repo
from experimenter import ExperimentLogger, ExperimentData


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
        with ExperimentLogger("unittest", {"testParams": True}, directory=self.__test_repo) as experiment:
            exp_name = experiment.name()
            self.assertEqual(len(repo.tags), 1)
            self.assertEqual(repo.tags[0].name, exp_name)

            # Store results
            experiment.record_results({"data":10})
            self.assertEqual(len(repo.tags), 1)
            self.assertEqual(repo.tags[0].name, exp_name)
            data = json.loads(repo.tags[0].object.message)
            self.assertEqual(data["parameters"], {"testParams": True})
            self.assertTrue("results" in data)
            self.assertEqual(data["results"], {"data":10})

            # Test with data
            d = ExperimentData(directory=self.__test_repo)
            self.assertEqual(len(d.experiment_data()), 1)
            self.assertEqual(d.experiment_data()[exp_name], data)
            self.assertEqual(d.experiment_data(repo.tags[0].tag.object.hexsha)[exp_name], data)

            # Create second experiment
            with ExperimentLogger("unittest2", {"testParams": True}, directory=self.__test_repo) as experiment2:
                exp2_name = experiment2.name()
                self.assertEqual(len(repo.tags), 2)
                self.assertEqual(repo.tags[0].name, exp2_name)
                self.assertEqual(len(d.experiment_data()), 2)
                self.assertEqual(len(d.experiment_data(must_contain_results=True)), 1)

                experiment2.record_results({"test": "test"})
        self.assertEqual(len(repo.tags), 2)
        self.assertEqual(len(d.experiment_data(must_contain_results=True)), 2)
        self.assertEqual(len(d.experiment_data()), 2)
        self.assertEqual(d.experiment_data(repo.tags[0].tag.object.hexsha)[experiment.name()], data)
        self.assertEqual(len(d.experiment_data(repo.tags[0].tag.object.hexsha)), 2)


        result = d.delete(exp2_name)
        self.assertTrue(result, exp2_name)
        self.assertEqual(len(repo.tags), 1)
        self.assertEqual(d.experiment_data(repo.tags[0].tag.object.hexsha)[experiment.name()], data)

        self.assertTrue(d.delete(exp_name))

    def test_uncommmited(self):
        repo = Repo(self.__test_repo)
        self.assertIsNotNone(repo)

        self.assertEqual(len(repo.untracked_files), 0)
        self.assertEqual(len(repo.tags), 0)
        with open(self.__test1_dir, 'w') as f:
            f.write(self.__original_content_test1)
            f.write("Updated!")



        with ExperimentLogger("unittest", {"testParams": True}, directory=self.__test_repo) as experiment:
            self.assertNotEqual(repo.tags[0].object.hexsha, repo.head.object.hexsha)
            self.assertEqual(repo.tags[0].commit.parents[0], repo.head.object)

            with open(self.__test1_dir) as f:
                content = f.read()
                self.assertEqual(content, self.__original_content_test1+"Updated!")

            experiment_name = experiment.name()

        # Restore
        self.assertTrue(experiment_name not in [t.name for t in repo.tags])  # Context manager must have deleted it

        with open(self.__test1_dir, 'w') as f:
            f.write(self.__original_content_test1)


    def tearDown(self):
        shutil.rmtree(self.__test_repo)

if __name__ == '__main__':
    unittest.main()