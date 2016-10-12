#!/usr/bin/env python

import json
import os
import sys
import uuid

from file_utils import F

class JAN:
    NewDir = "new_jan"
    MarkedUpDir = "marked_up_jan"
    NetworkedDir = "networked_jan"

    @staticmethod
    def new_from_json(json_string):
        jan = JAN()
        jan.map = json.loads(json_string)
        return jan

    @staticmethod
    def new_from_uri_and_type(uri, type):
        jan = JAN()
        jan.map = {
                'type': type,
                'link': uri,
                'uuid': JAN.uuid_from_uri(uri),
                'metadata': []
                }
        return jan

    @staticmethod
    def find_from_uri(uri):
        jan = JAN()
        jan.map = {'uuid': JAN.uuid_from_uri(uri)}
        for filename in [jan.networked_path(), jan.marked_up_path(),
                         jan.new_path()]:
             if F.file_exists(filename):
                 jan = JAN.new_from_json(F.slurp(filename))
                 return jan
        return None

    @staticmethod
    def uuid_from_uri(uri):
        return str(uuid.uuid5(uuid.NAMESPACE_URL, uri))

    def promote_new_to_marked_up(self):
        F.dump(self.marked_up_path(), self.to_json())
        os.remove(self.new_path())
        print "promoted jan " + self.uuid + " with link: " + self.link

    def path(self, dir):
        return dir + "/" + self.uuid + ".jan"

    def new_path(self):
        return self.path(self.NewDir)

    def marked_up_path(self):
        return self.path(self.MarkedUpDir)

    def networked_path(self):
        return self.path(self.NetworkedDir)

    def __getattr__(self, name):
        if name in self.map:
            return self.map[name]
        else:
            raise AttributeError

    def add_metadata(self, key, value):
        self.metadata.append({'name': key, 'value': value})

    def deduplicate_metadata(self):
        names = {}
        for meta in self.metadata:
            name, value = meta['name'], meta['value']
            if not(name in names):
                names[name] = {}
            names[name][value] = None
        self.map['metadata'] = []
        for name in names:
            for value in names[name].keys():
                self.add_metadata(name, value)

    def to_json(self):
        self.deduplicate_metadata()
        return json.dumps(self.map)

    def to_pretty_json(self, indent):
        return json.dumps(self.map, indent=indent)


if len(sys.argv) == 2 and "jan.py" in sys.argv[0]:
    print JAN.new_from_json(F.slurp(sys.argv[1])).to_pretty_json(2)