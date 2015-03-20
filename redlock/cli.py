from __future__ import print_function

import argparse
import sys
import textwrap

import redlock


def log(*args, **kwargs):
    if not log.quiet:
        print(*args, file=sys.stderr, **kwargs)


def lock(name, validity, redis, retry_count=3, retry_delay=200, **kwargs):
    if retry_count < 0:
        retry_count = 0
        is_blocking = True
    else:
        is_blocking = False

    while True:
        err = None
        try:
            dlm = redlock.Redlock(redis, retry_count=retry_count+1, retry_delay=retry_delay / 1000.0)
            lock = dlm.lock(name, validity)

            if lock is False:
                log("failed")
                err = 1
            else:
                log("ok")
                print(lock.key)
                return 0
        except Exception as e:
            log("error %s" % e)
            err = 3

        if is_blocking:
            # redlock already slept for retry-delay
            continue
        else:
            return err


def unlock(name, key, redis, **kwargs):
    try:
        dlm = redlock.Redlock(redis)
        lock = redlock.Lock(0, name, key)
        dlm.unlock(lock)
    except Exception as e:
        log("Error: %s" % e)
        return 3

    log("ok")
    return 0


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
            Return codes:
                0 if the action succeeded
                1 if the action failed (eg. timed out)
                2 if there was an error with the options
                3 if there was an error communicating with Redis (eg. socket timeout)
        """))
    parser.add_argument("--redis", action="append", default=None, help="Redis URL (eg. redis://localhost:6379/0", metavar="URL")
    parser.add_argument("--quiet", action="store_true", default=False, help="No stderr output, just a return code (and key for lock action)")

    subparsers = parser.add_subparsers(help='See command help via `%(prog)s <command> --help`')
    parser_lock = subparsers.add_parser('lock', help='Acquire a lock', description="""
        For non-blocking behaviour, set --retry-count=0 and --retry-delay=0.
        For infinitely blocking behaviour with retries every second, set --retry-count=-1 and --retry-delay=1000.
    """)
    parser_lock.set_defaults(func=lock)
    parser_lock.add_argument("--retry-count", type=int, default=3, help="Number of retries")
    parser_lock.add_argument("--retry-delay", type=int, default=200, help="Milliseconds between retries")
    parser_lock.add_argument("name", help="Lock resource name")
    parser_lock.add_argument("validity", type=int, help="Number of milliseconds the lock will be valid.")

    parser_unlock = subparsers.add_parser('unlock', help='Release a lock')
    parser_unlock.set_defaults(func=unlock)
    parser_unlock.add_argument("name", help="Lock resource name")
    parser_unlock.add_argument("key", help="Result returned by a prior 'lock' command")

    args = parser.parse_args()
    log.quiet = args.quiet

    if not args.redis:
        args.redis = ["redis://localhost:6379/0"]

    result = args.func(**vars(args))

    sys.exit(result)

if __name__ == "__main__":
    main()
