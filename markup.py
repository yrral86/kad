import json
import os
import re

from text_stats import TextStats

class MarkUpHandler:
    @staticmethod
    def new_file(path):
        json_string = slurp(path)
        jan = json.loads(json_string)
        type = jan['type']
        link = jan['link']
        if type == "py":
            filename = re.sub("file://", "", link)
            text = slurp(filename)
            text = re.sub("[.()\[\]_]", " ", text)
            print link
            ts = TextStats(text, 'python')
            ts.print_summary()
        elif type == "url":
            text = dump_url(link)
            print link
            ts = TextStats(text, 'english')
            ts.print_summary()
        else:
            print "type not yet supported:", type
            print link

def slurp(path):
    text = ""
    with open(path) as file:
        text = file.read()
    return text
    
def dump_url(url):
    return os.popen("lynx -dump -nolist " + url).read()