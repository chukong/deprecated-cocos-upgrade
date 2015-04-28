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
import subprocess
import cocos
import compare_diff
from argparse import ArgumentParser

UPGRADE_PATH = 'Upgrade'

def os_is_win32():
    return sys.platform == 'win32'


def os_is_mac():
    return sys.platform == 'darwin'

if __name__ == '__main__':
    parser = ArgumentParser(description='Generate prebuilt engine for Cocos Engine.')
    parser.add_argument('-s', dest='projSourcePath', help='Your Project path')
    parser.add_argument('-d', dest='projUpgradePath', help='Your Target Project path')
    parser.add_argument('-o', dest='projOriginPath', help='Your Origin Project path')

    (args, unknown) = parser.parse_known_args()

    if len(unknown) > 0:
        print('unknown arguments: %s' % unknown)
        sys.exit(1)

    if not os.path.exists(args.projSourcePath) or not os.path.exists(args.projUpgradePath)\
            or not os.path.exists(args.projOriginPath):
        cocos.Logging.warning("> Path is not exists.")
        sys.exit(1)

    print('Receive arguments src:%s dst:%s ori:%s' % (args.projSourcePath, args.projUpgradePath, args.projOriginPath))

    diff_file = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'diff')
    if os.path.exists(diff_file):
        os.remove(diff_file)

    if os_is_mac():
        diff_tool = 'diffmerge.sh'
    else:
        diff_tool = 'sgdm'

    cocos.Logging.info("> Preparing difference file %s ..." % diff_file)
    cmd = str.format('%s -diff %s %s %s' % (diff_tool, diff_file, args.projSourcePath, args.projOriginPath))
    ret = subprocess.call(cmd, shell=True)
    # if ret != 0:
    #     sys.exit(1)
    #os.system(cmd)

    cocos.Logging.info("> Compare every single difference ...")
    compareFiles = compare_diff.CompareFiles(diff_file)
    compareFiles.compare(args.projUpgradePath)
