# -*- coding: utf-8 -*-
"""
Created on Tue Sep 13 16:25:47 2016

@author: baronzaaz
"""

class Jan:
    def __init__(self, uuid,jantype,link):
        self.uuid = uuid
        self.jantype = jantype
        self.link = link

    def __str__(self):
        return 'Name: {self.uuid!s}, Catagory: {self.jantype!s}, Value: {self.link!s}'.format(**locals())
