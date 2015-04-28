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
import subprocess
import modify_file
import download_files
from argparse import ArgumentParser

UPGRADE_PATH = 'Upgrade'
PATCH_FILE_NAME = '0001-Upgrade.patch'
PATCH_ZIP_FILE_NAME = '0001-Upgrade.patch.zip'
FILES_SERVER_URL = 'http://cocos.qudao.info'
version_files = ['cocos2d/cocos/cocos2d.cpp',
                 'cocos2d/cocos/2d/cocos2d.cpp',
                 'frameworks/cocos2d-x/cocos/cocos2d.cpp',
                 'frameworks/cocos2d-x/cocos/2d/cocos2d.cpp',
                 'frameworks/js-bindings/bindings/manual/ScriptingCore.h']

def get_project_version(path, project_type):
    file_path = None
    for file in version_files:
        file_path = os.path.join(path, file)
        if os.path.exists(file_path):
            break

    if file_path is None:
        sys.exit(1)

    file_modifier = modify_file.FileModifier(file_path)
    if project_type == 'js':
        return file_modifier.findEngineVesion(r".*#define[ \t]+ENGINE_VERSION[ \t]+\"(.*)\"")
    elif project_type == 'lua' or project_type == 'cpp':
        return file_modifier.findEngineVesion(r".*return[ \t]+\"(.*)\";")

    return None

if __name__ == '__main__':
    parser = ArgumentParser(description='Upgrade Cocos Engine for your project.')
    parser.add_argument('-d', dest='projPath', help='Your Project path.')
    parser.add_argument('-n', dest='projName', help='Your Project name.')
    parser.add_argument('-v', dest='upgradeVersion', help='Engine version to be upgrade.')
    (args, unknown) = parser.parse_known_args()

    if len(unknown) > 0:
        print('unknown arguments: %s' % unknown)
        sys.exit(1)

    if not os.path.exists(args.projPath):
        cocos.Logging.warning("> Project is not exists.")
        sys.exit(1)

    print('Receive arguments target:%s name:%s version:%s' % (args.projPath, args.projName, args.upgradeVersion))

    project_type = cocos.check_project_type(args.projPath)
    if project_type is None:
        cocos.Logging.error("> This is not a cocos2d project.")
        sys.exit(1)
    project_version = get_project_version(args.projPath, project_type)
    project_version = project_version.split(' ')[1]

    # Download zip file or file.
    patch_file_url = str.format('%s/ftp/A/%s/%s_%s/%s' % (FILES_SERVER_URL, project_type, project_version, args.upgradeVersion, PATCH_ZIP_FILE_NAME))
    patch_path = str.format('%s/%s/%s_%s' % (os.path.realpath(os.path.dirname(__file__)), project_type, project_version, args.upgradeVersion))
    if not os.path.exists(patch_path):
        os.makedirs(patch_path)

    patch_file_path = str.format('%s/%s' % (patch_path, PATCH_FILE_NAME))
    patch_zipfile_path = str.format('%s/%s' % (patch_path, PATCH_ZIP_FILE_NAME))
    if not os.path.exists(patch_file_path) and not os.path.exists(patch_zipfile_path):
        installer = download_files.CocosZipInstaller(patch_file_url, patch_zipfile_path)
        installer.download_zip_file()
        installer.unpack_zipfile(patch_path)
        os.remove(patch_zipfile_path)
    elif not os.path.exists(patch_file_path):
        installer = download_files.CocosZipInstaller(patch_file_url, patch_zipfile_path)
        installer.unpack_zipfile(patch_path)
        os.remove(patch_zipfile_path)

    cmd = str.format('python cocos_upgrade2.py -d %s -n %s -p %s ' %
                     (args.projPath, args.projName, patch_file_path))
    ret = subprocess.call(cmd, cwd=os.path.realpath(os.path.dirname(__file__)), shell=True)
    if ret != 0:
        sys.exit(1)