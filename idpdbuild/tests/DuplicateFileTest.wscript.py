#!/usr/bin/python
from idpdbuild.DuplicateFileTask import DuplicateFileTask


def configure(ctx):
    print("Configuring")


def build(bld):
    test_txt = bld.path.find_resource("test.txt")
    bld.add_to_group(DuplicateFileTask(bld, test_txt))
