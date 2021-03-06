import os
import re

class F:
    @staticmethod
    def slurp(uri):
        filename = F.path_from_uri(uri)
        text = ""
        with open(filename) as file:
            text = file.read()
        return text

    @staticmethod
    def dump(filename, string):
        with open(filename, "w") as file:
            file.write(string)

    @staticmethod
    def uri_from_path(path):
        return "file://" + os.path.abspath(path)

    @staticmethod
    def path_from_uri(uri):
        return re.sub("file://", "", uri)

    @staticmethod
    def mv(old_uri, new_uri):
        os.rename(F.path_from_uri(old_uri),
                  F.path_from_uri(new_uri))

    @staticmethod
    def file_exists(filename):
        return os.path.isfile(filename)

    @staticmethod
    def json_from_file(filename):
        with open(filename,'r') as content_file:
            content = content_file.read()
        return content

    @staticmethod
    def ensure_directory(directory):
        if not(os.path.isdir(directory)):
            os.makedirs(directory)

    @staticmethod
    def dir_from_uri(uri):
        return os.path.dirname(F.path_from_uri(uri))

    @staticmethod
    def file_basename_from_uri(uri):
        return os.path.basename(re.sub("(.*)\.(.*)", "\g<1>", F.path_from_uri(uri)))