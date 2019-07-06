from re import search
from setuptools import setup, find_packages

with open('graphql_relay/version.py') as version_file:
    version = search('version = "(.*)"', version_file.read()).group(1)

with open('README.md') as readme_file:
    readme = readme_file.read()

setup(
    name='graphql-relay',
    version=version,
    description='Relay library for graphql-core-next',
    long_description=readme,
    long_description_content_type='text/markdown',
    keywords='graphql relay api',
    url='https://github.com/graphql-python/graphql-relay-py',
    author='Syrus Akbary',
    author_email='me@syrusakbary.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    install_requires=['graphql-core-next>=1.0.5'],
    python_requires='>=3.6',
    packages=find_packages(include=['graphql_relay']),
    zip_safe=False,
)
