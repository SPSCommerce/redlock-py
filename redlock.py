import redis
from datetime import datetime, timedelta
import string
import random
import time
from collections import namedtuple


Lock = namedtuple("Lock", ("validity", "resource", "key"))


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
                server = redis.StrictRedis(**connection_info)
                self.servers.append(server)
            except Exception as e:
                raise Warning(str(e))
        self.quorum = (len(self.servers) / 2) + 1
        self.retry_count = retry_count or self.default_retry_count
        self.retry_delay = retry_delay or self.default_retry_delay

    def lock_instance(self, server, resource, val, ttl):
        try:
            return server.set(resource, val, nx=True, ex=ttl)
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
        while retry < self.retry_count:
            n = 0
            start_time = datetime.utcnow()
            for server in self.servers:
                if self.lock_instance(server, resource, val, ttl):
                    n += 1
            drift = (ttl * self.clock_drift_factor) + 2
            now_time = datetime.utcnow()
            elapsed_time_minus_drift = ((now_time - start_time) - timedelta(milliseconds=drift)).total_seconds() * 1000
            validity = elapsed_time_minus_drift < ttl
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

