#!/usr/bin/env python

import json
import sys

class JAN:
    @staticmethod
    def new_from_json(json_string):
        jan = JAN()
        jan.map = json.loads(json_string)
        return jan

    def __getattr__(self, name):
        return self.map[name]

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
    with open(sys.argv[1]) as file:
        print JAN.new_from_json(file.read()).to_pretty_json(2)