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

PROJECT_NAME = 'testProject'
PACAKGE_NAME = 'org.cocos2dx.hellocpp'

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
    parser.add_argument('-s', dest='source_cocos', help='Source Cocos engine path')
    parser.add_argument('-d', dest='target_cocos', help='Target Cocos engine path')
    parser.add_argument('-o', dest='output_dir', help='The default is patch')
    parser.add_argument('-l', dest='project_type', help='cpp, lua or js')

    (args, unknown) = parser.parse_known_args()
    if len(unknown) > 0:
        print('unknown arguments: %s' % unknown)
        sys.exit(1)

    if not os.path.exists(args.source_cocos) or not os.path.exists(args.target_cocos):
        cocos.Logging.warning("> Path is not exists.")
        sys.exit(1)

    if args.output_dir is None:
        args.output_dir = os.path.join(os.getcwd(), 'diff')
    if os.path.exists(args.output_dir):
        shutil.rmtree(args.output_dir)
    os.mkdir(args.output_dir)
    # Create directory and file for upgrade.
    print('Receive arguments src:%s dst:%s output:%s' % (args.source_cocos, args.target_cocos, args.output_dir))

    source_path = os.path.join(os.getcwd(), 'source_cocos')
    if os.path.exists(source_path):
        shutil.rmtree(source_path)
    os.mkdir(source_path)

    target_path = os.path.join(os.getcwd(), 'target_cocos')
    if os.path.exists(target_path):
        shutil.rmtree(target_path)
    os.mkdir(target_path)

    # Create project.
    cocos.Logging.info("> Preparing patch file ...")
    cocos_console_path = str.format('%s/tools/cocos2d-console/bin/cocos' % args.source_cocos)
    cmd = str.format('%s new -l %s %s -p %s -d %s' %
                     (cocos_console_path, args.project_type, PROJECT_NAME, PACAKGE_NAME, source_path))
    ret = subprocess.call(cmd, shell=True)
    if ret != 0:
        sys.exit(1)

    cocos_console_path = str.format('%s/tools/cocos2d-console/bin/cocos' % args.target_cocos)
    cmd = str.format('%s new -l %s %s -p %s -d %s' %
                     (cocos_console_path, args.project_type, PROJECT_NAME, PACAKGE_NAME, target_path))
    ret = subprocess.call(cmd, shell=True)
    if ret != 0:
        sys.exit(1)

    # Create patch.
    work_path = os.path.join(source_path, PROJECT_NAME)
    cmd = "git init \n git add -A \n git commit -m \'Init project for cocos upgrade.\'"
    ret = subprocess.call(cmd, cwd=work_path, shell=True)
    if ret != 0:
        sys.exit(1)

    remove_dir_except(work_path, '.git')
    excopy.copy_files_in_dir(os.path.join(target_path, PROJECT_NAME), work_path)

    cmd = "git add -A \n git commit -m \'Upgrade\'\ngit tag cocos_upgrade"
    ret = subprocess.call(cmd, cwd=work_path, shell=True)
    if ret != 0:
        sys.exit(1)

    cmd = str.format('git format-patch -1 cocos_upgrade -o %s' % args.output_dir)
    ret = subprocess.call(cmd, cwd=work_path, shell=True)
    if ret != 0:
        sys.exit(1)

    shutil.rmtree(source_path)
    shutil.rmtree(target_path)


