import os
import time
import json
import logging
from git import Repo, TagReference

__all__ = ['ExperimentLogger']

class ExperimentLogger:
    def __init__(self, name, parameters, directory=".", tag_prefix="experiments/", description=None):
        '''
        Start logging a new experiment.
        :param name: the name of the experiment
        :type name: str
        :param parameters: a dictionary with all the parameters of the experiment.
        :type parameters: dict
        :param directory: a string of the directory of the git repository, where the experiment will be logged.
        :type directory: str
        :param tag_prefix: the prefix of the "folder" where the experiment-related tags will be placed
        :type tag_prefix: str
        '''
        self.__experiment_name = "exp_" + name + str(int(time.time()))
        self.__results_recorded = False
        self.__repository_directory = directory
        if tag_prefix[-1] != '/':
            tag_prefix += '/'
        self.__tag_name = tag_prefix + self.__experiment_name
        self.__parameters = parameters
        self.__description = description

    def __enter__(self):
        self.__start_experiment(self.__parameters)
        logging.info("Started experiment %s", self.__tag_name)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        repository = Repo(self.__repository_directory, search_parent_directories=True)
        print("exiting"+str((exc_type, exc_val, exc_tb)))
        if not self.__results_recorded:
            repository.delete_tag(self.__tag_name)
            logging.warning("Experiment %s cancelled, since no results were recorded.", self.__tag_name)
        logging.info("Experiment %s completed", self.__tag_name)

    def record_results(self, results):
        """
        Record the results of this experiment, by updating the tag.
        :param results: A dictionary containing the results of the experiment.
        :type results: dict
        """
        repository = Repo(self.__repository_directory, search_parent_directories=True)
        for tag in repository.tags:
            if tag.name == self.__tag_name:
                tag_object = tag
                break
        else:
            raise Exception("Experiment tag has been deleted since experiment started")
        data = json.loads(tag_object.tag.message)
        data["results"] = results
        TagReference.create(repository, self.__tag_name, message=json.dumps(data),
                            ref=tag_object.tag.object, force=True)
        self.__results_recorded = True

    def record_results_and_push(self, results, remote_name='origin'):
        """
        Record the results of this experiment, by updating the tag and push to remote
        :param results:  A dictionary containing the results of the experiment.
        :type results: dict
        :param remote_name: the name of the remote to push the tags (or None for the default)
        :type remote_name: str
        """
        #self.record_results(results)
        #self.__repository.remote(name=remote_name).push() #TODO: Create refspecs for tag
        raise NotImplemented()

    def name(self):
        return self.__tag_name

    def __tag_repo(self, data, repository):
        """
        Tag the current repository.
        :param data: a dictionary containing the data about the experiment
        :type data: dict
        """
        assert self.__tag_name not in [t.name for t in repository.tags]
        return TagReference.create(repository, self.__tag_name, message=json.dumps(data))

    def __get_files_to_be_added(self, repository):
        """
        :return: the files that have been modified and can be added
        """
        for root, dirs, files in os.walk(repository.working_dir):
            for f in files:
                relative_path = os.path.join(root, f)[len(repository.working_dir) + 1:]
                try:
                    repository.head.commit.tree[relative_path] # will fail if not tracked
                    yield relative_path
                except:
                    pass

    def __start_experiment(self, parameters):
        """
        Start an experiment by capturing the state of the code
        :param parameters: a dictionary containing the parameters of the experiment
        :type parameters: dict
        :return: the tag representing this experiment
        :rtype: TagReference
        """
        repository = Repo(self.__repository_directory, search_parent_directories=True)
        if len(repository.untracked_files) > 0:
            logging.warning("Untracked files will not be recorded: %s", repository.untracked_files)
        current_commit = repository.head.commit
        started_state_is_dirty = repository.is_dirty()

        if started_state_is_dirty:
            repository.index.add([p for p in self.__get_files_to_be_added(repository)])
            commit_obj = repository.index.commit("Temporary commit for experiment " + self.__experiment_name)
            sha = commit_obj.hexsha
        else:
            sha = repository.head.object.hexsha

        data = {"parameters": parameters, "started": time.time(), "description": self.__description,
                "commit_sha": sha}
        tag_object = self.__tag_repo(data, repository)

        if started_state_is_dirty:
            repository.head.reset(current_commit, working_tree=False, index=True)

        return tag_object
