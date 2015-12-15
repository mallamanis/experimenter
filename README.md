Experimenter
=======
Use git tags to log experiments and the exact code that was used to run those experiments. To install use
```
pip install experimenter
```
All contributions are welcome.

Use Cases
-----
  * It is the case that you might make some changes in your machine learning code, not necessarily worth committing, and spawn a process to run an experiment that uses these changes. However, by the time the experiment has finished you don't know what changes you were testing (presumably because you made more changes in the meanwhile).
  * You need a distributed way of collecting all the experiments (parameters and results), making sure that they have been run on the exact same version of the code.

Usage
-----
Create an `ExperimentLogger` object, passing the parameters of the experiment. When the experiment is finished, call
the `record_results()` method of that object, ie:

```python
with ExperimentLogger(name="NameOfExperiment", parameters=parameters_dict) as experiment_logger:
    ...
    experiment_logger.record_results(dict_of_results)
```

Behind the scenes, a git tag will be created (committing any changes you may have in the working tree, into a different branch). The tag will have a name of the form `exp_NameOfExperiment_timestamp` and in the message it will have a JSON representation of the parameters and the results (when/if recorded). The working state of the current branch will seemingly remain unaffected. Note that this is *not* thread-safe.

If no result is recorded (ie `record_results` is not called) within the `with` then the experiment will be deleted upon exit from that block. This is useful when stopping experiments or when experiments fail before finishing.

There is a command-line tool that helps with retrieving tests. In the git folder, run the command
```
> experimenter -c SHAofCodeState
```
to retrieve all the experiments that happened with the give code version. If `-c` is not provided then all experiments will be shown. If `-s` is provided only experiments that have results will be shown. The strict command is off by default. Use `--help` for more information.
 
TODO
------
   * A command line tool for starting/stopping experiments.
   * Auto-push tags method in `ExperimentLogger`

