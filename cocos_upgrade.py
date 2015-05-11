#!/usr/bin/python
# ----------------------------------------------------------------------------
# Upgrade the cocos2d engine to the specified version.
#
# Copyright 2015 (C) Zhang Bin
#
# License: MIT
# ----------------------------------------------------------------------------

import os
import subprocess
import excopy
import shutil
import sys
import json
import re

from xml.dom import minidom
from argparse import ArgumentParser

def run_shell(cmd, cwd=None):
    print('running : %s' % cmd)
    p = subprocess.Popen(cmd, shell=True, cwd=cwd)
    p.wait()

    if p.returncode:
        raise subprocess.CalledProcessError(returncode=p.returncode, cmd=cmd)

    return p.returncode

def remove_dir_except(root_dir, excpets):
    filelist = os.listdir(root_dir)
    for f in filelist:
        if f in excpets:
            continue

        filepath = os.path.join(root_dir, f)
        if os.path.isfile(filepath):
            os.remove(filepath)
        elif os.path.isdir(filepath):
            shutil.rmtree(filepath, True)

def get_deleted_files(game_proj_path, base_proj_path):
    ret = []
    for root, dirs, files in os.walk(base_proj_path):
        for f in files:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, base_proj_path)

            check_path = os.path.join(game_proj_path, rel_path)
            if not os.path.exists(check_path):
                ret.append(rel_path)

    return ret

def remove_deleted_files(proj_path, delete_files):
    for f in delete_files:
        full_path = os.path.join(proj_path, f)
        if os.path.isfile(full_path):
            os.remove(full_path)
        elif os.path.isdir(full_path):
            shutil.rmtree(full_path, ignore_errors=True)

def os_is_win32():
    return sys.platform == 'win32'

def os_is_mac():
    return sys.platform == 'darwin'

def config_merge_tool(repo_path):
    # TODO make users config different merge tools
    cmd = 'git config --local merge.tool diffmerge'
    run_shell(cmd, cwd=repo_path)
    if os_is_win32():
        diffmerge_cmd_path = r'sgdm.exe'
        merge_cmd = r'\"%s\" --merge --result=\"$MERGED\" \"$LOCAL\" -t1=BeforeUpgrade -t2=Merged -t3=EngineUpgrade \"$(if test -f \"$BASE\"; then echo \"$BASE\"; else echo \"$LOCAL\"; fi)\" \"$REMOTE\"' % diffmerge_cmd_path
        cmd = 'git config mergetool.diffmerge.cmd "%s"' % merge_cmd
        run_shell(cmd, cwd=repo_path)
    else:
        diffmerge_cmd_path = 'diffmerge.sh'
        cmd = 'git config mergetool.diffmerge.cmd \'%s --merge --result="$MERGED" -t1=BeforeUpgrade -t2=Merged -t3=EngineUpgrade "$LOCAL" "$(if test -f "$BASE"; then echo "$BASE"; else echo "$LOCAL"; fi)" "$REMOTE"\'' % diffmerge_cmd_path
        run_shell(cmd, cwd=repo_path)

    cmd = 'git config --local mergetool.diffmerge.trustExitCode true'
    run_shell(cmd, cwd=repo_path)

def config_author(repo_path):
    run_shell('git config --local user.name upgrade_engine', cwd=repo_path)
    run_shell('git config --local user.email upgrade_engine@cocos2d-x.org', cwd=repo_path)

def get_xml_attr(file_path, node_name, attr):
    try:
        doc = minidom.parse(file_path)
        ret = doc.getElementsByTagName(node_name)[0].getAttribute(attr)
    except:
        print('Get property "%s" of node "%s" from "%s" failed.' % (attr, node_name, file_path))
        ret = None
        pass
    return ret

def get_engine_version(file_path, language):
    if not os.path.isfile(file_path):
        return None

    if language == "js":
        pattern = r".*#define[ \t]+ENGINE_VERSION[ \t]+\"(.*)\""
    else:
        pattern = r".*return[ \t]+\"(.*)\";"

    ver = None
    f = open(file_path)
    for line in f.readlines():
        match = re.match(pattern, line)
        if match:
            ver = match.group(1)
            break
    f.close()

    return ver

def get_bundle_id(plist_path):
    ret = None
    if os.path.isfile(plist_path):
        f = open(plist_path)
        file_content = f.read()
        f.close()

        pattern = '<key>CFBundleIdentifier</key>.*<string>(.*)</string>'
        match = re.match(pattern, file_content)
        if match:
            ret = match.group(1)

    return ret

class ProjectInfo(object):
    PROJ_CFG_FILE = '.cocos-project.json'
    IDE_PROJ_FILE = '.project'

    # cpp project related paths
    CPP_SLN_PATH  = 'proj.win32'
    CPP_MANIFEST_PATH  = 'proj.android/AndroidManifest.xml'
    CPP_IOS_INFO_PLIST = 'proj.ios_mac/ios/Info.plist'
    CPP_MAC_INFO_PLIST = 'proj.ios_mac/mac/Info.plist'

    # script project related paths
    SCRIPT_SLN_PATH = 'frameworks/runtime-src/proj.win32'
    SCRIPT_MANIFEST_PATH  = 'frameworks/runtime-src/proj.android/AndroidManifest.xml'
    SCRIPT_IOS_INFO_PLIST = 'frameworks/runtime-src/proj.ios_mac/ios/Info.plist'
    SCRIPT_MAC_INFO_PLIST = 'frameworks/runtime-src/proj.ios_mac/mac/Info.plist'

    # engine version file path
    ENGINE_VERSION_FILES = {
        'cpp' : [
            'cocos2d/cocos/2d/cocos2d.cpp',
            'cocos2d/cocos/cocos2d.cpp'
        ],
        'lua' : [
            'frameworks/cocos2d-x/cocos/2d/cocos2d.cpp',
            'frameworks/cocos2d-x/cocos/cocos2d.cpp'
        ],
        'js' : [
            'frameworks/js-bindings/bindings/manual/ScriptingCore.h',
            'frameworks/cocos2d-x/cocos/scripting/js-bindings/manual/ScriptingCore.h'
        ]
    }

    def __init__(self, proj_path):
        self.proj_path = proj_path

        # init variables
        self.proj_lang = None
        self.is_runtime = False
        self.pkg_name = None
        self.proj_name = None
        self.ios_bundleid = None
        self.mac_bundleid = None
        self.engine_version = None

        # check the project file
        proj_cfg_file = os.path.join(self.proj_path, ProjectInfo.PROJ_CFG_FILE)
        if not os.path.exists(proj_cfg_file):
            return

        # read the project file
        f = open(proj_cfg_file)
        proj_info = json.load(f)
        f.close()

        # get language
        self.proj_lang = proj_info.get('project_type', None)

        # check whether is runtime project
        if self.proj_lang != 'cpp':
            ide_proj_file = os.path.join(self.proj_path, ProjectInfo.IDE_PROJ_FILE)
            if os.path.exists(ide_proj_file):
                self.is_runtime = True
            else:
                self.is_runtime = False

            # project related paths
            sln_path = os.path.join(self.proj_path, ProjectInfo.SCRIPT_SLN_PATH)
            manifest_path = os.path.join(self.proj_path, ProjectInfo.SCRIPT_MANIFEST_PATH)
            ios_info_path = os.path.join(self.proj_path, ProjectInfo.SCRIPT_IOS_INFO_PLIST)
            mac_info_path = os.path.join(self.proj_path, ProjectInfo.SCRIPT_MAC_INFO_PLIST)
        else:
            self.is_runtime = False

            # project related paths
            sln_path = os.path.join(self.proj_path, ProjectInfo.CPP_SLN_PATH)
            manifest_path = os.path.join(self.proj_path, ProjectInfo.CPP_MANIFEST_PATH)
            ios_info_path = os.path.join(self.proj_path, ProjectInfo.CPP_IOS_INFO_PLIST)
            mac_info_path = os.path.join(self.proj_path, ProjectInfo.CPP_MAC_INFO_PLIST)

        # get project name
        if os.path.isdir(sln_path):
            for f in os.listdir(sln_path):
                base_name, ext = os.path.splitext(f)
                if ext == '.sln':
                    self.proj_name = base_name
                    break

        # get android package name
        if os.path.isfile(manifest_path):
            self.pkg_name = get_xml_attr(manifest_path, 'manifest', 'package')

        # get ios bundle id
        # TODO get ios bundle id from info.plist
        self.ios_bundleid = self.pkg_name

        # get mac bundle id
        # TODO get mac bundle id from info.plist
        self.mac_bundleid = self.pkg_name

        # get the engine version of project
        if self.get_language() is not None:
            version_files = ProjectInfo.ENGINE_VERSION_FILES[self.get_language()]
            for f in version_files:
                full_path = os.path.join(self.proj_path, f)
                if os.path.isfile(full_path):
                    version = get_engine_version(full_path, self.get_language())
                    if version is not None:
                        self.engine_version = version
                        break

    def do_check(self):
        ret = True
        if self.get_proj_name() is None:
            print("Get the project name failed.")
            ret = False
        elif self.get_language() is None:
            print("Get the language of project failed.")
            ret = False

        return ret

    def get_language(self):
        return self.proj_lang

    def is_runtime_proj(self):
        return self.is_runtime

    def get_pkg_name(self):
        return self.pkg_name

    def get_proj_name(self):
        return self.proj_name

    def get_ios_bundleid(self):
        return self.ios_bundleid

    def get_mac_bundleid(self):
        return self.mac_bundleid

    def get_engine_version(self):
        return self.engine_version

    def print_info(self):
        print("project name : %s" % self.get_proj_name())
        print("language : %s" % self.get_language())
        print("package name : %s" % self.get_pkg_name())
        print("is runtime : %s" % self.is_runtime_proj())
        print("ios bundle id : %s" % self.get_ios_bundleid())
        print("mac bundle id : %s" % self.get_mac_bundleid())
        print("engine version : %s" % self.get_engine_version())

def check_path(path):
    ret = True
    if not os.path.isdir(path):
        print("'%s' is not a valid path." % path)
        ret = False

    return ret

def new_proj_with_info(proj_info, cocos_cmd, dst_path):
    if proj_info.get_pkg_name() is not None:
        pkg_arg = '-p %s' % proj_info.get_pkg_name()
    else:
        pkg_arg = ''

    if proj_info.is_runtime_proj():
        template_arg = '-p runtime'
    else:
        template_arg = ''

    cmd = '"%s" new -l %s %s -d %s %s %s' %\
          (cocos_cmd,
           proj_info.get_language(),
           pkg_arg,
           dst_path,
           template_arg,
           proj_info.get_proj_name())
    run_shell(cmd)

def commit_files_with_msg(repo_path, msg):
    run_shell('git add -A', cwd=repo_path)
    run_shell('git commit  -m "%s"' % msg, cwd=repo_path)

UPGRADE_BRANCH_NAME = 'upgrade-engine'
CONSOLE_PATH = 'tools/cocos2d-console/bin/cocos'
UPGRADE_DIR_SUFFIX = '_upgrade'

X_VERSION_FILES = [
    'cocos/2d/cocos2d.cpp',
    'cocos/cocos2d.cpp'
]

JS_VERSION_FILES = [
    'frameworks/js-bindings/bindings/manual/ScriptingCore.h',
    'frameworks/cocos2d-x/cocos/scripting/js-bindings/manual/ScriptingCore.h'
]

def do_upgrade(proj_path, src_engine_path, dst_engine_path, ignore_version):
    # print("project path : %s" % proj_path)
    # print("src engine : %s" % src_engine_path)
    # print("dst engine : %s" % dst_engine_path)

    proj_info = ProjectInfo(proj_path)
    # proj_info.print_info()

    # check the project information
    if not proj_info.do_check():
        sys.exit(1)

    # check the engine version
    # 1. The engine version of project should same with the src engine version
    # 2. The src engine version should different with dst engine version
    if not ignore_version:
        # get the engine version of the project
        proj_engine_ver = proj_info.get_engine_version()

        if proj_info.get_language() == 'js':
            engine_version_files = JS_VERSION_FILES
        else:
            engine_version_files = X_VERSION_FILES

        # get the engine version of the src engine
        src_engine_ver = None
        for f in engine_version_files:
            src_full_path = os.path.join(src_engine_path, f)
            if os.path.isfile(src_full_path):
                version = get_engine_version(src_full_path, proj_info.get_language())
                if version is not None:
                    src_engine_ver = version
                    break
        print("src engine version : %s" % src_engine_ver)

        # get the engine version of the dst engine
        dst_engine_ver = None
        for f in engine_version_files:
            dst_full_path = os.path.join(dst_engine_path, f)
            if os.path.isfile(dst_full_path):
                version = get_engine_version(dst_full_path, proj_info.get_language())
                if version is not None:
                    dst_engine_ver = version
                    break
        print("dst engine version : %s" % dst_engine_ver)

        # compare the project engine version & src engine version
        if (proj_engine_ver is not None) and (src_engine_ver is not None):
            if proj_engine_ver != src_engine_ver:
                print("The source engine version '%s' is different with the project engine version '%s'."
                      % (src_engine_ver, proj_engine_ver))
                sys.exit(1)

        # compare the dst engine version & src engine version
        if (dst_engine_ver is not None) and (src_engine_ver is not None):
            if dst_engine_ver == src_engine_ver:
                print("The source engine version '%s' is same with the destination engine version '%s'."
                      % (src_engine_ver, dst_engine_ver))
                sys.exit(1)

    temp_folder = os.path.join(os.path.dirname(proj_path), 'temp')
    try:
        if os.path.exists(temp_folder):
            shutil.rmtree(temp_folder)
    except:
        print("Delete folder %s failed. Please delete/rename it first." % temp_folder)
        sys.exit(1)

    work_dir = '%s%s' % (proj_path, UPGRADE_DIR_SUFFIX)
    try:
        if os.path.exists(work_dir):
            shutil.rmtree(work_dir)
    except:
        print("Delete folder %s failed. Please delete/rename it first." % work_dir)
        sys.exit(1)

    # create a new project with src engine
    src_cocos = os.path.join(src_engine_path, CONSOLE_PATH)
    new_proj_with_info(proj_info, src_cocos, temp_folder)

    # copy the new project to upgrade folder
    src_empty_proj_path = os.path.join(temp_folder, proj_info.get_proj_name())
    cpy_cfg = {
        'from' : src_empty_proj_path,
        'to' : work_dir
    }

    excopy.copy_files_with_config(cpy_cfg, src_empty_proj_path, work_dir)
    if os.path.exists(src_empty_proj_path):
        shutil.rmtree(src_empty_proj_path)

    # get the deleted files
    deleted_files = get_deleted_files(proj_path, work_dir)
    remove_deleted_files(work_dir, deleted_files)

    # init the git repo
    run_shell('git init', cwd=work_dir)
    config_author(work_dir)

    commit_files_with_msg(work_dir, "Init project for cocos upgrade.")

    # new branch for upgrade engine
    cmd = "git checkout -b %s" % UPGRADE_BRANCH_NAME
    run_shell(cmd, cwd=work_dir)

    # remove the files in work dir repo
    remove_dir_except(work_dir, [ '.git', '.gitignore'] )

    # new project with dst engine
    dst_cocos = os.path.join(dst_engine_path, CONSOLE_PATH)
    new_proj_with_info(proj_info, dst_cocos, temp_folder)

    # copy the dst empty project into work dir
    dst_empty_proj_path = os.path.join(temp_folder, proj_info.get_proj_name())
    cpy_cfg = {
        'from' : dst_empty_proj_path,
        'to' : work_dir
    }
    excopy.copy_files_with_config(cpy_cfg, dst_empty_proj_path, work_dir)

    # remove the deleted files
    remove_deleted_files(work_dir, deleted_files)

    # remove the temp dir
    shutil.rmtree(temp_folder, ignore_errors=True)

    # commit files
    commit_files_with_msg(work_dir, "Upgrade engine")

    # checkout master branch
    run_shell('git checkout master', cwd=work_dir)

    # remove files
    remove_dir_except(work_dir, [ '.git', '.gitignore' ] )

    # copy project files to work dir
    cpy_cfg = {
        'from' : proj_path,
        'to' : work_dir,
        'exclude' : [
            '.git'
        ]
    }
    excopy.copy_files_with_config(cpy_cfg, proj_path, work_dir)

    # commit files
    commit_files_with_msg(work_dir, "Project development")

    # merge
    has_conflict = False
    try:
        cmd = 'git merge %s' % UPGRADE_BRANCH_NAME
        run_shell(cmd, cwd=work_dir)
    except:
        has_conflict = True
        pass

    if has_conflict:
        try:
            config_merge_tool(work_dir)
            run_shell('git mergetool', cwd=work_dir)
        except:
            print('\nThere are conflicts not resolved. You should solve the conflicts manually.')
            pass

if __name__ == '__main__':
    if not os_is_win32() and not os_is_mac():
        print("Now the tool only supports Mac & Windows.")
        sys.exit(1)

    parser = ArgumentParser(description="Upgrade the engine version of cocos projects.")
    parser.add_argument('-p', dest='proj_path', help='Specify the project path.')
    parser.add_argument('-s', dest='src_engine', help='Specify the source engine path.')
    parser.add_argument('-d', dest='dst_engine', help='Specify the destination engine path.')
    parser.add_argument('-i', action='store_true', dest='ignore_version', help='Not check the version of specified project & engine.')
    (args, unknown) = parser.parse_known_args()

    if args.proj_path is None:
        print('Please specify the project path by -p.')
        sys.exit(1)

    if args.src_engine is None:
        print('Please specify the source engine path by -s.')
        sys.exit(1)

    if args.dst_engine is None:
        print('Please specify the destination engine path by -d.')
        sys.exit(1)

    proj_path = os.path.expanduser(args.proj_path)
    if not os.path.isabs(proj_path):
        proj_path = os.path.abspath(proj_path)
    proj_path = os.path.normpath(proj_path)
    if not check_path(proj_path):
        sys.exit(1)

    src_engine = os.path.expanduser(args.src_engine)
    if not os.path.isabs(src_engine):
        src_engine = os.path.abspath(src_engine)
    src_engine = os.path.normpath(src_engine)
    if not check_path(src_engine):
        sys.exit(1)

    dst_engine = os.path.expanduser(args.dst_engine)
    if not os.path.isabs(dst_engine):
        dst_engine = os.path.abspath(dst_engine)
    dst_engine = os.path.normpath(dst_engine)
    if not check_path(dst_engine):
        sys.exit(1)

    # do upgrade
    do_upgrade(proj_path, src_engine, dst_engine, args.ignore_version)
