#
# ----------------------------------------------------------------------------
# Generate patch for Cocos Upgrade.
#
# Copyright 2015 (C) lijun
#
# License: MIT
# ----------------------------------------------------------------------------

import os
import sys
import subprocess
import cocos
import excopy
import shutil
from argparse import ArgumentParser


def remove_dir_except(root_dir, excpet):
    filelist = os.listdir(root_dir)
    for f in filelist:
        filepath = os.path.join(root_dir, f)
        if os.path.isfile(filepath):
            os.remove(filepath)
        elif os.path.isdir(filepath) and f != excpet:
            shutil.rmtree(filepath, True)

if __name__ == '__main__':
    parser = ArgumentParser(description='Generate patch for Cocos Upgrade.')
    parser.add_argument('-s', dest='source_project', help='Source directory')
    parser.add_argument('-d', dest='target_project', help='Target directory')
    parser.add_argument('-o', dest='output_dir', help='The default is patch')

    (args, unknown) = parser.parse_known_args()
    if len(unknown) > 0:
        print('unknown arguments: %s' % unknown)
        sys.exit(1)

    if not os.path.exists(args.source_project) or not os.path.exists(args.target_project):
        cocos.Logging.warning("> Path is not exists.")
        sys.exit(1)

    if args.output_dir is None:
        args.output_dir = os.path.join(os.getcwd(), 'diff')
    if os.path.exists(args.output_dir):
        shutil.rmtree(args.output_dir)
    os.makedirs(args.output_dir)
    # Create directory and file for upgrade.
    print('Receive arguments src:%s dst:%s output:%s' % (args.source_project, args.target_project, args.output_dir))

    work_path = os.path.join(os.getcwd(), 'work_path')
    if os.path.exists(work_path):
        shutil.rmtree(work_path)
    os.mkdir(work_path)

    # Create project.
    excopy.copy_files_in_dir(args.source_project, work_path)

    # Create patch.
    cmd = "git init \n git add -A \n git commit -m \'Init project for cocos upgrade.\'"
    ret = subprocess.call(cmd, cwd=work_path, shell=True)
    if ret != 0:
        sys.exit(1)

    remove_dir_except(work_path, '.git')
    excopy.copy_files_in_dir(args.target_project, work_path)

    cmd = "git add -A \n git commit -m \'Upgrade\'\ngit tag cocos_upgrade"
    ret = subprocess.call(cmd, cwd=work_path, shell=True)
    if ret != 0:
        sys.exit(1)

    cmd = str.format('git format-patch -1 cocos_upgrade -o %s' % args.output_dir)
    ret = subprocess.call(cmd, cwd=work_path, shell=True)
    if ret != 0:
        sys.exit(1)

    shutil.rmtree(work_path);


