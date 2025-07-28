from setuptools import setup, find_packages


setup(
    name='starmap_client',
    description='Client for StArMap',
    version='2.4.0',
    keywords='stratosphere content artifact mapping cli',
    author='Jonathan Gangi',
    author_email='jgangi@redhat.com',
    url='https://github.com/release-engineering/starmap-client',
    license='GPLv3+',
    packages=find_packages(exclude=['tests', 'tests.*']),
    package_data={"starmap-client": ["py.typed"]},
    include_package_data=True,
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
    ],
    install_requires=[
        'attrs',
        'requests',
        'requests_mock',
        'urllib3',
    ],
    zip_safe=False,
)
