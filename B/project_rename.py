#!/usr/bin/python
# ----------------------------------------------------------------------------
# cocos "rename" plugin lijun
#
# Copyright 2015 (C) cocos2d-x.org
#
# License: MIT
# ----------------------------------------------------------------------------
'''
"rename" plugin for cocos command line tool
'''

# python
import os
import json
import cocos
from collections import OrderedDict


def replace_string(filepath, src_string, dst_string):
    """ From file's content replace specified string
    Arg:
        filepath: Specify a file contains the path
        src_string: old string
        dst_string: new string
    """
    if src_string is None or dst_string is None:
        raise TypeError

    content = ""
    f1 = open(filepath, "rb")
    for line in f1:
        strline = line.decode('utf8')
        if src_string in strline:
            content += strline.replace(src_string, dst_string)
        else:
            content += strline
    f1.close()
    f2 = open(filepath, "wb")
    f2.write(content.encode('utf8'))
    f2.close()
# end of replace_string

class TPCreator(object):

    def __init__(self, project_dir, project_name, project_package):
        self.project_dir = project_dir
        self.project_name = project_name
        self.package_name = project_package
        self.mac_bundleid = project_package
        self.ios_bundleid = project_package
        self.tp_json = 'cocos-project-template.json'

        tp_json_path = os.path.join(project_dir, self.tp_json)
        if not os.path.exists(tp_json_path):
            message = "Fatal: '%s' not found" % tp_json_path
            raise cocos.CCPluginError(message)

        f = open(tp_json_path)
        # keep the key order
        tpinfo = json.load(f, encoding='utf8', object_pairs_hook=OrderedDict)
        self.tp_default_step = tpinfo.pop('do_default')
        # keep the other steps
        self.tp_other_step = tpinfo

    def do_default_step(self):
        default_cmds = self.tp_default_step
        exclude_files = []
        if "exclude_from_template" in default_cmds:
            exclude_files = exclude_files + \
                default_cmds['exclude_from_template']
            default_cmds.pop('exclude_from_template')

        # should ignore teh xx-template-xx.json
        exclude_files.append(self.tp_json)
        self.do_cmds(default_cmds)

    def do_other_step(self, step, not_existed_error=True):
        if step not in self.tp_other_step:
            if not_existed_error:
                # handle as error
                message = "Fatal: creating step '%s' is not found" % step
                raise cocos.CCPluginError(message)
            else:
                # handle as warning
                cocos.Logging.warning("WARNING: Can't find step %s." % step)
                return

        cmds = self.tp_other_step[step]
        self.do_cmds(cmds)

    def do_cmds(self, cmds):
        for k, v in cmds.iteritems():
            # call cmd method by method/cmd name
            # get from
            # http://stackoverflow.com/questions/3951840/python-how-to-invoke-an-function-on-an-object-dynamically-by-name
            try:
                cmd = getattr(self, k)
            except AttributeError:
                raise cocos.CCPluginError("cmd = %s is not found" % k)

            try:
                cmd(v)
            except Exception as e:
                raise cocos.CCPluginError(str(e))

    def append_x_engine(self, v):
        None
        # cocos.Logging.info("> Copying cocos2d-x files...")

# cmd methods below

    def project_rename(self, v):
        """ will modify the file name of the file
        """
        dst_project_dir = self.project_dir
        dst_project_name = self.project_name
        src_project_name = v['src_project_name']
        cocos.Logging.info("> Rename project name from '%s' to '%s'" % (
            src_project_name, dst_project_name))
        files = v['files']
        for f in files:
            src = f.replace("PROJECT_NAME", src_project_name)
            dst = f.replace("PROJECT_NAME", dst_project_name)
            src_file_path = os.path.join(dst_project_dir, src)
            dst_file_path = os.path.join(dst_project_dir, dst)
            if os.path.exists(src_file_path):
                if os.path.exists(dst_file_path):
                    os.remove(dst_file_path)
                os.rename(src_file_path, dst_file_path)
            else:
                cocos.Logging.warning(
                    "%s not found" % os.path.join(dst_project_dir, src))

    def project_replace_project_name(self, v):
        """ will modify the content of the file
        """
        dst_project_dir = self.project_dir
        dst_project_name = self.project_name
        src_project_name = v['src_project_name']
        cocos.Logging.info("> Replace the project name from '%s' to '%s'" % (
            src_project_name, dst_project_name))
        files = v['files']
        for f in files:
            dst = f.replace("PROJECT_NAME", dst_project_name)
            if os.path.exists(os.path.join(dst_project_dir, dst)):
                replace_string(
                    os.path.join(dst_project_dir, dst), src_project_name, dst_project_name)
            else:
                cocos.Logging.warning(
                    "%s not found" % os.path.join(dst_project_dir, dst))

    def project_replace_package_name(self, v):
        """ will modify the content of the file
        """
        dst_project_dir = self.project_dir
        dst_project_name = self.project_name
        src_package_name = v['src_package_name']
        dst_package_name = self.package_name
        cocos.Logging.info("> Replace the project package name from '%s' to '%s'" % (
            src_package_name, dst_package_name))
        files = v['files']
        if not dst_package_name:
            raise cocos.CCPluginError('package name not specified')
        for f in files:
            dst = f.replace("PROJECT_NAME", dst_project_name)
            if os.path.exists(os.path.join(dst_project_dir, dst)):
                replace_string(
                    os.path.join(dst_project_dir, dst), src_package_name, dst_package_name)
            else:
                cocos.Logging.warning(
                    "%s not found" % os.path.join(dst_project_dir, dst))

    def project_replace_mac_bundleid(self, v):
        """ will modify the content of the file
        """
        if self.mac_bundleid is None:
            return

        dst_project_dir = self.project_dir
        dst_project_name = self.project_name
        src_bundleid = v['src_bundle_id']
        dst_bundleid = self.mac_bundleid
        cocos.Logging.info(
            "> Replace the mac bundle id from '%s' to '%s'" % (src_bundleid, dst_bundleid))
        files = v['files']
        for f in files:
            dst = f.replace("PROJECT_NAME", dst_project_name)
            if os.path.exists(os.path.join(dst_project_dir, dst)):
                replace_string(
                    os.path.join(dst_project_dir, dst), src_bundleid, dst_bundleid)
            else:
                cocos.Logging.warning(
                    "%s not found" % os.path.join(dst_project_dir, dst))

    def project_replace_ios_bundleid(self, v):
        """ will modify the content of the file
        """
        if self.ios_bundleid is None:
            return

        dst_project_dir = self.project_dir
        dst_project_name = self.project_name
        src_bundleid = v['src_bundle_id']
        dst_bundleid = self.ios_bundleid
        cocos.Logging.info(
            "> Replace the ios bundle id from '%s' to '%s'" % (src_bundleid, dst_bundleid))
        files = v['files']
        for f in files:
            dst = f.replace("PROJECT_NAME", dst_project_name)
            if os.path.exists(os.path.join(dst_project_dir, dst)):
                replace_string(
                    os.path.join(dst_project_dir, dst), src_bundleid, dst_bundleid)
            else:
                cocos.Logging.warning(
                    "%s not found" % os.path.join(dst_project_dir, dst))

