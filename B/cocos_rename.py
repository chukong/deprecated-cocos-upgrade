#
# ----------------------------------------------------------------------------
# Upgrade the cocos2d engine to the specified version.
#
# Copyright 2015 (C) lijun
#
# License: MIT
# ----------------------------------------------------------------------------

import os
import sys
import cocos
import project_rename
from argparse import ArgumentParser

def os_is_win32():
    return sys.platform == 'win32'


def os_is_mac():
    return sys.platform == 'darwin'

if __name__ == '__main__':
    parser = ArgumentParser(description='Generate prebuilt engine for Cocos Engine.')
    parser.add_argument('-s', dest='projPath', help='Your Project Path')
    parser.add_argument('-n', dest='projName', help='New Project name')
    parser.add_argument('-p', dest='packageName', help='New project package name')
    (args, unknown) = parser.parse_known_args()

    if len(unknown) > 0:
        print('unknown arguments: %s' % unknown)
        sys.exit(1)

    if not os.path.exists(args.projPath) or not os.path.exists(args.projPath + '/cocos-project-template.json'):
        cocos.Logging.warning("> src or cocos-project-template.json is not exists.")
        sys.exit(1)

    print('Receive arguments src:%s name:%s package:%s' % (args.projPath, args.projName, args.packageName))

    creator = project_rename.TPCreator(args.projPath, args.projName, args.packageName)
    creator.do_default_step()
