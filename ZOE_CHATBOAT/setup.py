from setuptools import setup, find_packages
from codecs import open
from os import path

import versioneer

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# get the dependencies and installs
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
dependency_links = [x.strip().replace('git+', '') for x in all_reqs if x.startswith('git+')]

setup(
    name='zoe-chatboat',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='package that can be installed with pip.',
    long_description=long_description,
    url='https://gitlab.infr.zglbl.net/zeta-datacloud/data-cloud-bizops/zoe-chatboat.git',
    license='BSD',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
    ],
    keywords='',
    packages=find_packages(exclude=['docs', 'tests*']),
    package_data={'./zoe-chatboat.config': ['*']},
    include_package_data=True,
    author='Chaitanya Tatisetti',
    install_requires=install_requires,
    dependency_links=dependency_links,
    author_email='ctatisetti@aptroid.com')
