from setuptools import setup

# TODO: Update setup base on the requirements file.

"""
Version History:

0.1 - Initial Version. More Proof of Concept.
0.2 - Updates BratTools so output will keep events and attributes as all.
"""

setup(name='BRATsynthetic',
      version='0.2',
      description='A Software Tool for the Generation of HIPAA Safe Harbor Compliant Replacement Text ',
      url='https://github.com/uabnlp/BRATsynthetic',
      author='Tobias O\'Leary',
      author_email='tobiasoleary@uab.edu',
      license='MIT',
      packages=['bratsynthetic'],
      install_requires=[
            'Faker',
      ],
      zip_safe=False)


