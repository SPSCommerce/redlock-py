import os

from setuptools import setup, find_packages

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

README = """
redlock-py - Redis distributed locks in Python

This python lib implements the Redis-based distributed lock manager algorithm
[described in this blog post](http://antirez.com/news/77).

To create a lock manager:

    dlm = Redlock([{"host": "localhost", "port": 6379, "db": 0}, ])

To acquire a lock:

    my_lock = dlm.lock("my_resource_name",1000)

Where the resource name is an unique identifier of what you are trying to lock
and 1000 is the number of milliseconds for the validity time.

The returned value is `False` if the lock was not acquired (you may try again),
otherwise an namedtuple representing the lock is returned, having three fields:

* validity, an integer representing the number of milliseconds the lock will be valid.
* resource, the name of the locked resource as specified by the user.
* key, a random value which is used to safe reclaim the lock.

To release a lock:

    dlm.unlock(my_lock)

It is possible to setup the number of retries (by default 3) and the retry
delay (by default 200 milliseconds) used to acquire the lock.


**Disclaimer**: This code implements an algorithm which is currently a proposal,
it was not formally analyzed. Make sure to understand how it works before using it
in your production environments.

The MIT License (MIT)

Copyright (c) 2014 SPS Commerce, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

setup(
    name='redlock-py',
    version='1.0.6',
    packages=find_packages(),
    include_package_data=True,
    description='Redis locking mechanism',
    long_description=README,
    url='https://github.com/SPSCommerce/identity-service',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'
    ],
    author='pjdecoursey@spscommerce.com',
    author_email='webapps@spscommerce.com',
    install_requires=["redis"],
    entry_points={
        'console_scripts': [
            'redlock = redlock.cli:main',
        ],
    }
)
