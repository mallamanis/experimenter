import os
import time
import json
import logging
from git import Repo, TagReference

__all__ = ['Experimenter']

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
        self.__repository = Repo(directory, search_parent_directories=True)
        if len(self.__repository.untracked_files) > 0:
            logging.warn("Untracked files will not be recorded: %s", self.__repository.untracked_files)
        if tag_prefix[-1] != '/':
            tag_prefix += '/'
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
        TagReference.create(self.__repository, self.__tag_name, message=json.dumps(data),
                            ref=self.__tag_object.tag.object, force=True)

    def cancel_experiment(self):
        """
        Cancel an experiment by removing the tag that has already been created.
        """
        self.__repository.delete_tag(self.__tag_name)

    def experiment_tag(self):
        return self.__tag_name

    def __tag_repo(self, data):
        """
        Tag the current repository.
        :param data: a dictionary containing the data about the experiment
        :type data: dict
        """
        assert self.__tag_name not in [t.name for t in self.__repository.tags]
        return TagReference.create(self.__repository, self.__tag_name, message=json.dumps(data))

    def __get_files_to_be_added(self):
        """
        :return: the files that have been modified and can be added
        """
        for root, dirs, files in os.walk(self.__repository.working_dir):
            if root.startswith(os.path.join(self.__repository.working_dir, ".git")):
                continue
            for f in files:
                relative_path = os.path.join(root, f)[len(self.__repository.working_dir)+1:]
                if relative_path not in self.__repository.untracked_files:
                    yield relative_path

    def __start_experiment(self, parameters):
        """
        Start an experiment by capturing the state of the code
        :param parameters: a dictionary containing the parameters of the experiment
        :type parameters: dict
        :return: the tag representing this experiment
        :rtype: TagReference
        """
        current_commit = self.__repository.head.commit
        started_state_is_dirty = self.__repository.is_dirty()

        if started_state_is_dirty:
            self.__repository.index.add([p for p in self.__get_files_to_be_added()])
            self.__repository.index.commit("Temporary commit for experiment " + self.__experiment_name)

        data = {"parameters": parameters, "started": time.time(), "results": {}}
        tag_object = self.__tag_repo(data)

        if started_state_is_dirty:
            self.__repository.head.reset(current_commit, working_tree=False, index=True)

        return tag_object
