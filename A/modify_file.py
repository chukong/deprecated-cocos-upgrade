import os
import sys
import re


def os_is_win32():
    return sys.platform == 'win32'


def os_is_mac():
    return sys.platform == 'darwin'


class FileModifier(object):
    def __init__(self, file_path):
        if os.path.isabs(file_path):
            self.file_path = file_path
        else:
            self.file_path = os.path.abspath(file_path)

        if not os.path.exists(self.file_path):
            print("Can't find file %s" % self.file_path)
            return

        f = open(file_path, "r")
        self.file_lines = f.readlines()
        f.close()

    def findEngineVesion(self, pattern):
        p = re.compile(pattern)
        for line in self.file_lines:
            match = p.match(line)
            if match:
                ret = match.group(1)
                return ret
        return None

    def replaceString(self, newString, oldString):
        if self.file_lines is None or newString is None or oldString is None:
            return

        i = 0
        for line in self.file_lines:
            i += 1
            str1 = line.lstrip()
            str2 = str1.rstrip()

            result, number = re.subn(oldString, newString, line)
            if number != 0:
                print("Replace %s from line %d" % (str2, i))
                self.file_lines.remove(line)
                self.file_lines.insert(i-1, result)

    def save(self, new_path=None):
        if self.file_lines is None:
            return

        if new_path is None:
            savePath = self.file_path
        else:
            if os.path.isabs(new_path):
                savePath = new_path
            else:
                savePath = os.path.abspath(new_path)

        print("Saving the Android.mk to %s" % savePath)
        f = open(savePath, "w")
        file_content = "".join(self.file_lines)
        f.write(file_content)
        f.close()
        # print("Saving Finished")

