#! /usr/bin/env python3

from setuptools import setup, find_packages
from os import path
from subprocess import check_output, CalledProcessError
from time import strftime, gmtime
from setuptools.command.egg_info import egg_info


class EggInfoFromGit(egg_info):

    def git_timestamp_tag(self):
        gitinfo = check_output(
            ['git', 'log', '--first-parent', '--max-count=1',
             '--format=format:%ct', '.']).strip()
        return strftime('.%Y%m%d%H%M%S', gmtime(int(gitinfo)))

    def tags(self):
        if self.tag_build is None:
            try:
                self.tag_build = self.git_timestamp_tag()
            except CalledProcessError:
                pass
        return egg_info.tags(self)


tagger = EggInfoFromGit


setup(
    name='SatScript',
    description="SatScript for BioWardrobe",
    long_description=open(path.join(path.dirname(__file__), 'README.md')).read(),
    version='1.0',
    url='https://github.com/michael-kotliar/SatScript',
    download_url='https://github.com/michael-kotliar/SatScript',
    author=['Artem Barski', 'Michael Kotliar'],
    author_email=['Artem.Barski@cchmc.org', 'misha.kotliar@gmail.com'],
    license='Apache-2.0',
    packages=find_packages(),
    install_requires=[
        "argparse",
        "matplotlib"
    ],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            "SatScript=saturation.main:main"
        ]
    },
    include_package_data=True,
    cmdclass={'egg_info': tagger},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Healthcare Industry',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Operating System :: OS Independent',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Operating System :: Microsoft :: Windows :: Windows 8.1',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Chemistry',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Medical Science Apps.'
    ]
)
