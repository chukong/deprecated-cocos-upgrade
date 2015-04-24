#!/usr/bin/python
# ----------------------------------------------------------------------------
# extend methods for copy files/dirs
#
# Copyright 2015 (C) zhangbin lijun
#
# License: MIT
# ----------------------------------------------------------------------------

import os
import shutil
import sys
import json
import cocos

def copy_files_in_dir(src, dst):

    for item in os.listdir(src):
        path = os.path.join(src, item)
        if os.path.isfile(path):
            shutil.copy(path, dst)
        if os.path.isdir(path):
            new_dst = os.path.join(dst, item)
            if not os.path.isdir(new_dst):
                os.makedirs(new_dst)
            copy_files_in_dir(path, new_dst)

def remove_directory(dir_path):
    if os.path.isdir(dir_path):
        shutil.rmtree(dir_path)

def copy_directory(src, dst):
    if os.path.isdir(src):
        shutil.copytree(src, dst, False)
    else:
        cocos.Logging.warning("> Directory is not exist %s" % src)

def os_is_win32():
    return sys.platform == 'win32'

def add_path_prefix(path_str):
    if not os_is_win32():
        return path_str

    if path_str.startswith("\\\\?\\"):
        return path_str

    ret = "\\\\?\\" + os.path.abspath(path_str)
    ret = ret.replace("/", "\\")
    return ret

def append_x_engine(src, dst):
    # check cocos engine exist
    cocosx_files_json = os.path.join(
        src, 'templates', 'cocos2dx_files.json')
    if not os.path.exists(cocosx_files_json):
        message = "Fatal: %s doesn\'t exist." % cocosx_files_json
        cocos.Logging.error(message)
        sys.exit(1)

    f = open(cocosx_files_json)
    data = json.load(f)
    f.close()

    fileList = data['common']

    # begin copy engine
    # cocos.Logging.info("> Copying cocos2d-x files...")

    for index in range(len(fileList)):
        srcfile = os.path.join(src, fileList[index])
        dstfile = os.path.join(dst, fileList[index])

        srcfile = add_path_prefix(srcfile)
        dstfile = add_path_prefix(dstfile)

        if not os.path.exists(os.path.dirname(dstfile)):
            os.makedirs(add_path_prefix(os.path.dirname(dstfile)))

        # copy file or folder
        if os.path.exists(srcfile):
            if os.path.isdir(srcfile):
                if os.path.exists(dstfile):
                    shutil.rmtree(dstfile)
                shutil.copytree(srcfile, dstfile)
            else:
                if os.path.exists(dstfile):
                    os.remove(dstfile)
                shutil.copy2(srcfile, dstfile)


def backup_directory(path):
    bak = path + "_bak"
    if not os.path.exists(bak):
        copy_directory(path, bak)
    else:
        cocos.Logging.warning("> There is an exist backup directory, please rename it. %s" % bak)
