[![Coverage Status](https://coveralls.io/repos/SPSCommerce/redlock-py/badge.png)](https://coveralls.io/r/SPSCommerce/redlock-py)

redlock-py - Redis distributed locks in Python

This python lib implements the Redis-based distributed lock manager algorithm [described in this blog post](http://antirez.com/news/77).

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


**Disclaimer**: This code implements an algorithm which is currently a proposal, it was not formally analyzed. Make sure to understand how it works before using it in your production environments.
