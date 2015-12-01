import os
import time
import json
import logging
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
        self.repository = Repo(directory, search_parent_directories=True)
        if len(self.repository.untracked_files) > 0:
            logging.warn("Untracked files will not be recorded: %s", self.repository.untracked_files)
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

    def __get_files_to_be_added(self):
        """
        :return: the files that have been modified and can be added
        """
        for root, dirs, files in os.walk(self.repository.working_dir):
            for f in files:
                relative_path = os.path.join(root, f)[len(self.repository.working_dir):]
                if relative_path not in self.repository.untracked_files:
                    yield relative_path

    def __start_experiment(self, parameters):
        """
        Start an experiment by capturing the state of the code
        :param parameters: a dictionary containing the parameters of the experiment
        :type parameters: dict
        :return: the tag representing this experiment
        :rtype: TagReference
        """
        current_commit = self.repository.head.commit
        started_state_is_dirty = self.repository.is_dirty()

        if started_state_is_dirty:
            self.repository.index.add([p for p in self.__get_files_to_be_added()])
            self.repository.index.commit("Temporary commit for experiment")

        data = {"parameters": parameters, "started": time.time(), "results": {}}
        tag_object = self.__tag_repo(data)

        if started_state_is_dirty:
            self.repository.head.reset(current_commit, working_tree=False, index=True)

        return tag_object
