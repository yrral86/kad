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
        uri = jan.link
        lang = None
        if type == "py":
            filename = re.sub("file://", "", uri)
            text = slurp(filename)
            text = re.sub("[.()\[\]_]", " ", text)
            lang = 'python'
        elif type == "url":
            text = dump_url(uri)
            for link in dump_links(uri):
                jan.add_metadata("link", link)
            lang = 'english'
        else:
            print "type not yet supported:", type
            print uri
        if lang != None:
            ts = TextStats(text, lang)
            top_twenty = ts.top_words(20)
            for word in top_twenty:
                jan.add_metadata("keyword", word)
            promote_jan(jan)

def slurp(path):
    text = ""
    with open(path) as file:
        text = file.read()
    return text

def dump_url(url):
    return os.popen("lynx -dump -nolist " + url).read()

def dump_links(url):
    string = os.popen("lynx -dump -listonly " +url).read()
    links = {}
    lines = string.split("\n")
    for line in lines:
        if re.match(".*http.*", line):
            links[re.sub(".*(http.*)", "\g<1>", line)] = None
    return links.keys()

def promote_jan(jan):
    with open("marked_up_jan/" + jan.uuid + ".jan", "w") as file:
        file.write(jan.to_json())
    os.remove("new_jan/" + jan.uuid + ".jan")
