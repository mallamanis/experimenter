import time
import json
from git import Repo, TagReference

class Experimenter:
    def __init__(self, name, parameters, directory=".", tag_prefix="experiments/"):
        '''
        Start logging a new experiment.
        :param name: the name of the experiment
        :type name: str
        :param parameters: a dictionary with all the parameters of the experiment.
        :type parameters: dict
        :param directory: a string of the directory of the git repository, where the experiment will be logged.
        :type directory: dict
        :param tag_prefix: the prefix of the "folder" where the experiment-related tags will be placed
        :type tag_prefix: str
        '''
        self.__experiment_name = "exp_" + name + str(int(time.time()))
        self.repository =  Repo(directory, search_parent_directories=True)
        self.__tag_name = tag_prefix + self.__experiment_name
        self.__tag_object = self.__start_experiment(parameters)

    def record_results(self, results):
        '''
        Record the results of this experiment, by updating the tag.
        :param results: A dictionary containing the results of the experiment.
        :type results: dict
        '''
        data = json.loads(self.__tag_object.tag.message)
        data["results"] = results
        TagReference.create(self.repository, self.__tag_name, message=json.dumps(data),
                            ref=self.__tag_object.tag.object, force=True)

    def experiment_tag(self):
        return self.__tag_name

    def __tag_repo(self, data):
        """
        Tag the current repository.
        :param data: a dictionary containing the data about the experiment
        :type data: dict
        """
        assert self.__tag_name not in [t.name for t in self.repository.tags]
        return TagReference.create(self.repository, self.__tag_name, message=json.dumps(data))


    def __start_experiment(self, parameters):
        """
        Start an experiment by capturing the state of the code
        :param parameters: a dictionary containing the parameters of the experiment
        :type parameters: dict
        :return: the tag representing this experiment
        :rtype: TagReference
        """
        #TODO: Switch branch (record old one)
        # TODO: Do a commit

        data = {"parameters": parameters, "started": time.time(), "results": {}}
        tag_object = self.__tag_repo(data)

        # TODO: Go back to original branch
        # TODO: Restore changes (as if they weren't committed)

        return tag_object
