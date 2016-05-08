from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='experimenter',
      version='0.1.6',
      description='Use git to record experiment results (as git tags) keeping the exact code that was used.',
      keywords='experiment reproducibility git',
      url='http://github.com/mallamanis/experimenter',
      author='Miltos Allamanis',
      author_email='mallamanis@gmail.com',
      license='MIT',
      packages=['experimenter'],
      install_requires=['gitpython', 'argparse'],
      test_suite='nose.collector',
      tests_require=['nose'],
      scripts=['bin/experimenter'],
      zip_safe=False)
