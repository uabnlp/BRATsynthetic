from setuptools import setup

setup(name='BRATsynthetic',
      version='0.1',
      description='A Software Tool for the Generation of HIPAA Safe Harbor Compliant Replacement Text ',
      url='https://github.com/uabnlp/BRATsynthetic',
      author='Tobias O\'Leary',
      author_email='tobiasoleary@uab.edu',
      license='MIT',
      packages=['bratsynthetic'],
      install_requires=[
          'Faker'
      ],
      zip_safe=False)


