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
import modify_template
import subprocess
from argparse import ArgumentParser

UPGRADE_PATH = 'Upgrade'

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

    cocos.Logging.info("> Copying cocos2d from engine directory ...")
    if project_type == 'cpp':
        temp_path = os.path.join(target_project_path, 'cocos2d')
        excopy.remove_directory(temp_path)
        excopy.copy_directory(os.path.join(temp_project_path, args.projName, 'cocos2d'), temp_path)
    elif project_type == 'lua':
        temp_path1 = os.path.join(target_project_path, 'frameworks')
        excopy.remove_directory(temp_path1)
        temp_path2 = os.path.join(target_project_path, 'runtime')
        excopy.remove_directory(temp_path2)
        excopy.copy_directory(os.path.join(temp_project_path, args.projName, 'frameworks'), temp_path1)
        excopy.copy_directory(os.path.join(temp_project_path, args.projName, 'runtime'), temp_path2)
    elif project_type == 'js':
        temp_path1 = os.path.join(target_project_path, 'frameworks')
        excopy.remove_directory(temp_path1)
        temp_path2 = os.path.join(target_project_path, 'runtime')
        excopy.remove_directory(temp_path2)
        temp_path3 = os.path.join(target_project_path, 'tools')
        excopy.remove_directory(temp_path3)
        excopy.copy_directory(os.path.join(temp_project_path, args.projName, 'frameworks'), temp_path1)
        excopy.copy_directory(os.path.join(temp_project_path, args.projName, 'runtime'), temp_path2)
        excopy.copy_directory(os.path.join(temp_project_path, args.projName, 'tools'), temp_path3)

    if project_type == 'js' or project_type == 'lua':
        real_project_path = os.path.join(target_project_path, 'frameworks', 'runtime-src')
    elif project_type == 'cpp':
        real_project_path = target_project_path

    # proj_file_path = os.path.join(real_project_path, 'proj.win32/%s.vcxproj' % args.projName)
    # cocos.Logging.info("> Modifing visual studio project for win32 ... ")
    # modify_template.modify_win32(proj_file_path)

    proj_file_path = os.path.join(real_project_path, 'proj.ios_mac/%s.xcodeproj/project.pbxproj' % args.projName)
    cocos.Logging.info("> Modifing xcode project for iOS&Mac ... ")
    modify_template.modify_mac_ios(proj_file_path)

    mk_file_path = os.path.join(real_project_path, 'proj.android/jni/Android.mk')
    cocos.Logging.info("> Modifing mk file for Android ...")
    modify_template.modify_android(mk_file_path)

    modify_file_path = os.path.join(real_project_path, 'proj.android/project.properties')
    fileModifier = modify_file.FileModifier(modify_file_path)
    fileModifier.replaceString('../cocos2d/cocos/platform/android/java', '../cocos2d/cocos/2d/platform/android/java')
    fileModifier.save()

    modify_file_path = os.path.join(real_project_path, 'proj.ios_mac/ios/AppController.mm')
    fileModifier = modify_file.FileModifier(modify_file_path)
    fileModifier.replaceString('platform/ios/CCEAGLView-ios.h', 'CCEAGLView.h')
    fileModifier.replaceString('GLViewImpl::create', 'GLView::create')
    fileModifier.save()

    modify_file_path = os.path.join(real_project_path, 'proj.ios_mac/ios/RootViewController.mm')
    fileModifier = modify_file.FileModifier(modify_file_path)
    fileModifier.replaceString('platform/ios/CCEAGLView-ios.h', 'CCEAGLView.h')
    fileModifier.save()

    modify_file_path = os.path.join(real_project_path, 'Classes/AppDelegate.cpp')
    fileModifier = modify_file.FileModifier(modify_file_path)
    fileModifier.replaceString('GLViewImpl::create', 'GLView::create')
    fileModifier.save()

    manifest_file_path = os.path.join(real_project_path, 'proj.android/AndroidManifest.xml')
    modify_template.modify_manifest(manifest_file_path)

    cmd = str.format('python cocos_compare.py -s %s -d %s -o %s ' %
                     (args.projPath, target_project_path, os.path.join(origin_project_path, args.projName)))
    subprocess.call(cmd, cwd=os.getcwd(), shell=True)
