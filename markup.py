import json
import os
import re

from text_stats import TextStats
from jan import JAN

class MarkUpHandler:
    @staticmethod
    def new_file(path):
        json_string = slurp(path)
        jan = JAN.new_from_json(json_string)
        type = jan.type
        link = jan.link
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
            top_ten = ts.top_words(10)
            for word in top_ten:
                jan.add_metadata("keyword", word)
            promote_jan(jan)
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

def promote_jan(jan):
    os.remove("new_jan/" + jan.uuid + ".jan")
    with open("marked_up_jan/" + jan.uuid + ".jan", "w") as file:
        file.write(jan.to_json())
