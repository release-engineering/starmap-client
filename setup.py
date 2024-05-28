from setuptools import setup, find_packages

setup(
    name='starmap-client',
    description='Client for StArMap',
    version='1.3.0',
    keywords='stratosphere content artifact mapping cli',
    author='Jonathan Gangi',
    author_email='jgangi@redhat.com',
    url='https://gitlab.cee.redhat.com/stratosphere/starmap-client',
    license='GPLv3+',
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    install_requires=[
        'attrs',
        'requests',
        'urllib3<2.0.0'
    ],
    zip_safe=False,
)
