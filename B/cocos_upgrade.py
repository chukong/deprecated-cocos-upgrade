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
import excopy
import cocos
import modify_file
import download_files
import subprocess
from argparse import ArgumentParser

UPGRADE_PATH = 'Upgrade'
PATCH_FILE_NAME = '0001-Upgrade.patch'
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
    parser = ArgumentParser(description='Generate prebuilt engine for Cocos Engine.')
    parser.add_argument('-s', dest='originCocos', help='Origin cocos engine path.')
    parser.add_argument('-d', dest='targetCocos', help='Target cocos engine path.')
    parser.add_argument('-p', dest='projPath', help='Your Project path.')
    parser.add_argument('-n', dest='projName', help='Your Project Name.')

    (args, unknown) = parser.parse_known_args()
    if len(unknown) > 0:
        print('unknown arguments: %s' % unknown)
        sys.exit(1)

    print('Receive arguments src:%s dst:%s project:%s' % (args.originCocos, args.targetCocos, args.projPath))
    if not os.path.exists(args.projPath) \
            or not os.path.exists(args.originCocos) \
            or not os.path.exists(args.targetCocos):
        cocos.Logging.warning("> Cocos engine or project path is not exists.")
        sys.exit(1)

    project_type = cocos.check_project_type(args.projPath)
    if project_type is None:
        cocos.Logging.error("> This is not a cocos2d project.")
        sys.exit(1)
    project_version = get_project_version(args.projPath, project_type)
    project_version = project_version.split(' ')[1]

    # Create project.
    target_path = args.projPath + UPGRADE_PATH
    target_project_path = os.path.join(target_path, 'Target')
    if not os.path.exists(target_project_path):
        cocos.Logging.info("> Copy your project into %s ..." % target_path)
        excopy.copy_directory(args.projPath, target_project_path)

    origin_project_path = os.path.join(target_path, 'Origin')
    if not os.path.exists(origin_project_path):
        cocos.Logging.info("> Create origin project ...")
        cocos_console_path = str.format('%s/tools/cocos2d-console/bin/cocos' % args.originCocos)
        cmd = str.format('%s new -l %s %s -p %s -d %s' %
                         (cocos_console_path, project_type, args.projName, 'org.cocos2dx.replace', origin_project_path))
        ret = subprocess.call(cmd, shell=True)
        if ret != 0:
            sys.exit(1)

    temp_project_path = os.path.join(target_path, 'Temp')
    if not os.path.exists(temp_project_path):
        cocos.Logging.info("> Create temp project ...")
        cocos_console_path = str.format('%s/tools/cocos2d-console/bin/cocos' % args.targetCocos)
        cmd = str.format('%s new -l %s %s -p %s -d %s' %
                         (cocos_console_path, project_type, args.projName, 'org.cocos2dx.replace', temp_project_path))
        ret = subprocess.call(cmd, shell=True)
        if ret != 0:
            sys.exit(1)

    cocos.Logging.info("> Upgrade engine ...")
    if project_type == 'cpp':
        temp_path = os.path.join(target_project_path, 'cocos2d')
        excopy.remove_directory(temp_path)
        excopy.copy_directory(os.path.join(temp_project_path, args.projName, 'cocos2d'), temp_path)
    elif project_type == 'lua':
        temp_path1 = os.path.join(target_project_path, 'frameworks', 'cocos2d-x')
        excopy.remove_directory(temp_path1)
        temp_path2 = os.path.join(target_project_path, 'runtime')
        excopy.remove_directory(temp_path2)
        excopy.copy_directory(os.path.join(temp_project_path, args.projName, 'frameworks', 'cocos2d-x'), temp_path1)
        excopy.copy_directory(os.path.join(temp_project_path, args.projName, 'runtime'), temp_path2)
    elif project_type == 'js':
        temp_path1 = os.path.join(target_project_path, 'frameworks', 'cocos2d-html5')
        excopy.remove_directory(temp_path1)
        temp_path2 = os.path.join(target_project_path, 'frameworks', 'js-bindings')
        excopy.remove_directory(temp_path1)
        temp_path3 = os.path.join(target_project_path, 'runtime')
        excopy.remove_directory(temp_path2)
        temp_path4 = os.path.join(target_project_path, 'tools')
        excopy.remove_directory(temp_path3)
        excopy.copy_directory(os.path.join(temp_project_path, args.projName, 'frameworks', 'cocos2d-html5'), temp_path1)
        excopy.copy_directory(os.path.join(temp_project_path, args.projName, 'frameworks' 'js-bindings'), temp_path2)
        excopy.copy_directory(os.path.join(temp_project_path, args.projName, 'runtime'), temp_path3)
        excopy.copy_directory(os.path.join(temp_project_path, args.projName, 'tools'), temp_path4)

    if project_type == 'js' or project_type == 'lua':
        real_project_path = os.path.join(target_project_path, 'frameworks', 'runtime-src')
    elif project_type == 'cpp':
        real_project_path = target_project_path

    upgradeVersion = get_project_version(target_project_path, project_type)
    upgradeVersion = upgradeVersion.split(' ')[1]

    # Download zip file or file.
    patch_file_url = str.format('%s/ftp/B/%s/%s_%s/%s' %
                                (FILES_SERVER_URL, project_type, project_version, upgradeVersion, PATCH_FILE_NAME))
    patch_path = str.format('%s/%s/%s_%s' % (os.path.realpath(os.path.dirname(__file__)), project_type, project_version, upgradeVersion))
    if not os.path.exists(patch_path):
        os.makedirs(patch_path)

    patch_file_path = str.format('%s/%s' % (patch_path, PATCH_FILE_NAME))
    if not os.path.exists(patch_file_path):
        installer = download_files.CocosZipInstaller(patch_file_url, patch_file_path)
        installer.download_file()

   # Apply patch
    cmd = str.format('python cocos_upgrade2.py -d %s -n %s -p %s ' %
                     (target_project_path, args.projName, patch_file_path))
    ret = subprocess.call(cmd, cwd=os.path.realpath(os.path.dirname(__file__)), shell=True)
    if ret != 0:
        sys.exit(1)

    # cocos.Logging.info("> Upgrade project ...")
    # proj_file_path = os.path.join(real_project_path, 'proj.win32/%s.vcxproj' % args.projName)
    # cocos.Logging.info("> Modifing visual studio project for win32 ... ")
    # modify_template.modify_win32(proj_file_path)
    #
    # proj_file_path = os.path.join(real_project_path, 'proj.ios_mac/%s.xcodeproj/project.pbxproj' % args.projName)
    # cocos.Logging.info("> Modifing xcode project for iOS&Mac ... ")
    # modify_template.modify_mac_ios(proj_file_path)
    #
    # mk_file_path = os.path.join(real_project_path, 'proj.android/jni/Android.mk')
    # cocos.Logging.info("> Modifing mk file for Android ...")
    # modify_template.modify_android(mk_file_path)
    #
    # modify_file_path = os.path.join(real_project_path, 'proj.android/project.properties')
    # fileModifier = modify_file.FileModifier(modify_file_path)
    # fileModifier.replaceString('../cocos2d/cocos/platform/android/java', '../cocos2d/cocos/2d/platform/android/java')
    # fileModifier.save()
    #
    # modify_file_path = os.path.join(real_project_path, 'proj.ios_mac/ios/AppController.mm')
    # fileModifier = modify_file.FileModifier(modify_file_path)
    # fileModifier.replaceString('platform/ios/CCEAGLView-ios.h', 'CCEAGLView.h')
    # fileModifier.replaceString('GLViewImpl::create', 'GLView::create')
    # fileModifier.save()
    #
    # modify_file_path = os.path.join(real_project_path, 'proj.ios_mac/ios/RootViewController.mm')
    # fileModifier = modify_file.FileModifier(modify_file_path)
    # fileModifier.replaceString('platform/ios/CCEAGLView-ios.h', 'CCEAGLView.h')
    # fileModifier.save()
    #
    # modify_file_path = os.path.join(real_project_path, 'Classes/AppDelegate.cpp')
    # fileModifier = modify_file.FileModifier(modify_file_path)
    # fileModifier.replaceString('GLViewImpl::create', 'GLView::create')
    # fileModifier.save()
    #
    # manifest_file_path = os.path.join(real_project_path, 'proj.android/AndroidManifest.xml')
    # modify_template.modify_manifest(manifest_file_path)

    cmd = str.format('python cocos_compare.py -s %s -d %s -o %s ' %
                     (args.projPath, target_project_path, os.path.join(origin_project_path, args.projName)))
    subprocess.call(cmd, cwd=os.path.realpath(os.path.dirname(__file__)), shell=True)
