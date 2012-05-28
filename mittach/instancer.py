#!/usr/bin/env python

"""
Mittach instance creation script
"""

from __future__ import absolute_import, division, with_statement

import sys
import os

from ConfigParser import RawConfigParser
from hashlib import sha1
from random import random


def main(args):
    args = [unicode(arg, "utf-8") for arg in args]
    try:
        instance_path = os.path.abspath(args[1])
    except IndexError:
        print "Error: missing instance path"
        return False
    try:
        mode = args[2]
    except IndexError:
        mode = "production"
        print "no mode specified, defaulting to %s" % mode

    settings = {
        "mode": mode,
        "secret": sha1(str(random())).hexdigest()
    }

    os.makedirs(instance_path)
    config_file = os.path.join(instance_path, "config.ini")
    print "creating %s instance in %s" % (mode, instance_path)
    _write_config(config_file, settings)

    return True


def _write_config(filepath, settings):
    config = RawConfigParser()

    section = "settings"
    config.add_section(section)

    for key, value in settings.items():
        config.set(section, key, value)

    with open(filepath, "wb") as fh:
        config.write(fh)


if __name__ == "__main__":
    status = not main(sys.argv)
    sys.exit(status)
