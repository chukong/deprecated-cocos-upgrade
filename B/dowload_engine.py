#!/usr/bin/python
# ----------------------------------------------------------------------------
# extend methods for copy files/dirs
#
# Copyright 2015 (C) zhangbin lijun
#
# License: MIT
# ----------------------------------------------------------------------------

import os
import modify_file
import subprocess
from zipfile import *

downloadMap = {
                    '3.5': 'http://www.cocos2d-x.org/filedown/cocos2d-x-3.5.zip',
                    '3.4': 'http://www.cocos2d-x.org/filedown/cocos2d-x-3.4.zip',
                    '3.3': 'http://www.cocos2d-x.org/filedown/cocos2d-x-3.3.zip',
                    '3.2': 'http://www.cocos2d-x.org/filedown/cocos2d-x-3.2.zip',
                    '3.1.1': 'http://cdn.cocos2d-x.org/cocos2d-x-3.1.1.zip',
                    '3.1': 'http://www.cocos2d-x.org/filedown/cocos2d-x-3.1-amazon',
                    '3.0': 'http://cdn.cocos2d-x.org/cocos2d-x-3.0.zip'
                }

def download_engine(projPath):
    file_path = os.path.join(projPath, 'cocos2d/cocos/2d/cocos2d.cpp')
    if not os.path.exists(file_path):
        file_path = os.path.join(projPath, 'cocos2d/cocos/cocos2d.cpp')
        if not os.path.exists(file_path):
            return ''

    fileModifier = modify_file.FileModifier(file_path)
    version = fileModifier.findEngineVesion()
    url = getDowloadUrl(version)
    if url is None:
        return ''

    subprocess.call('brew install wget', shell=True)
    subprocess.call('wget ' + url, shell=True)

    return ''

def unzip(src, dst):
    myzip = ZipFile(src)
    myfilelist = myzip.namelist()
    for name in myfilelist:
        f_handle = open(dst+name, "wb")
        f_handle.write(myzip.read(name))
        f_handle.close()
    myzip.close()

def getDowloadUrl(version):
    for key in downloadMap:
        result = version.find(key)
        if result > -1:
            return downloadMap[key]

    return None


