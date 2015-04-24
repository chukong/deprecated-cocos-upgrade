#
# ----------------------------------------------------------------------------
# Compare the difference in three files by a diff file created by DIFFMERGE.
#
# Copyright 2015 (C) lijun
#
# License: MIT
# ----------------------------------------------------------------------------


import os
import sys
import re

def os_is_win32():
    return sys.platform == 'win32'


def os_is_mac():
    return sys.platform == 'darwin'


class CompareFiles(object):
    FIND_DIFF_PATTERN = r"Files.*and.*are different"
    FIND_ONLY_LEFT_PATTERN = r"File only in left: '.*'"
    FIND_ONLY_RIGHT_PATTERN = r"File only in right: '.*'"

    def __init__(self, file_path):
        if os.path.isabs(file_path):
            self.file_path = file_path
        else:
            self.file_path = os.path.abspath(file_path)

        if not os.path.exists(self.file_path):
            print("Can't find file %s" % self.file_path)
            return

        if os_is_mac():
            self.diff_tool = 'diffmerge.sh'
        else:
            self.diff_tool = 'sgdm'

        f = open(file_path, "r")
        self.file_lines = f.readlines()
        f.close()

        match = re.compile('=== Left:.*/').match(self.file_lines[0])
        if match:
            self.left_path = match.group(0).lstrip('=== Left:')

        match = re.compile('=== Right:.*/').match(self.file_lines[1])
        if match:
            self.right_path = match.group(0).lstrip('=== Right:')

    # Compare with dst directory with DIFFMERGE
    def compare(self, dst):
        if self.left_path is None or self.right_path is None:
            return

        diff_pattern = re.compile(CompareFiles.FIND_DIFF_PATTERN)
        only_left_pattern = re.compile(CompareFiles.FIND_ONLY_LEFT_PATTERN)
        only_right_pattern = re.compile(CompareFiles.FIND_ONLY_RIGHT_PATTERN)

        i = 0
        for line in self.file_lines:
            i += 1
            str1 = line.lstrip()
            str2 = str1.rstrip()

            cmd = None
            if diff_pattern.match(str2):
                files = str2.split('\' and \'')
                leftFile = self.left_path + files[0][7:]
                rightFile = self.right_path + files[1][:-15]
                centerFile = os.path.join(dst, files[1][:-15])
                # cocos.Logging.info("Left:%s Right:%s" % (leftFile, rightFile))

                cmd = str.format('%s %s %s %s' % (self.diff_tool, leftFile, centerFile, rightFile))
                cmd += ' -caption Left_file_is_your_code_unchanged' \
                        '________Middle_file_is_your_code_changed' \
                        '________Right_file_is_engine_code_origin'
            # elif only_left_pattern.match(str2):
            #     leftFile = self.left_path + str2[20:][:-1]
            #     centerFile = os.path.join(dst, str2[20:][:-1])
            #     # cocos.Logging.info("Left:%s" % leftFile)
            #
            #     cmd = str.format('%s %s %s' % (self.diff_tool, leftFile, centerFile))
            #     cmd += ' -caption Left_file_is_your_code_unchanged' \
            #             '________Right_file_is_your_code_changed'
            # Since the file is only in the right, we don't care about it.
            # elif only_right_pattern.match(str2):
            #     rightFile = self.right_path + str2[21:][:-1]
            #     centerFile = os.path.join(dst, str2[21:][:-1])
            #     # cocos.Logging.info("Right:%s" % rightFile)
            #
            #     cmd = str.format('%s %s %s' % (self.diff_tool, centerFile, rightFile))
            #     cmd += ' -caption Left_file_is_your_code_changed' \
            #             '________Right_file_is_engine_code_origin'
            if cmd is not None:
                os.system(cmd)