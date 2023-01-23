#!/usr/bin/env python

if __name__ == '__main__':
    import sys
    from increment_version import IncrementVersion

    sys.tracebacklimit = 0

    if len(sys.argv) == 2:
        print IncrementVersion().increment(sys.argv[1])
    elif len(sys.argv) == 3:
        print IncrementVersion().increment(sys.argv[1], sys.argv[2])
    else:
        print "Usage: bump_version.py <pom_version> [<latest_tag>]"
        sys.exit(0)
