import redis
import string
import random
import time
from collections import namedtuple


Lock = namedtuple("Lock", ("validity", "resource", "key"))


class CannotObtainLock(Exception):
    pass


class Redlock(object):

    default_retry_count = 3
    default_retry_delay = 0.2
    clock_drift_factor = 0.01
    unlock_script = """
    if redis.call("get",KEYS[1]) == ARGV[1] then
        return redis.call("del",KEYS[1])
    else
        return 0
    end"""

    def __init__(self, connection_list, retry_count=None, retry_delay=None):
        self.servers = []
        for connection_info in connection_list:
            try:
                if isinstance(connection_info, basestring):
                    server = redis.StrictRedis.from_url(connection_info)
                else:
                    server = redis.StrictRedis(**connection_info)
                self.servers.append(server)
            except Exception as e:
                raise Warning(str(e))
        self.quorum = (len(connection_list) / 2) + 1

        if len(self.servers) < self.quorum:
            raise CannotObtainLock(
                "Failed to connect to the majority of redis servers")
        self.retry_count = retry_count or self.default_retry_count
        self.retry_delay = retry_delay or self.default_retry_delay

    def lock_instance(self, server, resource, val, ttl):
        try:
            return server.set(resource, val, nx=True, px=ttl)
        except:
            return False

    def unlock_instance(self, server, resource, val):
        try:
            server.eval(self.unlock_script, 1, resource, val)
        except:
            pass

    def get_unique_id(self):
        CHARACTERS = string.ascii_letters + string.digits
        return ''.join(random.choice(CHARACTERS) for _ in range(22))

    def lock(self, resource, ttl):
        retry = 0
        val = self.get_unique_id()

        # Add 2 milliseconds to the drift to account for Redis expires
        # precision, which is 1 millisecond, plus 1 millisecond min
        # drift for small TTLs.
        drift = int(ttl * self.clock_drift_factor) + 2

        while retry < self.retry_count:
            n = 0
            start_time = int(time.time() * 1000)
            for server in self.servers:
                if self.lock_instance(server, resource, val, ttl):
                    n += 1
            elapsed_time = int(time.time() * 1000) - start_time
            validity = int(ttl - elapsed_time - drift)
            if validity > 0 and n >= self.quorum:
                return Lock(validity, resource, val)
            else:
                for server in self.servers:
                    self.unlock_instance(server, resource, val)
                retry += 1
                time.sleep(self.retry_delay)
        return False

    def unlock(self, lock):
        for server in self.servers:
            self.unlock_instance(server, lock.resource, lock.key)
