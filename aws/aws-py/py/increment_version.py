#!/usr/bin/env python

import re

class IncrementVersion(object):
    def increment(self, pom_version, latest_tag=None):
        self.pom_version_is_valid(pom_version)

        if (latest_tag is not None and latest_tag is not "") and (self.version_number_matches(pom_version, latest_tag)):
            return self.increment_build_number(latest_tag)
        else:
            return "%s.%s" % (pom_version, "0")

    @staticmethod
    def increment_build_number(latest_tag):
        version_number_components = latest_tag.split(".")
        build_number = int(version_number_components[2]) + 1
        return "%s.%s.%d" % (version_number_components[0], version_number_components[1], build_number)

    @staticmethod
    def version_number_matches(pom_version, latest_tag):
        tag_version = latest_tag[0:latest_tag.rindex(".")]
        return pom_version == tag_version

    @staticmethod
    def pom_version_is_valid(pom_version):
        if (pom_version is None) or (re.match("^\d+.\d+$", pom_version) is None):
            raise InvalidVersionFormatError(
                "POM Version [%s] is not in the format of MAJOR.MINOR i.e. 1.2" % pom_version)


class InvalidVersionFormatError(Exception):
    def __init__(self, *args):
        super(InvalidVersionFormatError, self).__init__(*args)

