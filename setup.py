from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='experimenter',
      version='0.1',
      description='Use git to record experiment results along with the appropriate version of the code.',
      url='http://github.com/mallamanis/experimenter',
      author='Miltos Allamanis',
      author_email='mallamanis@gmail.com',
      license='MIT',
      packages=['experimenter'],
      install_requires=['gitpython'],
      zip_safe=False)