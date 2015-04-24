#!/usr/bin/python
# ----------------------------------------------------------------------------
# modify the runtime template for prebuilt engine
#
# Copyright 2015 (C) zhangbin lijun
#
# License: MIT
# ----------------------------------------------------------------------------

import os
import sys
import modify_pbxproj
import modify_vcxproj
import modify_mk
import cocos


def modify_mac_ios(proj_file_path):
    if not os.path.exists(proj_file_path):
        cocos.Logging.warning("> File is not exist: %s" % proj_file_path)
        sys.exit(1)

    # Remove library dependency in xcode project file.
    #proj_file_path = "/Users/calf/Documents/CocosUpgrade/HelloWorld/proj.ios_mac/HelloWorld.xcodeproj/project.pbxproj"
    pbx_proj = modify_pbxproj.XcodeProject.Load(proj_file_path)
    pbx_proj.remove_file_by_path2("libbox2d Mac.a")
    pbx_proj.remove_file_by_path2("libchipmunk Mac.a")
    pbx_proj.remove_file_by_path2("libcocos2dx-extensions Mac.a")
    pbx_proj.remove_file_by_path2("libCocosDenshion Mac.a")

    pbx_proj.remove_file_by_path2("libbox2d iOS.a")
    pbx_proj.remove_file_by_path2("libchipmunk iOS.a")
    pbx_proj.remove_file_by_path2("libcocos2dx-extensions iOS.a")
    pbx_proj.remove_file_by_path2("libCocosDenshion iOS.a")
    if pbx_proj.modified:
        pbx_proj.save()


def modify_android(mk_file_path):
    # Modify mk file for android project.
    android_proj = modify_mk.AndroidMK(mk_file_path)
    android_proj.remove_lib("cocosdenshion_static", "audio/android");
    android_proj.remove_lib("", "2d");
    android_proj.remove_lib("box2d_static", "Box2D");
    android_proj.remove_lib("cocosbuilder_static", "editor-support/cocosbuilder");
    android_proj.remove_lib("spine_static", "editor-support/spine");
    android_proj.remove_lib("cocostudio_static", "editor-support/cocostudio");
    android_proj.remove_lib("cocos_network_static", "network");
    android_proj.remove_lib("cocos_extension_static", "extensions");

    android_proj.add_lib("", ".");
    android_proj.save()


def modify_manifest(manifest_file_path):
    manifest_file = modify_vcxproj.VCXProject(manifest_file_path)
    manifest_file.repositionSo("android.app.lib_name")
    manifest_file.save()


def modify_win32(proj_file_path):
    if not os.path.exists(proj_file_path):
        cocos.Logging.warning("> File is not exist: %s" % proj_file_path)
        sys.exit(1)

    # Remove library dependency in visual studio project file.
    vcx_proj = modify_vcxproj.VCXProject(proj_file_path)
    vcx_proj.add_include_dirs('$(_COCOS_HEADER_WIN32_BEGIN)')
    vcx_proj.add_include_dirs('$(_COCOS_HEADER_WIN32_END)')
    vcx_proj.add_lib('$(_COCOS_LIB_WIN32_BEGIN)')
    vcx_proj.add_lib('$(_COCOS_LIB_WIN32_END)')
    # vcx_proj.add_addition_lib('$(_COCOS_LIB_PATH_WIN32_BEGIN)')
    # vcx_proj.add_addition_lib('$(_COCOS_LIB_PATH_WIN32_END)')
    # PreLinkEvent xcopy "$(ProjectDir)..\Resources" "$(OutDir)"
    vcx_proj.remove_proj_reference('..\cocos2d\cocos\2d\cocos2d.vcxproj')
    vcx_proj.remove_proj_reference('..\cocos2d\cocos\audio\proj.win32\CocosDenshion.vcxproj')
    vcx_proj.remove_proj_reference('..\cocos2d\external\chipmunk\proj.win32\chipmunk.vcxproj')

    # vcx_proj.add_proj_reference('..\cocos2d\cocos\2d\libcocos2d.vcxproj')
    # vcx_proj.add_proj_reference('..\cocos2d\cocos\editor-support\spine\proj.win32\libSpine.vcxproj')
    # vcx_proj.add_proj_reference('..\cocos2d\external\Box2D\proj.win32\libbox2d.vcxproj')


    vcx_proj.save()