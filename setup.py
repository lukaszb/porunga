import os
import sys
from setuptools import setup, find_packages

readme_file = os.path.abspath(os.path.join(os.path.dirname(__file__),
    'README.rst'))

try:
    long_description = open(readme_file).read()
except IOError as err:
    sys.stderr.write("[ERROR] Cannot find file specified as "
        "long_description (%s)\n" % readme_file)
    sys.exit(1)

extra_kwargs = {'tests_require': ['mock']}
if sys.version_info < (2, 7):
    extra_kwargs['tests_require'].append('unittest2')
if sys.version_info >= (3,):
    extra_kwargs['use_2to3'] = True

porunga = __import__('porunga')

setup(
    name='porunga',
    version=porunga.get_version(),
    url='https://github.com/lukaszb/porunga',
    author='Lukasz Balcerzak',
    author_email='lukaszbalcerzak@gmail.com',
    description=porunga.__doc__,
    long_description=long_description,
    zip_safe=False,
    packages=find_packages(),
    scripts=[],
    entry_points={
        'console_scripts': [
            'porunga = porunga:main',
        ],
    },
    test_suite='porunga.tests.collector',
    install_requires=['monolith', 'termcolor'],
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    **extra_kwargs
)

