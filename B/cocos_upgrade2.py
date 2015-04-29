#
# ----------------------------------------------------------------------------
# Upgrade the cocos2d engine to the specified version by a specified patch file
#
# Copyright 2015 (C) lijun
#
# License: MIT
# ----------------------------------------------------------------------------

import os
import sys
import cocos
import excopy
import subprocess
from argparse import ArgumentParser

UPGRADE_PATH = 'Upgrade'
REPLACE_NAME = 'HelloWorld'

if __name__ == '__main__':
    parser = ArgumentParser(description='Upgrade Cocos Engine for your project.')
    parser.add_argument('-d', dest='projPath', help='Your Project path.')
    parser.add_argument('-n', dest='projName', help='Your Project name.')
    parser.add_argument('-p', dest='patchFile', help='The patch file path.')
    (args, unknown) = parser.parse_known_args()

    if len(unknown) > 0:
        print('unknown arguments: %s' % unknown)
        sys.exit(1)

    if not os.path.exists(args.projPath) or not os.path.exists(args.patchFile):
        cocos.Logging.warning("> Project is not exists.")
        sys.exit(1)

    print('Receive arguments target:%s name:%s patch:%s' % (args.projPath, args.projName, args.patchFile))

    target_project_path = args.projPath
    diff_path = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'temp.diff')
    if os.path.exists(diff_path):
        os.remove(diff_path)

    # Creat a git repository if there is not a repository.
    cmd = "git init \n git add -A \n git commit -m \'Init project for cocos upgrade.\'"
    ret = subprocess.call(cmd, cwd=target_project_path, shell=True)
    # if ret != 0:
    #     sys.exit(1)

    cmd = "export LANG=C\nexport LANG=C"
    ret = subprocess.call(cmd, shell=True)
    if ret != 0:
        sys.exit(1)
        
    cmd = str.format('sed -e \'s/%s/%s/g\' %s > %s'
                     % (REPLACE_NAME, args.projName, args.patchFile, diff_path))
    ret = subprocess.call(cmd, shell=True)
    if ret != 0:
        sys.exit(1)

    # Apply patch.
    cmd = str.format("git apply --reject -p 1 %s" % diff_path)
    ret = subprocess.call(cmd, cwd=target_project_path, shell=True)

    # Apply rejected patch if it is not applied completely.
    cmd = 'find . -name \'*.rej\''
    ret = subprocess.check_output(cmd, cwd=target_project_path, shell=True)
    files = ret.split('\n')

    for rejectFile in files:
        originFile, extension = os.path.splitext(rejectFile)
        temp, extension = os.path.splitext(originFile)
        # Wiggle would causes conflicts in these files that is hard to resolve, so we leave those to you.
        if extension == '.pbxproj' or extension == '.filters' or extension == '.vcxproj':
            continue
        cmd = str.format("wiggle --replace %s %s" % (originFile, rejectFile))
        ret = subprocess.call(cmd, cwd=target_project_path, shell=True)

    # Remove .porig file created by wiggle.
    cmd = 'find . -name \'*.porig\' | xargs rm -f'
    ret = subprocess.call(cmd, cwd=target_project_path, shell=True)

    # Compare .rej file created by git.
    cmd = 'find . -name \'*.rej\' | xargs rm -f'
    ret = subprocess.call(cmd, cwd=target_project_path, shell=True)

    # Commit all changes.
    cmd = str.format("git add -A \n git commit -m \'cocos upgrade\'")
    ret = subprocess.call(cmd, cwd=target_project_path, shell=True)
    if ret != 0:
        sys.exit(1)