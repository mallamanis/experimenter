from git import Repo
from git.repo.fun import name_to_object
import json

class ExperimentData:

    def __init__(self, directory=".", tag_prefix="experiments/"):
        self.__repository = Repo(directory, search_parent_directories=True)
        self.__tag_prefix = tag_prefix

    def experiments(self, commit=None, must_contain_results=False):
        """
        :param commit: the commit that all the experiments should have happened or None to include all
        :type commit: str
        :param must_contain_results: include only tags that contain results
        :type must_contain_results: bool
        :return: all the experiment data
        """
        results = []
        for tag in self.__repository.tags:
            data = json.loads(tag.tag.message)
            if "results" not in data  and must_contain_results:
                continue
            if commit is not None and tag.tag.object.hexsha == name_to_object(self.__repository, commit):
                continue
            results.append(data)

if __name__ == "__main__":
    #TODO:
    pass