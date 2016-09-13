#!/usr/bin/env python

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
gi.require_version('WebKit2', '4.0')
from gi.repository import WebKit2

class KAD:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("shell.glade")
        self.builder.connect_signals(self)

        window = self.builder.get_object("main_window")
        accelerators = Gtk.AccelGroup()
        window.add_accel_group(accelerators)
        key, mod = Gtk.accelerator_parse("<Control>l")
        self.location_entry = self.builder.get_object("location_entry")
        self.location_entry.add_accelerator("grab-focus", accelerators, key, mod, Gtk.AccelFlags.VISIBLE)
        browser_window = self.builder.get_object("browser_window")

        self.browser_view = WebKit2.WebView()
        self.browser_view.connect("load-changed", self.load_changed)
        browser_window.add(self.browser_view)

        window.maximize()
        window.show_all()
        self.location_entry.set_text("http://www.google.com")
        self.location_entry_activate()
        self.browser_view.get_settings().set_property("enable-developer-extras",True)

    def load(self, uri):
        self.browser_view.load_uri(uri)

    def main(self):
        Gtk.main()

    def main_window_delete(self, *args):
        Gtk.main_quit(*args)

    def save_button_clicked(self, *args):
        print self.browser_view.get_uri()

    def location_entry_activate(self, *args):
        uri = self.location_entry.get_text()
        self.load(uri)

    def load_changed(self, *args):
        if (args[1] == WebKit2.LoadEvent.FINISHED):
            uri = self.browser_view.get_uri()
            self.location_entry.set_text(uri)

kad = KAD()
kad.main()
