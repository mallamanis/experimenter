from git import Repo
from git.repo.fun import name_to_object
import json

__all__ = ['ExperimentData']

class ExperimentData:

    def __init__(self, directory=".", tag_prefix="experiments/"):
        self.__repository = Repo(directory, search_parent_directories=True)
        self.__tag_prefix = tag_prefix

    def experiment_results(self, commit=None, must_contain_results=False):
        """
        :param commit: the commit that all the experiments should have happened or None to include all
        :type commit: str
        :param must_contain_results: include only tags that contain results
        :type must_contain_results: bool
        :return: all the experiment data
        """
        results = []
        for tag in self.__repository.tags:
            if not tag.startswith(self.__tag_prefix):
                continue
            data = json.loads(tag.tag.message)
            if "results" not in data and must_contain_results:
                continue
            if commit is not None and tag.tag.object.hexsha == name_to_object(self.__repository, commit):
                continue
            results.append(data)
        return results

    def delete(self, experiment_name):
        """
        Delete an experiment by removing the associated tag.
        :param experiment_name: the name of the experiment to be deleted
        :type experiment_name: str
        :rtype bool
        :return if deleting succeeded
        """
        target_tag = self.__tag_prefix + experiment_name
        if target_tag not in [t.name for t in self.__repository.tags]:
            return False
        self.__repository.delete_tag(target_tag)
        return target_tag not in [t.name for t in self.__repository.tags]

    def update_remote(self, remote_name=None):
        """
        Update the (default) remote by pushing the tags and removing (deleted) tags. TODO: is this last thing possible?
        :return:
        """
        raise NotImplemented() # TODO

if __name__ == "__main__":
    #TODO:
    pass